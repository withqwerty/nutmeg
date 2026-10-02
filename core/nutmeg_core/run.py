"""Record a run: `nutmeg run <file>`.

Each run gets `runs/R<n>/` in the project:

    run.json      what ran: file, interpreter and version, arguments, input and
                  code hashes, exit code, outputs, and the gate card's status
    gate.json     the card shown before the run (or built at run time)
    code/         copies of the script and SQL files
    stdout.txt    redacted
    stderr.txt    redacted
    outputs/      the folder in $NUTMEG_OUTPUT_DIR, for files the script writes

A recorded run is the only evidence for a computed claim.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import card as cards
from .gate import pending_key
from .project import append_receipt
from .redact import Redactor, inside_repo


class RunError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


TEXT_OUTPUTS = (".csv", ".tsv", ".json", ".jsonl", ".txt", ".md", ".html", ".log", ".sql", ".yaml", ".yml")
MAX_REDACT_BYTES = 50 * 1024 * 1024


def _age_seconds(stamp):
    try:
        then = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return float("inf")
    return (datetime.now(timezone.utc) - then).total_seconds()


def _redact_file(path, redactor):
    """Mask secrets in a text output file the run wrote."""
    if path.suffix.lower() not in TEXT_OUTPUTS or path.stat().st_size > MAX_REDACT_BYTES:
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    cleaned = redactor.text(text)
    if cleaned != text:
        path.write_text(cleaned, encoding="utf-8")


def next_run_id(project):
    runs = Path(project) / "runs"
    highest = 0
    if runs.is_dir():
        for folder in runs.iterdir():
            if folder.name.startswith("R") and folder.name[1:].isdigit():
                highest = max(highest, int(folder.name[1:]))
    return f"R{highest + 1}"


def interpreter_version(name):
    """The first line the interpreter prints for --version, or None."""
    if not shutil.which(name):
        return None
    try:
        result = subprocess.run([name, "--version"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    text = (result.stdout or result.stderr or "").strip()
    return text.splitlines()[0] if text else None


def _snapshot(project):
    """mtime and size of every file in the project outside runs/."""
    seen = {}
    for path in Path(project).rglob("*"):
        if path.is_file() and "runs" not in path.relative_to(project).parts[:1]:
            stat = path.stat()
            seen[path] = (stat.st_mtime_ns, stat.st_size)
    return seen


def _changed_files(before, project):
    after = _snapshot(project)
    return sorted(p for p, sig in after.items() if before.get(p) != sig)


def execute(run_args, repo_root, project, cwd, stream=True):
    """Run and record. Returns (run_id, exit_code, run record)."""
    repo_root, project, cwd = Path(repo_root), Path(project), Path(cwd)
    redactor = Redactor.for_repo(repo_root)

    # Refuse before anything runs: paths outside the repo, missing files.
    try:
        script = inside_repo(cwd / Path(run_args["file"]).expanduser(), repo_root)
        for raw in run_args["sql"] + run_args["input"] + ([run_args["db"]] if run_args["db"] else []):
            inside_repo(cwd / Path(raw).expanduser(), repo_root)
    except ValueError as exc:
        raise RunError(str(exc))
    if not script.is_file():
        raise RunError(f"{run_args['file']} does not exist")
    if script.suffix.lower() == ".sql" and run_args["script_args"]:
        raise RunError("a .sql run takes no arguments after --: they would be options to the SQL client")
    try:
        argv, interpreter, stdin_file = cards.choose_interpreter(script, run_args["interpreter"], run_args["db"])
    except cards.CardError as exc:
        raise RunError(str(exc))
    argv = argv + run_args["script_args"]

    # The card as things stand now, and the one the gate showed, if any. A card
    # older than an hour is stale: the run counts as not shown.
    key = pending_key(cards.run_key(run_args, repo_root, cwd))
    shown, pending_path = cards.load_pending(project, key)
    if shown is not None and _age_seconds(shown.get("created")) > cards.PENDING_MAX_AGE_SECONDS:
        shown = None
    current = cards.build_run_card(run_args, repo_root, project, cwd)
    if current["problems"]:
        raise RunError("; ".join(current["problems"]))
    changed_since_gate = []
    if shown is not None:
        shown_inputs = {i["path"]: i.get("sha256") for i in shown.get("inputs", [])}
        shown_code = {c["path"]: c.get("sha256") for c in shown.get("code", [])}
        changed_since_gate += [i["path"] for i in current["inputs"] if shown_inputs.get(i["path"]) != i["sha256"]]
        changed_since_gate += [c["path"] for c in current["code"] if shown_code.get(c["path"]) != c["sha256"]]
        if shown.get("argv") != current.get("argv"):
            changed_since_gate.append("command")

    run_id = next_run_id(project)
    folder = project / "runs" / run_id
    (folder / "code").mkdir(parents=True)
    (folder / "outputs").mkdir()
    for entry in current["code"]:
        # Keep the repository path, so files that share a name do not overwrite each other,
        # and redact the copy: the hash in run.json is the original file's.
        copy = folder / "code" / entry["path"]
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_text(redactor.text(entry["text"]), encoding="utf-8")
    gate_card = shown if shown is not None else current
    gate_card = {**gate_card, "gate_shown": shown is not None and shown.get("review") != "queued",
                 "changed_since_gate": changed_since_gate}
    gate_card.pop("card_path", None)
    (folder / "gate.json").write_text(json.dumps(gate_card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if pending_path.exists():
        pending_path.unlink()

    env = dict(os.environ, NUTMEG_RUN_ID=run_id, NUTMEG_OUTPUT_DIR=str(folder / "outputs"),
               NUTMEG_PROJECT=str(project))
    before = _snapshot(project)
    started, clock = _now(), time.monotonic()
    try:
        stdin = stdin_file.open("rb") if stdin_file else subprocess.DEVNULL
        try:
            result = subprocess.run(argv, cwd=cwd, env=env, stdin=stdin, capture_output=True)
        finally:
            if stdin_file:
                stdin.close()
        exit_code = result.returncode
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
    except OSError as exc:
        exit_code, stdout, stderr = 127, "", f"could not start {interpreter}: {exc}\n"
    duration = round(time.monotonic() - clock, 3)

    stdout, stderr = redactor.text(stdout), redactor.text(stderr)
    (folder / "stdout.txt").write_text(stdout, encoding="utf-8")
    (folder / "stderr.txt").write_text(stderr, encoding="utf-8")

    outputs = []
    for path in sorted(p for p in (folder / "outputs").rglob("*") if p.is_file()):
        _redact_file(path, redactor)
        outputs.append({"path": str(path.relative_to(repo_root)), "sha256": cards.sha256_path(path)})
    for path in _changed_files(before, project):
        outputs.append({"path": str(path.relative_to(repo_root)), "sha256": cards.sha256_path(path)})

    record = {
        "id": run_id,
        "file": current["file"],
        "interpreter": interpreter,
        "interpreter_version": interpreter_version(argv[0]),
        "argv": current["argv"],
        "cwd": cards._rel(cwd, repo_root),
        "code": [{"path": c["path"], "sha256": c["sha256"]} for c in current["code"]],
        "inputs": [{"path": i["path"], "sha256": i["sha256"]} for i in current["inputs"]],
        "sends": current["services"]["declared"],
        "started": started,
        "duration_seconds": duration,
        "exit_code": exit_code,
        "status": "ok" if exit_code == 0 else "failed",
        "gate": {"shown": shown is not None and shown.get("review") != "queued",
                 "queued_for_review": shown is not None and shown.get("review") == "queued",
                 "changed_since_gate": changed_since_gate},
        "outputs": outputs,
    }
    (folder / "run.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    append_receipt(project, "run", run_id=run_id, file=record["file"], status=record["status"],
                   gate_shown=record["gate"]["shown"], queued_for_review=record["gate"]["queued_for_review"],
                   changed_since_gate=changed_since_gate)

    if stream:
        if stdout:
            sys.stdout.write(stdout if stdout.endswith("\n") else stdout + "\n")
        if stderr:
            sys.stderr.write(stderr if stderr.endswith("\n") else stderr + "\n")
    return run_id, exit_code, record


def review_queue(project):
    """Runs that went ahead under run-then-review and nobody has reviewed yet."""
    project = Path(project)
    reviewed = set()
    receipts = project / "receipts.jsonl"
    if receipts.is_file():
        for line in receipts.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("kind") == "run_reviewed":
                reviewed.add(record.get("run_id"))
    queue = []
    runs = project / "runs"
    if runs.is_dir():
        for folder in sorted(runs.iterdir(), key=lambda p: int(p.name[1:]) if p.name[1:].isdigit() else 0):
            meta = folder / "run.json"
            if not meta.is_file():
                continue
            try:
                record = json.loads(meta.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if record.get("gate", {}).get("queued_for_review") and record["id"] not in reviewed:
                queue.append(record)
    return queue
