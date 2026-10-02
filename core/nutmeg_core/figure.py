"""Chart provenance: `nutmeg figure register`.

Each figure gets `figures/<name>.prov.json` (the contract in
docs/provenance-contract.md) and a footnote. The footnote has a short form
that fits under a chart and a long form in the provenance file. The data
behind the chart is kept as a CSV or JSON snapshot, so a reviewer sees the
rows that were plotted.
"""
import csv
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .card import sha256_path
from .ledger import Ledger
from .redact import inside_repo

CONTRACT = "nutmeg-figure-provenance/v1"
IMAGE_TYPES = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".pdf")
SNAPSHOT_TYPES = (".csv", ".json")
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")


class FigureError(ValueError):
    pass


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def count_rows(path):
    path = Path(path)
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", errors="replace", newline="") as handle:
            return max(0, sum(1 for _ in csv.reader(handle)) - 1)
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("rows") or data.get("data") or []
    return len(data) if isinstance(data, list) else 0


def footnotes(prov):
    """(short, long) footnote text for a provenance record."""
    sources = " + ".join(s["name"] for s in prov["sources"])
    parts = [f"Source: {sources}"]
    if prov.get("competition_season"):
        parts.append(prov["competition_season"])
    if prov.get("filters"):
        parts.append(prov["filters"])
    parts.append(f"n = {prov['n']}")
    if prov.get("metric"):
        parts.append(prov["metric"])
    parts.append(prov.get("uncertainty") or "no uncertainty shown")
    parts.append(prov["date"])
    if prov["claims"]:
        parts.append(", ".join(prov["claims"]))
    short = " · ".join(parts)

    lines = [f"Figure: {prov['figure']}"]
    for source in prov["sources"]:
        panel = f" (panel {source['panel']})" if source.get("panel") else ""
        lines.append(f"Source{panel}: {source['name']}")
    for label, key in (("Competition and season", "competition_season"), ("Filters", "filters"),
                       ("Metric", "metric"), ("Uncertainty", "uncertainty")):
        lines.append(f"{label}: {prov.get(key) or 'not stated'}")
    lines.append(f"Sample: n = {prov['n']}; {prov['rows']} rows in {prov['data_snapshot']}")
    lines.append(f"Run: {prov.get('run_id') or 'none'}; claims: {', '.join(prov['claims']) or 'none'}")
    lines.append(f"Made: {prov['date']}")
    return short, "\n".join(lines)


def register(project, repo_root, name, data, sources, claims, n=None, competition_season=None, filters=None,
             metric=None, uncertainty=None, run_id=None, image=None, panels=None):
    """Write figures/<name>.prov.json and return the record."""
    project, repo_root = Path(project), Path(repo_root)
    if not NAME.match(name or ""):
        raise FigureError("name the figure with letters, digits, dots, hyphens or underscores, for example shot-map")
    if not data:
        raise FigureError(f"figure {name}: pass --data with the CSV or JSON of the rows the chart plots")
    try:
        snapshot = inside_repo(data, repo_root)
    except ValueError as exc:
        raise FigureError(f"figure {name}: {exc}")
    if snapshot.suffix.lower() not in SNAPSHOT_TYPES or not snapshot.is_file():
        raise FigureError(f"figure {name}: the data snapshot must be an existing .csv or .json file ({data})")
    if not sources:
        raise FigureError(f"figure {name}: pass --source for each data source the chart uses")

    claims = list(dict.fromkeys(claims or []))
    known = Ledger(project / "claims.jsonl").claims()
    missing = [c for c in claims if c not in known]
    if missing:
        raise FigureError(f"figure {name}: {', '.join(missing)} not in the ledger")
    if run_id and not (project / "runs" / run_id / "run.json").is_file():
        raise FigureError(f"figure {name}: run {run_id} not found")

    if image:
        try:
            resolved = inside_repo(image, repo_root)
        except ValueError as exc:
            raise FigureError(f"figure {name}: the chart file must be inside the repository ({exc})")
        if resolved.suffix.lower() not in IMAGE_TYPES:
            raise FigureError(f"figure {name}: --image must be a chart file ({', '.join(IMAGE_TYPES)}), "
                              f"not {resolved.name}")
        image = resolved.relative_to(repo_root.resolve()).as_posix()
    figures = project / "figures"
    figures.mkdir(exist_ok=True)
    kept = figures / f"{name}.data{snapshot.suffix.lower()}"
    if snapshot.resolve() != kept.resolve():
        shutil.copyfile(snapshot, kept)
    rows = count_rows(kept)

    panels = panels or []
    source_list = [{"name": s, **({"panel": panels[i]} if i < len(panels) and panels[i] else {})}
                   for i, s in enumerate(sources)]
    prov = {
        "contract": CONTRACT,
        "figure": name,
        "image": str(Path(image)) if image else None,
        "sources": source_list,
        "competition_season": competition_season,
        "filters": filters,
        "n": n if n is not None else rows,
        "metric": metric,
        "uncertainty": uncertainty,
        "run_id": run_id,
        "claims": claims,
        "data_snapshot": kept.relative_to(repo_root).as_posix(),
        "data_sha256": sha256_path(kept),
        "rows": rows,
        "date": _today(),
    }
    prov["footnote"], prov["footnote_long"] = footnotes(prov)
    (figures / f"{name}.prov.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return prov


def load_all(project):
    figures = Path(project) / "figures"
    out = []
    if figures.is_dir():
        for path in sorted(figures.glob("*.prov.json")):
            try:
                out.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                out.append({"figure": path.name, "error": "unreadable provenance file"})
    return out
