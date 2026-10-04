import json

import pytest

from nutmeg_core import figure as figures
from nutmeg_core.cli import main
from nutmeg_core.ledger import Ledger


@pytest.fixture
def project(repo):
    main(["new", "demo", "--data-in-git", "no"])
    folder = repo / "research" / "demo"
    (folder / "runs" / "R1").mkdir(parents=True)
    (folder / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "status": "ok"}))
    ledger = Ledger(folder / "claims.jsonl")
    ledger.append({"kind": "computed", "statement": "214 left-backs", "value": 214, "evidence": {"run_id": "R1"}})
    ledger.append({"kind": "computed", "statement": "Robertson 9.23", "value": 9.23, "evidence": {"run_id": "R1"}})
    (repo / "out").mkdir()
    (repo / "out" / "carries.csv").write_text("player,prog_p90\nRobertson,9.23\nUdogie,8.6\nEstupinan,8.07\n")
    return folder


def test_register_writes_provenance_and_footnote(project, repo, capsys):
    assert main(["figure", "register", "carries", "--data", "out/carries.csv", "--source", "StatsBomb open data",
                 "--claims", "C1,C2", "--n", "214", "--season", "Premier League 2015/16", "--filters", "min 900 minutes",
                 "--metric", "progressive actions per 90", "--uncertainty", "none shown", "--run", "R1",
                 "--image", "out/carries.png"]) == 0
    out = capsys.readouterr().out
    prov = json.loads((project / "figures" / "carries.prov.json").read_text())
    assert prov["contract"] == "nutmeg-figure-provenance/v1"
    assert prov["rows"] == 3 and prov["n"] == 214 and prov["claims"] == ["C1", "C2"]
    assert prov["data_snapshot"] == "research/demo/figures/carries.data.csv"
    for part in ("Source: StatsBomb open data", "Premier League 2015/16", "min 900 minutes", "n = 214", "C1, C2"):
        assert part in prov["footnote"] and part in out
    assert "Sample: n = 214; 3 rows" in prov["footnote_long"]


def test_register_without_snapshot_is_refused(project, capsys):
    assert main(["figure", "register", "carries", "--source", "Opta"]) == 2
    assert "figure carries" in capsys.readouterr().err


def test_unknown_claim_is_refused(project, capsys):
    assert main(["figure", "register", "carries", "--data", "out/carries.csv", "--source", "Opta", "--claims", "C9"]) == 2
    assert "C9" in capsys.readouterr().err


def test_snapshot_outside_repo_is_refused(project, tmp_path_factory, capsys):
    outside = tmp_path_factory.mktemp("o") / "x.csv"
    outside.write_text("a\n1\n")
    assert main(["figure", "register", "x", "--data", str(outside), "--source", "Opta"]) == 2


def test_multi_panel_lists_both_sources(project, repo):
    prov = figures.register(project, repo, "panels", "out/carries.csv", ["StatsBomb", "Opta"], ["C1"],
                            panels=["left", "right"])
    assert "Source (panel left): StatsBomb" in prov["footnote_long"]
    assert "Source (panel right): Opta" in prov["footnote_long"]
    assert prov["footnote"].startswith("Source: StatsBomb + Opta")


def test_snapshot_is_ignored_when_data_stays_out_of_git(project, repo):
    import subprocess
    figures.register(project, repo, "carries", "out/carries.csv", ["Opta"], ["C1"])
    result = subprocess.run(["git", "check-ignore", "-q", "research/demo/figures/carries.data.csv"], cwd=repo)
    assert result.returncode == 0


def test_paths_are_relative_to_the_working_directory(project, repo, monkeypatch):
    (repo / "sub").mkdir()
    (repo / "sub" / "rows.csv").write_text("a\n1\n")
    (repo / "sub" / "chart.png").write_bytes(b"png")
    monkeypatch.chdir(repo / "sub")
    assert main(["figure", "register", "sub-fig", "--data", "rows.csv", "--source", "Opta", "--image", "chart.png"]) == 0
    prov = json.loads((project / "figures" / "sub-fig.prov.json").read_text())
    assert prov["image"] == "sub/chart.png" and prov["rows"] == 1
