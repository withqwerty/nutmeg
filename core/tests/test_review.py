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
                   "status": "verified"})
    ledger.append({"kind": "interpretation", "statement": "elite", "evidence": {"claims": ["C1"]},
                   "status": "supported"})
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
