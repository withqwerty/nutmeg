import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from nutmeg_core import gate
from nutmeg_core.cli import main

from conftest import set_user_hooks

PLUGIN = Path(__file__).resolve().parents[2]
WRAPPER = PLUGIN / "hooks" / "run-hook.sh"


@pytest.fixture
def project(repo):
    main(["new", "club", "--data-in-git", "no"])
    (repo / "analysis.py").write_text("import pandas as pd\nprint(1.78)\n")
    (repo / "q.sql").write_text("select player_id, sum(xg) from shots group by 1;\n")
    return repo / "research" / "club"


# --- the command matcher ---------------------------------------------------

@pytest.mark.parametrize("command", [
    "nutmeg run analysis.py --sql q.sql",
    'python3 "/plugins/nutmeg/core/nutmeg.py" run analysis.py --sql q.sql',
    "python3 /x/core/nutmeg.py --project research/club run analysis.py",
    "NUTMEG_X=1 nutmeg run analysis.py",
    "nutmeg run analysis.py 2>&1",
])
def test_both_nutmeg_forms_match(command):
    parsed = gate.parse(command)
    assert parsed.kind == "nutmeg" and parsed.subcommand == "run"
    assert parsed.namespace.file == "analysis.py"


@pytest.mark.parametrize("command", [
    "nutmeg run a.py && rm x",
    "nutmeg run a.py; rm x",
    "nutmeg run a.py | tee log",
    "nutmeg run a.py > out.txt",
    "nutmeg run $(echo a.py)",
    "nutmeg run `echo a.py`",
    "nutmeg run a.py\nrm x",
    "cd research && python3 analysis.py",
])
def test_compound_commands_are_not_runs(command):
    assert gate.parse(command).kind == "compound"


@pytest.mark.parametrize("command", [
    "python3 analysis.py", "python analysis.py", "python3.11 analysis.py", "Rscript model.R",
    "duckdb db.duckdb -c 'select 1'", "sqlite3 x.db", "psql -c 'select 1'", "bq query 'select 1'",
    "uv run python analysis.py", "/usr/bin/python3 analysis.py",
])
def test_direct_interpreters_match(command):
    assert gate.parse(command).kind == "interpreter"


@pytest.mark.parametrize("command", ["ls -la", "git status", "echo 'python3 a.py'", "ls && git status",
                                     "nutmeg claim list"])
def test_other_commands_pass(command):
    parsed = gate.parse(command)
    assert parsed.kind in ("other", "nutmeg")
    assert parsed.subcommand not in gate.GATED_SUBCOMMANDS


# --- decisions -------------------------------------------------------------

def test_no_project_no_decision(repo):
    assert gate.decide("nutmeg run analysis.py", repo, None) is None


def test_run_asks_with_script_and_sql(project, repo):
    decision = gate.decide("nutmeg run analysis.py --sql q.sql", repo, project, repo)
    assert decision.decision == "ask"
    assert "analysis.py" in decision.reason
    assert "select player_id, sum(xg) from shots group by 1;" in decision.reason
    assert list((project / "runs" / ".pending").glob("*.json"))


def test_full_form_gives_same_card(project, repo):
    short = gate.decide("nutmeg run analysis.py --sql q.sql", repo, project, repo)
    full = gate.decide(f'python3 "{PLUGIN}/core/nutmeg.py" run analysis.py --sql q.sql', repo, project, repo)
    assert short.card["code"] == full.card["code"]
    assert len(list((project / "runs" / ".pending").glob("*.json"))) == 1


def test_compound_run_is_never_allowed(project, repo):
    decision = gate.decide("nutmeg run analysis.py && rm x", repo, project, repo)
    assert decision.decision == "ask"
    assert "cannot show" in decision.reason


def test_direct_python_asks_not_recorded(project, repo):
    decision = gate.decide("python3 analysis.py", repo, project, repo)
    assert decision.decision == "ask"
    assert "NOT RECORDED" in decision.reason
    assert "nutmeg run analysis.py" in decision.reason
    assert "print(1.78)" in decision.reason


def test_other_commands_get_no_decision(project, repo):
    assert gate.decide("git status", repo, project, repo) is None
    assert gate.decide("nutmeg claim list", repo, project, repo) is None


def test_bad_run_arguments_still_ask(project, repo):
    decision = gate.decide("nutmeg run", repo, project, repo)
    assert decision.decision == "ask" and "refuse" in decision.reason


def test_hook_output_shape(project, repo):
    out = gate.decide("nutmeg run analysis.py", repo, project, repo).hook_output()
    assert out["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"


# --- the wrapper and the hook script ---------------------------------------

def _hook(repo, command, env_path=None, hooks=True):
    set_user_hooks(hooks)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
    if env_path is not None:
        env["PATH"] = env_path
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(repo)})
    return subprocess.run(["/bin/sh", str(WRAPPER), "gate_hook.py"], input=payload, capture_output=True,
                          text=True, env=env, cwd=repo)


def test_wrapper_without_project_exits_before_python(repo, tmp_path):
    # PATH without python3: if the wrapper tried Python it would warn.
    result = _hook(repo, "nutmeg run analysis.py", env_path="/nonexistent")
    assert result.returncode == 0 and result.stdout == "" and result.stderr == ""


def test_wrapper_without_python_warns_once(project, repo, tmp_path):
    bin_dir = tmp_path / "bin"  # an empty PATH: no python3
    bin_dir.mkdir()
    first = _hook(repo, "nutmeg run analysis.py", env_path=str(bin_dir))
    assert first.returncode == 0
    assert "python3 3.10 or newer was not found" in json.loads(first.stdout)["systemMessage"]
    second = _hook(repo, "nutmeg run analysis.py", env_path=str(bin_dir))
    assert second.returncode == 0 and second.stdout == ""


@pytest.mark.skipif(shutil.which("python3") is None, reason="needs python3 on PATH")
def test_hook_end_to_end(project, repo):
    result = _hook(repo, "nutmeg run analysis.py --sql q.sql")
    assert result.returncode == 0, result.stderr
    out = json.loads(result.stdout)["hookSpecificOutput"]
    assert out["permissionDecision"] == "ask" and "q.sql" in out["permissionDecisionReason"]
    assert _hook(repo, "git status").stdout == ""


# --- the research hooks are off by default -----------------------------------

def test_hooks_off_by_default_leave_every_command_alone(project, repo):
    for command in ("python3 analysis.py", "nutmeg run analysis.py --sql q.sql", "python3 a.py | tee out.txt"):
        result = _hook(repo, command, hooks=False)
        assert result.returncode == 0 and result.stdout == "", command


def test_team_config_turns_the_hooks_on(project, repo):
    (repo / ".nutmeg").mkdir()
    (repo / ".nutmeg" / "team.json").write_text(json.dumps({"hooks": True}))
    out = json.loads(_hook(repo, "python3 analysis.py", hooks=False).stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"


def test_config_set_hooks_turns_them_on_and_off(project, repo, capsys):
    assert main(["config", "set", "--hooks", "on"]) == 0
    assert "Research hooks (run gate and stop check): on (your setting)" in capsys.readouterr().out
    assert main(["config", "set", "--hooks", "off"]) == 0
    assert "off (turn on with `nutmeg config set --hooks on`)" in capsys.readouterr().out


def test_hooks_stay_on_when_another_user_setting_is_broken(project, repo):
    path = Path(os.environ["NUTMEG_USER_CONFIG"])
    path.write_text(json.dumps({"hooks": True, "autonomy_run": "L9"}))
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "nutmeg run analysis.py"}, "cwd": str(repo)})
    result = subprocess.run(["/bin/sh", str(WRAPPER), "gate_hook.py"], input=payload, capture_output=True,
                            text=True, env=env, cwd=repo)
    out = json.loads(result.stdout)["hookSpecificOutput"]
    assert out["permissionDecision"] == "ask" and "config is broken" in out["permissionDecisionReason"]
