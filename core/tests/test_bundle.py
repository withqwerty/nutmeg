import json
import zipfile

import pytest

from nutmeg_core import gate
from nutmeg_core.cli import main


@pytest.fixture
def project(repo):
    main(["new", "demo", "--data-in-git", "no"])
    folder = repo / "research" / "demo"
    (folder / "data" / "events.csv").write_text("player,xg\nA,0.4\n")
    (folder / "runs" / "R1" / "outputs").mkdir(parents=True)
    (folder / "runs" / "R1" / "outputs" / "table.csv").write_text("player,xg\nA,0.4\n")
    (folder / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "status": "ok"}))
    (folder / "runs" / "R1" / "stdout.txt").write_text("A 0.4\n")
    (folder / "figures" / "shots.data.csv").write_text("x,y\n1,2\n")
    (folder / "figures" / "shots.prov.json").write_text("{}")
    (folder / "report.md").write_text("Report.\n")
    return folder


def names(path):
    with zipfile.ZipFile(path) as archive:
        return set(archive.namelist()), json.loads(archive.read("demo/bundle-manifest.json"))


def test_raw_no_keeps_hashes_only(project, repo, capsys):
    assert main(["bundle", "--raw", "no", "--out", "out/b.zip"]) == 0
    files, manifest = names(repo / "out" / "b.zip")
    assert "demo/report.md" in files and "demo/claims.jsonl" in files and "demo/data/manifest.json" in files
    assert "demo/runs/R1/run.json" in files
    for raw in ("demo/data/events.csv", "demo/runs/R1/outputs/table.csv", "demo/figures/shots.data.csv",
                "demo/runs/R1/stdout.txt"):
        assert raw not in files
    omitted = {o["path"] for o in manifest["raw_omitted"]}
    assert {"data/events.csv", "runs/R1/outputs/table.csv", "figures/shots.data.csv"} <= omitted
    assert all(len(o["sha256"]) == 64 for o in manifest["raw_omitted"])
    assert manifest["raw_data"] is False


def test_raw_yes_includes_data_and_licence_note(project, repo):
    (repo / ".nutmeg").mkdir()
    (repo / ".nutmeg" / "team.json").write_text(json.dumps({"licences": {"opta": "internal use only"}}))
    assert main(["bundle", "--raw", "yes", "--out", "out/b.zip"]) == 0
    files, manifest = names(repo / "out" / "b.zip")
    assert "demo/data/events.csv" in files and "demo/figures/shots.data.csv" in files
    assert manifest["licences"] == {"opta": "internal use only"}


def test_missing_raw_choice_is_refused(project, capsys):
    assert main(["bundle"]) == 2
    assert "--raw yes" in capsys.readouterr().err


def test_no_lockfile_records_python_and_packages(project, repo):
    main(["bundle", "--raw", "no", "--out", "out/b.zip"])
    _, manifest = names(repo / "out" / "b.zip")
    assert manifest["environment"]["lockfiles"] == [] and manifest["environment"]["python"]
    (repo / "uv.lock").write_text("version = 1\n")
    main(["bundle", "--raw", "no", "--out", "out/c.zip"])
    files, manifest = names(repo / "out" / "c.zip")
    assert manifest["environment"]["lockfiles"] == ["uv.lock"] and "environment/uv.lock" in files


def test_bundle_redacts_secrets(project, repo):
    (repo / ".env").write_text("KEY=secret-key-445566\n")
    (project / "report.md").write_text("used secret-key-445566\n")
    main(["bundle", "--raw", "no", "--out", "out/b.zip"])
    with zipfile.ZipFile(repo / "out" / "b.zip") as archive:
        assert b"secret-key-445566" not in archive.read("demo/report.md")


def test_bundle_gate_shows_raw_choice_and_licence(project, repo):
    (repo / ".nutmeg").mkdir()
    (repo / ".nutmeg" / "team.json").write_text(json.dumps({"licences": {"opta": "internal use only"}}))
    yes = gate.decide("nutmeg bundle --raw yes", repo, project, repo)
    assert yes.decision == "ask" and "RAW DATA INCLUDED" in yes.reason and "opta: internal use only" in yes.reason
    no = gate.decide("nutmeg bundle --raw no", repo, project, repo)
    assert "Raw data left out" in no.reason
    missing = gate.decide("nutmeg bundle", repo, project, repo)
    assert "will refuse" in missing.reason
