"""Gate cards: what the user sees before a run.

A card lists, in this order:

1. data sent and services: hosts found in the code (labelled "detected"),
   hosts the run declares with --sends, local modules and packages nutmeg did
   not inspect, and the AI provider, which receives what the run prints;
2. inputs, with hashes;
3. the exact code and SQL, or only what changed since the last run of the
   same file.

Nutmeg shows; it never blocks a step because of what the card lists.
"""
import argparse
import difflib
import hashlib
import json
import re
import shlex
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .redact import Redactor, inside_repo

TEXT_CODE_LINES = 60  # code lines shown in the permission prompt; the card file has all
TEXT_DIFF_LINES = 80
SCRIPT_EXTENSIONS = (".py", ".r", ".sql")

_URL = re.compile(r"\bhttps?://([A-Za-z0-9.-]+\.[A-Za-z]{2,}|localhost)(?::\d+)?", re.IGNORECASE)
_PY_IMPORT = re.compile(r"^\s*(?:from\s+(\.*[\w.]*)\s+import\b|import\s+([\w.]+(?:\s*,\s*[\w.]+)*))", re.MULTILINE)
_R_LIBRARY = re.compile(r"\b(?:library|require|requireNamespace)\(\s*[\"']?([A-Za-z][\w.]*)", re.MULTILINE)
_R_SOURCE = re.compile(r"\bsource\(\s*[\"']([^\"']+)[\"']", re.MULTILINE)
_R_NAMESPACE = re.compile(r"\b([A-Za-z][\w.]*)::")


class CardError(ValueError):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CardError(message)


def add_run_arguments(parser):
    parser.add_argument("file", help="the script to run: .py, .R or .sql")
    parser.add_argument("--sql", action="append", default=[], metavar="FILE",
                        help="a SQL file the script runs (shown on the card and copied into the run)")
    parser.add_argument("--input", action="append", default=[], metavar="PATH",
                        help="a data file or folder the run reads (hashed and listed)")
    parser.add_argument("--db", metavar="PATH", help="database file for a .sql run (default: in memory)")
    parser.add_argument("--sends", action="append", default=[], metavar="HOST:COLUMNS",
                        help="declare data the run sends to a service, for example api.example.com:player_id,minutes")
    parser.add_argument("--interpreter", help="command to run the file with (default: from the extension)")
    parser.epilog = "Arguments after -- go to the script, for example: nutmeg run a.py --input data.csv -- --season 2025"
    return parser


def split_script_args(args):
    """Split `... -- script args` into (nutmeg args, script args)."""
    args = list(args)
    if "--" in args:
        index = args.index("--")
        return args[:index], args[index + 1:]
    return args, []


def parse_run_args(args):
    own, script_args = split_script_args(args)
    namespace = add_run_arguments(_Parser(prog="nutmeg run", add_help=False)).parse_args(own)
    namespace.script_args = script_args
    return normalise_run_args(namespace)


def normalise_run_args(namespace):
    script_args = list(getattr(namespace, "script_args", None) or [])
    return {
        "file": namespace.file,
        "sql": list(namespace.sql),
        "input": list(namespace.input),
        "db": namespace.db,
        "sends": list(namespace.sends),
        "interpreter": namespace.interpreter,
        "script_args": script_args,
    }


def run_key(run_args, repo_root, cwd):
    """The run's arguments with paths resolved, so the gate and the run agree."""
    def resolve(path):
        return str((Path(cwd) / Path(path).expanduser()).resolve()) if path else path

    return {
        "file": resolve(run_args["file"]),
        "sql": [resolve(p) for p in run_args["sql"]],
        "input": [resolve(p) for p in run_args["input"]],
        "db": resolve(run_args["db"]),
        "sends": run_args["sends"],
        "interpreter": run_args["interpreter"],
        "script_args": run_args["script_args"],
    }


def project_from_global(global_args, cwd):
    if "--project" in global_args:
        index = global_args.index("--project")
        if index + 1 < len(global_args):
            return (Path(cwd) / global_args[index + 1]).resolve()
    return None


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_path(path):
    """Hash a file, or a folder as the hash of its files' paths and hashes."""
    path = Path(path)
    digest = hashlib.sha256()
    if path.is_dir():
        for child in sorted(p for p in path.rglob("*") if p.is_file()):
            digest.update(str(child.relative_to(path)).encode("utf-8"))
            digest.update(sha256_path(child).encode("ascii"))
        return digest.hexdigest()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _size(path):
    path = Path(path)
    if path.is_dir():
        return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
    return path.stat().st_size


def _columns(path):
    path = Path(path)
    if path.suffix.lower() not in (".csv", ".tsv") or not path.is_file():
        return None
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            header = handle.readline().strip()
    except OSError:
        return None
    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    return [c.strip().strip('"') for c in header.split(sep)][:40] if header else None


def _rel(path, repo_root):
    try:
        return str(Path(path).resolve().relative_to(Path(repo_root).resolve()))
    except ValueError:
        return str(path)


# --- what the code touches ------------------------------------------------

def detect_hosts(text):
    return sorted({m.group(1).lower() for m in _URL.finditer(text or "")})


def _local_module(name, search_dirs):
    for folder in search_dirs:
        if (folder / f"{name}.py").is_file() or (folder / name / "__init__.py").is_file() or (folder / name).is_dir():
            return folder / name
    return None


def detect_dependencies(path, text, repo_root, cwd):
    """Return (local modules, packages) the code uses but nutmeg did not inspect."""
    suffix = Path(path).suffix.lower()
    local, packages = set(), set()
    search = [Path(path).parent, Path(cwd), Path(repo_root)]
    if suffix == ".py":
        stdlib = set(getattr(sys, "stdlib_module_names", ()))
        for match in _PY_IMPORT.finditer(text):
            if match.group(1) is not None:
                names = [match.group(1)]
            else:
                names = [n.strip() for n in match.group(2).split(",")]
            for name in names:
                if name.startswith("."):
                    local.add(name)
                    continue
                top = name.split(".")[0]
                if not top or top in stdlib:
                    continue
                found = _local_module(top, search)
                if found is not None:
                    local.add(_rel(found, repo_root) + ("" if found.is_dir() else ".py"))
                else:
                    packages.add(top)
    elif suffix == ".r":
        packages.update(_R_LIBRARY.findall(text))
        packages.update(n for n in _R_NAMESPACE.findall(text) if n not in ("base", "stats", "utils"))
        local.update(_R_SOURCE.findall(text))
    return sorted(local), sorted(packages)


def choose_interpreter(path, override=None, db=None):
    """Return (argv prefix, name, stdin file or None) for running `path`."""
    path = Path(path)
    if override:
        argv = shlex.split(override)
        return argv + [str(path)], argv[0], None
    suffix = path.suffix.lower()
    if suffix == ".py":
        return ["python3", str(path)], "python3", None
    if suffix == ".r":
        return ["Rscript", str(path)], "Rscript", None
    if suffix == ".sql":
        tool = "duckdb" if shutil.which("duckdb") else "sqlite3"
        argv = [tool] + ([str(db)] if db else [])
        return argv, tool, path
    raise CardError(f"nutmeg run supports .py, .R and .sql files; use --interpreter for {path.name}")


# --- building cards -------------------------------------------------------

def _code_entry(path, repo_root):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return {"path": _rel(path, repo_root), "sha256": sha256_path(path), "lines": text.count("\n") + 1, "text": text}


def previous_run(project, rel_file):
    """The latest recorded run of the same file, as its run.json, or None."""
    runs = Path(project) / "runs"
    if not runs.is_dir():
        return None
    latest = None
    for folder in runs.iterdir():
        meta = folder / "run.json"
        if not folder.name.startswith("R") or not meta.is_file():
            continue
        try:
            record = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if record.get("file") == rel_file:
            number = int(folder.name[1:]) if folder.name[1:].isdigit() else 0
            if latest is None or number > latest[0]:
                latest = (number, record, folder)
    return None if latest is None else (latest[1], latest[2])


def _changes(card, project):
    found = previous_run(project, card["file"])
    if found is None:
        return None
    record, folder = found
    changes = {"since": record["id"], "code": [], "inputs": [], "same": False}
    old_code = {c["path"]: c["sha256"] for c in record.get("code", [])}
    for entry in card["code"]:
        if old_code.get(entry["path"]) == entry["sha256"]:
            continue
        old_file = folder / "code" / Path(entry["path"]).name
        old_text = old_file.read_text(encoding="utf-8", errors="replace") if old_file.is_file() else ""
        diff = list(difflib.unified_diff(old_text.splitlines(), entry["text"].splitlines(),
                                         f"{record['id']}/{entry['path']}", entry["path"], lineterm="", n=1))
        changes["code"].append({"path": entry["path"], "diff": diff})
    old_inputs = {i["path"]: i.get("sha256") for i in record.get("inputs", [])}
    for entry in card["inputs"]:
        if old_inputs.get(entry["path"]) != entry.get("sha256"):
            changes["inputs"].append(entry["path"])
    for path in old_inputs:
        if path not in {i["path"] for i in card["inputs"]}:
            changes["inputs"].append(f"{path} (no longer an input)")
    changes["same"] = not changes["code"] and not changes["inputs"]
    return changes


def build_run_card(run_args, repo_root, project, cwd, recorded=True, command=None):
    repo_root, cwd = Path(repo_root), Path(cwd)
    card = {
        "kind": "run" if recorded else "direct",
        "recorded": recorded,
        "project": _rel(project, repo_root),
        "created": _now(),
        "command": command,
        "file": None,
        "interpreter": None,
        "services": {"detected": [], "declared": [], "local_modules": [], "packages": [],
                     "ai_provider": "what the run prints goes back to the AI model in this session"},
        "inputs": [],
        "code": [],
        "changes": None,
        "problems": [],
    }
    paths = [("file", run_args["file"])] + [("sql", p) for p in run_args["sql"]]
    script = None
    for role, raw in paths:
        try:
            resolved = inside_repo(Path(cwd) / Path(raw).expanduser(), repo_root)
        except ValueError as exc:
            card["problems"].append(str(exc))
            continue
        if not resolved.is_file():
            card["problems"].append(f"{raw} does not exist")
            continue
        entry = _code_entry(resolved, repo_root)
        card["code"].append(entry)
        if role == "file":
            script = resolved
            card["file"] = entry["path"]
    if script is not None:
        try:
            _, name, _ = choose_interpreter(script, run_args.get("interpreter"), run_args.get("db"))
            card["interpreter"] = name
        except CardError as exc:
            card["problems"].append(str(exc))

    hosts, local, packages = set(), set(), set()
    for entry in card["code"]:
        hosts.update(detect_hosts(entry["text"]))
        mods, pkgs = detect_dependencies(repo_root / entry["path"], entry["text"], repo_root, cwd)
        local.update(mods)
        packages.update(pkgs)
    card["services"]["detected"] = sorted(hosts)
    card["services"]["local_modules"] = sorted(local)
    card["services"]["packages"] = sorted(packages)
    for declared in run_args["sends"]:
        host, _, columns = declared.partition(":")
        card["services"]["declared"].append({"host": host, "columns": [c for c in columns.split(",") if c]})

    inputs = list(run_args["input"]) + ([run_args["db"]] if run_args.get("db") else [])
    for raw in inputs:
        try:
            resolved = inside_repo(Path(cwd) / Path(raw).expanduser(), repo_root)
        except ValueError as exc:
            card["problems"].append(str(exc))
            continue
        if not resolved.exists():
            card["problems"].append(f"input {raw} does not exist")
            card["inputs"].append({"path": _rel(resolved, repo_root), "sha256": None})
            continue
        card["inputs"].append({"path": _rel(resolved, repo_root), "sha256": sha256_path(resolved),
                               "bytes": _size(resolved), "columns": _columns(resolved)})
    if card["file"]:
        card["changes"] = _changes(card, project)
    return Redactor.for_repo(repo_root).obj(card)


def build_direct_card(tokens, repo_root, project, cwd):
    """A card for a direct interpreter call, which nutmeg will not record."""
    command = shlex.join(tokens)
    script = next((t for t in tokens[1:] if Path(t).suffix.lower() in SCRIPT_EXTENSIONS and not t.startswith("-")), None)
    run_args = {"file": script, "sql": [], "input": [], "db": None, "sends": [], "interpreter": None, "script_args": []}
    if script:
        card = build_run_card(run_args, repo_root, project, cwd, recorded=False, command=command)
        card["changes"] = None
    else:
        # Inline code (python3 -c, duckdb -c, psql -c ...): the command itself is all there is to show.
        card = {
            "kind": "direct", "recorded": False, "project": _rel(project, repo_root), "created": _now(),
            "command": command, "file": None, "interpreter": None,
            "services": {"detected": detect_hosts(command), "declared": [], "local_modules": [], "packages": [],
                         "ai_provider": "what the command prints goes back to the AI model in this session"},
            "inputs": [], "code": [], "changes": None, "problems": [],
        }
    card["interpreter"] = Path(tokens[0]).name
    return Redactor.for_repo(repo_root).obj(card)


def save_pending(project, key, card):
    folder = Path(project) / "runs" / ".pending"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{key}.json"
    path.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    card["card_path"] = str(path)
    return path


def load_pending(project, key):
    path = Path(project) / "runs" / ".pending" / f"{key}.json"
    if not path.is_file():
        return None, path
    try:
        return json.loads(path.read_text(encoding="utf-8")), path
    except (OSError, json.JSONDecodeError):
        return None, path


# --- rendering ------------------------------------------------------------

def _human_bytes(count):
    if count is None:
        return ""
    for unit in ("B", "KB", "MB", "GB"):
        if count < 1024 or unit == "GB":
            return f"{count:.0f} {unit}" if unit == "B" else f"{count:.1f} {unit}"
        count /= 1024


def _numbered(text, limit):
    lines = text.splitlines()
    shown = [f"{i:>4} | {line}" for i, line in enumerate(lines[:limit], start=1)]
    if len(lines) > limit:
        shown.append(f"     … {len(lines) - limit} more lines in the card file")
    return shown


def render_text(card):
    """The card as plain text for the permission prompt and the terminal."""
    out = []
    if card["recorded"]:
        out.append(f"nutmeg run gate · {card['project']} · needs approval; nothing has run yet")
        out.append(f"If approved, nutmeg runs {card['file'] or '?'} with {card['interpreter'] or '?'} "
                   "and records the code, inputs and outputs.")
    else:
        out.append(f"nutmeg research gate · {card['project']} · needs approval; nothing has run yet")
        out.append(f"NOT RECORDED: `{card['command']}` would run directly. Numbers from it cannot be ledger claims.")
        if card.get("file"):
            out.append(f"To record it, run: nutmeg run {card['file']}")
        else:
            out.append("To record analysis, put it in a .py, .R or .sql file and use `nutmeg run <file>`.")

    for problem in card["problems"]:
        out.append(f"PROBLEM: {problem}")

    services = card["services"]
    out.append("")
    out.append("Data sent and services")
    for host in services["detected"]:
        out.append(f"- detected: {host} (a URL in the code)")
    for item in services["declared"]:
        columns = ", ".join(item["columns"]) or "columns not stated"
        out.append(f"- declared: {item['host']}: {columns}")
    if services["local_modules"]:
        out.append(f"- not inspected (local code): {', '.join(services['local_modules'])}")
    if services["packages"]:
        out.append(f"- not inspected (packages): {', '.join(services['packages'])}")
    if not (services["detected"] or services["declared"] or services["local_modules"] or services["packages"]):
        out.append("- no hosts, local modules or packages found")
    out.append(f"- AI provider: {services['ai_provider']}")

    out.append("")
    out.append("Inputs")
    if not card["inputs"]:
        out.append("- none declared (pass --input for each data file the run reads)")
    for item in card["inputs"]:
        if item.get("sha256") is None:
            out.append(f"- {item['path']}: missing")
            continue
        columns = f"; columns: {', '.join(item['columns'])}" if item.get("columns") else ""
        out.append(f"- {item['path']} · {_human_bytes(item.get('bytes'))} · sha256 {item['sha256'][:12]}{columns}")

    changes = card.get("changes")
    if changes and changes["same"]:
        out.append("")
        out.append(f"Same code, SQL and inputs as run {changes['since']}.")
    elif changes:
        out.append("")
        out.append(f"Changes since run {changes['since']}")
        for path in changes["inputs"]:
            out.append(f"- input changed: {path}")
        budget = TEXT_DIFF_LINES
        for entry in changes["code"]:
            lines = [line for line in entry["diff"] if not line.startswith(("---", "+++"))]
            out.extend(lines[:budget])
            if len(lines) > budget:
                out.append(f"     … {len(lines) - budget} more diff lines in the card file")
            budget = max(0, budget - len(lines))
    else:
        for entry in card["code"]:
            out.append("")
            label = "SQL" if entry["path"].lower().endswith(".sql") else "Code"
            out.append(f"{label}: {entry['path']} ({entry['lines']} lines)")
            out.extend(_numbered(entry["text"], TEXT_CODE_LINES))
    if card.get("card_path"):
        out.append("")
        out.append(f"Full card: {card['card_path']}")
    return "\n".join(out)
