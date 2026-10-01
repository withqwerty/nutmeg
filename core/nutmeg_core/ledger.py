"""The claim ledger: one JSON record per line in a project's `claims.jsonl`.

Every number, provider fact, ID, citation, definition and interpretation in a
project's outputs is a claim. Each kind needs its own evidence. The file is
append-only: a change to a claim appends a new version with the same ID, and
the latest version wins on read. Git merges concurrent appends with the
`merge=union` attribute.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

KINDS = ("computed", "provider_fact", "identity", "literature", "definition", "interpretation")

# Evidence fields each kind must carry. Fields that a check verifies later
# (a provider fact's docs source, a citation's quote match) are optional here,
# so an unresolved claim can still be recorded and then reported as open.
REQUIRED_EVIDENCE = {
    "computed": ("run_id",),
    "provider_fact": ("provider",),
    "identity": ("reep_id", "release"),
    "literature": ("citation",),
    "definition": ("definition",),
    "interpretation": ("claims",),
}

STATUSES = ("draft", "verified", "disputed", "withdrawn")
INTERPRETATION_STATUSES = ("draft", "supported", "contested", "withdrawn")

REST_TYPES = ("docs", "registry", "rule", "user", "paper", "claim")

# A reason is one sentence; the detail lives in rests_on.
MAX_WHY_LENGTH = 240

# Fields nutmeg sets on write; callers do not supply them.
SYSTEM_FIELDS = ("version", "at")


class ClaimError(ValueError):
    """A claim record that fails validation. `field` names the bad field."""

    def __init__(self, field, message):
        super().__init__(f"{field}: {message}")
        self.field = field


def statuses_for(kind):
    return INTERPRETATION_STATUSES if kind == "interpretation" else STATUSES


def validate(record):
    """Raise ClaimError if the record is not a valid claim."""
    if not isinstance(record, dict):
        raise ClaimError("record", "must be a JSON object")
    claim_id = record.get("id")
    if not isinstance(claim_id, str) or not claim_id.strip():
        raise ClaimError("id", "missing claim ID")
    kind = record.get("kind")
    if kind not in KINDS:
        raise ClaimError("kind", f"unknown kind {kind!r}; use one of {', '.join(KINDS)}")
    statement = record.get("statement")
    if not isinstance(statement, str) or not statement.strip():
        raise ClaimError("statement", "missing the text of the claim as it appears in the output")

    status = record.get("status", "draft")
    if status not in statuses_for(kind):
        if kind == "interpretation" and status == "verified":
            raise ClaimError("status", "an interpretation is never verified; use supported or contested")
        raise ClaimError("status", f"unknown status {status!r} for a {kind} claim; use one of {', '.join(statuses_for(kind))}")

    evidence = record.get("evidence")
    if not isinstance(evidence, dict):
        raise ClaimError("evidence", f"a {kind} claim needs an evidence object with {', '.join(REQUIRED_EVIDENCE[kind])}")
    for field in REQUIRED_EVIDENCE[kind]:
        value = evidence.get(field)
        if value is None or value == "" or value == []:
            raise ClaimError(f"evidence.{field}", f"a {kind} claim needs evidence.{field}")

    if kind == "computed" and "value" not in record:
        raise ClaimError("value", "a computed claim needs the value it shows")
    if kind == "interpretation":
        linked = evidence["claims"]
        if not isinstance(linked, list) or not all(isinstance(c, str) and c for c in linked):
            raise ClaimError("evidence.claims", "must be a list of claim IDs this interpretation rests on")
        if claim_id in linked:
            raise ClaimError("evidence.claims", "an interpretation cannot rest on itself")

    rests_on = record.get("rests_on")
    if rests_on is not None:
        if not isinstance(rests_on, dict) or rests_on.get("type") not in REST_TYPES or not rests_on.get("ref"):
            raise ClaimError("rests_on", f"must be {{type, ref}} with type one of {', '.join(REST_TYPES)}")
    for field in ("why", "note", "author", "signer"):
        if field in record and record[field] is not None and not isinstance(record[field], str):
            raise ClaimError(field, "must be text")
    why = record.get("why")
    if isinstance(why, str) and ("\n" in why.strip() or len(why) > MAX_WHY_LENGTH):
        raise ClaimError("why", f"keep the reason to one line of at most {MAX_WHY_LENGTH} characters; put detail in rests_on")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Ledger:
    """Read and append claims in one `claims.jsonl` file."""

    def __init__(self, path, redactor=None):
        self.path = Path(path)
        self.redactor = redactor

    def read(self):
        """Return (latest claim per ID in first-seen order, problems).

        A problem is (line number, message). A bad line never hides the
        valid lines around it.
        """
        latest, problems = {}, []
        if not self.path.exists():
            return latest, problems
        with self.path.open(encoding="utf-8") as handle:
            for lineno, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    problems.append((lineno, f"not valid JSON ({exc.msg})"))
                    continue
                try:
                    validate(record)
                except ClaimError as exc:
                    problems.append((lineno, f"claim {record.get('id', '?') if isinstance(record, dict) else '?'}: {exc}"))
                    continue
                latest[record["id"]] = record
        return latest, problems

    def claims(self):
        return self.read()[0]

    def get(self, claim_id):
        return self.claims().get(claim_id)

    def history(self, claim_id):
        """Every valid version of one claim, oldest first."""
        versions = []
        if not self.path.exists():
            return versions
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict) and record.get("id") == claim_id:
                    versions.append(record)
        return versions

    def next_id(self):
        highest = 0
        for claim_id in self.claims():
            if claim_id[:1] == "C" and claim_id[1:].isdigit():
                highest = max(highest, int(claim_id[1:]))
        return f"C{highest + 1}"

    def append(self, record):
        """Validate and append a claim; return the record as written.

        A record without an ID gets the next free ID. A record with an
        existing ID becomes that claim's next version.
        """
        record = {k: v for k, v in dict(record).items() if k not in SYSTEM_FIELDS}
        if not record.get("id"):
            record["id"] = self.next_id()
        record.setdefault("status", "draft")
        if self.redactor is not None:
            record = self.redactor.obj(record)
        validate(record)
        record["version"] = len(self.history(record["id"])) + 1
        record["at"] = _now()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record

    def update(self, claim_id, **changes):
        """Append a new version of an existing claim with some fields changed."""
        current = self.get(claim_id)
        if current is None:
            raise KeyError(claim_id)
        return self.append({**current, **changes})
