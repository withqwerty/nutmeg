"""Score the public eval suite and the private held-out set.

Usage (from the nutmeg repo root):

    NUTMEG_HOLDOUT_DIR=../nutmeg-evals-holdout python3 evals/_scaffold/run_suites.py \
        [--suite both|public|holdout] [--case GLOB] [--runs 1] [--model sonnet] [--judge-model haiku] \
        [--engine auto|plugin|live] [--out DIR] [--loop]

The held-out set lives in a private repository (never in this one). For `claude plugin eval`, which only reads
cases below the plugin, the runner links each held-out case and the replay mocks into a gitignored
`evals-holdout/` folder and removes it afterwards, whatever happens. Results go to a folder outside the
repository (a new temporary folder unless --out names one), so no held-out text lands here.

Engines: `plugin` runs `claude plugin eval` (replay mock, its own sandbox); `live` runs
`evals/_scaffold/run_live.py` (real football-docs server). `auto` uses `live` for cases that grant Bash, because
plugin eval refuses them on some machines, and `plugin` for the rest.

`--loop` is the hill-climbing check: it refuses to start unless the held-out set has at least 10 cases.
"""
import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_live  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LINK_DIR = "evals-holdout"
MARKER = ".nutmeg-run-suites"
MIN_LOOP_CASES = 10
SKIP = {"mocks", "results"}
GATED = ("Bash", "Write", "Edit", "WebFetch", "WebSearch", "mcp__")


class SuiteError(Exception):
    pass


def _inside(path, folder):
    path, folder = Path(path).resolve(), Path(folder).resolve()
    return path == folder or folder in path.parents


def list_cases(eval_dir, pattern=None):
    eval_dir = Path(eval_dir)
    names = sorted(p.name for p in eval_dir.iterdir()
                   if p.is_dir() and not p.name.startswith((".", "_")) and p.name not in SKIP
                   and (p / "prompt.md").is_file())
    return [n for n in names if pattern is None or fnmatch.fnmatch(n, pattern)]


def allowed_tools(eval_dir, name):
    meta = run_live.load_case(name, eval_dir)[1]
    tools = meta.get("allowed_tools") or []
    return [tools] if isinstance(tools, str) else list(tools)


def needs_bash(eval_dir, name):
    return any(t == "Bash" or t.startswith("Bash(") for t in allowed_tools(eval_dir, name))


def holdout_dir(value, root=ROOT):
    """The held-out folder, or None. It must exist and must not sit inside this repository."""
    if not value:
        return None
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise SuiteError(f"NUTMEG_HOLDOUT_DIR is not a folder: {value}")
    if _inside(path, root):
        raise SuiteError("the held-out set must live outside the public repository (KTD14); "
                         f"{value} is inside {root}")
    return path


def results_dir(value, root=ROOT):
    if not value:
        return Path(tempfile.mkdtemp(prefix="nutmeg-suites-"))
    path = Path(value).expanduser().resolve()
    if _inside(path, root):
        raise SuiteError(f"--out must be outside the repository, so held-out results never land in it: {value}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def loop_ready(holdout, minimum=MIN_LOOP_CASES):
    """Refuse the hill-climbing loop without a big enough held-out set."""
    if holdout is None:
        raise SuiteError("the loop needs the held-out set: set NUTMEG_HOLDOUT_DIR")
    count = len(list_cases(holdout))
    if count < minimum:
        raise SuiteError(f"the loop needs at least {minimum} held-out cases; {holdout.name} has {count}")
    return count


def _owner_alive(link):
    """Whether the run that made this link folder is still running (its process id is in the marker)."""
    try:
        pid = int((link / MARKER).read_text().split()[0])
    except (OSError, ValueError, IndexError):
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def check_link_free(root=ROOT):
    """The link folder must be absent or one a finished run left behind; never delete anything else."""
    link = Path(root) / LINK_DIR
    if link.is_symlink() or link.is_file() or (link.exists() and not (link / MARKER).is_file()):
        raise SuiteError(f"{link} exists and is not a folder this runner made; remove it first")
    if link.exists() and _owner_alive(link):
        raise SuiteError(f"another run_suites.py run is using {link}; wait for it to finish")
    return link


@contextmanager
def linked_holdout(holdout, cases, root=ROOT):
    """Link the held-out cases and the replay mocks below the plugin; always remove the links."""
    link = check_link_free(root)
    if link.exists():
        shutil.rmtree(link)  # left over from a run that was killed
    try:
        link.mkdir()  # fails if another run made it in the meantime
    except FileExistsError:
        raise SuiteError(f"another run_suites.py run is using {link}; wait for it to finish")
    try:
        (link / MARKER).write_text(f"{os.getpid()} made by evals/_scaffold/run_suites.py; safe to delete when "
                                   "that process has ended\n")
        (link / "mocks").symlink_to(Path(root) / "evals" / "mocks", target_is_directory=True)
        for name in cases:
            (link / name).symlink_to(holdout / name, target_is_directory=True)
        yield link
    finally:
        shutil.rmtree(link, ignore_errors=True)


def run_plugin(eval_dir_name, name, tools, args, out, root=ROOT):
    """One case through `claude plugin eval`; returns (score, error)."""
    case_out = out / eval_dir_name / name
    case_out.mkdir(parents=True, exist_ok=True)
    cmd = ["claude", "plugin", "eval", str(root), "--eval-dir", eval_dir_name, "--case", name,
           "--runs", str(args.runs), "--ablation", "none", "--scaffold", "--no-publish", "--trust-plugin",
           "--threshold", "0", "--model", args.model, "--judge-model", args.judge_model,
           "--output-dir", str(case_out), "--report", str(case_out / "report.html")]
    grants = [t for t in tools if t.startswith(GATED)]
    if grants:
        cmd += ["--allow-tools", *grants]
    subprocess.run(cmd, cwd=root, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    result = case_out / "aggregate-result.json"
    if not result.is_file():
        return 0.0, "plugin eval wrote no result"
    data = json.loads(result.read_text())
    case = next((c for c in data.get("cases", []) if c.get("name") == name), None)
    if case is None:
        return 0.0, "case not in the plugin eval result"
    errors = [r.get("error") for r in case.get("arms", {}).get("with", []) if r.get("error")]
    return float(case.get("aggregates", {}).get("score") or 0.0), (errors[0] if errors else None)


def run_live_case(eval_dir, name, args, out=None, label="holdout"):
    """One case through run_live; returns (score, error). Each run's verdicts and answer go to `out`."""
    scores = []
    for n in range(args.runs):
        outcome = run_live.run_once(name, args.model, getattr(args, "keep", False), args.judge_model, eval_dir)
        verdicts = outcome["verdicts"]
        scores.append(sum(verdicts.values()) / max(1, len(verdicts)))
        if out is not None:
            folder = Path(out) / label
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{name}-run{n + 1}.json").write_text(json.dumps(outcome, indent=2) + "\n")
            print(f"    run {n + 1}: " + ", ".join(f"{g} {'PASS' if ok else 'FAIL'}" for g, ok in verdicts.items())
                  + f" · ${outcome['cost']:.2f}", flush=True)
    return sum(scores) / max(1, len(scores)), None


def engine_for(eval_dir, name, engine):
    if engine != "auto":
        return engine
    return "live" if needs_bash(eval_dir, name) else "plugin"


def score_suite(label, eval_dir, eval_dir_name, cases, args, out, root=ROOT):
    rows = []
    for name in cases:
        engine = engine_for(eval_dir, name, args.engine)
        if engine == "plugin":
            score, error = run_plugin(eval_dir_name, name, allowed_tools(eval_dir, name), args, out, root)
        else:
            score, error = run_live_case(eval_dir, name, args, out, label)
        rows.append({"suite": label, "case": name, "engine": engine, "score": round(score, 3), "error": error})
        print(f"  {label:8} {name:32} {engine:6} {score:.2f}" + (f"  ({error[:80]})" if error else ""), flush=True)
    return rows


def mean(rows):
    return round(sum(r["score"] for r in rows) / len(rows), 3) if rows else None


def main(argv=None, root=ROOT, environ=None):
    environ = os.environ if environ is None else environ
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--suite", choices=["both", "public", "holdout"], default="both")
    parser.add_argument("--case", help="only cases whose name matches this glob")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--judge-model", default="haiku")
    parser.add_argument("--engine", choices=["auto", "plugin", "live"], default="auto")
    parser.add_argument("--out", help="results folder, outside the repository (default: a new temporary folder)")
    parser.add_argument("--keep", action="store_true", help="keep each live run's work folder")
    parser.add_argument("--loop", action="store_true",
                        help="hill-climbing check: refuse unless the held-out set has at least 10 cases")
    args = parser.parse_args(argv)
    try:
        holdout = holdout_dir(environ.get("NUTMEG_HOLDOUT_DIR"), root)
        if args.loop:
            loop_ready(holdout)
        if args.suite == "holdout" and holdout is None:
            raise SuiteError("--suite holdout needs NUTMEG_HOLDOUT_DIR")
        if holdout is not None and args.suite != "public" and any(
                engine_for(holdout, name, args.engine) == "plugin" for name in list_cases(holdout, args.case)):
            check_link_free(root)
        out = results_dir(args.out, root)
    except SuiteError as exc:
        print(f"run_suites: {exc}", file=sys.stderr)
        return 2

    summary = {"public": None, "holdout": None, "notes": [], "rows": []}
    if args.suite in ("both", "public"):
        cases = list_cases(Path(root) / "evals", args.case)
        if not cases:
            summary["notes"].append("public suite: no case matches --case")
        rows = score_suite("public", Path(root) / "evals", "evals", cases, args, out, root)
        summary["rows"] += rows
        summary["public"] = mean(rows)
    if args.suite in ("both", "holdout"):
        if holdout is None:
            summary["notes"].append("held-out set not run: NUTMEG_HOLDOUT_DIR is not set")
        else:
            cases = list_cases(holdout, args.case)
            if not cases:
                summary["notes"].append("held-out set: no case matches --case")
            if any(engine_for(holdout, name, args.engine) == "plugin" for name in cases):
                with linked_holdout(holdout, cases, root) as link:
                    rows = score_suite("holdout", link, LINK_DIR, cases, args, out, root)
            else:  # live runs read the held-out folder where it is; nothing is linked
                rows = score_suite("holdout", holdout, LINK_DIR, cases, args, out, root)
            summary["rows"] += rows
            summary["holdout"] = mean(rows)

    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for label in ("public", "holdout"):
        value = summary[label]
        count = sum(1 for r in summary["rows"] if r["suite"] == label)
        print(f"{label} score: " + (f"{value:.2f} over {count} case(s)" if value is not None else "not run"))
    for note in summary["notes"]:
        print(note)
    print(f"results: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
