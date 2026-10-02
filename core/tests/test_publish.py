import json

import pytest

from nutmeg_core import figure as figures
from nutmeg_core import gate
from nutmeg_core.cli import main
from nutmeg_core.ledger import Ledger


@pytest.fixture
def project(repo):
    main(["new", "demo", "--data-in-git", "yes"])
    folder = repo / "research" / "demo"
    (folder / "runs" / "R1").mkdir(parents=True)
    (folder / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "status": "ok"}))
    Ledger(folder / "claims.jsonl").append({"kind": "computed", "statement": "Robertson 9.23", "value": 9.23,
                                            "evidence": {"run_id": "R1"}})
    (repo / "out").mkdir()
    (repo / "out" / "carries.csv").write_text("player,prog_p90\nRobertson,9.23\nUdogie,8.6\nEstupinan,8.07\nKerkez,6.94\n")
    (repo / "out" / "a.csv").write_text("source,v\nStatsBomb,1\n")
    figures.register(folder, repo, "carries", "out/carries.csv", ["Opta"], ["C1"], filters="min 900 minutes")
    figures.register(folder, repo, "panels", "out/a.csv", ["StatsBomb", "Opta"], ["C1"])
    return folder


def test_publish_refuses_with_open_orphan(project, capsys):
    (project / "report.md").write_text("Robertson leads with 9.23 [C1]. Kerkez has 7.7.\n")
    assert main(["publish"]) == 2
    err = capsys.readouterr().err
    assert "publish refused" in err and "7.7" in err
    assert not (project / "published.json").exists()


def test_publish_records_files_and_figures(project, repo, capsys):
    (project / "report.md").write_text("Robertson leads with 9.23 [C1].\n")
    assert main(["publish", "--to", "site/lb"]) == 0
    history = json.loads((project / "published.json").read_text())
    sources = [f["source"] for f in history[0]["files"]]
    assert "research/demo/report.md" in sources and "research/demo/figures/carries.prov.json" in sources
    assert (repo / "site" / "lb" / "report.md").is_file()
    assert [f["figure"] for f in history[0]["figures"]] == ["carries", "panels"]
    receipt = json.loads((project / "receipts.jsonl").read_text().splitlines()[-1])
    assert receipt["kind"] == "publish"


def test_publish_gate_shows_chart_data(project, repo):
    (project / "report.md").write_text("Robertson leads with 9.23 [C1].\n")
    decision = gate.decide("nutmeg publish", repo, project, repo)
    assert decision.decision == "ask"
    for text in ("Figure carries · n = 4 · 4 rows · filters: min 900 minutes", "player | prog_p90", "Robertson | 9.23",
                 "Figure panels", "sources: StatsBomb, Opta"):
        assert text in decision.reason, text
    assert "Kerkez" not in decision.reason  # first three rows only


def test_publish_gate_says_it_will_refuse(project, repo):
    (project / "report.md").write_text("Kerkez has 7.7.\n")
    decision = gate.decide("nutmeg publish", repo, project, repo)
    assert "REFUSED" in decision.reason and "7.7" in decision.reason


def test_publish_outside_repo_is_refused(project, capsys):
    (project / "report.md").write_text("Robertson leads with 9.23 [C1].\n")
    assert main(["publish", "--to", "../elsewhere"]) == 2
