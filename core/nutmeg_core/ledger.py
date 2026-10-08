"""The claim ledger: one JSON record per line in a project's `claims.jsonl`.

Every number, provider fact, ID, citation, definition and interpretation in a
project's outputs is a claim. Each kind needs its own evidence. The file is
append-only: a change to a claim appends a new version with the same ID, and
the latest version wins on read. Git merges concurrent appends with the
`merge=union` attribute.
"""
import json
import re
import secrets
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

try:  # POSIX only; on other systems appends are not locked
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

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

REST_TYPES = ("docs", "registry", "rule", "user", "paper", "claim", "metric")
# A football-docs metric card or variant ID, for example ppda or ppda.statsbomb-hudl (from list_metrics).
METRIC_REF = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9][a-z0-9_-]*)?$")

# A reason is one sentence; the detail lives in rests_on.
MAX_WHY_LENGTH = 240

# Fields that describe one version's change and are not carried forward.
PER_VERSION_FIELDS = ("note", "by", "previous_status", "previous_signer", "signer")

# Fields whose change makes a claim a new statement that needs checking again.
CONTENT_FIELDS = ("kind", "statement", "value", "evidence", "why", "rests_on", "headline")

# Bookkeeping only the review commands (trusted callers) may write.
SYSTEM_OWNED = ("previous_status", "previous_signer")

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
        if rests_on["type"] == "metric" and not METRIC_REF.match(str(rests_on["ref"])):
            raise ClaimError("rests_on", "a metric reference is a football-docs metric card or variant ID from "
                                         "list_metrics, for example ppda.statsbomb-hudl")
    for field in ("why", "note", "author", "signer", "by"):
        if field in record and record[field] is not None and not isinstance(record[field], str):
            raise ClaimError(field, "must be text")
    why = record.get("why")
    if isinstance(why, str) and ("\n" in why.strip() or len(why) > MAX_WHY_LENGTH):
        raise ClaimError("why", f"keep the reason to one line of at most {MAX_WHY_LENGTH} characters; put detail in rests_on")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@contextmanager
def _locked(path):
    """Hold an exclusive lock on `<path>.lock` while allocating an ID and appending."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(f"{path}.lock", "a") as lock:
        if fcntl is not None:
            fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock, fcntl.LOCK_UN)


APPROVED_STATUSES = ("verified", "supported")


def _guard(record, history, trusted):
    """Apply the rules every new version must follow, whoever writes it."""
    record = dict(record)
    latest = history[-1] if history else None
    if history:
        # Authorship is fixed by the first version; a claim first written without one stays without one.
        if history[0].get("author"):
            record["author"] = history[0]["author"]
        else:
            record.pop("author", None)
    if not trusted:
        for field in SYSTEM_OWNED:
            record.pop(field, None)
    changed = latest is not None and any(record.get(k) != latest.get(k) for k in CONTENT_FIELDS)
    if changed:
        record.pop("signer", None)
        if record.get("status") in APPROVED_STATUSES:
            record["status"] = "draft"
    if not trusted:
        same_approval = (latest is not None and not changed and record.get("status") == latest.get("status")
                         and record.get("signer") == latest.get("signer"))
        if record.get("status") in APPROVED_STATUSES and not same_approval:
            record["status"] = "draft"
        if record.get("signer") and not same_approval:
            record.pop("signer", None)
    return record


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

    def append(self, record, trusted=False):
        """Validate and append a claim; return the record as written.

        A record without an ID gets the next free ID. A record with an
        existing ID becomes that claim's next version. Only trusted callers
        (sign-off and resolve) may set a verified or supported status or a
        signer; a change to a claim's content returns it to draft and clears
        its sign-off, whoever makes it. A claim keeps its first author.
        """
        record = {k: v for k, v in dict(record).items() if k not in SYSTEM_FIELDS}
        with _locked(self.path):
            if not record.get("id"):
                record["id"] = self.next_id()
            record.setdefault("status", "draft")
            if self.redactor is not None:
                record = self.redactor.obj(record)
            validate(record)
            history = self.history(record["id"])
            record = _guard(record, history, trusted)
            if not record.get("origin"):
                # The origin ties a claim's versions together. Two teammates who both create
                # C5 get different origins, so a merged ledger shows the clash instead of
                # silently treating one claim as a new version of the other.
                record["origin"] = history[-1].get("origin") if history else secrets.token_hex(4)
            record["version"] = len(history) + 1
            record["at"] = _now()
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record

    def conflicts(self):
        """Claim IDs used by more than one claim (different origins), with who made each."""
        seen = {}
        for version in self._all_versions():
            origin = version.get("origin") or "legacy"
            seen.setdefault(version["id"], {}).setdefault(origin, version.get("author") or version.get("by") or "unknown")
        return {cid: origins for cid, origins in seen.items() if len(origins) > 1}

    def _all_versions(self):
        if not self.path.exists():
            return []
        out = []
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict) and isinstance(record.get("id"), str):
                    out.append(record)
        return out

    def update(self, claim_id, trusted=False, **changes):
        """Append a new version of an existing claim with some fields changed."""
        current = self.get(claim_id)
        if current is None:
            raise KeyError(claim_id)
        # A note and its author belong to the version that made the change.
        carried = {k: v for k, v in current.items() if k not in PER_VERSION_FIELDS}
        # A claim whose content changes goes back to draft: its earlier check or sign-off no longer holds.
        if "status" not in changes and any(k in changes and changes[k] != current.get(k) for k in CONTENT_FIELDS):
            changes = {**changes, "status": "draft"}
        return self.append({**carried, **changes}, trusted=trusted)
