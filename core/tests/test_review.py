import json

import pytest

from nutmeg_core.cli import main
from nutmeg_core.ledger import Ledger
from nutmeg_core.why import why_lines


@pytest.fixture
def project(repo):
    main(["new", "demo", "--data-in-git", "yes"])
    folder = repo / "research" / "demo"
    ledger = Ledger(folder / "claims.jsonl")
    ledger.append({"kind": "computed", "statement": "npxG 1.78", "value": 1.78, "evidence": {"run_id": "R1"},
                   "status": "verified"}, trusted=True)
    ledger.append({"kind": "interpretation", "statement": "elite", "evidence": {"claims": ["C1"]},
                   "status": "supported"}, trusted=True)
    return folder


def test_contest_then_resolve(project, repo, capsys):
    assert main(["contest", "C1", "--note", "excludes extra time?"]) == 0
    claim = Ledger(project / "claims.jsonl").get("C1")
    assert claim["status"] == "disputed" and claim["note"] == "excludes extra time?" and claim["by"] == "Test Analyst"
    text = "\n".join(why_lines(project, repo, "C1"))
    assert "disputed · Test Analyst · excludes extra time?" in text
    assert main(["resolve", "C1", "--note", "checked: extra time excluded"]) == 0
    claim = Ledger(project / "claims.jsonl").get("C1")
    assert claim["status"] == "verified" and claim["note"] == "checked: extra time excluded"
    kinds = [json.loads(l)["kind"] for l in (project / "receipts.jsonl").read_text().splitlines()]
    assert kinds[-2:] == ["contest", "resolve"]


def test_interpretation_is_contested_not_disputed(project):
    assert main(["contest", "C2", "--note", "one season only"]) == 0
    assert Ledger(project / "claims.jsonl").get("C2")["status"] == "contested"
    assert main(["resolve", "C2", "--note", "added a second season"]) == 0
    assert Ledger(project / "claims.jsonl").get("C2")["status"] == "supported"


def test_resolve_needs_a_dispute(project, capsys):
    assert main(["resolve", "C1", "--note", "x"]) == 2
    assert "nothing to resolve" in capsys.readouterr().err


def test_note_does_not_carry_to_later_versions(project):
    main(["contest", "C1", "--note", "why?"])
    Ledger(project / "claims.jsonl").update("C1", value=1.79, statement="npxG 1.79")
    assert "note" not in Ledger(project / "claims.jsonl").get("C1")


def test_contest_unknown_claim(project, capsys):
    assert main(["contest", "C9", "--note", "x"]) == 2


def test_withdraw_takes_a_claim_out_of_use(project, capsys):
    from nutmeg_core import check as checks
    (project / "runs" / "R1").mkdir(parents=True)
    (project / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "status": "ok", "exit_code": 0}))
    (project / "report.md").write_text("Penalty-free xG was 1.78 [C1].\n")
    assert checks.run_checks(project)[0] == []
    assert main(["claim", "withdraw", "C1", "--note", "replaced by per-match claims"]) == 0
    claim = Ledger(project / "claims.jsonl").get("C1")
    assert claim["status"] == "withdrawn" and claim["by"] == "Test Analyst" and "signer" not in claim
    assert "outputs that still cite it" in capsys.readouterr().out
    # The report still cites C1, so the check now fails for it.
    assert checks.run_checks(project)[0]
    kinds = [json.loads(l)["kind"] for l in (project / "receipts.jsonl").read_text().splitlines()]
    assert kinds[-1] == "withdraw"


def test_withdraw_needs_a_note_and_a_live_claim(project):
    with pytest.raises(SystemExit):
        main(["claim", "withdraw", "C1"])
    assert main(["claim", "withdraw", "C9", "--note", "x"]) != 0
    assert main(["claim", "withdraw", "C1", "--note", "dropped"]) == 0
    assert main(["claim", "withdraw", "C1", "--note", "again"]) != 0
