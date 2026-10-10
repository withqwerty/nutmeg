"""`nutmeg data add|list`: where each input file came from, and what it looked like then.

Each entry in a project's `data/manifest.json` records a file's path, sha256, size, source, licence, retrieval date,
who added it, and a short profile of a CSV (rows, columns, fully duplicated rows, repeated values in ID columns,
empty columns). The run gate card shows each input's provenance; `nutmeg check` warns about run inputs with none.
A provenance record does not make data correct: it makes it possible to see where it came from and whether it has
changed, and its profile surfaces common scrape errors (double-counted rows) before they reach a claim.
"""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .card import sha256_path
from .project import append_receipt
from .redact import inside_repo

MANIFEST = "data/manifest.json"
PROFILE_ROWS = 2_000_000


class ProvenanceError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(project):
    path = Path(project) / MANIFEST
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    data.setdefault("files", [])
    return data


def lookup(project, rel):
    return next((f for f in load(project)["files"] if f.get("path") == rel), None)


def _id_like(name):
    low = name.lower()
    return low == "id" or low.endswith("_id") or low.endswith("id") and len(low) <= 10


def profile(path):
    """A short profile of a CSV file: rows, columns, duplicated rows, repeated ID values, empty columns."""
    path = Path(path)
    if path.suffix.lower() not in (".csv", ".tsv"):
        return None
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, delimiter="\t" if path.suffix.lower() == ".tsv" else ",")
            header = next(reader, [])
            seen, dupes, rows = set(), 0, 0
            ids = {i: {} for i, name in enumerate(header) if _id_like(name)}
            filled = [0] * len(header)
            for row in reader:
                rows += 1
                if rows > PROFILE_ROWS:
                    return {"rows": f"more than {PROFILE_ROWS}", "columns": header}
                key = tuple(row)
                if key in seen:
                    dupes += 1
                else:
                    seen.add(key)
                for i, value in enumerate(row[:len(header)]):
                    if value.strip():
                        filled[i] += 1
                    if i in ids:
                        ids[i][value] = ids[i].get(value, 0) + 1
    except (OSError, UnicodeDecodeError, csv.Error):
        return None
    repeated = {header[i]: sum(1 for c in counts.values() if c > 1) for i, counts in ids.items()}
    return {"rows": rows, "columns": header, "duplicate_rows": dupes,
            "repeated_ids": {k: v for k, v in repeated.items() if v},
            "empty_columns": [header[i] for i, n in enumerate(filled) if n == 0]}


def concerns(entry):
    """Plain-language notes about a profile that are worth a look before analysis."""
    prof = entry.get("profile") or {}
    out = []
    if prof.get("duplicate_rows"):
        out.append(f"{prof['duplicate_rows']} row(s) are exact duplicates of another row")
    for column, count in (prof.get("repeated_ids") or {}).items():
        out.append(f"{count} value(s) of {column} appear more than once")
    if prof.get("empty_columns"):
        out.append(f"empty column(s): {', '.join(prof['empty_columns'])}")
    return out


def add(project, repo_root, file, source, by, licence=None, retrieved=None, note=None):
    project, repo_root = Path(project), Path(repo_root)
    try:
        path = inside_repo(file, repo_root)
    except ValueError as exc:
        raise ProvenanceError(str(exc))
    if not path.is_file():
        raise ProvenanceError(f"{file} does not exist")
    if not (source or "").strip():
        raise ProvenanceError("say where the file came from with --source (a URL, a provider and product, or a person)")
    rel = path.relative_to(repo_root.resolve() if path.is_relative_to(repo_root.resolve()) else repo_root).as_posix()
    entry = {"path": rel, "sha256": sha256_path(path), "bytes": path.stat().st_size, "source": source.strip(),
             "licence": licence, "retrieved": retrieved, "added_at": _now(), "added_by": by, "note": note,
             "profile": profile(path)}
    data = load(project)
    data["files"] = [f for f in data["files"] if f.get("path") != rel] + [entry]
    target = project / MANIFEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    append_receipt(project, "data_added", path=rel, sha256=entry["sha256"], source=entry["source"], by=by)
    return entry


def state(repo_root, entry):
    """'current', 'changed' (the file differs from when it was recorded) or 'missing'."""
    path = Path(repo_root) / entry["path"]
    if not path.is_file():
        return "missing"
    return "current" if sha256_path(path) == entry.get("sha256") else "changed"
