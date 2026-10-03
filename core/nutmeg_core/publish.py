"""`nutmeg publish`: approve a project's outputs for publication.

Publish refuses while `nutmeg check` has open problems. Otherwise it records
what was published (each output file and figure with its hash) in
`published.json` and a receipt, and with `--to DIR` copies the outputs there.
The gate hook shows the preview (each figure's n, filters and first rows)
before publish runs.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from . import check as checks
from .card import sha256_path
from .figure import IMAGE_TYPES, load_all
from .project import append_receipt
from .bundle import RedactionError, write_redacted
from .redact import Redactor, inside_repo
from .why import sample_rows

PREVIEW_ROWS = 3


class PublishError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def preview(project, repo_root):
    """What a publish would release, plus the open problems that block it."""
    project, repo_root = Path(project), Path(repo_root)
    state = checks.check(project)
    outputs = [p.relative_to(repo_root).as_posix() for p in checks.output_files(project)]
    figures = []
    for prov in load_all(project):
        if prov.get("error"):
            figures.append({"figure": prov["figure"], "error": prov["error"]})
            continue
        header, rows = sample_rows(repo_root, prov.get("data_snapshot", ""), limit=PREVIEW_ROWS)
        figures.append({
            "figure": prov["figure"],
            "image": prov.get("image"),
            "n": prov.get("n"),
            "rows": prov.get("rows"),
            "filters": prov.get("filters"),
            "sources": [s["name"] for s in prov.get("sources", [])],
            "claims": prov.get("claims", []),
            "footnote": prov.get("footnote"),
            "header": header,
            "first_rows": rows,
        })
    return {"outputs": outputs, "figures": figures, "open": state["open"]}


def render_preview(data, project_label):
    out = [f"nutmeg publish gate · {project_label} · needs approval; nothing has been published yet"]
    if data["open"]:
        out.append(f"REFUSED: {len(data['open'])} open problem(s) from `nutmeg check`; publish will refuse:")
        out += [f"- {checks.describe(f)}" for f in data["open"][:10]]
        return "\n".join(out)
    out.append("Outputs: " + (", ".join(data["outputs"]) or "none"))
    if not data["figures"]:
        out.append("Figures: none registered (`nutmeg figure register`)")
    for fig in data["figures"]:
        out.append("")
        if fig.get("error"):
            out.append(f"Figure {fig['figure']}: {fig['error']}")
            continue
        out.append(f"Figure {fig['figure']} · n = {fig['n']} · {fig['rows']} rows · filters: {fig['filters'] or 'none stated'}")
        out.append(f"  sources: {', '.join(fig['sources'])} · claims: {', '.join(fig['claims']) or 'none'}")
        if fig["header"]:
            out.append("  " + " | ".join(fig["header"]))
            out += ["  " + " | ".join(row) for row in fig["first_rows"]]
    return "\n".join(out)


def publish(project, repo_root, by, to=None):
    project, repo_root = Path(project), Path(repo_root)
    data = preview(project, repo_root)
    if data["open"]:
        raise PublishError(
            f"{len(data['open'])} open problem(s); fix them or accept each with a reason "
            "(`nutmeg check --accept <id> --reason ...`), then publish again:\n"
            + "\n".join(f"- {checks.describe(f)}" for f in data["open"]))
    files = [repo_root / p for p in data["outputs"]]
    figures_dir = project / "figures"
    for fig in data["figures"]:
        if fig.get("image"):
            try:
                image = inside_repo(fig["image"], repo_root)
            except ValueError as exc:
                raise PublishError(f"figure {fig['figure']}: its chart file is outside the repository ({exc})")
            if image.suffix.lower() not in IMAGE_TYPES:
                raise PublishError(f"figure {fig['figure']}: {fig['image']} is not a chart file")
            if image.is_file():
                files.append(image)
        prov = figures_dir / f"{fig['figure']}.prov.json"
        if prov.is_file():
            files.append(prov)
    real_repo = repo_root.resolve()
    project_real = project.resolve()
    for f in files:
        resolved = f.resolve()
        if real_repo not in resolved.parents:
            raise PublishError(f"{f} links outside the repository; nutmeg will not publish it")
    # Where each file goes: project files keep their place; files from elsewhere in the repository go
    # under _assets/. Two files may never share a destination.
    plan = {}
    for f in files:
        if not f.is_file():
            continue
        resolved = f.resolve()
        rel = (resolved.relative_to(project_real) if project_real in resolved.parents
               else Path("_assets") / resolved.relative_to(real_repo))
        key = rel.as_posix()
        if key in plan and plan[key] != resolved:
            raise PublishError(f"two files would be published as {key}; rename one")
        plan[key] = resolved
    redactor = Redactor.for_repo(repo_root)
    record = {
        "at": _now(),
        "by": by,
        "files": [],
        "figures": [{k: fig.get(k) for k in ("figure", "n", "rows", "filters", "claims")} for fig in data["figures"]],
        "to": None,
    }
    if to:
        try:
            target = inside_repo(to, repo_root)
        except ValueError as exc:
            raise PublishError(str(exc))
        target_real = target.resolve()
        # Never write over what is being published: the folder must not be, or hold, any source file.
        for key, source in plan.items():
            destination = (target / key)
            if source == target_real or target_real in source.parents or (
                    destination.exists() and destination.resolve() == source):
                raise PublishError(f"--to {to} holds the files being published ({key}); choose a folder outside them")
        target.mkdir(parents=True, exist_ok=True)
        for key, source in plan.items():
            destination = target / key
            destination.parent.mkdir(parents=True, exist_ok=True)
            # No symlinks on the way: the file must land inside the publish folder.
            if destination.is_symlink() or target_real not in destination.parent.resolve().parents \
                    and destination.parent.resolve() != target_real:
                raise PublishError(f"{destination} leads outside {to}; remove the link and publish again")
            try:
                with open(destination, "wb") as sink:
                    write_redacted(source, sink, redactor)
            except RedactionError as exc:
                destination.unlink(missing_ok=True)
                raise PublishError(str(exc))
            record["files"].append({"path": key, "source": source.relative_to(real_repo).as_posix(),
                                    "sha256": sha256_path(destination)})
        record["to"] = target.relative_to(real_repo).as_posix()
    else:
        record["files"] = [{"path": key, "source": source.relative_to(real_repo).as_posix(),
                            "sha256": sha256_path(source)} for key, source in plan.items()]
    history_path = project / "published.json"
    try:
        history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.is_file() else []
    except json.JSONDecodeError:
        history = []
    history.append(record)
    history_path.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    append_receipt(project, "publish", by=by, files=len(record["files"]), figures=len(record["figures"]), to=record["to"])
    return record
