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
from .redact import Redactor, inside_repo

LOCKFILES = ("uv.lock", "poetry.lock", "Pipfile.lock", "requirements.txt", "requirements-lock.txt",
             "environment.yml", "environment.yaml", "renv.lock", "pyproject.toml", "package-lock.json")
ALWAYS = ("question.md", "plan.md", "claims.jsonl", "receipts.jsonl", "checks.json", "published.json",
          "project.json", "data/manifest.json")


class BundleError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


CREDENTIAL_NAMES = (".env", ".nutmeg.credentials.local", ".netrc", ".pgpass", "credentials.json")
CREDENTIAL_SUFFIXES = (".pem", ".key", ".p12", ".pfx")
# Pages that embed sample rows: left out of a bundle without raw data.
SAMPLE_PAGES = ("workspace.html",)


def is_credential(rel):
    name = Path(rel).name
    return name in CREDENTIAL_NAMES or name.startswith(".env.") or Path(rel).suffix.lower() in CREDENTIAL_SUFFIXES


def run_outputs(project):
    """Project-relative paths that any recorded run wrote (raw by provenance, not by folder)."""
    project = Path(project)
    out = set()
    runs = project / "runs"
    if not runs.is_dir():
        return out
    for meta in runs.glob("*/run.json"):
        try:
            record = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for item in record.get("outputs", []):
            path = Path(item.get("path", ""))
            parts = path.parts
            # run.json paths are repository-relative: research/<slug>/...
            if len(parts) > 2 and parts[0] == project.parent.name and parts[1] == project.name:
                out.add(Path(*parts[2:]).as_posix())
    return out


def is_raw(rel, produced=()):
    """Whether a project-relative path is raw data (KTD13)."""
    parts = Path(rel).parts
    if parts[:1] == ("data",) and rel != "data/manifest.json":
        return True
    if parts[:1] == ("runs",) and len(parts) >= 3 and (parts[2] == "outputs" or parts[2] in ("stdout.txt", "stderr.txt")):
        return True
    if parts[:1] == ("figures",) and (".data." in Path(rel).name):
        return True
    # Anything a run wrote, except the reports and provenance files the project publishes.
    return rel in produced and not rel.endswith((".md", ".prov.json"))


def collect(project):
    """(kept, raw, skipped) project-relative paths. Symlinks out of the project and credential files are skipped."""
    project = Path(project)
    real = project.resolve()
    produced = run_outputs(project)
    kept, raw, skipped = [], [], []
    for path in sorted(p for p in project.rglob("*") if p.is_file()):
        rel = path.relative_to(project).as_posix()
        if rel.startswith(("bundles/", "runs/.pending/")) or rel.endswith(".lock"):
            continue
        resolved = path.resolve()
        if resolved != real and real not in resolved.parents:
            skipped.append(f"{rel} (links outside the project)")
            continue
        if is_credential(rel):
            skipped.append(f"{rel} (credentials)")
            continue
        (raw if is_raw(rel, produced) else kept).append(rel)
    return kept, raw, skipped


def chart_assets(project, repo_root):
    """Registered chart images outside the project folder, as repository-relative paths inside the repo."""
    from .figure import load_all

    repo = Path(repo_root).resolve()
    project_real = Path(project).resolve()
    assets = []
    for prov in load_all(project):
        image = prov.get("image")
        if not image:
            continue
        path = (repo / image).resolve()
        if path.is_file() and repo in path.parents and project_real not in path.parents:
            assets.append(path.relative_to(repo).as_posix())
    return sorted(set(assets))


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
    kept, raw, _ = collect(project)
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
        held = len(raw) + sum(1 for k in kept if Path(k).name in SAMPLE_PAGES)
        out.append(f"Raw data left out: {held} file(s), listed in the manifest by hash only "
                   "(the workspace page is left out too: it shows sample rows).")
    return "\n".join(out)


def _payload(path, redactor):
    """File bytes with secrets masked in anything that decodes as text."""
    data = path.read_bytes()
    if len(data) <= 50 * 1024 * 1024:
        try:
            return redactor.text(data.decode("utf-8")).encode("utf-8")
        except UnicodeDecodeError:
            pass
    return data


def bundle(project, repo_root, raw_choice, by, out=None):
    project, repo_root = Path(project), Path(repo_root)
    if raw_choice not in ("yes", "no"):
        raise BundleError("choose --raw yes (include raw data, check its licence) or --raw no (hashes only)")
    redactor = Redactor.for_repo(repo_root)
    kept, raw, skipped = collect(project)
    held = list(raw)
    if raw_choice == "no":
        held += [k for k in kept if Path(k).name in SAMPLE_PAGES]
        kept = [k for k in kept if Path(k).name not in SAMPLE_PAGES]
    include = kept + (raw if raw_choice == "yes" else [])
    stamp = _now().replace(":", "").replace("-", "")
    target = Path(out) if out else project / "bundles" / f"{project.name}-{stamp}.zip"
    if not target.is_absolute():
        target = Path.cwd() / target
    try:
        target = inside_repo(target, repo_root)
    except ValueError as exc:
        raise BundleError(f"write the bundle inside the repository: {exc}")
    target.parent.mkdir(parents=True, exist_ok=True)
    ensure_research_files(repo_root)

    files, omitted = [], []
    env = redactor.obj(environment(repo_root))
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for rel in include:
            path = project / rel
            archive.writestr(f"{project.name}/{rel}", _payload(path, redactor))
            files.append({"path": rel, "sha256": sha256_path(path), "bytes": path.stat().st_size})
        for rel in chart_assets(project, repo_root):
            path = repo_root / rel
            archive.writestr(f"assets/{rel}", _payload(path, redactor))
            files.append({"path": f"assets/{rel}", "sha256": sha256_path(path), "bytes": path.stat().st_size})
        for rel in (held if raw_choice == "no" else []):
            omitted.append({"path": rel, "sha256": sha256_path(project / rel)})
        for name in env.get("lockfiles", []):
            archive.writestr(f"environment/{name}", _payload(repo_root / name, redactor))
        manifest = redactor.obj({
            "contract": "nutmeg-bundle/v1",
            "project": project.name,
            "created": _now(),
            "by": by,
            "raw_data": raw_choice == "yes",
            "files": files,
            "raw_omitted": omitted,
            "skipped": skipped,
            "licences": _licences(repo_root) if raw_choice == "yes" else {},
            "environment": env,
        })
        archive.writestr(f"{project.name}/bundle-manifest.json", json.dumps(manifest, indent=2) + "\n")
    append_receipt(project, "bundle", by=by, raw=raw_choice, files=len(files), omitted=len(omitted),
                   path=target.relative_to(repo_root).as_posix())
    return target, manifest
