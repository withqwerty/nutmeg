"""PreToolUse hook: show a gate card before runs inside a research project.

Called through run-hook.sh, which has already found an active project. Prints
a permission decision as JSON, or nothing to leave the command to Claude
Code's normal permission flow.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

from nutmeg_core import gate, project  # noqa: E402


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    command = (data.get("tool_input") or {}).get("command") or ""
    cwd = data.get("cwd") or os.getcwd()
    repo = Path(os.environ.get("NUTMEG_REPO_ROOT") or cwd)
    active = project.active_project(repo)
    try:
        decision = gate.decide(command, repo, active, cwd)
    except Exception as exc:  # a broken gate must not wave a run through
        if active is None or gate.parse(command).kind == "other":
            return 0
        decision = gate.Decision("ask", f"nutmeg research gate failed ({exc}); read the command yourself before approving.")
    if decision is not None:
        print(json.dumps(decision.hook_output()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
