import json
import shutil

import pytest

from nutmeg_core import gate
from nutmeg_core.cli import main

pytestmark = pytest.mark.skipif(shutil.which("python3") is None, reason="needs python3 on PATH")


@pytest.fixture
def project(repo):
    main(["new", "club", "--data-in-git", "no"])
    (repo / "data").mkdir()
    (repo / "data" / "events.csv").write_text("player_id,xg\n1,0.4\n2,0.3\n")
    return repo / "research" / "club"


def test_run_records_everything(project, repo, capsys):
    (repo / "analysis.py").write_text(
        "import csv, os\nrows = list(csv.DictReader(open('data/events.csv')))\n"
        "total = sum(float(r['xg']) for r in rows)\nprint(round(total, 2))\n"
        "open(os.path.join(os.environ['NUTMEG_OUTPUT_DIR'], 'total.txt'), 'w').write(str(total))\n")
    assert main(["run", "analysis.py", "--input", "data/events.csv"]) == 0
    folder = project / "runs" / "R1"
    record = json.loads((folder / "run.json").read_text())
    assert record["status"] == "ok" and record["exit_code"] == 0
    assert record["file"] == "analysis.py" and record["interpreter"] == "python3"
    assert record["interpreter_version"].startswith("Python 3")
    assert record["inputs"][0]["path"] == "data/events.csv"
    assert (folder / "code" / "analysis.py").is_file()
    assert (folder / "stdout.txt").read_text().strip() == "0.7"
    assert any(o["path"].endswith("outputs/total.txt") for o in record["outputs"])
    assert (folder / "gate.json").is_file()
    assert json.loads((folder / "gate.json").read_text())["gate_shown"] is False
    receipts = [json.loads(line) for line in (project / "receipts.jsonl").read_text().splitlines()]
    assert receipts[-1]["kind"] == "run" and receipts[-1]["run_id"] == "R1"
    out = capsys.readouterr()
    assert "0.7" in out.out and "recorded run R1" in out.err


def test_gate_card_is_moved_into_the_run(project, repo):
    (repo / "a.py").write_text("print(1)\n")
    gate.decide("nutmeg run a.py --input data/events.csv", repo, project, repo)
    assert len(list((project / "runs" / ".pending").glob("*.json"))) == 1
    assert main(["run", "a.py", "--input", "data/events.csv"]) == 0
    assert not list((project / "runs" / ".pending").glob("*.json"))
    shown = json.loads((project / "runs" / "R1" / "gate.json").read_text())
    assert shown["gate_shown"] is True and shown["changed_since_gate"] == []


def test_input_changed_after_gate_is_flagged(project, repo, capsys):
    (repo / "a.py").write_text("print(1)\n")
    gate.decide("nutmeg run a.py --input data/events.csv", repo, project, repo)
    (repo / "data" / "events.csv").write_text("player_id,xg\n1,0.9\n")
    assert main(["run", "a.py", "--input", "data/events.csv"]) == 0
    record = json.loads((project / "runs" / "R1" / "run.json").read_text())
    assert record["gate"]["changed_since_gate"] == ["data/events.csv"]
    assert "changed after the gate card" in capsys.readouterr().err


def test_failing_script_is_recorded_as_failed(project, repo):
    (repo / ".env").write_text("OPTA_KEY=opta-secret-123456\n")
    (repo / "bad.py").write_text("raise SystemExit('auth failed for opta-secret-123456')\n")
    assert main(["run", "bad.py"]) == 1
    folder = project / "runs" / "R1"
    record = json.loads((folder / "run.json").read_text())
    assert record["status"] == "failed" and record["exit_code"] == 1
    stderr = (folder / "stderr.txt").read_text()
    assert "auth failed" in stderr and "opta-secret-123456" not in stderr
    assert (folder / "code" / "bad.py").is_file()


def test_input_outside_repo_is_refused(project, repo, capsys):
    (repo / "a.py").write_text("print(1)\n")
    assert main(["run", "a.py", "--input", "~/.aws/credentials"]) == 2
    assert "outside the repository" in capsys.readouterr().err
    assert not (project / "runs" / "R1").exists()


def test_rerun_with_one_changed_line_shows_only_the_change(project, repo):
    (repo / "a.py").write_text("".join(f"x{i} = {i}\n" for i in range(30)) + "print(x1)\n")
    assert main(["run", "a.py"]) == 0
    (repo / "a.py").write_text("".join(f"x{i} = {i}\n" for i in range(30)) + "print(x2)\n")
    decision = gate.decide("nutmeg run a.py", repo, project, repo)
    assert "Changes since run R1" in decision.reason
    assert "-print(x1)" in decision.reason and "+print(x2)" in decision.reason
    assert "x10 = 10" not in decision.reason


def test_unchanged_rerun_says_so(project, repo):
    (repo / "a.py").write_text("print(1)\n")
    main(["run", "a.py"])
    decision = gate.decide("nutmeg run a.py", repo, project, repo)
    assert "Same code, SQL and inputs as run R1" in decision.reason


def test_script_args_after_double_dash(project, repo):
    (repo / "a.py").write_text("import sys\nprint(sys.argv[1:])\n")
    assert main(["run", "a.py", "--", "--season", "2025"]) == 0
    assert "['--season', '2025']" in (project / "runs" / "R1" / "stdout.txt").read_text()


@pytest.mark.skipif(not (shutil.which("duckdb") or shutil.which("sqlite3")), reason="needs duckdb or sqlite3")
def test_sql_run_records_the_tool(project, repo):
    (repo / "q.sql").write_text("select 40 + 2;\n")
    assert main(["run", "q.sql"]) == 0
    record = json.loads((project / "runs" / "R1" / "run.json").read_text())
    assert record["interpreter"] == ("duckdb" if shutil.which("duckdb") else "sqlite3")
    assert "42" in (project / "runs" / "R1" / "stdout.txt").read_text()


def test_gate_command_prints_card_without_running(project, repo, capsys):
    (repo / "a.py").write_text("open('ran.txt', 'w').write('x')\n")
    assert main(["gate", "a.py"]) == 0
    assert "nutmeg run gate" in capsys.readouterr().out
    assert not (repo / "ran.txt").exists()
    assert not (project / "runs" / "R1").exists()
