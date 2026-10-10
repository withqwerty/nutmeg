"""Score the public eval suite and the private held-out set.

Usage (from the nutmeg repo root):

    NUTMEG_HOLDOUT_DIR=../nutmeg-evals-holdout python3 evals/_scaffold/run_suites.py \
        [--suite both|public|holdout] [--case GLOB] [--runs 1] [--model claude-sonnet-5-5] [--judge-model claude-sonnet-5-5] \
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
import fcntl
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


LOCK_FILE = ".evals-holdout.lock"


def check_link_free(root=ROOT):
    """The link folder must be absent or one this runner made; never delete anything else."""
    link = Path(root) / LINK_DIR
    if link.is_symlink() or link.is_file() or (link.exists() and not (link / MARKER).is_file()):
        raise SuiteError(f"{link} exists and is not a folder this runner made; remove it first")
    return link


@contextmanager
def linked_holdout(holdout, cases, root=ROOT):
    """Link the held-out cases and the replay mocks below the plugin; always remove the links.

    An exclusive lock, held from the stale-folder cleanup to the final removal, keeps two runs apart: the second
    one refuses instead of deleting the first one's links.
    """
    lock = open(Path(root) / LOCK_FILE, "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock.close()
        raise SuiteError(f"another run_suites.py run is using {Path(root) / LINK_DIR}; wait for it to finish")
    try:
        link = check_link_free(root)
        if link.exists():
            shutil.rmtree(link)  # left over from a run that was killed (the lock shows nobody is using it)
        link.mkdir()
        try:
            (link / MARKER).write_text("made by evals/_scaffold/run_suites.py; safe to delete when no run holds "
                                       f"{LOCK_FILE}\n")
            (link / "mocks").symlink_to(Path(root) / "evals" / "mocks", target_is_directory=True)
            for name in cases:
                (link / name).symlink_to(holdout / name, target_is_directory=True)
            yield link
        finally:
            shutil.rmtree(link, ignore_errors=True)
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


def check_temp_outside(root=ROOT):
    """Results and live work folders default to the temporary folder; it must not be inside the repository."""
    temp = Path(tempfile.gettempdir()).resolve()
    if _inside(temp, root):
        raise SuiteError(f"the temporary folder ({temp}) is inside the repository; set TMPDIR to a folder outside "
                         "it, so no run output or held-out answer lands here")
    return temp


def run_plugin(eval_dir_name, name, tools, args, out, root=ROOT):
    """One case through `claude plugin eval`; returns (score, error)."""
    # A new folder for every call, so a failed call can never read an earlier call's result.
    (out / eval_dir_name).mkdir(parents=True, exist_ok=True)
    case_out = Path(tempfile.mkdtemp(prefix=f"{name}-", dir=out / eval_dir_name))
    cmd = ["claude", "plugin", "eval", str(root), "--eval-dir", eval_dir_name, "--case", name,
           "--runs", str(args.runs), "--ablation", "none", "--scaffold", "--no-publish", "--trust-plugin",
           "--threshold", "0", "--model", args.model, "--judge-model", args.judge_model,
           "--output-dir", str(case_out), "--report", str(case_out / "report.html")]
    grants = [t for t in tools if t.startswith(GATED)]
    if grants:
        cmd += ["--allow-tools", *grants]
    done = subprocess.run(cmd, cwd=root, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if done.returncode != 0:
        return 0.0, f"plugin eval exited {done.returncode}: {(done.stderr or done.stdout).strip()[-200:]}"
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
        try:
            outcome = run_live.run_once(name, args.model, getattr(args, "keep", False), args.judge_model, eval_dir)
        except run_live.BudgetExceeded as exc:
            print(f"    run {n + 1}: skipped ({exc})", flush=True)
            if not scores:
                return None, f"skipped: {exc}"
            break
        verdicts = outcome["verdicts"]
        scores.append(sum(verdicts.values()) / max(1, len(verdicts)))
        if out is not None:
            folder = Path(out) / label
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{name}-run{n + 1}.json").write_text(json.dumps(outcome, indent=2) + "\n")
            eff = outcome.get("efficiency") or {}
            tok = eff.get("tokens") or {}
            print(f"    run {n + 1}: " + ", ".join(f"{g} {'PASS' if ok else 'FAIL'}" for g, ok in verdicts.items())
                  + f" · ${outcome['cost']:.2f} · {eff.get('turns')} turns · {eff.get('nutmeg_calls')} nutmeg calls"
                  + f" · tokens in {tok.get('input', 0):,}/cache-write {tok.get('cache_write', 0):,}"
                  + f"/cache-read {tok.get('cache_read', 0):,}/out {tok.get('output', 0):,}"
                  + (f" · ENDED: {eff.get('subtype')}" if eff.get("subtype") not in (None, "success") else ""),
                  flush=True)
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
        if score is None:  # skipped before any run (the spend cap): not scored, so it does not count as a zero
            print(f"  {label:8} {name:32} {engine:6} skipped ({error})", flush=True)
            continue
        row = {"suite": label, "case": name, "engine": engine, "score": round(score, 3), "error": error}
        if engine == "live" and out is not None:
            row["efficiency"] = case_efficiency(Path(out) / label, name)
        rows.append(row)
        print(f"  {label:8} {name:32} {engine:6} {score:.2f}" + (f"  ({error[:80]})" if error else ""), flush=True)
    return rows


def _median(values):
    values = sorted(v for v in values if v is not None)
    if not values:
        return None
    mid = len(values) // 2
    return values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2


def case_efficiency(folder, name):
    """Over a case's live runs: median cost, turns and nutmeg calls; turn-limit and error endings; the share of runs
    where every grader passed (pass@1) and whether all of them did (pass^k)."""
    runs = []
    for path in sorted(Path(folder).glob(f"{name}-run*.json")):
        try:
            outcome = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        eff = outcome.get("efficiency") or {}
        verdicts = outcome.get("verdicts") or {}
        runs.append({"cost": outcome.get("cost"), "turns": eff.get("turns"), "nutmeg_calls": eff.get("nutmeg_calls"),
                     "turn_limit": bool(eff.get("hit_turn_limit")),
                     "error": eff.get("subtype") not in (None, "success", "error_max_turns"),
                     "all_pass": bool(verdicts) and all(verdicts.values())})
    if not runs:
        return None
    return {"cost": _median(r["cost"] for r in runs), "turns": _median(r["turns"] for r in runs),
            "nutmeg_calls": _median(r["nutmeg_calls"] for r in runs),
            "turn_limit_hits": sum(r["turn_limit"] for r in runs), "errors": sum(r["error"] for r in runs),
            "pass_at_1": round(sum(r["all_pass"] for r in runs) / len(runs), 3),
            "pass_all_k": all(r["all_pass"] for r in runs), "runs": len(runs)}


def suite_efficiency(rows):
    """Medians over a suite's cases; turn-limit hits and errors in total; mean pass@1 and the share passing pass^k."""
    effs = [r["efficiency"] for r in rows if r.get("efficiency")]
    if not effs:
        return None
    return {"cost": _median(e["cost"] for e in effs), "turns": _median(e["turns"] for e in effs),
            "nutmeg_calls": _median(e["nutmeg_calls"] for e in effs),
            "turn_limit_hits": sum(e["turn_limit_hits"] for e in effs), "errors": sum(e["errors"] for e in effs),
            "pass_at_1": round(sum(e["pass_at_1"] for e in effs) / len(effs), 3),
            "pass_all_k": round(sum(e["pass_all_k"] for e in effs) / len(effs), 3), "cases": len(effs)}


def paired(now_rows, before_rows, key):
    """Case-by-case comparison: mean difference in score (or mean log ratio for cost) with a standard error."""
    import math
    before = {(r["suite"], r["case"]): r for r in before_rows}
    diffs = []
    for row in now_rows:
        old = before.get((row["suite"], row["case"]))
        if old is None:
            continue
        if key == "score":
            diffs.append(row["score"] - old["score"])
        else:
            a, b = (old.get("efficiency") or {}).get(key), (row.get("efficiency") or {}).get(key)
            if a and b:
                diffs.append(math.log(b / a))
    if len(diffs) < 2:
        return None
    mean_d = sum(diffs) / len(diffs)
    sd = math.sqrt(sum((d - mean_d) ** 2 for d in diffs) / (len(diffs) - 1))
    return {"mean": mean_d, "se": sd / math.sqrt(len(diffs)), "n": len(diffs)}


def compare_lines(now, before):
    """Paired, case-by-case changes against an earlier summary.json, with standard errors."""
    out = []
    for label in ("public", "holdout"):
        now_rows = [r for r in now.get("rows", []) if r["suite"] == label]
        if not now_rows:
            continue
        before_rows = [r for r in before.get("rows", []) if r["suite"] == label]
        parts = [f"{label}:"]
        s = paired(now_rows, before_rows, "score")
        if s:
            parts.append(f"score {s['mean']:+.3f} ± {s['se']:.3f} (n={s['n']})")
        for key in ("cost", "turns", "nutmeg_calls"):
            c = paired(now_rows, before_rows, key)
            if c:
                import math
                parts.append(f"{key} {math.exp(c['mean']) - 1:+.0%} (± {c['se']:.2f} log)")
        out.append(" · ".join(parts))
    return out


def mean(rows):
    return round(sum(r["score"] for r in rows) / len(rows), 3) if rows else None


def main(argv=None, root=ROOT, environ=None):
    environ = os.environ if environ is None else environ
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--suite", choices=["both", "public", "holdout"], default="both")
    parser.add_argument("--case", help="only cases whose name matches this glob")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--model", default="claude-sonnet-5-5")
    parser.add_argument("--judge-model", default="claude-sonnet-5-5")
    parser.add_argument("--engine", choices=["auto", "plugin", "live"], default="auto")
    parser.add_argument("--out", help="results folder, outside the repository (default: a new temporary folder)")
    parser.add_argument("--keep", action="store_true", help="keep each live run's work folder")
    parser.add_argument("--compare", help="an earlier summary.json: print the change in score and efficiency")
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
        check_temp_outside(root)
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
                try:
                    with linked_holdout(holdout, cases, root) as link:
                        rows = score_suite("holdout", link, LINK_DIR, cases, args, out, root)
                except SuiteError as exc:
                    print(f"run_suites: {exc}", file=sys.stderr)
                    return 2
            else:  # live runs read the held-out folder where it is; nothing is linked
                rows = score_suite("holdout", holdout, LINK_DIR, cases, args, out, root)
            summary["rows"] += rows
            summary["holdout"] = mean(rows)

    summary["efficiency"] = {label: suite_efficiency([r for r in summary["rows"] if r["suite"] == label])
                             for label in ("public", "holdout")}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for label in ("public", "holdout"):
        value = summary[label]
        count = sum(1 for r in summary["rows"] if r["suite"] == label)
        print(f"{label} score: " + (f"{value:.2f} over {count} case(s)" if value is not None else "not run"))
        eff = summary["efficiency"].get(label)
        if eff:
            print(f"  per case (median): ${eff['cost'] or 0:.2f} · {eff['turns']} turns · {eff['nutmeg_calls']} nutmeg "
                  f"calls; turn-limit hits {eff['turn_limit_hits']}, errors {eff['errors']}; "
                  f"pass@1 {eff['pass_at_1']:.2f}, pass^k {eff['pass_all_k']:.2f}")
    if args.compare:
        try:
            before = json.loads(Path(args.compare).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"cannot read {args.compare}: {exc}")
        else:
            print("compared with " + args.compare + ":")
            for line in compare_lines(summary, before):
                print("  " + line)
    for note in summary["notes"]:
        print(note)
    print(f"results: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
