"""Stop hook: check the active research project's outputs before a step ends.

Called through run-hook.sh, which has already found an active project. Blocks
the stop once for each new open problem, with the list; a second stop
(stop_hook_active) is always allowed. Open problems stay in checks.json, and
publishing refuses until each is fixed or accepted with a reason.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

from nutmeg_core import check, project  # noqa: E402


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}
    if data.get("stop_hook_active"):
        return 0
    repo = Path(os.environ.get("NUTMEG_REPO_ROOT") or data.get("cwd") or os.getcwd())
    active = project.active_project(repo)
    if active is None or not check.output_files(active):
        return 0
    try:
        state = check.check(active)
    except Exception as exc:  # never trap the user in a loop because the check broke
        print(json.dumps({"systemMessage": f"nutmeg check could not run: {exc}"}))
        return 0
    new = [f for f in state["open"] if f["id"] not in state["last_blocked"]]
    if not new:
        return 0
    state["last_blocked"] = sorted(set(state["last_blocked"]) | {f["id"] for f in state["open"]})
    check.save_state(active, state)
    name = active.relative_to(repo) if active.is_relative_to(repo) else active
    lines = [f"nutmeg check: {len(state['open'])} open problem(s) in the outputs of {name}:"]
    lines += [f"- {check.describe(f)}" for f in state["open"][:20]]
    if len(state["open"]) > 20:
        lines.append(f"- … {len(state['open']) - 20} more (run `nutmeg check`)")
    lines.append(
        "Fix each one: add the missing claim with its evidence, or correct the output, then run `nutmeg check`. "
        "If the user says a problem is not one, record their reason with "
        "`nutmeg check --accept <id> --reason \"...\"`. Publishing refuses while problems are open."
    )
    print(json.dumps({"decision": "block", "reason": "\n".join(lines)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
