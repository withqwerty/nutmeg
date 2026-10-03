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
