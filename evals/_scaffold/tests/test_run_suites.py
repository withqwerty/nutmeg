import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_suites  # noqa: E402


def make_case(folder, name, tools=("Read", "Glob")):
    case = folder / name
    (case / "graders").mkdir(parents=True)
    (case / "prompt.md").write_text(f"---\nallowed_tools: [{', '.join(tools)}]\n---\n\nHeld-out prompt for {name}.\n")
    (case / "graders" / "g.md").write_text("---\ntype: regex\n---\n\nyes\n")
    return case


@pytest.fixture
def layout(tmp_path):
    root = tmp_path / "plugin"
    (root / "evals" / "mocks" / "football-docs").mkdir(parents=True)
    make_case(root / "evals", "public-plain")
    make_case(root / "evals", "public-bash", tools=("Read", "Bash(python3:*)"))
    holdout = tmp_path / "private-holdout"
    holdout.mkdir()
    make_case(holdout, "secret-one", tools=("Read", "Bash(python3:*)"))
    make_case(holdout, "secret-two")
    out = tmp_path / "results"
    return root, holdout, out


@pytest.fixture
def fake_runners(monkeypatch):
    calls = []

    def plugin(eval_dir_name, name, tools, args, out, root):
        link = Path(root) / eval_dir_name
        calls.append(("plugin", eval_dir_name, name, link.exists(), (link / "mocks").exists()))
        return 1.0, None

    def live(eval_dir, name, args, out=None, label=None):
        calls.append(("live", str(eval_dir), name, Path(eval_dir).exists(), None))
        return 0.5, None

    monkeypatch.setattr(run_suites, "run_plugin", plugin)
    monkeypatch.setattr(run_suites, "run_live_case", live)
    return calls


def test_without_holdout_only_public_runs_and_says_so(layout, fake_runners, capsys):
    root, _, out = layout
    assert run_suites.main(["--out", str(out)], root=root, environ={}) == 0
    printed = capsys.readouterr().out
    assert "public score: 0.75 over 2 case(s)" in printed
    assert "holdout score: not run" in printed
    assert "NUTMEG_HOLDOUT_DIR is not set" in printed
    summary = json.loads((out / "summary.json").read_text())
    assert summary["holdout"] is None and summary["public"] == 0.75


def test_with_holdout_both_scores_print_and_the_link_is_removed(layout, fake_runners, capsys):
    root, holdout, out = layout
    assert run_suites.main(["--out", str(out)], root=root, environ={"NUTMEG_HOLDOUT_DIR": str(holdout)}) == 0
    printed = capsys.readouterr().out
    assert "public score: 0.75" in printed and "holdout score: 0.75" in printed
    # The plugin engine saw the linked folder with the mocks; the link is gone afterwards.
    plugin_holdout = [c for c in fake_runners if c[0] == "plugin" and c[1] == run_suites.LINK_DIR]
    assert plugin_holdout == [("plugin", run_suites.LINK_DIR, "secret-two", True, True)]
    assert not (root / run_suites.LINK_DIR).exists()
    # No held-out text anywhere in the plugin folder.
    for path in root.rglob("*"):
        if path.is_file():
            assert "Held-out prompt for secret" not in path.read_text(errors="replace")


def test_auto_engine_sends_bash_cases_live(layout, fake_runners):
    root, holdout, out = layout
    run_suites.main(["--out", str(out)], root=root, environ={"NUTMEG_HOLDOUT_DIR": str(holdout)})
    engines = {name: engine for engine, _, name, _, _ in fake_runners}
    assert engines == {"public-plain": "plugin", "public-bash": "live", "secret-two": "plugin", "secret-one": "live"}


def test_the_link_is_removed_when_a_run_fails(layout, monkeypatch):
    root, holdout, out = layout

    def boom(*a, **k):
        raise RuntimeError("claude crashed")

    monkeypatch.setattr(run_suites, "run_plugin", boom)
    monkeypatch.setattr(run_suites, "run_live_case", boom)
    with pytest.raises(RuntimeError):
        run_suites.main(["--suite", "holdout", "--out", str(out)], root=root,
                        environ={"NUTMEG_HOLDOUT_DIR": str(holdout)})
    assert not (root / run_suites.LINK_DIR).exists()


def test_loop_refuses_fewer_than_ten_holdout_cases(layout, fake_runners, capsys):
    root, holdout, out = layout
    code = run_suites.main(["--loop", "--out", str(out)], root=root, environ={"NUTMEG_HOLDOUT_DIR": str(holdout)})
    assert code == 2
    assert "at least 10 held-out cases" in capsys.readouterr().err
    assert fake_runners == []


def test_loop_starts_with_ten_holdout_cases(layout, fake_runners):
    root, holdout, out = layout
    for i in range(8):
        make_case(holdout, f"extra-{i}")
    assert run_suites.main(["--loop", "--suite", "holdout", "--out", str(out)], root=root,
                           environ={"NUTMEG_HOLDOUT_DIR": str(holdout)}) == 0
    assert len(fake_runners) == 10


def test_loop_without_holdout_refuses(layout, fake_runners, capsys):
    root, _, out = layout
    assert run_suites.main(["--loop", "--out", str(out)], root=root, environ={}) == 2
    assert "NUTMEG_HOLDOUT_DIR" in capsys.readouterr().err


def test_holdout_inside_the_repo_is_refused(layout, fake_runners, capsys):
    root, _, out = layout
    inside = root / "evals" / "private"
    inside.mkdir()
    assert run_suites.main(["--out", str(out)], root=root, environ={"NUTMEG_HOLDOUT_DIR": str(inside)}) == 2
    assert "outside the public repository" in capsys.readouterr().err


def test_results_inside_the_repo_are_refused(layout, fake_runners, capsys):
    root, holdout, _ = layout
    code = run_suites.main(["--out", str(root / "evals" / "results")], root=root,
                           environ={"NUTMEG_HOLDOUT_DIR": str(holdout)})
    assert code == 2
    assert "--out must be outside the repository" in capsys.readouterr().err


def test_default_results_go_to_a_temporary_folder(layout, fake_runners, capsys):
    root, _, _ = layout
    run_suites.main(["--suite", "public"], root=root, environ={})
    line = [l for l in capsys.readouterr().out.splitlines() if l.startswith("results: ")][0]
    folder = Path(line.split(": ", 1)[1])
    assert (folder / "summary.json").is_file()
    assert root.resolve() not in folder.resolve().parents


def test_a_folder_the_runner_did_not_make_is_never_deleted(layout, fake_runners, capsys):
    root, holdout, out = layout
    mine = root / run_suites.LINK_DIR
    mine.mkdir()
    (mine / "notes.txt").write_text("someone's work")
    code = run_suites.main(["--suite", "holdout", "--out", str(out)], root=root,
                           environ={"NUTMEG_HOLDOUT_DIR": str(holdout)})
    assert code == 2
    assert "not a folder this runner made" in capsys.readouterr().err
    assert (mine / "notes.txt").read_text() == "someone's work"


def test_case_glob_filters_both_suites(layout, fake_runners):
    root, holdout, out = layout
    run_suites.main(["--case", "*-two", "--out", str(out)], root=root, environ={"NUTMEG_HOLDOUT_DIR": str(holdout)})
    assert [c[2] for c in fake_runners] == ["secret-two"]


def test_a_glob_that_matches_nothing_says_so(layout, fake_runners, capsys):
    root, holdout, out = layout
    run_suites.main(["--case", "public-*", "--out", str(out)], root=root, environ={"NUTMEG_HOLDOUT_DIR": str(holdout)})
    assert "held-out set: no case matches --case" in capsys.readouterr().out


def test_plugin_runner_reads_the_case_score(tmp_path, monkeypatch):
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        out = Path(cmd[cmd.index("--output-dir") + 1])
        (out / "aggregate-result.json").write_text(json.dumps({"cases": [
            {"name": "c1", "aggregates": {"score": 0.5}, "arms": {"with": [{"error": None}]}}]}))

    monkeypatch.setattr(run_suites.subprocess, "run", fake_run)
    args = type("A", (), {"runs": 1, "model": "sonnet", "judge_model": "haiku"})()
    score, error = run_suites.run_plugin("evals", "c1", ["Read", "Bash(python3:*)", "Write"], args, tmp_path, tmp_path)
    assert (score, error) == (0.5, None)
    assert seen["cmd"][seen["cmd"].index("--allow-tools") + 1:][:2] == ["Bash(python3:*)", "Write"]


def test_a_running_run_blocks_a_second_one(layout, fake_runners, capsys):
    root, holdout, out = layout
    busy = root / run_suites.LINK_DIR
    busy.mkdir()
    (busy / run_suites.MARKER).write_text(f"{os.getpid()} made by run_suites\n")
    code = run_suites.main(["--suite", "holdout", "--out", str(out)], root=root,
                           environ={"NUTMEG_HOLDOUT_DIR": str(holdout)})
    assert code == 2
    assert "another run_suites.py run" in capsys.readouterr().err
    assert (busy / run_suites.MARKER).exists()


def test_a_folder_left_by_a_dead_run_is_replaced(layout, fake_runners):
    root, holdout, out = layout
    stale = root / run_suites.LINK_DIR
    stale.mkdir()
    (stale / run_suites.MARKER).write_text("99999999 made by run_suites\n")
    assert run_suites.main(["--suite", "holdout", "--out", str(out)], root=root,
                           environ={"NUTMEG_HOLDOUT_DIR": str(holdout)}) == 0
    assert not stale.exists()


def test_live_only_holdout_runs_link_nothing(layout, fake_runners):
    root, holdout, out = layout
    busy = root / run_suites.LINK_DIR
    busy.mkdir()
    (busy / run_suites.MARKER).write_text(f"{os.getpid()} made by run_suites\n")
    # secret-one grants Bash, so it runs live from the held-out folder, even while another run holds the link.
    assert run_suites.main(["--suite", "holdout", "--case", "secret-one", "--out", str(out)], root=root,
                           environ={"NUTMEG_HOLDOUT_DIR": str(holdout)}) == 0
    assert fake_runners == [("live", str(holdout.resolve()), "secret-one", True, None)]


def test_live_runner_saves_each_run_outside_the_repo(tmp_path, monkeypatch):
    def fake_once(name, model, keep, judge_model, eval_dir):
        return {"case": name, "verdicts": {"a": True, "b": False}, "judged": {}, "cost": 0.1, "last": "answer",
                "bash": [], "work": None}

    monkeypatch.setattr(run_suites.run_live, "run_once", fake_once)
    args = type("A", (), {"runs": 2, "model": "sonnet", "judge_model": "haiku", "keep": False})()
    score, error = run_suites.run_live_case(tmp_path / "cases", "c1", args, tmp_path / "out", "holdout")
    assert (score, error) == (0.5, None)
    saved = json.loads((tmp_path / "out" / "holdout" / "c1-run2.json").read_text())
    assert saved["last"] == "answer"
