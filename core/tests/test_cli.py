import json
import subprocess
import sys
from pathlib import Path

from nutmeg_core.cli import main

NUTMEG = Path(__file__).resolve().parents[1] / "nutmeg.py"


def test_help_runs_with_no_install(tmp_path):
    result = subprocess.run([sys.executable, str(NUTMEG), "--help"], capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0
    assert "claim" in result.stdout


def test_claim_add_list_show(tmp_path, capsys):
    project = tmp_path / "research" / "demo"
    project.mkdir(parents=True)
    claim = {"kind": "computed", "statement": "PPDA 9.4", "value": 9.4, "evidence": {"run_id": "R1"}}
    assert main(["--project", str(project), "claim", "add", "--json", json.dumps(claim)]) == 0
    assert json.loads(capsys.readouterr().out)["id"] == "C1"
    assert main(["--project", str(project), "claim", "list"]) == 0
    assert "PPDA 9.4" in capsys.readouterr().out
    assert main(["--project", str(project), "claim", "show", "C1"]) == 0
    assert json.loads(capsys.readouterr().out)["value"] == 9.4


def test_rejected_claim_names_the_field(tmp_path, capsys):
    project = tmp_path / "p"
    project.mkdir()
    claim = {"kind": "computed", "statement": "PPDA 9.4", "value": 9.4, "evidence": {}}
    assert main(["--project", str(project), "claim", "add", "--json", json.dumps(claim)]) == 2
    assert "evidence.run_id" in capsys.readouterr().err


def test_missing_project_is_a_usage_error(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("NUTMEG_PROJECT", raising=False)
    assert main(["claim", "list"]) == 2
    assert "no research project" in capsys.readouterr().err
