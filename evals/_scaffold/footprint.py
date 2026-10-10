"""How much context nutmeg puts in front of the model.

- Skills and agents: from `claude plugin details nutmeg` (Claude Code's own estimate): the always-on cost paid in
  every session (names and descriptions) and the on-invoke cost of each body.
- The SessionStart hook's text: `plugin details` does not count it, so it is measured here (characters / 4).

Usage: python3 evals/_scaffold/footprint.py [--json] [--check]
  --check compares with footprint_budget.json and exits 1 when something grew past its budget.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUDGET_FILE = Path(__file__).with_name("footprint_budget.json")
HOOK_HARD_LIMIT_CHARS = 10_000  # Claude Code replaces longer additionalContext with a file path and a preview


def hook_text(root=ROOT):
    return json.loads((root / "hooks" / "session-start.json").read_text())["hookSpecificOutput"]["additionalContext"]


def _tokens(text):
    value = text.replace(",", "").replace("~", "").strip()
    return int(float(value[:-1]) * 1000) if value.endswith("k") else int(float(value))


def plugin_details(root=ROOT):
    """Parse `claude plugin details nutmeg`: {"always_on": n, "components": {name: (always_on, on_invoke)}}."""
    out = subprocess.run(["claude", "--plugin-dir", str(root), "plugin", "details", "nutmeg"], capture_output=True,
                         text=True, stdin=subprocess.DEVNULL, timeout=120).stdout
    always = re.search(r"Always-on:\s+~?([\d,.]+k?)\s+tok", out)
    components = {}
    for line in out.splitlines():
        m = re.match(r"\s{2}([a-z][\w-]+)\s+~?([\d,.]+k?)\s+~?([\d,.]+k?)\s*$", line)
        if m:
            components[m.group(1)] = (_tokens(m.group(2)), _tokens(m.group(3)))
    return {"always_on": _tokens(always.group(1)) if always else None, "components": components}


def footprint(root=ROOT, details=True):
    hook = hook_text(root)
    data = {"hook": {"chars": len(hook), "tokens_est": round(len(hook) / 4)}}
    if details:
        data.update(plugin_details(root))
    return data


def check(data, budget):
    over = []
    if data["hook"]["chars"] > HOOK_HARD_LIMIT_CHARS:
        over.append(f"hook text {data['hook']['chars']} chars > hard limit {HOOK_HARD_LIMIT_CHARS}")
    if data["hook"]["tokens_est"] > budget["hook_tokens"]:
        over.append(f"hook {data['hook']['tokens_est']} tokens > budget {budget['hook_tokens']}")
    if data.get("always_on") and data["always_on"] > budget["always_on_tokens"]:
        over.append(f"always-on {data['always_on']} tokens > budget {budget['always_on_tokens']}")
    for name, (_, on_invoke) in (data.get("components") or {}).items():
        limit = budget["on_invoke_tokens"].get(name, budget["on_invoke_tokens"]["default"])
        if on_invoke > limit:
            over.append(f"{name} on-invoke {on_invoke} tokens > budget {limit}")
    return over


if __name__ == "__main__":
    data = footprint()
    if "--json" in sys.argv:
        print(json.dumps(data, indent=2))
    else:
        print(f"hook (every session, not in plugin details)  ~{data['hook']['tokens_est']:,} tokens  ({data['hook']['chars']:,} chars)")
        print(f"skills and agents always-on                  ~{data.get('always_on') or 0:,} tokens")
        for name, (always, invoke) in sorted((data.get("components") or {}).items(), key=lambda x: -x[1][1]):
            print(f"  {name:20} always-on ~{always:>4}  on-invoke ~{invoke:,}")
    if "--check" in sys.argv:
        over = check(data, json.loads(BUDGET_FILE.read_text()))
        for line in over:
            print("OVER BUDGET: " + line)
        sys.exit(1 if over else 0)
