import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_live  # noqa: E402


def test_judge_input_is_the_last_message_without_a_file_target(tmp_path):
    assert run_live.judge_input("answer", "", tmp_path) == "answer"


def test_judge_input_adds_the_named_files(tmp_path):
    report = tmp_path / "research" / "demo" / "report.md"
    report.parent.mkdir(parents=True)
    report.write_text("| Match | Shots |\n| A | 29 |\n")
    text = run_live.judge_input("answer", "file:research/*/report.md", tmp_path)
    assert text.startswith("answer")
    assert "--- research/demo/report.md ---" in text and "| A | 29 |" in text


def test_judge_input_with_no_matching_file_is_the_last_message(tmp_path):
    assert run_live.judge_input("answer", "file:research/*/report.md", tmp_path) == "answer"


def test_agent_env_isolates_the_user_config_and_blocks_pip_outside_a_venv(tmp_path):
    env = run_live.agent_env(tmp_path)
    assert env["NUTMEG_USER_CONFIG"] == str(tmp_path / ".nutmeg-user.json")
    assert env["PIP_REQUIRE_VIRTUALENV"] == "1"


def _exec_case(tmp_path, script):
    folder = tmp_path / "case"
    (folder / "graders").mkdir(parents=True)
    (folder / "graders" / "check.py").write_text(script)
    work = tmp_path / "work"
    work.mkdir()
    (work / "result.txt").write_text("42")
    return folder, work


def test_exec_grade_passes_when_the_check_exits_zero(tmp_path):
    folder, work = _exec_case(tmp_path, "import sys, pathlib\nw = pathlib.Path(sys.argv[1])\n"
                                        "sys.exit(0 if (w / 'result.txt').read_text() == '42' else 1)\n")
    ok, notes = run_live.exec_grade(folder, {"script": "check.py"}, work)
    assert ok and notes[0].startswith("PASS")


def test_exec_grade_fails_and_keeps_the_reason(tmp_path):
    folder, work = _exec_case(tmp_path, "print('wrong value'); raise SystemExit(1)\n")
    ok, notes = run_live.exec_grade(folder, {"script": "check.py"}, work)
    assert not ok and "wrong value" in notes[0]


def test_exec_grade_works_on_a_copy_and_leaves_the_run_unchanged(tmp_path):
    folder, work = _exec_case(tmp_path, "import sys, pathlib\n(pathlib.Path(sys.argv[1]) / 'result.txt').write_text('changed')\n")
    ok, _ = run_live.exec_grade(folder, {"script": "check.py"}, work)
    assert ok and (work / "result.txt").read_text() == "42"


def test_exec_grade_refuses_a_script_outside_the_graders_folder(tmp_path):
    folder, work = _exec_case(tmp_path, "")
    (folder / "outside.py").write_text("")
    ok, notes = run_live.exec_grade(folder, {"script": "../outside.py"}, work)
    assert not ok and "not found" in notes[0]
