"""`nutmeg check`: every number, citation and provider fact in a project's
outputs must trace to the ledger.

Outputs are the project's Markdown files other than the question card and the
plan (for example `report.md`), files under `reports/`, and figure captions
(`figures/*.md`, `figures/*.txt`). The chat is not checked.

Failures:
- orphan: a number with no ledger claim of that value;
- ambiguous: a number that matches more than one claim and names none;
- mismatch: a number next to a claim ID whose value differs;
- unresolved citation: a literature claim without a resolved source and a
  quote match of "normalised" or better;
- unsourced fact: a provider fact without a football-docs source;
- broken link: an interpretation that rests on a missing or withdrawn claim.

Open failures persist in `checks.json`. `nutmeg check --accept <id> --reason`
records an override in the receipts; the failure then stays closed.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .ledger import Ledger
from .project import append_receipt

CHECKS_FILE = "checks.json"
NOT_OUTPUTS = {"question.md", "plan.md"}
GOOD_QUOTE_MATCHES = ("exact", "normalised")

# A number as shown: 1,234.5  -0.41  26%  +3
_NUMBER = re.compile(r"(?<![\w.,/:#-])([-+−]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)(\s?%)?(?![\w/]|\.\d)")
_CLAIM_REF = re.compile(r"\[(C\d+)(?:\s*,\s*C\d+)*\]")
_CLAIM_IDS = re.compile(r"C\d+")

# Words after a four-digit number that make it a count, not a year.
UNITS = ("minutes", "mins", "passes", "shots", "touches", "carries", "actions", "pressures", "duels",
         "metres", "meters", "yards", "km", "kilometres", "points", "goals", "games", "matches",
         "appearances", "players", "events", "rows", "tackles", "sprints")

# Spans whose numbers are not claims.
_SKIP_SPANS = [
    re.compile(r"`[^`]*`"),                                     # inline code
    re.compile(r"\]\([^)]*\)"),                                  # link targets
    re.compile(r"https?://\S+"),                                 # bare URLs
    re.compile(r"\[C\d+(?:\s*,\s*C\d+)*\]"),                     # claim references
    re.compile(r"\b(?:18|19|20|21)\d{2}\s*[/–-]\s*\d{2}(?:\d{2})?\b"),  # seasons 2025/26, 2025-2026
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),                        # ISO dates
    re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),                  # 12/03/2025
    re.compile(r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?(?:\s+\d{4})?\b", re.I),
    re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:,\s*\d{4})?\b", re.I),
    re.compile(r"(?<![\d.,])\d{1,2}\s?[-–]\s?\d{1,2}(?![\d%]|[.,]\d)"),  # scorelines 2-1, 3–0 (not 1.2–1.8 or 0.12-0.18)
    re.compile(r"\b(?:per|/)\s?90\b|\bp90\b", re.I),             # per 90
    re.compile(r"\b(?:80|90|95|99)\s?%\s*(?=(?:CI|confidence|credible|prediction|interval))", re.I),  # 95% CI
    re.compile(r"\b(?:top|bottom|last|first|next)\s+\d+\b", re.I),  # top 5
    re.compile(r"\b\d+(?:st|nd|rd|th)\b"),                        # ordinals
    # years, but not counts such as "2010 minutes"
    re.compile(r"\b(?:18|19|20|21)\d{2}\b(?!\s+(?:" + "|".join(UNITS) + r")\b)", re.I),
]
_LIST_MARKER = re.compile(r"^\s*(?:\d+[.)]\s+|#+\s+\d+(?:\.\d+)*\.?\s)")
_FENCE = re.compile(r"^\s*(```|~~~)")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def output_files(project):
    project = Path(project)
    files = [p for p in project.glob("*.md") if p.name not in NOT_OUTPUTS]
    files += sorted((project / "reports").rglob("*.md")) if (project / "reports").is_dir() else []
    if (project / "figures").is_dir():
        files += sorted(p for p in (project / "figures").iterdir() if p.suffix in (".md", ".txt"))
    return sorted(set(files))


# A dash between two numbers in a range or interval ("1.2–1.8", "0.12-0.18"): each end is a number.
_RANGE_DASH = re.compile(r"(?<=\d)(\s?)[-–](\s?)(?=\d)")


def _masked(line):
    """The line with skipped spans blanked out, so positions stay the same."""
    chars = list(_RANGE_DASH.sub(lambda m: m.group(1) + " " + m.group(2), line))
    marker = _LIST_MARKER.match(line)
    if marker:
        chars[: marker.end()] = " " * marker.end()
    for pattern in _SKIP_SPANS:
        for match in pattern.finditer(line):
            chars[match.start(): match.end()] = " " * (match.end() - match.start())
    return "".join(chars)


def shown_numbers(text):
    """Yield (line number, shown text, decimals, is percent, value, claim IDs named nearby, context)."""
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        masked = _masked(line)
        refs = [(m.start(), _CLAIM_IDS.findall(m.group(0))) for m in _CLAIM_REF.finditer(line)]
        for match in _NUMBER.finditer(masked):
            raw = match.group(1)
            percent = bool(match.group(2))
            plain = raw.replace(",", "").replace("−", "-").lstrip("+")
            decimals = len(plain.split(".")[1]) if "." in plain else 0
            # A claim reference names this number when it is the first one after it,
            # close by, in the same sentence, with no other number in between.
            named = []
            following = next(((start, ids) for start, ids in refs if start >= match.end()), None)
            if following is not None:
                start, ids = following
                gap = masked[match.end():start]
                if len(gap) <= 40 and ". " not in gap and not re.search(r"\d", gap):
                    named = ids
            context = line.strip()
            yield lineno, raw + ("%" if percent else ""), decimals, percent, float(plain), named, context


def _numeric_values(claim):
    value = claim.get("value")
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, str):
        return [float(v.replace(",", "")) for v in re.findall(r"-?\d[\d,]*(?:\.\d+)?", value)]
    if isinstance(value, list):
        return [float(v) for v in value if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return []


def _matches(shown, decimals, percent, value):
    candidates = [value * 100, value] if percent else [value]
    return any(round(c, decimals) == round(shown, decimals) for c in candidates)


def _failure_id(*parts):
    return "F-" + hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:8]


def run_checks(project):
    """Return (failures, warnings). Each failure is a dict with an `id`."""
    project = Path(project)
    claims, problems = Ledger(project / "claims.jsonl").read()
    live = {cid: c for cid, c in claims.items() if c.get("status") != "withdrawn"}
    failures, warnings = [], []

    for lineno, message in problems:
        warnings.append(f"claims.jsonl line {lineno}: {message}")

    for path in output_files(project):
        rel = path.relative_to(project).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, raw, decimals, percent, shown, named, context in shown_numbers(text):
            where = {"file": rel, "line": lineno, "shown": raw, "context": context[:160]}
            if named:
                bad = [cid for cid in named if cid not in live]
                if bad:
                    failures.append({**where, "kind": "broken link", "id": _failure_id("ref", rel, raw, *bad),
                                     "message": f"{raw} cites {', '.join(bad)}, which is not in the ledger or is withdrawn"})
                    continue
                if any(_matches(shown, decimals, percent, v) for cid in named for v in _numeric_values(live[cid])):
                    continue
                values = "; ".join(f"{cid} = {live[cid].get('value')}" for cid in named)
                failures.append({**where, "kind": "mismatch", "id": _failure_id("mismatch", rel, raw, *named),
                                 "message": f"{raw} does not match the claim it cites ({values})"})
                continue
            hits = sorted({cid for cid, claim in live.items()
                           if any(_matches(shown, decimals, percent, v) for v in _numeric_values(claim))})
            if len(hits) == 1:
                continue
            if not hits:
                failures.append({**where, "kind": "orphan", "id": _failure_id("orphan", rel, raw, context[:80]),
                                 "message": f"{raw} has no ledger claim with that value"})
            else:
                failures.append({**where, "kind": "ambiguous", "id": _failure_id("ambiguous", rel, raw, context[:80]),
                                 "message": f"{raw} matches {', '.join(hits)}; name the claim next to it, for example {raw} [{hits[0]}]"})

    for cid, origins in Ledger(project / "claims.jsonl").conflicts().items():
        failures.append({"kind": "id clash", "id": _failure_id("clash", cid, *sorted(origins)), "claim": cid,
                         "message": f"{cid} is used by {len(origins)} different claims (made by "
                                    f"{', '.join(sorted(set(origins.values())))}), probably after a merge; give one "
                                    "of them a new ID in claims.jsonl and in the outputs that cite it"})

    for cid, claim in live.items():
        evidence = claim.get("evidence") or {}
        if claim["kind"] == "computed":
            run_file = project / "runs" / str(evidence.get("run_id")) / "run.json"
            try:
                run = json.loads(run_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                run = None
            if run is None:
                failures.append({"kind": "unrecorded run", "id": _failure_id("run", cid, evidence.get("run_id")),
                                 "claim": cid, "message": f"{cid} ({claim['statement'][:60]}) cites run "
                                 f"{evidence.get('run_id')}, which is not recorded in runs/"})
            elif run.get("status") != "ok":
                failures.append({"kind": "failed run", "id": _failure_id("failedrun", cid, run.get("id")),
                                 "claim": cid, "message": f"{cid} ({claim['statement'][:60]}) cites run "
                                 f"{run.get('id')}, which failed (exit {run.get('exit_code')})"})
        if claim["kind"] == "literature":
            match = evidence.get("match")
            if not evidence.get("source_id") or match not in GOOD_QUOTE_MATCHES:
                state = "no resolved source" if not evidence.get("source_id") else f"quote match is {match or 'missing'}"
                failures.append({"kind": "unresolved citation", "id": _failure_id("lit", cid), "claim": cid,
                                 "message": f"{cid} ({claim['statement'][:60]}): {state}; resolve it with the "
                                            "football-docs paper tools (get_paper or get_web_source, then match_quote)"})
        elif claim["kind"] == "provider_fact":
            if not evidence.get("source"):
                failures.append({"kind": "unsourced fact", "id": _failure_id("fact", cid), "claim": cid,
                                 "message": f"{cid} ({claim['statement'][:60]}): no football-docs source"})
        elif claim["kind"] == "interpretation":
            missing = [c for c in evidence.get("claims", []) if c not in live]
            if missing:
                failures.append({"kind": "broken link", "id": _failure_id("interp", cid, *missing), "claim": cid,
                                 "message": f"{cid} rests on {', '.join(missing)}, which is not in the ledger or is withdrawn"})
    return failures, warnings


def load_state(project):
    path = Path(project) / CHECKS_FILE
    if not path.is_file():
        return {"open": [], "accepted": [], "last_blocked": []}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {}
    state.setdefault("open", [])
    state.setdefault("accepted", [])
    state.setdefault("last_blocked", [])
    return state


def save_state(project, state):
    (Path(project) / CHECKS_FILE).write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check(project):
    """Run the checks, update checks.json, and return the state."""
    failures, warnings = run_checks(project)
    state = load_state(project)
    accepted = {a["id"] for a in state["accepted"]}
    state["open"] = [f for f in failures if f["id"] not in accepted]
    state["warnings"] = warnings
    state["checked_at"] = _now()
    save_state(project, state)
    return state


def accept(project, failure_id, reason, by):
    """Close an open failure with a recorded reason."""
    if not reason or not reason.strip():
        raise ValueError("give a reason with --reason")
    state = check(project)
    match = next((f for f in state["open"] if f["id"] == failure_id), None)
    if match is None:
        raise ValueError(f"{failure_id} is not an open failure; run `nutmeg check` to list them")
    record = {"id": failure_id, "reason": reason.strip(), "by": by, "at": _now(), "failure": match}
    state["accepted"].append(record)
    state["open"] = [f for f in state["open"] if f["id"] != failure_id]
    save_state(project, state)
    append_receipt(project, "check_accepted", failure=failure_id, reason=reason.strip(), by=by,
                   message=match["message"])
    return record


def describe(failure):
    where = f"{failure['file']} line {failure['line']}: " if failure.get("file") else ""
    return f"{failure['id']} {where}{failure['message']}"
