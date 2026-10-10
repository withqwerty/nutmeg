import json
import subprocess
import sys
from pathlib import Path

from nutmeg_core.cli import main
from nutmeg_core.ledger import Ledger

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


def test_missing_project_is_a_usage_error(repo, capsys):
    assert main(["claim", "list"]) == 2
    assert "no active research project" in capsys.readouterr().err


def test_claim_add_takes_a_batch_in_one_call(repo, capsys):
    main(["new", "batch", "--data-in-git", "yes"])
    project = repo / "research" / "batch"
    (project / "runs" / "R1").mkdir(parents=True)
    (project / "runs" / "R1" / "run.json").write_text('{"id": "R1", "status": "ok"}')
    lines = [
        {"kind": "computed", "statement": "a is 1", "value": 1, "evidence": {"run_id": "R1"}},
        {"kind": "computed", "statement": "b is 2", "value": 2, "evidence": {"run_id": "R1"}},
        {"kind": "computed", "statement": "no evidence", "value": 3},
        {"kind": "definition", "statement": "PPDA is passes per defensive action", "evidence": {"definition": "x"}},
    ]
    (repo / "claims.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    capsys.readouterr()
    assert main(["claim", "add", "--file", "claims.jsonl"]) == 1
    out, err = capsys.readouterr()
    assert "Added 3 claim(s): C1, C2, C3" in out and "rejected claim 3 (no evidence)" in err
    assert main(["claim", "add", "--json", json.dumps(lines[:2])]) == 0
    assert "Added 2 claim(s): C4, C5" in capsys.readouterr().out
    claims = Ledger(project / "claims.jsonl").claims()
    assert len(claims) == 5 and all(c.get("author") for c in claims.values())


def test_a_bad_line_in_a_batch_adds_nothing(repo, capsys):
    main(["new", "batch2", "--data-in-git", "yes"])
    (repo / "c.jsonl").write_text('{"kind": "definition", "statement": "x", "evidence": {"definition": "y"}}\nnot json\n')
    assert main(["claim", "add", "--file", "c.jsonl"]) == 2
    assert "line 2 is not valid JSON" in capsys.readouterr().err
    assert not Ledger(repo / "research" / "batch2" / "claims.jsonl").claims()
