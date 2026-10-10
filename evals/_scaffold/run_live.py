"""Run eval cases live with `claude -p --plugin-dir`, outside `claude plugin eval`.

Usage (from the nutmeg repo root):

    python3 evals/_scaffold/run_live.py research-run-gate research-orphan-number \
        [--model claude-sonnet-5-5] [--judge-model claude-sonnet-5-5] [--runs 1] [--keep]

Use it for cases that grant Bash when `claude plugin eval` cannot run them on
this machine (for example, its Bash sandbox refuses to start when a
credentials file points at missing files). Each run gets a fresh git
repository with the case's scaffold, loads this plugin with only the
football-docs MCP server, and allows the case's `allowed_tools`. Graders:
regex (target trace, last message or file:<glob>) and tool_used run locally;
exec graders run a trusted check script from the case's graders/ folder against a
copy of the work folder (it may change the data and rerun the agent's code);
llm graders ask the judge model for PASS or FAIL about the last message, plus
the files a `target: file:<glob>` names. The real football-docs server is used,
not the replay mock. Hooks run, so a gate "ask" is denied (no user), as in a
headless session.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVALS = ROOT / "evals"


def frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    head, _, body = text[3:].partition("\n---")
    meta = {}
    for line in head.strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1].replace("''", "'")
        meta[key.strip()] = value
    return meta, body.lstrip("\n")


def load_case(name, eval_dir=EVALS):
    folder = (Path(eval_dir) / name).resolve()  # the scaffold runs in a temporary folder
    meta, prompt = frontmatter((folder / "prompt.md").read_text())
    graders = {}
    for path in sorted((folder / "graders").glob("*.md")):
        gmeta, body = frontmatter(path.read_text())
        gmeta["body"] = body.strip()
        graders[path.stem] = gmeta
    return folder, meta, prompt.strip(), graders


def exec_grade(folder, grader, work, timeout=180):
    """Run a trusted check script from the case's graders/ folder against a copy of the run's work folder.

    The script gets the copy's path, so it can change the data and rerun the agent's code without touching the run
    itself. The grader passes when the script exits 0; its last output lines are kept as the reason."""
    graders_dir = (Path(folder) / "graders").resolve()
    script = (graders_dir / str(grader.get("script", ""))).resolve()
    if not script.is_file() or graders_dir not in script.parents:
        return False, [f"FAIL exec grader script not found in graders/: {grader.get('script')}"]
    scratch = Path(tempfile.mkdtemp(prefix="nutmeg-exec-"))
    copy = scratch / "work"
    try:
        shutil.copytree(work, copy, symlinks=True, ignore=shutil.ignore_patterns(".git"))
        result = subprocess.run([sys.executable, str(script), str(copy)], capture_output=True, text=True,
                                timeout=timeout, stdin=subprocess.DEVNULL, env=dict(os.environ, PIP_REQUIRE_VIRTUALENV="1"))
        tail = (result.stdout + result.stderr).strip()[-600:]
        return result.returncode == 0, [("PASS " if result.returncode == 0 else "FAIL ") + tail]
    except subprocess.TimeoutExpired:
        return False, ["FAIL exec grader timed out"]
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def agent_env(work):
    """Each run gets its own nutmeg user config (the scaffold may write it), never the operator's. pip refuses to
    install outside a virtual environment, so a run that tries to change the machine's Python is recorded, not done."""
    return dict(os.environ, NUTMEG_USER_CONFIG=str(Path(work) / ".nutmeg-user.json"), PIP_REQUIRE_VIRTUALENV="1")


def result_efficiency(event):
    """What the agent run cost, from its result event. Cost is the headline; token classes are kept apart because a
    cache read costs a small fraction of other input. `modelUsage` covers subagents and compaction too (`usage` covers
    the main loop only)."""
    tokens = {"input": 0, "cache_write": 0, "cache_read": 0, "output": 0}
    for usage in (event.get("modelUsage") or {}).values():
        tokens["input"] += usage.get("inputTokens") or 0
        tokens["cache_write"] += usage.get("cacheCreationInputTokens") or 0
        tokens["cache_read"] += usage.get("cacheReadInputTokens") or 0
        tokens["output"] += usage.get("outputTokens") or 0
    if not any(tokens.values()):  # older versions: main loop only
        usage = event.get("usage") or {}
        tokens = {"input": usage.get("input_tokens") or 0, "cache_write": usage.get("cache_creation_input_tokens") or 0,
                  "cache_read": usage.get("cache_read_input_tokens") or 0, "output": usage.get("output_tokens") or 0}
    return {"cost": event.get("total_cost_usd"), "tokens": tokens, "turns": event.get("num_turns"),
            "seconds": round((event.get("duration_ms") or 0) / 1000, 1), "subtype": event.get("subtype"),
            "terminal_reason": event.get("terminal_reason"), "is_error": bool(event.get("is_error")),
            "hit_turn_limit": event.get("subtype") == "error_max_turns"}


# --- spend cap ------------------------------------------------------------------------------------------------------
# With NUTMEG_EVAL_BUDGET_USD and NUTMEG_EVAL_SPEND_FILE set, every agent and judge call adds its reported cost to the
# spend file (one line per call, locked, so parallel runs share one total). A new agent run starts only while the
# total plus a reserve for runs already in flight stays under the cap; a judge call starts only while the total is
# under the cap. Without the variables nothing is tracked or refused.

BUDGET_ENV, SPEND_ENV = "NUTMEG_EVAL_BUDGET_USD", "NUTMEG_EVAL_SPEND_FILE"
RUN_RESERVE_USD = 20.0  # room for agent runs already started when the cap check passes
UNREPORTED_RUN_USD = 3.0  # what a run that timed out (and so reported no cost) is counted as


class BudgetExceeded(RuntimeError):
    pass


def _budget():
    cap, path = os.environ.get(BUDGET_ENV), os.environ.get(SPEND_ENV)
    return (float(cap), Path(path)) if cap and path else (None, None)


def spent():
    cap, path = _budget()
    if path is None or not path.is_file():
        return 0.0
    total = 0.0
    for line in path.read_text().splitlines():
        try:
            total += float(line.split()[0])
        except (ValueError, IndexError):
            continue
    return total


def check_budget(reserve=0.0):
    cap, _ = _budget()
    if cap is not None and spent() + reserve >= cap:
        raise BudgetExceeded(f"eval budget reached: ${spent():.2f} spent of ${cap:.2f}")


def record_spend(cost, label):
    cap, path = _budget()
    if path is None:
        return
    import fcntl
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.write(f"{float(cost or 0.0):.6f} {label}\n")
        fcntl.flock(handle, fcntl.LOCK_UN)


def run_once(name, model, keep, judge_model, eval_dir=EVALS):
    check_budget(reserve=float(os.environ.get("NUTMEG_EVAL_RESERVE_USD") or RUN_RESERVE_USD))
    folder, meta, prompt, graders = load_case(name, eval_dir)
    work = Path(tempfile.mkdtemp(prefix=f"nutmeg-live-{name}-"))
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    subprocess.run(["git", "config", "user.name", "Eval Analyst"], cwd=work, check=True)
    if (folder / "scaffold.sh").exists():
        subprocess.run(["bash", str(folder / "scaffold.sh")], cwd=work, check=True)
    mcp = work.parent / f"{work.name}-mcp.json"
    mcp.write_text(json.dumps({"mcpServers": json.loads((ROOT / ".mcp.json").read_text())["mcpServers"]}))
    allowed = meta.get("allowed_tools") or ["Read", "Glob", "Grep", "Skill"]
    allowed = list(allowed) + ["mcp__plugin_nutmeg_football-docs", "mcp__football-docs"]
    cmd = ["claude", "-p", prompt, "--plugin-dir", str(ROOT), "--model", model, "--setting-sources", "project",
           "--strict-mcp-config", "--mcp-config", str(mcp), "--allowedTools", ",".join(allowed),
           "--max-turns", str(meta.get("max_turns", 10)), "--output-format", "stream-json", "--verbose"]
    if meta.get("disallowed_tools"):
        cmd += ["--disallowedTools", ",".join(meta["disallowed_tools"])]
    env = agent_env(work)
    timeout = int(meta.get("timeout_seconds", 300))
    try:
        result = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=timeout,
                                stdin=subprocess.DEVNULL, env=env)
        lines = result.stdout.splitlines()
    except subprocess.TimeoutExpired as exc:
        lines = (exc.stdout or b"").decode(errors="replace").splitlines() if isinstance(exc.stdout, bytes) else (exc.stdout or "").splitlines()
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    trace = "\n".join(lines)
    calls, last, cost = [], "", 0.0  # (tool name, JSON of its input)
    efficiency = {}  # tokens, turns and time the agent used: nutmeg's own cost to a user, not the judge's
    for event in events:
        if event.get("type") == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") == "tool_use":
                    calls.append((block.get("name", ""), json.dumps(block.get("input", {}))))
                if block.get("type") == "text":
                    last = block["text"]
        if event.get("type") == "result":
            last = event.get("result") or last
            cost = event.get("total_cost_usd") or 0.0
            efficiency.update(result_efficiency(event))
    reported = any(event.get("type") == "result" for event in events)
    # A run that timed out reports no cost but still spent money: count an estimate.
    record_spend(cost if reported else UNREPORTED_RUN_USD, f"agent {name}" + ("" if reported else " (estimate)"))
    verdicts, judged = {}, {}
    for gname, grader in graders.items():
        kind = grader.get("type")
        if kind == "regex":
            where = grader.get("target", "")
            if where.startswith("file:"):
                # The contents of the files the run left behind, for example file:research/*/claims.jsonl
                target = "\n".join(p.read_text(errors="replace") for p in sorted(work.glob(where[5:])) if p.is_file())
            else:
                target = trace if where == "trace" else last
            hit = re.search(grader["body"], target, re.I if grader.get("flags") == "i" else 0) is not None
            verdicts[gname] = hit if grader.get("match", "contains") == "contains" else not hit
        elif kind == "tool_used":
            pattern = grader.get("input_match", "")
            pattern = pattern[1:-1] if pattern[:1] == "'" and pattern[-1:] == "'" else pattern
            tool = grader.get("tool", "")
            count = sum(1 for name, payload in calls
                        if (name == tool or name.endswith("__" + tool)) and re.search(pattern.replace('\\"', '"'), payload))
            low, high = int(grader.get("min", 1)), grader.get("max")
            verdicts[gname] = count >= low and (high is None or count <= int(high))
        elif kind == "exec":
            verdicts[gname], judged[gname] = exec_grade(folder, grader, work)
        elif kind == "llm":
            response = judge_input(last, grader.get("target", ""), work)
            verdicts[gname], judged[gname] = judge_votes(grader["body"], response, judge_model)
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    mcp.unlink(missing_ok=True)
    efficiency["tool_calls"] = len(calls)
    efficiency["nutmeg_calls"] = sum(1 for tool, payload in calls if tool == "Bash" and "nutmeg.py" in payload)
    return {"case": name, "verdicts": verdicts, "judged": judged, "cost": cost, "last": last, "efficiency": efficiency,
            "bash": [payload for tool, payload in calls if tool == "Bash"],
            "work": str(work) if keep else None}


JUDGE_VOTES = 3
# A judge needs no tools, MCP servers, slash commands or Claude Code's long system prompt: a lean call costs far less.
JUDGE_FLAGS = ["--system-prompt", "You grade responses against a criterion. Reply with PASS or FAIL on the first line, "
               "then one sentence of reason.", "--tools", "", "--disallowedTools", "mcp__*", "--strict-mcp-config",
               "--setting-sources", "project", "--disable-slash-commands", "--no-session-persistence",
               "--output-format", "json"]
FILE_CHARS = 20000


def judge_input(last, where, work):
    """The last message, plus the files a `file:<glob>` target names (the judge sees what the run wrote)."""
    if not where.startswith("file:"):
        return last
    files = [p for p in sorted(Path(work).glob(where[5:])) if p.is_file()]
    return last + "".join(f"\n\n--- {p.relative_to(work)} ---\n" + p.read_text(errors="replace")[:FILE_CHARS]
                          for p in files)


def judge_votes(criteria, response, model, votes=JUDGE_VOTES):
    """Ask the judge `votes` times; return (passed by majority, the replies)."""
    prompt = ("You grade an AI assistant's final response against a criterion. Reply with exactly PASS or FAIL "
              "on the first line, then one sentence of reason.\n\nCriterion:\n" + criteria +
              "\n\nResponse:\n" + (response or "(empty)"))
    replies, passes = [], 0
    for _ in range(votes):
        check_budget()
        try:
            out = subprocess.run(["claude", "-p", prompt, "--model", model, *JUDGE_FLAGS],
                                 capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=300)
            try:
                data = json.loads(out.stdout)
                reply = str(data.get("result") or "").strip()
                record_spend(data.get("total_cost_usd"), "judge")
            except (json.JSONDecodeError, AttributeError):
                reply = out.stdout.strip()
        except subprocess.TimeoutExpired:
            reply = "(judge timed out)"
        replies.append(reply[:400])
        # The verdict may come as PASS, **PASS**, "PASS:" ...: take the first PASS or FAIL near the start.
        match = re.search(r"\b(PASS|FAIL)\b", reply[:80].upper())
        passes += bool(match and match.group(1) == "PASS")
    return passes * 2 > votes, replies


def judge(criteria, response, model):
    return judge_votes(criteria, response, model)[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", nargs="+")
    parser.add_argument("--model", default="claude-sonnet-5-5")
    parser.add_argument("--judge-model", default="claude-sonnet-5-5")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--keep", action="store_true", help="keep the work folders")
    parser.add_argument("--json", help="write the results here")
    parser.add_argument("--eval-dir", default=str(EVALS),
                        help="folder that holds the cases (for example a private held-out set)")
    args = parser.parse_args()
    results = []
    for name in args.cases:
        for _ in range(args.runs):
            try:
                outcome = run_once(name, args.model, args.keep, args.judge_model, args.eval_dir)
            except BudgetExceeded as exc:
                print(f"{name}: skipped ({exc})")
                continue
            results.append(outcome)
            passed = sum(outcome["verdicts"].values())
            print(f"{name}: {passed}/{len(outcome['verdicts'])} graders pass · ${outcome['cost']:.2f}")
            for gname, ok in outcome["verdicts"].items():
                print(f"  {'PASS' if ok else 'FAIL'} {gname}")
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2))
    total = sum(sum(r["verdicts"].values()) / max(1, len(r["verdicts"])) for r in results) / max(1, len(results))
    print(f"score {total:.2f} over {len(results)} run(s)")
    sys.exit(0)
