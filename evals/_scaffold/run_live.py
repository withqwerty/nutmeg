"""Run eval cases live with `claude -p --plugin-dir`, outside `claude plugin eval`.

Usage (from the nutmeg repo root):

    python3 evals/_scaffold/run_live.py research-run-gate research-orphan-number \
        [--model sonnet] [--judge-model haiku] [--runs 1] [--keep]

Use it for cases that grant Bash when `claude plugin eval` cannot run them on
this machine (for example, its Bash sandbox refuses to start when a
credentials file points at missing files). Each run gets a fresh git
repository with the case's scaffold, loads this plugin with only the
football-docs MCP server, and allows the case's `allowed_tools`. Graders:
regex (target trace or last message) and tool_used run locally; llm graders
ask the judge model for PASS or FAIL. The real football-docs server is used,
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


def load_case(name):
    folder = EVALS / name
    meta, prompt = frontmatter((folder / "prompt.md").read_text())
    graders = {}
    for path in sorted((folder / "graders").glob("*.md")):
        gmeta, body = frontmatter(path.read_text())
        gmeta["body"] = body.strip()
        graders[path.stem] = gmeta
    return folder, meta, prompt.strip(), graders


def run_once(name, model, keep, judge_model):
    folder, meta, prompt, graders = load_case(name)
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
    timeout = int(meta.get("timeout_seconds", 300))
    try:
        result = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
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
    verdicts = {}
    for gname, grader in graders.items():
        kind = grader.get("type")
        if kind == "regex":
            target = trace if grader.get("target") == "trace" else last
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
        elif kind == "llm":
            verdicts[gname] = judge(grader["body"], last, judge_model)
    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    mcp.unlink(missing_ok=True)
    return {"case": name, "verdicts": verdicts, "cost": cost, "last": last,
            "bash": [payload for tool, payload in calls if tool == "Bash"],
            "work": str(work) if keep else None}


def judge(criteria, response, model):
    prompt = ("You grade an AI assistant's final response against a criterion. Reply with exactly PASS or FAIL "
              "on the first line, then one sentence of reason.\n\nCriterion:\n" + criteria +
              "\n\nResponse:\n" + (response or "(empty)"))
    out = subprocess.run(["claude", "-p", prompt, "--model", model, "--setting-sources", "project",
                          "--strict-mcp-config", "--max-turns", "1"], capture_output=True, text=True,
                         stdin=subprocess.DEVNULL, timeout=180)
    return out.stdout.strip().upper().startswith("PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", nargs="+")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--judge-model", default="haiku")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--keep", action="store_true", help="keep the work folders")
    parser.add_argument("--json", help="write the results here")
    args = parser.parse_args()
    results = []
    for name in args.cases:
        for _ in range(args.runs):
            outcome = run_once(name, args.model, args.keep, args.judge_model)
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
