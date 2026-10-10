import json

import pytest

from nutmeg_core import project as projects
from nutmeg_core.cli import main


def test_new_creates_every_file(repo, capsys):
    assert main(["new", "shortlist-lb", "--data-in-git", "yes", "--question", "Which left-backs fit our press?"]) == 0
    folder = repo / "research" / "shortlist-lb"
    for name in ("project.json", "question.md", "plan.md", "claims.jsonl", "receipts.jsonl", "data/manifest.json"):
        assert (folder / name).is_file(), name
    for name in ("runs", "figures", "data"):
        assert (folder / name).is_dir(), name
    assert (repo / "research" / ".active").read_text().strip() == "shortlist-lb"
    assert ".active" in (repo / "research" / ".gitignore").read_text().splitlines()
    assert "claims.jsonl merge=union" in (repo / "research" / ".gitattributes").read_text().splitlines()
    assert "Which left-backs fit our press?" in (folder / "question.md").read_text()
    meta = json.loads((folder / "project.json").read_text())
    assert meta["author"] == "Test Analyst" and meta["data_in_git"] == "yes"
    receipt = json.loads((folder / "receipts.jsonl").read_text().splitlines()[0])
    assert receipt["kind"] == "project_created" and receipt["data_in_git_from"] == "user"
    assert not (folder / ".gitignore").exists()


def test_marker_is_ignored_by_git(repo):
    import subprocess
    main(["new", "demo", "--data-in-git", "yes"])
    result = subprocess.run(["git", "check-ignore", "research/.active"], cwd=repo, capture_output=True, text=True)
    assert result.returncode == 0
    attr = subprocess.run(["git", "check-attr", "merge", "research/demo/claims.jsonl"], cwd=repo, capture_output=True, text=True)
    assert attr.stdout.strip().endswith("merge: union")


def test_data_out_of_git(repo):
    import subprocess
    assert main(["new", "demo", "--data-in-git", "no"]) == 0
    folder = repo / "research" / "demo"
    (folder / "data" / "events.csv").write_text("x\n")
    (folder / "runs" / "R1" / "outputs").mkdir(parents=True)
    (folder / "runs" / "R1" / "outputs" / "table.csv").write_text("x\n")
    (folder / "figures" / "shots.data.csv").write_text("x\n")
    for path, ignored in (
        ("research/demo/data/events.csv", True),
        ("research/demo/data/manifest.json", False),
        ("research/demo/runs/R1/outputs/table.csv", True),
        ("research/demo/figures/shots.data.csv", True),
        ("research/demo/claims.jsonl", False),
    ):
        result = subprocess.run(["git", "check-ignore", "-q", path], cwd=repo)
        assert (result.returncode == 0) == ignored, path


def test_new_without_policy_or_flag_asks(repo, capsys):
    assert main(["new", "demo"]) == 2
    assert "Ask the user" in capsys.readouterr().err
    assert not (repo / "research" / "demo").exists()


def test_team_policy_applies(repo, capsys):
    (repo / ".nutmeg").mkdir()
    (repo / ".nutmeg" / "team.json").write_text(json.dumps({"data_in_git": "no"}))
    assert main(["new", "demo"]) == 0
    assert (repo / "research" / "demo" / ".gitignore").exists()
    assert main(["new", "other", "--data-in-git", "yes"]) == 2
    assert "team policy" in capsys.readouterr().err


def test_second_new_switches_marker_and_keeps_first(repo):
    main(["new", "first", "--data-in-git", "yes"])
    (repo / "research" / "first" / "notes.md").write_text("keep me")
    main(["new", "second", "--data-in-git", "yes"])
    assert projects.active_slug(repo) == "second"
    assert (repo / "research" / "first" / "notes.md").read_text() == "keep me"
    assert main(["open", "first"]) == 0
    assert projects.active_slug(repo) == "first"


def test_new_refuses_existing_slug_and_bad_slug(repo, capsys):
    main(["new", "demo", "--data-in-git", "yes"])
    assert main(["new", "demo", "--data-in-git", "yes"]) == 2
    assert "already exists" in capsys.readouterr().err
    assert main(["new", "Bad Slug", "--data-in-git", "yes"]) == 2


def test_close_removes_only_the_marker(repo):
    main(["new", "demo", "--data-in-git", "yes"])
    before = sorted(p.relative_to(repo) for p in (repo / "research").rglob("*"))
    assert main(["close"]) == 0
    after = sorted(p.relative_to(repo) for p in (repo / "research").rglob("*"))
    assert set(before) - set(after) == {(repo / "research" / ".active").relative_to(repo)}
    assert projects.active_project(repo) is None


def test_commands_use_the_active_project(repo, capsys):
    main(["new", "demo", "--data-in-git", "yes"])
    claim = {"kind": "computed", "statement": "PPDA 9.4", "value": 9.4, "evidence": {"run_id": "R1"}}
    assert main(["claim", "add", "--json", json.dumps(claim)]) == 0
    assert (repo / "research" / "demo" / "claims.jsonl").read_text().strip()
    main(["close"])
    capsys.readouterr()
    assert main(["claim", "list"]) == 2
    assert "no active research project" in capsys.readouterr().err


def test_plan_choice_without_why_fails_with_its_name(repo, capsys):
    main(["new", "demo", "--data-in-git", "yes"])
    plan = repo / "research" / "demo" / "plan.md"
    plan.write_text(plan.read_text() + "\n### filter: at least 900 minutes\n- rests_on: rule metric-misuse per-90 minimum\n")
    capsys.readouterr()
    assert main(["plan", "check"]) == 1
    out = capsys.readouterr().out
    assert "at least 900 minutes" in out and "why" in out


def test_plan_choose_writes_a_valid_choice(repo, capsys):
    main(["new", "demo", "--data-in-git", "yes"])
    plan = repo / "research" / "demo" / "plan.md"
    plan.write_text(plan.read_text() + "\n## Notes\n\nfree text\n")
    assert main(["plan", "choose", "--kind", "metric", "--choice", "npxG per 90",
                 "--why", "Penalties distort per-player comparisons.",
                 "--rests-type", "docs", "--rests-ref", "football-docs statsbomb shot.statsbomb_xg"]) == 0
    assert main(["plan", "check"]) == 0
    text = plan.read_text()
    assert text.index("### metric: npxG per 90") < text.index("## Notes")
    choices = projects.parse_choices(text)
    assert choices[0]["why"] == "Penalties distort per-player comparisons."
    assert choices[0]["rests_on"].startswith("docs ")


def test_plan_choose_rejects_a_long_reason(repo, capsys):
    main(["new", "demo", "--data-in-git", "yes"])
    assert main(["plan", "choose", "--kind", "metric", "--choice", "xG", "--why", "x" * 300,
                 "--rests-type", "user", "--rests-ref", "asked for xG"]) == 2


def test_status(repo, capsys):
    assert main(["status"]) == 0
    assert "No active" in capsys.readouterr().out
    main(["new", "demo", "--data-in-git", "yes"])
    capsys.readouterr()
    assert main(["status"]) == 0
    assert "research/demo" in capsys.readouterr().out
