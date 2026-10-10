"""Research projects: a folder per question under `research/` in the user's repo.

    research/
      .active             the slug of the active project (gitignored, per user)
      .gitignore          ignores .active
      .gitattributes      claims.jsonl and receipts.jsonl merge with union
      <slug>/
        project.json      slug, author, created, data-in-git choice
        question.md       the question card
        plan.md           the plan; each choice has a reason and what it rests on
        claims.jsonl      the claim ledger
        receipts.jsonl    approvals, overrides and gate-setting changes
        runs/             one folder per recorded run
        figures/          charts, provenance files and data snapshots
        data/manifest.json
        .gitignore        written when data stays out of git
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .ledger import METRIC_REF, REST_TYPES, MAX_WHY_LENGTH

RESEARCH_DIR = "research"
ACTIVE_FILE = ".active"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")

# Kept out of git when the project says data stays out (relative to the project).
DATA_IGNORE = (
    "data/*",
    "!data/manifest.json",
    "runs/*/outputs/",
    "figures/*.data.csv",
    "figures/*.data.json",
)

QUESTION_TEMPLATE = """# {title}

**Question:** {question}

**Asked by:** {author} · {date}

**Decision or output it informs:** _(for example a shortlist, a match report, a social post)_

**Data and scope:** _(competitions, seasons, providers)_

**Out of scope:** _(what this project will not answer)_
"""

PLAN_TEMPLATE = """# Plan: {title}

Each choice says why it was made and what it rests on. Add choices with
`nutmeg plan choose`; check them with `nutmeg plan check`.

## Choices
"""


class ProjectError(ValueError):
    pass


def find_repo_root(start):
    """The nearest folder above `start` that holds `.git`, else `start`."""
    start = Path(start).resolve()
    for folder in (start, *start.parents):
        if (folder / ".git").exists():
            return folder
    return start


def open_ledger(project):
    """The project's ledger, redacting secrets on every write."""
    from .ledger import Ledger
    from .redact import Redactor

    return Ledger(Path(project) / "claims.jsonl", redactor=Redactor.for_repo(find_repo_root(project)))


def research_root(repo_root):
    return Path(repo_root) / RESEARCH_DIR


def active_slug(repo_root):
    marker = research_root(repo_root) / ACTIVE_FILE
    try:
        slug = marker.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return slug or None


def active_project(repo_root):
    """The active project folder, or None."""
    slug = active_slug(repo_root)
    if not slug:
        return None
    folder = research_root(repo_root) / slug
    return folder if folder.is_dir() else None


def _ensure_line(path, line):
    """Append `line` to a text file unless it is already there."""
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    if line in existing:
        return
    with path.open("a", encoding="utf-8") as handle:
        if existing and not path.read_text(encoding="utf-8").endswith("\n"):
            handle.write("\n")
        handle.write(line + "\n")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


RESEARCH_IGNORES = (ACTIVE_FILE, ".python-warned", ".config-seen", "*/runs/.pending/", "*/claims.jsonl.lock",
                    "*/bundles/")
RESEARCH_ATTRIBUTES = ("claims.jsonl merge=union", "receipts.jsonl merge=union")


def ensure_research_files(repo_root):
    """Keep research/.gitignore and research/.gitattributes up to date (older projects lack newer lines)."""
    root = research_root(repo_root)
    root.mkdir(parents=True, exist_ok=True)
    for line in RESEARCH_IGNORES:
        _ensure_line(root / ".gitignore", line)
    for line in RESEARCH_ATTRIBUTES:
        _ensure_line(root / ".gitattributes", line)


def set_active(repo_root, slug):
    root = research_root(repo_root)
    if not (root / slug).is_dir():
        raise ProjectError(f"no research project called {slug}")
    (root / ACTIVE_FILE).write_text(slug + "\n", encoding="utf-8")


def create(repo_root, slug, data_in_git, question="", author="unknown", title=None, policy_source="user"):
    """Create a project folder and make it active. Returns the folder."""
    if not SLUG.match(slug):
        raise ProjectError("use a short slug of lowercase letters, digits and hyphens, for example shortlist-lb")
    if data_in_git not in ("yes", "no"):
        raise ProjectError("data_in_git must be yes or no")
    root = research_root(repo_root)
    folder = root / slug
    if folder.exists():
        raise ProjectError(f"research/{slug} already exists; switch to it with `nutmeg open {slug}`")

    ensure_research_files(repo_root)

    for sub in ("runs", "figures", "data"):
        (folder / sub).mkdir(parents=True)
    title = title or slug.replace("-", " ").capitalize()
    date = _now()[:10]
    (folder / "question.md").write_text(
        QUESTION_TEMPLATE.format(title=title, question=question or "_(one sentence)_", author=author, date=date),
        encoding="utf-8",
    )
    (folder / "plan.md").write_text(PLAN_TEMPLATE.format(title=title), encoding="utf-8")
    (folder / "claims.jsonl").touch()
    (folder / "receipts.jsonl").touch()
    (folder / "data" / "manifest.json").write_text(json.dumps({"files": []}, indent=2) + "\n", encoding="utf-8")
    meta = {"slug": slug, "title": title, "author": author, "created": _now(), "data_in_git": data_in_git}
    (folder / "project.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    if data_in_git == "no":
        (folder / ".gitignore").write_text(
            "# Data, run outputs and figure snapshots stay out of git (data_in_git: no).\n"
            + "\n".join(DATA_IGNORE) + "\n",
            encoding="utf-8",
        )
    append_receipt(folder, "project_created", author=author, data_in_git=data_in_git, data_in_git_from=policy_source)
    set_active(repo_root, slug)
    return folder


def close(repo_root):
    """Clear the active marker. Returns the slug that was active, or None."""
    slug = active_slug(repo_root)
    marker = research_root(repo_root) / ACTIVE_FILE
    if marker.exists():
        marker.unlink()
    return slug


# --- the plan's choices ---------------------------------------------------

CHOICE_KINDS = ("question", "metric", "filter", "join", "threshold", "source", "method", "chart", "other")

_CHOICE_HEADING = re.compile(r"^###\s+(?P<kind>[a-z_]+):\s*(?P<choice>.+?)\s*$")
_FIELD = re.compile(r"^\s*[-*]\s*(?P<name>why|rests_on|rests on|after_results|after results):\s*(?P<value>.*?)\s*$",
                    re.IGNORECASE)


def parse_choices(plan_text):
    """Return the choices under `## Choices` as dicts with kind, choice, why, rests_on, after_results, line.

    after_results is set on a choice made after the results were seen: what changed and who asked."""
    choices, in_section, current = [], False, None
    for lineno, line in enumerate(plan_text.splitlines(), start=1):
        if line.startswith("## "):
            in_section = line.strip().lower() == "## choices"
            current = None
            continue
        if not in_section:
            continue
        heading = _CHOICE_HEADING.match(line)
        if heading:
            current = {"kind": heading["kind"], "choice": heading["choice"], "why": None, "rests_on": None,
                       "after_results": None, "line": lineno}
            choices.append(current)
            continue
        if line.startswith("### "):
            current = {"kind": None, "choice": line[4:].strip(), "why": None, "rests_on": None, "after_results": None,
                       "line": lineno}
            choices.append(current)
            continue
        field = _FIELD.match(line)
        if field and current is not None:
            name = field["name"].lower().replace(" ", "_")
            current[name] = field["value"] or None
    return choices


def check_choices(choices):
    """Return a list of problems, each naming the choice."""
    problems = []
    for item in choices:
        name = f"choice \"{item['choice']}\" (plan.md line {item['line']})"
        if item["kind"] not in CHOICE_KINDS:
            problems.append(f"{name}: start the heading with a kind, one of {', '.join(CHOICE_KINDS)}, for example `### metric: npxG per 90`")
        if not item["why"]:
            problems.append(f"{name}: no `why` line; say in one sentence why it was chosen")
        elif len(item["why"]) > MAX_WHY_LENGTH:
            problems.append(f"{name}: the reason is longer than one sentence; move the detail to rests_on")
        rests = (item["rests_on"] or "").split(None, 1)
        if not rests:
            problems.append(f"{name}: no `rests_on` line; name a docs page, rule, paper, claim or the user's words")
        elif rests[0] not in REST_TYPES or len(rests) < 2:
            problems.append(f"{name}: rests_on must be `<type> <reference>` with type one of {', '.join(REST_TYPES)}")
        elif rests[0] == "metric" and not METRIC_REF.match(rests[1].strip()):
            problems.append(f"{name}: a metric reference is a football-docs metric card or variant ID from "
                            "list_metrics, for example ppda.statsbomb-hudl")
    return problems


def add_choice(project, kind, choice, why, rests_type, rests_ref, after_results=None):
    """Append a choice block to plan.md after validating it.

    after_results marks a choice made after the results were seen (what it replaces, and who asked); the
    publish card lists these choices, and earlier choices stay in the plan."""
    item = {"kind": kind, "choice": choice, "why": why, "rests_on": f"{rests_type} {rests_ref}", "line": 0}
    problems = check_choices([item])
    if problems:
        raise ProjectError(problems[0])
    plan = Path(project) / "plan.md"
    text = plan.read_text(encoding="utf-8") if plan.exists() else PLAN_TEMPLATE.format(title=Path(project).name)
    lines = text.rstrip("\n").split("\n")
    try:
        start = next(i for i, line in enumerate(lines) if line.strip().lower() == "## choices")
    except StopIteration:
        lines += ["", "## Choices"]
        start = len(lines) - 1
    # Insert at the end of the Choices section, before any later `## ` section.
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    block = ["", f"### {kind}: {choice}", f"- why: {why}", f"- rests_on: {rests_type} {rests_ref}"]
    if after_results is not None:
        note = " ".join(str(after_results).split())
        if not note:
            raise ProjectError("--after-results needs a note: what this choice replaces and who asked for it")
        block.append(f"- after_results: {note}")
    if end < len(lines):
        block.append("")
    lines[end:end] = block
    plan.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- the locked plan --------------------------------------------------------------------------------------------------
#
# The plan as it stood when the first run started is the primary specification: choices made before any result was
# seen. nutmeg locks it automatically at that run. Later choices, and locked choices that were changed or removed,
# are deviations: they are allowed, and the publish card and workspace list them, so readers can tell what came
# after the results. `nutmeg plan lock --reason` locks again (a new phase of work); each lock records the hash of
# the one before, so the chain shows if a lock file was edited.

PLAN_LOCK = "plan_lock.json"


def _choice_key(choice):
    return f"{choice.get('kind')}: {' '.join(str(choice.get('choice') or '').split())}"


def _choice_hash(choice):
    import hashlib
    text = "\n".join(str(choice.get(k) or "") for k in ("kind", "choice", "why", "rests_on"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def plan_locks(project):
    path = Path(project) / PLAN_LOCK
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data.get("locks", []) if isinstance(data, dict) else []


def lock_plan(project, run_id=None, reason=None, by=None):
    """Lock the plan as it stands now. Returns the lock."""
    import hashlib
    project = Path(project)
    plan = project / "plan.md"
    choices = parse_choices(plan.read_text(encoding="utf-8")) if plan.is_file() else []
    locks = plan_locks(project)
    previous = locks[-1]["hash"] if locks else None
    lock = {"at": _now(), "run_id": run_id, "reason": reason, "by": by, "previous": previous,
            "choices": [{"key": _choice_key(c), "hash": _choice_hash(c)} for c in choices]}
    lock["hash"] = hashlib.sha256(json.dumps(lock, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    locks.append(lock)
    (project / PLAN_LOCK).write_text(json.dumps({"locks": locks}, indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8")
    append_receipt(project, "plan_locked", run_id=run_id, reason=reason, by=by, choices=len(choices), hash=lock["hash"])
    return lock


def lock_chain_ok(project):
    """True when each lock's hash matches its content and points at the one before."""
    import hashlib
    previous = None
    for lock in plan_locks(project):
        body = {k: v for k, v in lock.items() if k != "hash"}
        if lock.get("previous") != previous:
            return False
        if hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()[:16] != lock.get("hash"):
            return False
        previous = lock.get("hash")
    return True


def deviations(project):
    """Choices added, changed or removed since the latest lock: {lock, added, changed, removed}."""
    project = Path(project)
    locks = plan_locks(project)
    if not locks:
        return {"lock": None, "added": [], "changed": [], "removed": []}
    lock = locks[-1]
    plan = project / "plan.md"
    choices = parse_choices(plan.read_text(encoding="utf-8")) if plan.is_file() else []
    locked = {c["key"]: c["hash"] for c in lock["choices"]}
    current = {_choice_key(c): c for c in choices}
    added = [c for k, c in current.items() if k not in locked]
    changed = [c for k, c in current.items() if k in locked and _choice_hash(c) != locked[k]]
    removed = [k for k in locked if k not in current]
    return {"lock": lock, "added": added, "changed": changed, "removed": removed}


def deviation_lines(project):
    dev = deviations(project)
    if dev["lock"] is None:
        plan = Path(project) / "plan.md"
        late = [c for c in (parse_choices(plan.read_text(encoding="utf-8")) if plan.is_file() else [])
                if c.get("after_results")]
        return ["Plan: not locked yet (it locks at the first `nutmeg run`)."] + [
            f"- after seeing results: {c['kind']}: {c['choice']} ({c['after_results']})" for c in late]
    lock = dev["lock"]
    where = f"run {lock['run_id']}" if lock.get("run_id") else (lock.get("reason") or "by hand")
    out = [f"Plan locked at {where} ({lock['at']})."]
    for c in dev["added"]:
        tag = f" · after seeing results ({c['after_results']})" if c.get("after_results") else ""
        out.append(f"- added after the lock: {c['kind']}: {c['choice']}{tag}")
    for c in dev["changed"]:
        out.append(f"- changed after the lock: {c['kind']}: {c['choice']}")
    for key in dev["removed"]:
        out.append(f"- removed after the lock: {key}")
    if not (dev["added"] or dev["changed"] or dev["removed"]):
        out.append("- no changes since the lock")
    if not lock_chain_ok(project):
        out.append("- WARNING: plan_lock.json does not match its own hashes; it was edited by hand")
    return out


def append_receipt(project, kind, **fields):
    """Record an approval, override or setting change in receipts.jsonl."""
    from .redact import Redactor

    record = Redactor.for_repo(find_repo_root(project)).obj({"kind": kind, "at": _now(), **fields})
    with (Path(project) / "receipts.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record
