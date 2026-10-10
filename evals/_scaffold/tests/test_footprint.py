import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import footprint  # noqa: E402


def test_hook_text_stays_within_its_budget_and_claude_codes_limit():
    budget = json.loads(footprint.BUDGET_FILE.read_text())
    data = footprint.footprint(details=False)
    assert footprint.check(data, budget) == [], "the session hook grew past its budget; raise it on purpose, with a reason"


def test_check_reports_each_kind_of_growth():
    budget = {"hook_tokens": 10, "hook_research_tokens": 10_000, "always_on_tokens": 100,
              "on_invoke_tokens": {"default": 50, "research": 80}}
    data = {"hook": {"chars": 12_000, "tokens_est": 3_000}, "always_on": 150,
            "components": {"research": (10, 90), "learn": (10, 40)}}
    over = footprint.check(data, budget)
    assert len(over) == 4 and any("research on-invoke 90" in o for o in over)
