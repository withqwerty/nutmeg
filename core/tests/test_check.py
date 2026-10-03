import json
import shutil
import subprocess
import os
from pathlib import Path

import pytest

from nutmeg_core import check as checks
from nutmeg_core.cli import main
from nutmeg_core.ledger import Ledger

FIXTURE = Path(__file__).parent / "fixtures" / "clean_project"
PLUGIN = Path(__file__).resolve().parents[2]
WRAPPER = PLUGIN / "hooks" / "run-hook.sh"


@pytest.fixture
def project(repo):
    main(["new", "demo", "--data-in-git", "yes"])
    folder = repo / "research" / "demo"
    (folder / "runs" / "R1").mkdir(parents=True)
    (folder / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "status": "ok", "exit_code": 0}))
    return folder


def add(project, **claim):
    return Ledger(project / "claims.jsonl").append(claim)


def computed(project, value, statement="a number"):
    return add(project, kind="computed", statement=statement, value=value, evidence={"run_id": "R1"})


def test_clean_fixture_has_no_problems(tmp_path):
    folder = tmp_path / "clean"
    shutil.copytree(FIXTURE, folder)
    failures, warnings = checks.run_checks(folder)
    assert failures == [], failures
    assert warnings == []


def test_orphan_number(project):
    (project / "report.md").write_text("npxG/90 rose to 1.78 this season.\n")
    failures, _ = checks.run_checks(project)
    assert [(f["kind"], f["shown"], f["line"]) for f in failures] == [("orphan", "1.78", 1)]


def test_percentage_matches_a_fraction(project):
    computed(project, 0.2614)
    (project / "report.md").write_text("He wins 26% of aerial duels.\n")
    assert checks.run_checks(project)[0] == []


@pytest.mark.parametrize("text", [
    "In 2025/26 he started every game.",
    "Reep ID Q214 is the club.",
    "They won 2-1 at home.",
    "Data pulled on 2026-09-30.",
    "Compare per 90 rates.",
    "The top 5 leagues.",
    "See `qualifier 213`.",
    "1. First item",
])
def test_non_claim_numbers_are_skipped(project, text):
    (project / "report.md").write_text(text + "\n")
    assert checks.run_checks(project)[0] == []


def test_count_that_looks_like_a_year_is_checked(project):
    (project / "report.md").write_text("He played 2010 minutes.\n")
    assert [f["kind"] for f in checks.run_checks(project)[0]] == ["orphan"]


def test_ambiguous_match_is_reported(project):
    computed(project, 0.41, "xG per shot")
    computed(project, 0.414, "xA per 90")
    (project / "report.md").write_text("A figure of 0.41 stands out.\n")
    failures, _ = checks.run_checks(project)
    assert failures[0]["kind"] == "ambiguous" and "C1, C2" in failures[0]["message"]
    (project / "report.md").write_text("A figure of 0.41 [C2] stands out.\n")
    assert checks.run_checks(project)[0] == []


def test_named_claim_with_wrong_value_is_a_mismatch(project):
    computed(project, 1.81)
    (project / "report.md").write_text("npxG/90 rose to 1.78 [C1].\n")
    assert checks.run_checks(project)[0][0]["kind"] == "mismatch"


def test_withdrawn_claim_does_not_count(project):
    claim = computed(project, 1.78)
    Ledger(project / "claims.jsonl").update(claim["id"], status="withdrawn")
    (project / "report.md").write_text("npxG/90 rose to 1.78.\n")
    assert checks.run_checks(project)[0][0]["kind"] == "orphan"


def test_literature_needs_a_good_quote_match(project):
    add(project, kind="literature", statement="Singh introduced xT",
        evidence={"citation": "Singh (2019)", "source_id": "web:karun.in", "match": "none"})
    add(project, kind="literature", statement="Rathke on xG", evidence={"citation": "Rathke (2017)"})
    add(project, kind="literature", statement="Fine", evidence={"citation": "x", "source_id": "doi:1", "match": "exact"})
    kinds = [(f["kind"], f["claim"]) for f in checks.run_checks(project)[0]]
    assert kinds == [("unresolved citation", "C1"), ("unresolved citation", "C2")]


def test_provider_fact_needs_a_source(project):
    add(project, kind="provider_fact", statement="Opta x is 0 to 100", evidence={"provider": "opta"})
    failures = checks.run_checks(project)[0]
    assert failures[0]["kind"] == "unsourced fact"


def test_accept_closes_and_writes_a_receipt(project, capsys):
    (project / "report.md").write_text("npxG/90 rose to 1.78.\n")
    assert main(["check"]) == 1
    failure_id = checks.load_state(project)["open"][0]["id"]
    assert main(["check", "--accept", failure_id]) == 2
    assert main(["check", "--accept", failure_id, "--reason", "quoted from the club's own report"]) == 0
    assert checks.load_state(project)["open"] == []
    receipt = json.loads((project / "receipts.jsonl").read_text().splitlines()[-1])
    assert receipt["kind"] == "check_accepted" and receipt["failure"] == failure_id
    assert main(["check"]) == 0


# --- the Stop hook -----------------------------------------------------------

def _stop(repo, active=False, env_path=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
    if env_path:
        env["PATH"] = env_path
    payload = json.dumps({"hook_event_name": "Stop", "stop_hook_active": active, "cwd": str(repo)})
    return subprocess.run(["/bin/sh", str(WRAPPER), "stop_check.py"], input=payload, capture_output=True,
                          text=True, env=env, cwd=repo)


def test_stop_blocks_once_then_allows_and_failure_stays_open(project, repo):
    (project / "report.md").write_text("npxG/90 rose to 1.78.\n")
    first = _stop(repo)
    out = json.loads(first.stdout)
    assert out["decision"] == "block" and "1.78" in out["reason"]
    assert _stop(repo, active=True).stdout == ""
    assert _stop(repo).stdout == ""  # same problem, not blocked again
    assert len(checks.load_state(project)["open"]) == 1
    (project / "report.md").write_text("npxG/90 rose to 1.78. xG per shot was 0.12.\n")
    assert json.loads(_stop(repo).stdout)["decision"] == "block"  # a new problem blocks again


def test_stop_without_project_exits_before_python(repo):
    result = _stop(repo, env_path="/nonexistent")
    assert result.returncode == 0 and result.stdout == "" and result.stderr == ""


def test_stop_with_no_outputs_does_nothing(project, repo):
    assert _stop(repo).stdout == ""


def _plan_metric(project, choice):
    assert main(["plan", "choose", "--kind", "metric", "--choice", choice, "--why", "the brief asks for it",
                 "--rests-type", "user", "--rests-ref", "brief"]) == 0


def test_plan_metric_without_a_definition_warns(project):
    _plan_metric(project, "left-foot pass share: passes with the left foot over all foot passes")
    warnings = checks.run_checks(project)[1]
    assert any('plan metric "left-foot pass share" has no glossary entry' in w for w in warnings)


def test_definition_claim_with_the_term_clears_the_warning(project):
    _plan_metric(project, "left-foot pass share: passes with the left foot over all foot passes")
    add(project, kind="definition", statement="The share of foot passes made with the left foot",
        evidence={"definition": "left-foot passes / foot passes", "term": "left-foot pass share"})
    assert not any("left-foot pass share" in w for w in checks.run_checks(project)[1])


def test_long_metric_text_asks_for_a_short_name(project):
    _plan_metric(project, "minutes played from starting xi, substitution events and each match's last event")
    warnings = [w for w in checks.run_checks(project)[1] if w.startswith("plan metric")]
    assert len(warnings) == 1
    assert "has no short name" in warnings[0] and "### metric: minutes played:" in warnings[0]
    assert "each match's last event" not in warnings[0]


@pytest.mark.parametrize("value", [0.2054, 0.1987, 1.2010])
def test_decimal_digits_that_look_like_a_year_are_read_whole(project, value):
    # Found by the held-out Cruyff run: the year mask ate "2054" in "0.2054", leaving a bare "0".
    computed(project, value)
    (project / "report.md").write_text(f"xG: East Germany {value:.4f} [C1].\n")
    assert checks.run_checks(project)[0] == []
    rows = checks.shown_numbers(f"xG: East Germany {value:.4f}.")
    assert [r[1] for r in rows] == [f"{value:.4f}"]


def test_years_and_seasons_are_still_masked(project):
    computed(project, 31)
    (project / "report.md").write_text("In 2019 he scored 31 [C1] goals; the 2015/16 season and May 2019 were quieter.\n")
    assert checks.run_checks(project)[0] == []
    assert [r[1] for r in checks.shown_numbers("A count of 1999.5 metres.")] == ["1999.5"]


def test_year_lists_are_still_masked(project):
    # Codex review 5: "2023,2024" must stay two years, not an orphan count.
    (project / "report.md").write_text("Years covered: 2023,2024 and 2019, 2020.\n")
    assert checks.run_checks(project)[0] == []


def test_a_withdrawn_claim_cited_without_a_number_fails(project):
    # Codex review 5: a fact cited with no number next to it must not pass once its claim is withdrawn.
    add(project, kind="provider_fact", statement="Coordinates use yards", evidence={"provider": "statsbomb",
                                                                                    "source": "football-docs"})
    (project / "report.md").write_text("Coordinates use yards [C1].\n\n```\nnot checked [C9]\n```\n")
    assert checks.run_checks(project)[0] == []
    Ledger(project / "claims.jsonl").update("C1", status="withdrawn", note="replaced")
    failures = checks.run_checks(project)[0]
    assert [(f["kind"], f["line"]) for f in failures] == [("broken link", 1)]
    assert "C1" in failures[0]["message"]


def test_a_missing_claim_next_to_a_number_is_reported_once(project):
    (project / "report.md").write_text("It was 7 [C4].\n")
    failures = checks.run_checks(project)[0]
    assert [f["kind"] for f in failures] == ["broken link"]
