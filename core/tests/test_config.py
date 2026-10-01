import json
import shutil

import pytest

from nutmeg_core import config, gate
from nutmeg_core import check as checks
from nutmeg_core.cli import main
from nutmeg_core.ledger import Ledger


def team(repo, **values):
    (repo / ".nutmeg").mkdir(exist_ok=True)
    (repo / ".nutmeg" / "team.json").write_text(json.dumps(values))


def user(repo, **values):
    path = repo / ".no-user-config.json"
    path.write_text(json.dumps(values))


# --- merging ---------------------------------------------------------------

def test_team_floor_l2_beats_user_l3(repo):
    team(repo, max_autonomy={"run": "L2"})
    user(repo, persona="fanalyst", autonomy_run="L3")
    settings = config.load_effective(repo)
    assert settings["levels"]["run"] == "L2" and "team limit L2" in settings["reasons"]["run"]
    assert settings["levels"]["plan"] == "L3"


def test_user_stricter_than_team_wins(repo):
    team(repo, max_autonomy={"run": "L3"})
    user(repo, persona="fanalyst", autonomy_run="L1")
    assert config.load_effective(repo)["levels"]["run"] == "L1"


def test_missing_team_file_uses_user_and_defaults(repo):
    assert config.load_effective(repo)["levels"] == {"plan": "L2", "run": "L2", "publish": "L2"}
    user(repo, persona="fanalyst")
    assert config.load_effective(repo)["levels"]["run"] == "L3"


def test_bad_level_is_an_error(repo):
    team(repo, max_autonomy={"run": "L9"})
    with pytest.raises(config.ConfigError):
        config.load_effective(repo)


def test_run_then_review_needs_team_permission_and_l3(repo):
    user(repo, persona="fanalyst", run_then_review=True)
    assert config.load_effective(repo)["run_then_review"] is True
    team(repo, allow_run_then_review=False)
    settings = config.load_effective(repo)
    assert settings["run_then_review"] is False and "does not allow" in settings["reasons"]["run_then_review"]
    team(repo, max_autonomy={"run": "L2"})
    assert "needs run level L3" in config.load_effective(repo)["reasons"]["run_then_review"]


def test_service_status():
    assert config.service_status("api.statsbomb.com", ["statsbomb.com"]) == "approved by team"
    assert config.service_status("api.example.io", ["statsbomb.com"]) == "not on the team list"
    assert config.service_status("api.example.io", []) == ""


# --- the gate (U9) -----------------------------------------------------------

@pytest.fixture
def project(repo):
    main(["new", "club", "--data-in-git", "no"])
    (repo / "a.py").write_text("import urllib.request\nurllib.request.urlopen('https://api.scout.io/x')\n")
    return repo / "research" / "club"


def test_fanalyst_run_then_review_allows_and_queues(project, repo, capsys):
    user(repo, persona="fanalyst", run_then_review=True)
    gate.decide("nutmeg status", repo, project, repo)  # nothing gated: settings not read
    decision = gate.decide("nutmeg run a.py", repo, project, repo)
    assert decision.decision == "allow" and "review queue" in decision.reason
    (repo / "a.py").write_text("print(1)\n")
    gate.decide("nutmeg run a.py", repo, project, repo)
    if shutil.which("python3"):
        main(["run", "a.py"])
        run = json.loads((project / "runs" / "R1" / "run.json").read_text())
        assert run["gate"]["queued_for_review"] is True and run["gate"]["shown"] is False
        capsys.readouterr()
        main(["queue"])
        assert "R1 a.py" in capsys.readouterr().out
        main(["queue", "--done", "R1", "--note", "looked fine"])
        assert "empty" in capsys.readouterr().out


def test_club_persona_l2_asks(project, repo):
    user(repo, persona="club")
    assert gate.decide("nutmeg run a.py", repo, project, repo).decision == "ask"


def test_team_floor_overrides_run_then_review(project, repo):
    team(repo, max_autonomy={"run": "L2"})
    user(repo, persona="fanalyst", run_then_review=True)
    assert gate.decide("nutmeg run a.py", repo, project, repo).decision == "ask"


def test_l1_card_says_you_run_it(project, repo):
    user(repo, persona="club", autonomy_run="L1")
    decision = gate.decide("nutmeg run a.py", repo, project, repo)
    assert decision.decision == "ask" and "L1 (suggest)" in decision.reason


def test_config_change_mid_session_asks_again(project, repo):
    user(repo, persona="fanalyst", run_then_review=True)
    assert gate.decide("nutmeg run a.py", repo, project, repo).decision == "allow"
    user(repo, persona="fanalyst", run_then_review=True, autonomy_plan="L2")
    decision = gate.decide("nutmeg run a.py", repo, project, repo)
    assert decision.decision == "ask" and "Gate settings changed" in decision.reason
    kinds = [json.loads(l)["kind"] for l in (project / "receipts.jsonl").read_text().splitlines()]
    assert "gate_settings_changed" in kinds
    assert gate.decide("nutmeg run a.py", repo, project, repo).decision == "allow"


def test_card_names_team_approved_services(project, repo):
    team(repo, approved_services=["statsbomb.com"])
    decision = gate.decide("nutmeg run a.py --sends api.statsbomb.com:player_id", repo, project, repo)
    assert "api.scout.io (a URL in the code) · not on the team list" in decision.reason
    assert "api.statsbomb.com: player_id · approved by team" in decision.reason


def test_broken_config_asks(project, repo):
    team(repo, max_autonomy="L3")
    decision = gate.decide("nutmeg run a.py", repo, project, repo)
    assert decision.decision == "ask" and "config is broken" in decision.reason


# --- sign-off (R23) ------------------------------------------------------------

def test_author_cannot_sign_own_headline_claim(project, repo, capsys):
    team(repo, signoff={"required": True})
    claim = {"kind": "definition", "statement": "Progressive actions defined", "evidence": {"definition": "x"}}
    assert main(["claim", "add", "--headline", "--json", json.dumps(claim)]) == 0
    stored = Ledger(project / "claims.jsonl").get("C1")
    assert stored["author"] == "Test Analyst" and stored["headline"] is True
    kinds = [f["kind"] for f in checks.run_checks(project)[0]]
    assert kinds == ["needs sign-off"]
    assert main(["signoff", "C1"]) == 2
    assert "different person" in capsys.readouterr().err
    user(repo, name="Second Analyst")
    assert main(["signoff", "C1", "--note", "checked the definition"]) == 0
    assert Ledger(project / "claims.jsonl").get("C1")["status"] == "verified"
    assert checks.run_checks(project)[0] == []


def test_changed_claim_loses_verification(project):
    ledger = Ledger(project / "claims.jsonl")
    ledger.append({"kind": "definition", "statement": "a", "evidence": {"definition": "x"}, "status": "verified",
                   "signer": "Ben"})
    ledger.update("C1", statement="a, changed")
    latest = ledger.get("C1")
    assert latest["status"] == "draft" and "signer" not in latest


def test_config_set_records_a_receipt(project, repo, capsys):
    assert main(["config", "set", "--persona", "fanalyst", "--run-then-review", "yes"]) == 0
    assert "run-then-review: on" in capsys.readouterr().out
    receipt = json.loads((project / "receipts.jsonl").read_text().splitlines()[-1])
    assert receipt["kind"] == "config_changed"
