import json

import pytest

from nutmeg_core import check as checks
from nutmeg_core import gate
from nutmeg_core import project as projects
from nutmeg_core.cli import main
from nutmeg_core.ledger import ClaimError, Ledger

WORDS = ["--claim", "Mendes makes us more dangerous than anyone we had",
         "--rests-on", "valuing passes and carries by how close they take the ball to goal",
         "--would-change", "a few big games driving it, or a fuller squad median"]


@pytest.fixture
def project(repo):
    main(["new", "signings", "--data-in-git", "yes"])
    folder = repo / "research" / "signings"
    main(["plan", "choose", "--kind", "filter", "--choice", "at least 900 minutes", "--why", "Per 90 needs a floor.",
          "--rests-type", "rule", "--rests-ref", "metric-misuse"])
    (repo / "analysis.py").write_text("import sys\nprint(sys.argv[1:])\n")
    return folder


def run(*args):
    return main(["run", "analysis.py", *(["--", *args] if args else [])])


def test_the_first_run_locks_the_plan(project):
    assert not projects.plan_locks(project)
    assert run() == 0
    locks = projects.plan_locks(project)
    assert len(locks) == 1 and locks[0]["run_id"] == "R1" and locks[0]["choices"][0]["key"] == "filter: at least 900 minutes"
    run("--min", "600")
    assert len(projects.plan_locks(project)) == 1  # later runs do not lock again


def test_changes_after_the_lock_are_listed(project, capsys):
    run()
    main(["plan", "choose", "--kind", "method", "--choice", "compare with the worst player", "--why", "Asked for.",
          "--rests-type", "user", "--rests-ref", "'try it'", "--after-results", "replaces the median comparison"])
    assert "listed as a deviation" in capsys.readouterr().out
    plan = project / "plan.md"
    plan.write_text(plan.read_text().replace("Per 90 needs a floor.", "Per 90 needs a floor of minutes."))
    lines = "\n".join(projects.deviation_lines(project))
    assert "added after the lock: method: compare with the worst player · after seeing results" in lines
    assert "changed after the lock: filter: at least 900 minutes" in lines


def test_a_removed_choice_and_an_edited_lock_are_shown(project):
    run()
    (project / "plan.md").write_text("# Plan\n\n## Choices\n")
    assert "removed after the lock: filter: at least 900 minutes" in "\n".join(projects.deviation_lines(project))
    data = json.loads((project / "plan_lock.json").read_text())
    data["locks"][0]["choices"] = []
    (project / "plan_lock.json").write_text(json.dumps(data))
    assert any("edited by hand" in line for line in projects.deviation_lines(project))


def test_locking_again_needs_a_reason_and_starts_a_new_baseline(project, capsys):
    run()
    main(["plan", "choose", "--kind", "metric", "--choice", "xT per 90", "--why", "Threat.", "--rests-type", "rule",
          "--rests-ref", "glossary"])
    assert main(["plan", "lock"]) == 2
    assert main(["plan", "lock", "--reason", "phase 2"]) == 0
    locks = projects.plan_locks(project)
    assert locks[1]["previous"] == locks[0]["hash"] and projects.lock_chain_ok(project)
    assert "no changes since the lock" in "\n".join(projects.deviation_lines(project))


def test_alternatives_are_validated(project):
    ledger = Ledger(project / "claims.jsonl")
    with pytest.raises(ClaimError):
        ledger.append({"kind": "computed", "statement": "x 1", "value": 1,
                       "evidence": {"run_id": "R1", "alternatives": [{"run_id": "R2", "value": 1}]}})
    with pytest.raises(ClaimError):
        ledger.append({"kind": "interpretation", "statement": "y", "evidence": {
            "claims": ["C1"], "alternatives": [{"run_id": "R2", "choice": "mean"}]}})
    with pytest.raises(ClaimError):
        ledger.append({"kind": "computed", "statement": "x 1", "value": 1,
                       "evidence": {"run_id": "R1", "no_alternatives": " "}})


def _three_runs():
    run(); run("--min", "600"); run("--mean")


def test_alternative_values_count_as_the_claims_numbers(project):
    _three_runs()
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "Mendes 0.31", "value": 0.31,
        "evidence": {"run_id": "R1", "alternatives": [{"run_id": "R2", "choice": "600 minutes", "value": 0.29},
                                                      {"run_id": "R3", "choice": "mean", "value": 0.33}]}})
    (project / "report.md").write_text("Mendes adds 0.31 [C1] (0.29 to 0.33 across alternatives [C1]).\n")
    assert checks.check(project)["open"] == []


def test_an_alternative_must_be_a_recorded_run_and_is_never_dropped(project):
    _three_runs()
    ledger = Ledger(project / "claims.jsonl")
    ledger.append({"kind": "computed", "statement": "Mendes 0.31", "value": 0.31, "evidence": {
        "run_id": "R1", "alternatives": [{"run_id": "R9", "choice": "made up", "value": 0.3}]}})
    assert [f["kind"] for f in checks.check(project)["open"]] == ["unrecorded alternative"]
    ledger.update("C1", evidence={"run_id": "R1", "alternatives": [
        {"run_id": "R2", "choice": "600 minutes", "value": 0.29}]})
    kinds = [f["kind"] for f in checks.check(project)["open"]]
    assert kinds == ["alternative dropped"]


def test_publish_needs_alternatives_for_headlines_and_shows_the_range(project, repo, capsys):
    _three_runs()
    ledger = Ledger(project / "claims.jsonl")
    ledger.append({"kind": "computed", "statement": "Mendes 0.31", "value": 0.31, "headline": True,
                   "evidence": {"run_id": "R1"}})
    (project / "report.md").write_text("Mendes adds 0.31 [C1].\n")
    main(["teachback", *WORDS])
    assert main(["publish"]) == 2
    assert "shows one specification only" in capsys.readouterr().err
    ledger.update("C1", evidence={"run_id": "R1", "alternatives": [
        {"run_id": "R2", "choice": "600 minutes", "value": 0.29}, {"run_id": "R3", "choice": "mean", "value": 0.33}]})
    main(["teachback", *WORDS])
    reason = gate.decide("nutmeg publish", repo, project, repo).reason
    assert "C1 = 0.31; alternatives 600 minutes: 0.29; mean: 0.33; range 0.29 to 0.33" in reason
    assert "Plan locked at run R1" in reason
    assert main(["publish"]) == 0


def test_a_reason_for_no_alternatives_is_enough(project, capsys):
    _three_runs()
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "Mendes played 1710 minutes",
        "value": 1710, "headline": True,
        "evidence": {"run_id": "R1", "no_alternatives": "A count of minutes has no defensible alternative."}})
    (project / "report.md").write_text("Mendes played 1710 minutes [C1].\n")
    main(["teachback", *WORDS])
    assert main(["publish"]) == 0
