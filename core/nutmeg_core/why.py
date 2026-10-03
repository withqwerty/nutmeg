"""`nutmeg why` and `nutmeg trace`: show what a claim rests on.

`why` prints one claim as a card in a fixed order: the claim, its value or
fact, its definition, its evidence (run and code lines, docs source, Reep ID
and release, paper and quote), filters, n, up to five sample rows, the reason,
and its notes and status history.

`trace` prints the project as a tree of inputs, runs, claims and figures,
labelled with W3C PROV terms (prov:used, prov:wasGeneratedBy,
prov:wasDerivedFrom).
"""
import csv
import json
import re
from pathlib import Path

from .ledger import Ledger
from .redact import inside_repo

SAMPLE_ROWS = 5
_CODE_LINES = re.compile(r"^(?:(?P<file>[^:]+):)?(?P<start>\d+)(?:-(?P<end>\d+))?$")


def _run_record(project, run_id):
    path = Path(project) / "runs" / str(run_id) / "run.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _code_excerpt(project, run, spec):
    """Lines `file:start-end` from the run's copy of the code."""
    match = _CODE_LINES.match(str(spec).strip())
    if not match or run is None:
        return []
    name = match["file"] or (run.get("file") or "")
    code_dir = (Path(project) / "runs" / str(run["id"]) / "code").resolve()
    try:
        copy = inside_repo(name, code_dir) if not Path(name).is_absolute() else None
    except ValueError:
        copy = None
    if copy is None:
        return [f"(code lines must name a file in run {run['id']}'s code copy, not {name})"]
    if not copy.is_file():
        # A bare file name: find the one copy with that name.
        found = [p for p in code_dir.rglob(Path(name).name) if p.is_file()] if code_dir.is_dir() else []
        if len(found) != 1:
            return [f"(code copy {name} not found in run {run['id']})"]
        copy = found[0]
    # Whatever was picked, it must really be inside the run's code copy (no symlinks out of it),
    # and the code copy must be inside the project.
    project_real = Path(project).resolve()
    real_copy = copy.resolve()
    if code_dir not in real_copy.parents or project_real not in code_dir.parents:
        return [f"(code lines must name a file in run {run['id']}'s code copy, not {name})"]
    copy = real_copy
    lines = copy.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(match["start"])
    end = int(match["end"] or start)
    return [f"{n:>4} | {lines[n - 1]}" for n in range(start, min(end, len(lines)) + 1)]


def sample_rows(repo_root, snapshot, limit=SAMPLE_ROWS):
    """Up to `limit` rows from a CSV or JSON data snapshot, as (header, rows)."""
    try:
        path = inside_repo(snapshot, repo_root)
    except ValueError:
        return None, []
    if not path.is_file():
        return None, []
    if path.suffix.lower() in (".csv", ".tsv"):
        with path.open(encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.reader(handle, delimiter="\t" if path.suffix.lower() == ".tsv" else ",")
            header = next(reader, None)
            return header, [row for _, row in zip(range(limit), reader)]
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None, []
        if isinstance(data, dict):
            data = data.get("rows") or data.get("data") or []
        rows = [r for r in data if isinstance(r, dict)][:limit]
        header = list(rows[0]) if rows else None
        return header, [[str(r.get(k, "")) for k in header] for r in rows] if header else []
    return None, []


def _status_text(claim):
    return claim.get("status", "draft")


def why_lines(project, repo_root, claim_id):
    """The why card as a list of lines. Raises KeyError for an unknown claim."""
    ledger = Ledger(Path(project) / "claims.jsonl")
    claims = ledger.claims()
    claim = claims.get(claim_id)
    if claim is None:
        raise KeyError(claim_id)
    evidence = claim.get("evidence") or {}
    kind = claim["kind"]
    out = [f"{claim['id']} · {kind} · {_status_text(claim)}", f"  {claim['statement']}"]

    # 1. Value or fact
    if "value" in claim:
        out.append(f"Value: {claim['value']}")
    # 2. Definition
    definition = evidence.get("definition") or evidence.get("metric")
    if definition:
        out.append(f"Definition: {definition}")

    # 3. Evidence, by kind
    out.append("Evidence:")
    if kind == "computed":
        run = _run_record(project, evidence.get("run_id"))
        if run is None:
            out.append(f"  run {evidence.get('run_id')}: not found in runs/ (the claim has no recorded run)")
        else:
            out.append(f"  run {run['id']}: {run.get('file')} with {run.get('interpreter')} · {run.get('status')}"
                       f" · {run.get('started')}")
            for item in run.get("inputs", []):
                out.append(f"  input: {item['path']} · sha256 {str(item.get('sha256'))[:12]}")
            if evidence.get("code_lines"):
                out.append(f"  code {evidence['code_lines']}:")
                out.extend("  " + line for line in _code_excerpt(project, run, evidence["code_lines"]))
    elif kind == "provider_fact":
        out.append(f"  provider: {evidence.get('provider')}")
        out.append(f"  docs source: {evidence.get('source') or 'none recorded'}")
    elif kind == "identity":
        out.append(f"  Reep ID: {evidence.get('reep_id')} · release {evidence.get('release')}")
        for name, value in sorted((evidence.get("provider_ids") or {}).items()):
            out.append(f"  {name}: {value}")
    elif kind == "literature":
        out.append(f"  citation: {evidence.get('citation')}")
        out.append(f"  source: {evidence.get('source_id') or 'not resolved'}")
        out.append(f"  quote match: {evidence.get('match') or 'not checked'}")
        if evidence.get("quote"):
            out.append(f"  quote: “{evidence['quote']}”")
    elif kind == "definition":
        out.append(f"  source: {evidence.get('source') or 'none recorded'}")
    elif kind == "interpretation":
        out.append("  rests on:")
        for linked in evidence.get("claims", []):
            other = claims.get(linked)
            if other is None:
                out.append(f"    {linked}: not in the ledger")
            else:
                out.append(f"    {linked} · {other['kind']} · {_status_text(other)} · {other['statement']}")

    # 4. Filters, n, sample rows
    if evidence.get("filters"):
        filters = evidence["filters"]
        text = ", ".join(f"{k} = {v}" for k, v in filters.items()) if isinstance(filters, dict) else str(filters)
        out.append(f"Filters: {text}")
    if evidence.get("n") is not None:
        out.append(f"n: {evidence['n']}")
    if evidence.get("snapshot"):
        header, rows = sample_rows(repo_root, evidence["snapshot"])
        if header is None:
            out.append(f"Sample rows: snapshot {evidence['snapshot']} not found")
        else:
            out.append(f"Sample rows (first {len(rows)} of {evidence['snapshot']}):")
            out.append("  " + " | ".join(header))
            out.extend("  " + " | ".join(row) for row in rows)

    # 5. Reason
    if claim.get("why"):
        out.append(f"Why: {claim['why']}")
    rests = claim.get("rests_on")
    if rests:
        out.append(f"Rests on: {rests['type']} · {rests['ref']}")

    # 6. Notes and status history
    out.append("History:")
    for version in ledger.history(claim_id):
        who = version.get("by") or version.get("author") or ""
        note = f" · {version['note']}" if version.get("note") else ""
        out.append(f"  v{version.get('version', '?')} {version.get('at', '')} {version.get('status', 'draft')}"
                   f"{' · ' + who if who else ''}{note}")
    return out


def trace_lines(project, repo_root):
    project = Path(project)
    claims = Ledger(project / "claims.jsonl").claims()
    out = [f"Trace · {project.relative_to(repo_root) if project.is_relative_to(repo_root) else project}"]
    runs = []
    runs_dir = project / "runs"
    if runs_dir.is_dir():
        for folder in runs_dir.iterdir():
            record = _run_record(project, folder.name) if folder.name[1:].isdigit() else None
            if record:
                runs.append(record)
    runs.sort(key=lambda r: int(r["id"][1:]))
    used_claims = set()
    for run in runs:
        out.append(f"{run['id']} {run.get('file')} · {run.get('status')} · {run.get('started')}  [prov:Activity]")
        for item in run.get("inputs", []):
            out.append(f"  prov:used {item['path']} · sha256 {str(item.get('sha256'))[:12]}")
        for code in run.get("code", []):
            out.append(f"  prov:used {code['path']} (code) · sha256 {str(code.get('sha256'))[:12]}")
        for cid, claim in claims.items():
            if claim["kind"] == "computed" and (claim.get("evidence") or {}).get("run_id") == run["id"]:
                used_claims.add(cid)
                value = f" = {claim['value']}" if "value" in claim else ""
                out.append(f"  ← prov:wasGeneratedBy {cid} {claim['statement']}{value} · {claim.get('status')}")
    others = [c for cid, c in claims.items() if cid not in used_claims and c["kind"] != "interpretation"]
    if others:
        out.append("Claims from sources other than runs  [prov:Entity]")
        for claim in others:
            out.append(f"  {claim['id']} {claim['kind']} · {claim['statement']} · {claim.get('status')}")
    interpretations = [c for c in claims.values() if c["kind"] == "interpretation"]
    if interpretations:
        out.append("Interpretations")
        for claim in interpretations:
            rests = ", ".join((claim.get("evidence") or {}).get("claims", []))
            out.append(f"  {claim['id']} {claim['statement']} · {claim.get('status')}  prov:wasDerivedFrom {rests}")
    figures = sorted((project / "figures").glob("*.prov.json")) if (project / "figures").is_dir() else []
    if figures:
        out.append("Figures")
        for path in figures:
            try:
                prov = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            out.append(f"  {prov.get('figure', path.name)}  prov:wasDerivedFrom {', '.join(prov.get('claims', []))}")
    if len(out) == 1:
        out.append("  (no runs or claims yet)")
    return out
