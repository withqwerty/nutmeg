"""Regression tests for the code review of U1-U5 (bypasses, leaks and false passes)."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from nutmeg_core import check as checks
from nutmeg_core import gate
from nutmeg_core.cli import main
from nutmeg_core.ledger import Ledger
from nutmeg_core.redact import Redactor, parse_env_file

PLUGIN = Path(__file__).resolve().parents[2]
HAS_PYTHON = shutil.which("python3") is not None


@pytest.fixture
def project(repo):
    main(["new", "club", "--data-in-git", "no"])
    (repo / "a.py").write_text("print(1)\n")
    return repo / "research" / "club"


# 1. A `#` inside a word is not a comment in bash, so the chain after it is seen.
def test_hash_inside_a_word_does_not_hide_a_chain(project, repo):
    assert gate.parse("nutmeg run a.py# && printf CHAIN").kind == "compound"
    assert gate.parse("nutmeg run a.py # comment").kind == "compound"
    assert gate.decide("nutmeg run a.py# && printf CHAIN", repo, project, repo).card is None


# 2. Wrappers do not hide an interpreter or a nutmeg run.
@pytest.mark.parametrize("command", [
    "/usr/bin/env python3 a.py", "env -i python3 a.py", "env -u HOME python3 a.py",
    "conda run -n analysis python3 a.py", "uv run --project . python3 a.py", "command python3 a.py",
    "timeout 60 python3 a.py", "nice -n 10 Rscript m.R", "poetry run python a.py", "pixi run -e dev python a.py",
])
def test_wrapped_interpreters_are_caught(command):
    assert gate.parse(command).kind == "interpreter", command


def test_wrapped_nutmeg_run_is_a_run():
    parsed = gate.parse('uv run --with pandas python3 "/p/core/nutmeg.py" run a.py')
    assert parsed.kind == "nutmeg" and parsed.subcommand == "run"


def test_unreadable_wrapper_asks():
    assert gate.parse("env -S 'python3 a.py'").kind == "compound"
    assert gate.parse("uv run --unknown-flag value python3 a.py").kind in ("interpreter", "compound")


# 3. --interpreter cannot swap in other code, and the card shows the full command.
def test_interpreter_with_inline_code_is_refused(project, repo, capsys):
    decision = gate.decide("nutmeg run a.py --interpreter \"python3 -c 'print(999)'\"", repo, project, repo)
    assert "code-running options" in decision.reason
    assert main(["run", "a.py", "--interpreter", "python3 -c 'print(999)'"]) == 2
    assert not (project / "runs" / "R1").exists()


def test_card_shows_command_and_script_args(project, repo):
    decision = gate.decide("nutmeg run a.py -- --mode send --to everyone", repo, project, repo)
    assert "Command: python3 a.py --mode send --to everyone" in decision.reason


@pytest.mark.skipif(not HAS_PYTHON, reason="needs python3")
def test_changed_script_args_show_on_rerun(project, repo):
    main(["run", "a.py", "--", "--season", "2024"])
    decision = gate.decide("nutmeg run a.py -- --season 2025", repo, project, repo)
    assert "command was: python3 a.py --season 2024" in decision.reason
    assert "command now: python3 a.py --season 2025" in decision.reason


# 4. Gate and CLI agree on the project and on option spelling.
def test_abbreviated_option_is_refused_by_both(project, repo, capsys):
    decision = gate.decide("nutmeg --proj research/club run a.py", repo, project, repo)
    assert decision is not None and decision.decision == "ask"
    with pytest.raises(SystemExit):
        main(["--proj", "research/club", "run", "a.py"])


def test_project_equals_form_and_env_target_the_other_project(project, repo):
    main(["new", "other", "--data-in-git", "no"])
    main(["open", "club"])
    gate.decide("nutmeg --project=research/other run a.py", repo, project, repo)
    assert list((repo / "research" / "other" / "runs" / ".pending").glob("*.json"))
    assert not (project / "runs" / ".pending").exists()
    gate.decide("NUTMEG_PROJECT=research/other nutmeg run a.py --input a.py", repo, project, repo)
    assert len(list((repo / "research" / "other" / "runs" / ".pending").glob("*.json"))) == 2


# 5. The pending card is bound to the working directory, and goes stale.
def test_pending_card_depends_on_cwd(project, repo):
    (repo / "sub").mkdir()
    gate.decide(f"nutmeg run {repo / 'a.py'}", repo, project, repo)
    gate.decide(f"nutmeg run {repo / 'a.py'}", repo, project, repo / "sub")
    assert len(list((project / "runs" / ".pending").glob("*.json"))) == 2


@pytest.mark.skipif(not HAS_PYTHON, reason="needs python3")
def test_stale_pending_card_counts_as_not_shown(project, repo):
    gate.decide("nutmeg run a.py", repo, project, repo)
    pending = next((project / "runs" / ".pending").glob("*.json"))
    card = json.loads(pending.read_text())
    card["created"] = "2020-01-01T00:00:00Z"
    pending.write_text(json.dumps(card))
    main(["run", "a.py"])
    assert json.loads((project / "runs" / "R1" / "run.json").read_text())["gate"]["shown"] is False


# 6. Code copies and text outputs are redacted.
@pytest.mark.skipif(not HAS_PYTHON, reason="needs python3")
def test_code_copy_and_outputs_are_redacted(project, repo):
    (repo / ".env").write_text("OPTA_KEY=opta-secret-123456\n")
    (repo / "leak.py").write_text(
        "import os\nKEY = 'opta-secret-123456'\n"
        "open(os.path.join(os.environ['NUTMEG_OUTPUT_DIR'], 'out.csv'), 'w').write('key,' + KEY)\n")
    assert main(["run", "leak.py"]) == 0
    run = project / "runs" / "R1"
    for path in run.rglob("*"):
        if path.is_file():
            assert "opta-secret-123456" not in path.read_text(errors="replace"), path


# 7. Notes, gate errors, why output and snapshots do not leak or escape the repo.
def test_contest_note_is_redacted(project, repo):
    (repo / ".env").write_text("TOKEN=tok-secret-998877\n")
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "x", "value": 1, "evidence": {"run_id": "R1"}})
    main(["contest", "C1", "--note", "re-ran with tok-secret-998877"])
    assert "tok-secret-998877" not in (project / "claims.jsonl").read_text()
    assert "tok-secret-998877" not in (project / "receipts.jsonl").read_text()


def test_gate_error_is_redacted(project, repo):
    (repo / ".env").write_text("TOKEN=tok-secret-998877\n")
    decision = gate.decide("nutmeg run --bogus tok-secret-998877", repo, project, repo)
    assert "tok-secret-998877" not in decision.reason


def test_why_does_not_read_snapshots_outside_the_repo(project, repo, tmp_path_factory, capsys):
    outside = tmp_path_factory.mktemp("outside") / "private.csv"
    outside.write_text("name,salary\nX,1000000\n")
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "x", "value": 1,
                                             "evidence": {"run_id": "R1", "snapshot": str(outside)}})
    main(["why", "C1"])
    assert "1000000" not in capsys.readouterr().out


# 8. Dotenv comments and quotes.
def test_dotenv_comments_and_quotes(tmp_path):
    (tmp_path / ".env").write_text(
        'API_KEY=super-secret-123 # production\nQ="quoted-secret-1" # note\nS=\'single-secret-1\'\n')
    values = parse_env_file(tmp_path / ".env")
    assert values == {"API_KEY": "super-secret-123", "Q": "quoted-secret-1", "S": "single-secret-1"}
    assert Redactor.for_repo(tmp_path, environ={}).text("x super-secret-123 y") == "x [REDACTED] y"


# 9. A computed claim needs a run that was recorded and succeeded.
def test_computed_claim_without_a_recorded_run_fails_the_check(project):
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "npxG", "value": 1.78,
                                             "evidence": {"run_id": "R999"}})
    (project / "report.md").write_text("npxG was 1.78 [C1].\n")
    kinds = [f["kind"] for f in checks.run_checks(project)[0]]
    assert kinds == ["unrecorded run"]


def test_computed_claim_from_a_failed_run_fails_the_check(project):
    (project / "runs" / "R1").mkdir(parents=True)
    (project / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "status": "failed", "exit_code": 1}))
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "npxG", "value": 1.78,
                                             "evidence": {"run_id": "R1"}})
    assert [f["kind"] for f in checks.run_checks(project)[0]] == ["failed run"]


# 10. Two teammates who both create C1 are a clash, not two versions.
def test_merged_id_clash_is_reported(project):
    path = project / "claims.jsonl"
    Ledger(path).append({"kind": "definition", "statement": "a", "evidence": {"definition": "x"}, "author": "Ana"})
    mine = path.read_text()
    path.write_text("")
    Ledger(path).append({"kind": "definition", "statement": "b", "evidence": {"definition": "y"}, "author": "Ben"})
    path.write_text(mine + path.read_text())  # what a union merge produces
    assert list(Ledger(path).conflicts()) == ["C1"]
    failures = checks.run_checks(project)[0]
    assert failures[0]["kind"] == "id clash" and "Ana" in failures[0]["message"] and "Ben" in failures[0]["message"]


def test_versions_of_one_claim_keep_one_origin(project):
    ledger = Ledger(project / "claims.jsonl")
    first = ledger.append({"kind": "definition", "statement": "a", "evidence": {"definition": "x"}})
    ledger.update("C1", statement="a2")
    assert ledger.get("C1")["origin"] == first["origin"]
    assert ledger.conflicts() == {}


# 11. Code files that share a name keep separate copies.
@pytest.mark.skipif(not HAS_PYTHON, reason="needs python3")
def test_same_named_sql_files_keep_separate_copies(project, repo):
    for side in ("home", "away"):
        (repo / "queries" / side).mkdir(parents=True)
        (repo / "queries" / side / "q.sql").write_text(f"select '{side}';\n")
    assert main(["run", "a.py", "--sql", "queries/home/q.sql", "--sql", "queries/away/q.sql"]) == 0
    code = project / "runs" / "R1" / "code"
    assert (code / "queries" / "home" / "q.sql").read_text() == "select 'home';\n"
    assert (code / "queries" / "away" / "q.sql").read_text() == "select 'away';\n"


# 12. Decimal ranges are two numbers; scorelines are none.
def test_decimal_ranges(project):
    (project / "runs" / "R1").mkdir(parents=True)
    (project / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "status": "ok"}))
    (project / "report.md").write_text("Between 1.2–1.8 goals; xG 0.12-0.18 per shot; a 95% CI. They won 2-1.\n")
    shown = sorted(f["shown"] for f in checks.run_checks(project)[0])
    assert shown == ["0.12", "0.18", "1.2", "1.8"]


# 13. The wrapper stops on Windows-style paths.
@pytest.mark.parametrize("path", ["C:/Users/test/repo", "C:\\Users\\test\\repo", "relative/dir"])
def test_wrapper_terminates_on_odd_paths(path):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=path)
    result = subprocess.run(["/bin/sh", str(PLUGIN / "hooks" / "run-hook.sh"), "gate_hook.py"], input="{}",
                            capture_output=True, text=True, env=env, timeout=10)
    assert result.returncode == 0 and result.stdout == ""


# 14. SessionStart output stays valid JSON for any plugin path.
@pytest.mark.parametrize("name", ["plain", "with space", "a&b|c", 'quo"te', "back\\slash"])
def test_session_start_json_for_odd_paths(tmp_path, name):
    root = tmp_path / name
    (root / "hooks").mkdir(parents=True)
    for f in ("session-start.json", "session-start.sh"):
        shutil.copy(PLUGIN / "hooks" / f, root / "hooks" / f)
    result = subprocess.run(["/bin/sh", str(root / "hooks" / "session-start.sh")], capture_output=True, text=True,
                            env=dict(os.environ, CLAUDE_PLUGIN_ROOT=str(root)))
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "@PLUGIN_ROOT@" not in context
    assert f'python3 "{root}/core/nutmeg.py"' in context
