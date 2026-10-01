"""`nutmeg bundle --raw yes|no`: package a project so someone else can check it.

A bundle always holds the question, plan, ledger, receipts, checks, outputs,
figure provenance, run records with their (redacted) code, the data manifest
and the environment (lockfiles, or the interpreter versions and package list).
Raw data is included only with `--raw yes`. Raw data means `data/`, run output
files and printed output, and figure data snapshots; without it the manifest
keeps only their hashes. The gate shows the choice and the team's licence
notes before the bundle is written.
"""
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from .card import sha256_path
from .config import ConfigError, load_effective
from .project import append_receipt, ensure_research_files
from .redact import Redactor

LOCKFILES = ("uv.lock", "poetry.lock", "Pipfile.lock", "requirements.txt", "requirements-lock.txt",
             "environment.yml", "environment.yaml", "renv.lock", "pyproject.toml", "package-lock.json")
TEXT_TYPES = (".md", ".txt", ".json", ".jsonl", ".csv", ".tsv", ".py", ".r", ".sql", ".yml", ".yaml", ".toml",
              ".lock", ".log", ".html")
ALWAYS = ("question.md", "plan.md", "claims.jsonl", "receipts.jsonl", "checks.json", "published.json",
          "project.json", "data/manifest.json")


class BundleError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_raw(rel):
    """Whether a project-relative path is raw data (KTD13)."""
    parts = Path(rel).parts
    if parts[:1] == ("data",) and rel != "data/manifest.json":
        return True
    if parts[:1] == ("runs",) and len(parts) >= 3 and (parts[2] == "outputs" or parts[2] in ("stdout.txt", "stderr.txt")):
        return True
    if parts[:1] == ("figures",) and (".data." in Path(rel).name):
        return True
    return False


def collect(project):
    """(kept, raw) project-relative paths."""
    project = Path(project)
    kept, raw = [], []
    for path in sorted(p for p in project.rglob("*") if p.is_file()):
        rel = path.relative_to(project).as_posix()
        if rel.startswith(("bundles/", "runs/.pending/")) or rel.endswith(".lock"):
            continue
        (raw if is_raw(rel) else kept).append(rel)
    return kept, raw


def environment(repo_root):
    """Lockfiles in the repository, or the interpreter and package list."""
    files = [name for name in LOCKFILES if (Path(repo_root) / name).is_file()]
    if files:
        return {"lockfiles": files}
    try:
        freeze = subprocess.run(["python3", "-m", "pip", "freeze"], capture_output=True, text=True, timeout=60)
        packages = freeze.stdout.splitlines() if freeze.returncode == 0 else []
    except (OSError, subprocess.SubprocessError):
        packages = []
    return {"lockfiles": [], "python": sys.version.split()[0], "packages": packages,
            "note": "no lockfile in the repository; package list from `python3 -m pip freeze`"}


def _licences(repo_root):
    try:
        return load_effective(repo_root)["licences"]
    except ConfigError:
        return {}


def render_preview(project, repo_root, namespace, label):
    raw_choice = getattr(namespace, "raw", None)
    kept, raw = collect(project)
    out = [f"nutmeg bundle gate · {label} · needs approval; nothing has been written yet"]
    if raw_choice not in ("yes", "no"):
        out.append("nutmeg bundle will refuse: choose --raw yes (include raw data) or --raw no (hashes only).")
        return "\n".join(out)
    out.append(f"Always included: {len(kept)} file(s): question, plan, ledger, receipts, outputs, run records and code.")
    if raw_choice == "yes":
        out.append(f"RAW DATA INCLUDED: {len(raw)} file(s) (data/, run outputs, figure snapshots).")
        out += [f"- {r}" for r in raw[:15]]
        licences = _licences(repo_root)
        if licences:
            out.append("Licence notes from the team config:")
            out += [f"- {provider}: {note}" for provider, note in sorted(licences.items())]
        else:
            out.append("Check the data licence before you share raw data; the team config has no licence notes.")
    else:
        out.append(f"Raw data left out: {len(raw)} file(s), listed in the manifest by hash only.")
    return "\n".join(out)


def bundle(project, repo_root, raw_choice, by, out=None):
    project, repo_root = Path(project), Path(repo_root)
    if raw_choice not in ("yes", "no"):
        raise BundleError("choose --raw yes (include raw data, check its licence) or --raw no (hashes only)")
    redactor = Redactor.for_repo(repo_root)
    kept, raw = collect(project)
    include = kept + (raw if raw_choice == "yes" else [])
    stamp = _now().replace(":", "").replace("-", "")
    target = Path(out) if out else project / "bundles" / f"{project.name}-{stamp}.zip"
    if not target.is_absolute():
        target = Path.cwd() / target
    target.parent.mkdir(parents=True, exist_ok=True)
    ensure_research_files(repo_root)

    files, omitted = [], []
    env = environment(repo_root)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for rel in include:
            path = project / rel
            data = path.read_bytes()
            if path.suffix.lower() in TEXT_TYPES:
                try:
                    data = redactor.text(data.decode("utf-8")).encode("utf-8")
                except UnicodeDecodeError:
                    pass
            archive.writestr(f"{project.name}/{rel}", data)
            files.append({"path": rel, "sha256": sha256_path(path), "bytes": path.stat().st_size})
        for rel in raw if raw_choice == "no" else []:
            omitted.append({"path": rel, "sha256": sha256_path(project / rel)})
        for name in env.get("lockfiles", []):
            archive.write(repo_root / name, f"environment/{name}")
        manifest = {
            "contract": "nutmeg-bundle/v1",
            "project": project.name,
            "created": _now(),
            "by": by,
            "raw_data": raw_choice == "yes",
            "files": files,
            "raw_omitted": omitted,
            "licences": _licences(repo_root) if raw_choice == "yes" else {},
            "environment": env,
        }
        archive.writestr(f"{project.name}/bundle-manifest.json", json.dumps(manifest, indent=2) + "\n")
    append_receipt(project, "bundle", by=by, raw=raw_choice, files=len(files), omitted=len(omitted),
                   path=target.relative_to(repo_root).as_posix() if target.is_relative_to(repo_root) else str(target))
    return target, manifest
