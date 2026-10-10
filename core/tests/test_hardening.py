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
    assert "may only add the flags" in decision.reason
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
    for f in ("session-start.json", "session-start.sh", "session-start-research.txt"):
        shutil.copy(PLUGIN / "hooks" / f, root / "hooks" / f)
    project = tmp_path / "project"
    (project / "research").mkdir(parents=True)
    result = subprocess.run(["/bin/sh", str(root / "hooks" / "session-start.sh")], capture_output=True, text=True,
                            env=dict(os.environ, CLAUDE_PLUGIN_ROOT=str(root), CLAUDE_PROJECT_DIR=str(project)))
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "@PLUGIN_ROOT@" not in context and "@RESEARCH@" not in context
    assert f'python3 "{root}/core/nutmeg.py"' in context


def test_research_rules_load_only_in_projects_with_research(tmp_path):
    """Sessions without research projects do not pay for the research-project rules."""
    plain, research = tmp_path / "plain", tmp_path / "with-research"
    plain.mkdir()
    (research / "research").mkdir(parents=True)
    out = {}
    for name, project in (("plain", plain), ("research", research)):
        result = subprocess.run(["/bin/sh", str(PLUGIN / "hooks" / "session-start.sh")], capture_output=True, text=True,
                                env=dict(os.environ, CLAUDE_PLUGIN_ROOT=str(PLUGIN), CLAUDE_PROJECT_DIR=str(project)))
        out[name] = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "teachback" not in out["plain"] and "claim add" not in out["plain"] and "@RESEARCH@" not in out["plain"]
    assert "teachback --shown" in out["research"] and "claim add --file" in out["research"]
    assert "Provider facts" in out["plain"] and "Help the user understand" in out["plain"]
    assert len(out["plain"]) < len(out["research"])


# --- second review (findings on U6-U10, U14) ------------------------------------------------

@pytest.mark.parametrize("command", [
    "env --split-string='python3 -c print(1)'", "env -Spython3", "sh -c 'nutmeg publish'", "bash -c 'python3 a.py'",
    "env --chdir=sub nutmeg run a.py", "env -C sub python3 a.py", "uv run --directory sub python a.py",
    "conda run --cwd sub python a.py", "find . -name '*.py' -exec python3 {} ;", "xargs python3",
])
def test_string_and_directory_wrappers_ask(command):
    assert gate.parse(command).kind == "compound", command


def test_nutmeg_project_option_behind_uv_is_still_a_run():
    parsed = gate.parse('uv run python3 "/p/core/nutmeg.py" --project research/club run a.py')
    assert parsed.kind == "nutmeg" and parsed.subcommand == "run"


@pytest.mark.parametrize("interpreter", ["python3 -cprint(123)", "python3 other.py", "sh", "env python3",
                                         "python3 -m http.server"])
def test_interpreter_must_be_one_program(project, repo, interpreter):
    decision = gate.decide(f"nutmeg run a.py --interpreter '{interpreter}'", repo, project, repo)
    assert "PROBLEM" in decision.reason


def test_interpreter_with_safe_flag_is_allowed(project, repo):
    decision = gate.decide("nutmeg run a.py --interpreter 'python3 -u'", repo, project, repo)
    assert "PROBLEM" not in decision.reason and "Command: python3 -u a.py" in decision.reason


def test_other_repositorys_project_uses_its_own_team_floor(repo, tmp_path_factory):
    other = tmp_path_factory.mktemp("other")
    subprocess.run(["git", "init", "-q", str(other)], check=True)
    (other / ".nutmeg").mkdir()
    (other / ".nutmeg" / "team.json").write_text(json.dumps({"max_autonomy": {"run": "L2"}}))
    (other / "research" / "p" / "runs").mkdir(parents=True)
    (other / "a.py").write_text("print(1)\n")
    main(["new", "mine", "--data-in-git", "yes"])
    (repo / ".no-user-config.json").write_text(json.dumps({"persona": "fanalyst", "run_then_review": True}))
    decision = gate.decide(f"nutmeg --project {other}/research/p run {other}/a.py", repo,
                           repo / "research" / "mine", repo)
    assert decision.decision == "ask"


def test_broken_user_config_cannot_switch_off_signoff(project, repo):
    (repo / ".nutmeg").mkdir()
    (repo / ".nutmeg" / "team.json").write_text(json.dumps({"signoff": {"required": True}}))
    (repo / ".no-user-config.json").write_text(json.dumps({"autonomy_run": "L9"}))
    Ledger(project / "claims.jsonl").append({"kind": "definition", "statement": "x", "evidence": {"definition": "y"},
                                             "headline": True, "author": "A"})
    kinds = [f["kind"] for f in checks.run_checks(project)[0]]
    assert "needs sign-off" in kinds


def test_claim_add_cannot_keep_verification_after_an_edit(project, repo):
    ledger = Ledger(project / "claims.jsonl")
    ledger.append({"kind": "definition", "statement": "x", "evidence": {"definition": "y"}, "author": "A"})
    ledger.update("C1", trusted=True, status="verified", signer="B")
    edited = {**ledger.get("C1"), "statement": "x, quietly changed"}
    main(["claim", "add", "--json", json.dumps(edited)])
    latest = ledger.get("C1")
    assert latest["status"] == "draft" and "signer" not in latest and latest["author"] == "A"


def test_untrusted_writer_cannot_set_verified(project):
    written = Ledger(project / "claims.jsonl").append({"kind": "definition", "statement": "x",
                                                       "evidence": {"definition": "y"}, "status": "verified"})
    assert written["status"] == "draft"


def test_explicit_id_still_gets_an_author_and_cannot_self_sign(project, repo, capsys):
    (repo / ".nutmeg").mkdir()
    (repo / ".nutmeg" / "team.json").write_text(json.dumps({"signoff": {"required": True}}))
    claim = {"id": "C2", "kind": "definition", "statement": "x", "evidence": {"definition": "y"}, "headline": True}
    assert main(["claim", "add", "--json", json.dumps(claim)]) == 0
    assert Ledger(project / "claims.jsonl").get("C2")["author"] == "Test Analyst"
    assert main(["signoff", "C2"]) == 2


def test_code_lines_cannot_read_outside_the_run(project, repo, capsys):
    (project / "runs" / "R1" / "code").mkdir(parents=True)
    (project / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "file": "a.py", "status": "ok"}))
    secret = repo / "private.txt"
    secret.write_text("TOP SECRET LINE\n")
    for spec in (f"{secret}:1-1", "../../../../private.txt:1-1"):
        Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "x", "value": 1,
                                                 "evidence": {"run_id": "R1", "code_lines": spec}})
    for cid in ("C1", "C2"):
        main(["why", cid])
        assert "TOP SECRET" not in capsys.readouterr().out


def _bundle_names(path):
    import zipfile
    with zipfile.ZipFile(path) as archive:
        return {n: archive.read(n) for n in archive.namelist()}


def test_raw_no_bundle_leaves_out_the_workspace_and_run_written_files(project, repo):
    (project / "runs" / "R1").mkdir(parents=True)
    (project / "runs" / "R1" / "run.json").write_text(json.dumps({
        "id": "R1", "status": "ok",
        "outputs": [{"path": "research/club/tables/players.csv"}, {"path": "research/club/dump.prov.json"},
                    {"path": "research/club/table.md"}]}))
    (project / "tables").mkdir()
    (project / "tables" / "players.csv").write_text("player,salary\nX,999\n")
    (project / "dump.prov.json").write_text('{"rows": [["X", 999]]}')
    (project / "table.md").write_text("| X | 999 |\n")
    (project / "report.md").write_text("Report.\n")
    (project / "workspace.html").write_text("<pre>sample rows</pre>")
    (project / "data").mkdir(exist_ok=True)
    (project / "data" / "private.csv").write_text("secret,row\n")
    (project / "alias.csv").symlink_to(project / "data" / "private.csv")
    main(["bundle", "--raw", "no", "--out", "out/b.zip"])
    names = _bundle_names(repo / "out" / "b.zip")
    for raw in ("workspace.html", "tables/players.csv", "dump.prov.json", "table.md", "alias.csv"):
        assert f"club/{raw}" not in names, raw
    assert "club/report.md" in names  # written by hand, not by a run
    manifest = json.loads(names["club/bundle-manifest.json"])
    assert {"workspace.html", "tables/players.csv", "alias.csv"} <= {o["path"] for o in manifest["raw_omitted"]}


def test_bundle_redacts_lockfiles_and_skips_credentials(project, repo):
    (repo / ".env").write_text("TOKEN=pkg-token-778899\n")
    (repo / "requirements.txt").write_text("private-pkg @ https://pkg-token-778899@pypi.example.org/simple\n")
    (project / ".env").write_text("TOKEN=pkg-token-778899\n")
    (project / "chart.svg").write_text("<svg><!-- pkg-token-778899 --></svg>")
    main(["bundle", "--raw", "yes", "--out", "out/b.zip"])
    names = _bundle_names(repo / "out" / "b.zip")
    assert "club/.env" not in names
    assert all(b"pkg-token-778899" not in data for data in names.values())


def test_bundle_out_must_be_inside_the_repo(project, repo, tmp_path_factory, capsys):
    outside = tmp_path_factory.mktemp("o") / "b.zip"
    assert main(["bundle", "--raw", "no", "--out", str(outside)]) == 2
    assert not outside.exists()


def test_bundle_skips_symlinks_out_of_the_project(project, repo, tmp_path_factory):
    secret = tmp_path_factory.mktemp("s") / "secret.csv"
    secret.write_text("very,secret\n")
    (project / "linked.csv").symlink_to(secret)
    main(["bundle", "--raw", "yes", "--out", "out/b.zip"])
    names = _bundle_names(repo / "out" / "b.zip")
    assert "club/linked.csv" not in names


def test_chart_image_outside_repo_is_refused(project, repo, tmp_path_factory, capsys):
    image = tmp_path_factory.mktemp("i") / "customer.png"
    image.write_bytes(b"png")
    (repo / "rows.csv").write_text("a\n1\n")
    assert main(["figure", "register", "x", "--data", "rows.csv", "--source", "Opta", "--image", str(image)]) == 2


def test_publish_keeps_paths_and_bundle_includes_chart_assets(project, repo):
    (project / "runs" / "R1").mkdir(parents=True)
    (project / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "status": "ok"}))
    for name in ("first", "second"):
        (project / "reports" / name).mkdir(parents=True)
        (project / "reports" / name / "report.md").write_text(f"{name} report\n")
    (repo / "out").mkdir()
    (repo / "out" / "rows.csv").write_text("a\n1\n")
    (repo / "out" / "chart.png").write_bytes(b"png")
    assert main(["figure", "register", "chart", "--data", "out/rows.csv", "--source", "Opta", "--image",
                 "out/chart.png"]) == 0
    assert main(["publish", "--to", "public"]) == 0
    assert (repo / "public" / "reports" / "first" / "report.md").read_text() == "first report\n"
    assert (repo / "public" / "reports" / "second" / "report.md").read_text() == "second report\n"
    assert (repo / "public" / "_assets" / "out" / "chart.png").is_file()
    main(["bundle", "--raw", "no", "--out", "out/b.zip"])
    assert "assets/out/chart.png" in _bundle_names(repo / "out" / "b.zip")


def test_live_harness_grades_the_named_tool():
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_live", PLUGIN / "evals" / "_scaffold" / "run_live.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = (PLUGIN / "evals" / "_scaffold" / "run_live.py").read_text()
    assert 'grader.get("tool", "")' in source and "bash_commands" not in source


@pytest.mark.parametrize("name", ["new\nline", "tab\there", "cr\rhere"])
def test_session_start_json_with_control_characters(tmp_path, name):
    root = tmp_path / name
    (root / "hooks").mkdir(parents=True)
    for f in ("session-start.json", "session-start.sh", "session-start-research.txt"):
        shutil.copy(PLUGIN / "hooks" / f, root / "hooks" / f)
    project = tmp_path / "project"
    (project / "research").mkdir(parents=True)
    result = subprocess.run(["/bin/sh", str(root / "hooks" / "session-start.sh")], capture_output=True, text=True,
                            env=dict(os.environ, CLAUDE_PLUGIN_ROOT=str(root), CLAUDE_PROJECT_DIR=str(project)))
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert f'python3 "{root}/core/nutmeg.py"' in context


# --- third review --------------------------------------------------------------------------

@pytest.mark.parametrize("command", [
    "sh -c 'python3 a.py' > log", "X=1 bash -c 'python3 a.py'", "tcsh -c 'python3 a.py'", "csh -c 'nutmeg run a.py'",
    "env -Csub nutmeg run a.py", "sudo -D sub nutmeg run a.py", "git status && sh -c 'python3 a.py'",
])
def test_third_review_wrapper_variants_ask(command):
    assert gate.parse(command).kind == "compound", command


@pytest.mark.parametrize("command", [
    'git commit -m "python3"', 'git commit -m "fix core/nutmeg.py"', "env -C sub make test", "make test", "pytest",
    'git commit -m "python3 fix" && git push',
])
def test_ordinary_commands_do_not_ask(command):
    assert gate.parse(command).kind == "other", command


@pytest.mark.parametrize("interpreter", ["csh", "tcsh", "perl", "node"])
def test_interpreter_allowlist(project, repo, interpreter):
    assert "PROBLEM" in gate.decide(f"nutmeg run a.py --interpreter {interpreter}", repo, project, repo).reason


@pytest.mark.skipif(shutil.which("sqlite3") is None and shutil.which("duckdb") is None, reason="needs a SQL client")
def test_sql_run_refuses_client_options(project, repo, capsys):
    (repo / "safe.sql").write_text("select 1;\n")
    assert main(["run", "safe.sql", "--", "-cmd", "select 'EXTRA';"]) == 2
    assert "EXTRA" not in capsys.readouterr().out


def test_inherited_nutmeg_project_uses_that_repositorys_floor(repo, tmp_path_factory, monkeypatch):
    other = tmp_path_factory.mktemp("other")
    subprocess.run(["git", "init", "-q", str(other)], check=True)
    (other / ".nutmeg").mkdir()
    (other / ".nutmeg" / "team.json").write_text(json.dumps({"max_autonomy": {"run": "L2"}}))
    (other / "research" / "p" / "runs").mkdir(parents=True)
    (other / "a.py").write_text("print(1)\n")
    main(["new", "mine", "--data-in-git", "yes"])
    (repo / ".no-user-config.json").write_text(json.dumps({"persona": "fanalyst", "run_then_review": True}))
    monkeypatch.setenv("NUTMEG_PROJECT", str(other / "research" / "p"))
    decision = gate.decide(f"nutmeg run {other}/a.py", repo, repo / "research" / "mine", repo)
    assert decision.decision == "ask"


def test_forged_previous_status_cannot_become_verified(project):
    ledger = Ledger(project / "claims.jsonl")
    ledger.append({"kind": "definition", "statement": "x", "evidence": {"definition": "y"}, "status": "disputed",
                   "previous_status": "verified", "previous_signer": "Boss"})
    main(["resolve", "C1", "--note", "fine"])
    latest = ledger.get("C1")
    assert latest["status"] == "draft" and not latest.get("signer")


def test_contest_then_resolve_keeps_the_sign_off_when_unchanged(project):
    ledger = Ledger(project / "claims.jsonl")
    ledger.append({"kind": "definition", "statement": "x", "evidence": {"definition": "y"}, "author": "A"})
    ledger.update("C1", trusted=True, status="verified", signer="B")
    main(["contest", "C1", "--note", "really?"])
    main(["resolve", "C1", "--note", "yes"])
    latest = ledger.get("C1")
    assert latest["status"] == "verified" and latest["signer"] == "B"


def test_edit_during_dispute_resolves_to_draft(project):
    ledger = Ledger(project / "claims.jsonl")
    ledger.append({"kind": "definition", "statement": "x", "evidence": {"definition": "y"}, "author": "A"})
    ledger.update("C1", trusted=True, status="verified", signer="B")
    main(["contest", "C1", "--note", "really?"])
    ledger.update("C1", statement="x, edited")
    main(["resolve", "C1", "--note", "edited"])
    assert ledger.get("C1")["status"] == "draft"


def test_reason_change_clears_verification(project):
    ledger = Ledger(project / "claims.jsonl")
    ledger.append({"kind": "definition", "statement": "x", "evidence": {"definition": "y"}, "author": "A",
                   "why": "first reason"})
    ledger.update("C1", trusted=True, status="verified", signer="B")
    main(["claim", "add", "--json", json.dumps({**ledger.get("C1"), "why": "a different reason"})])
    assert ledger.get("C1")["status"] == "draft"


def test_authorless_legacy_claim_stays_authorless(project):
    path = project / "claims.jsonl"
    path.write_text(json.dumps({"id": "C1", "kind": "definition", "statement": "x", "evidence": {"definition": "y"},
                                "status": "draft", "version": 1, "at": "2026-01-01T00:00:00Z"}) + "\n")
    Ledger(path).append({**Ledger(path).get("C1"), "author": "B"})
    assert "author" not in Ledger(path).get("C1")


@pytest.mark.parametrize("signoff", [[], {"required": []}, ["x"], {"required": "yes"}])
def test_malformed_team_signoff_is_a_failure_not_a_pass(project, repo, signoff):
    (repo / ".nutmeg").mkdir(exist_ok=True)
    (repo / ".nutmeg" / "team.json").write_text(json.dumps({"signoff": signoff}))
    failures, _ = checks.run_checks(project)
    assert any(f["kind"] == "config" for f in failures)


def test_why_fallback_does_not_follow_symlinks_out(project, repo, tmp_path_factory, capsys):
    secret = tmp_path_factory.mktemp("s") / "leak.txt"
    secret.write_text("EXTERNAL SECRET\n")
    code = project / "runs" / "R1" / "code" / "sub"
    code.mkdir(parents=True)
    (code / "leak.txt").symlink_to(secret)
    (project / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "file": "a.py", "status": "ok"}))
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "x", "value": 1,
                                             "evidence": {"run_id": "R1", "code_lines": "leak.txt:1"}})
    main(["why", "C1"])
    assert "EXTERNAL SECRET" not in capsys.readouterr().out


def test_image_must_be_a_chart_file(project, repo, capsys):
    (repo / "rows.csv").write_text("a\n1\n")
    (repo / "data").mkdir()
    (repo / "data" / "private.csv").write_text("x\n")
    assert main(["figure", "register", "x", "--data", "rows.csv", "--source", "O", "--image", "data/private.csv"]) == 2


def test_lockfile_symlink_out_of_repo_is_not_bundled(project, repo, tmp_path_factory):
    secret = tmp_path_factory.mktemp("s") / "reqs.txt"
    secret.write_text("internal-only-package==1.0\n")
    (repo / "requirements.txt").symlink_to(secret)
    main(["bundle", "--raw", "no", "--out", "out/b.zip"])
    names = _bundle_names(repo / "out" / "b.zip")
    assert not any(b"internal-only-package" in data for data in names.values())


def test_large_text_is_still_redacted(project, repo, monkeypatch):
    from nutmeg_core import bundle as bundling
    (repo / ".env").write_text("TOKEN=big-secret-123456\n")
    (project / "notes.txt").write_text(("filler line\n" * 1000) + "big-secret-123456\n")
    main(["bundle", "--raw", "no", "--out", "out/b.zip"])
    assert b"big-secret-123456" not in _bundle_names(repo / "out" / "b.zip")["club/notes.txt"]
    assert "50 * 1024" not in (PLUGIN / "core" / "nutmeg_core" / "bundle.py").read_text()


def test_publish_redacts_and_refuses_symlinked_destinations(project, repo, tmp_path_factory, capsys):
    (repo / ".env").write_text("TOKEN=pub-secret-445566\n")
    (project / "report.md").write_text("Report made with pub-secret-445566.\n")
    assert main(["publish", "--to", "public"]) == 0
    assert "pub-secret-445566" not in (repo / "public" / "report.md").read_text()
    outside = tmp_path_factory.mktemp("outside")
    (repo / "public2").mkdir()
    (repo / "public2" / "reports").symlink_to(outside)
    (project / "reports").mkdir()
    (project / "reports" / "r.md").write_text("hello\n")
    assert main(["publish", "--to", "public2"]) == 2
    assert not list(outside.iterdir())


def test_publish_refuses_colliding_destinations(project, repo, capsys):
    (project / "runs" / "R1").mkdir(parents=True, exist_ok=True)
    (repo / "out").mkdir()
    (repo / "out" / "rows.csv").write_text("a\n1\n")
    (repo / "out" / "chart.png").write_bytes(b"one")
    (project / "_assets" / "out").mkdir(parents=True)
    (project / "_assets" / "out" / "chart.md").write_text("caption\n")
    main(["figure", "register", "c1", "--data", "out/rows.csv", "--source", "O", "--image", "out/chart.png"])
    (project / "_assets" / "out" / "chart.png").write_bytes(b"two")
    main(["figure", "register", "c2", "--data", "out/rows.csv", "--source", "O", "--image",
          "research/club/_assets/out/chart.png"])
    assert main(["publish", "--to", "public"]) == 2
    assert "two files would be published" in capsys.readouterr().err


# --- fourth review ---------------------------------------------------------------------------

@pytest.mark.parametrize("command", [
    "git status\npython3 analysis.py", "if true; then python3 analysis.py; fi",
    "for f in *.py; do python3 \"$f\"; done", "! python3 a.py", "{ nutmeg run a.py; }",
])
def test_newlines_and_shell_keywords_do_not_hide_runs(command):
    assert gate.parse(command).kind in ("compound", "interpreter"), command


def test_publish_into_the_project_folder_is_refused(project, repo, capsys):
    (project / "report.md").write_text("Report.\n")
    assert main(["publish", "--to", "research/club"]) == 2
    assert (project / "report.md").read_text() == "Report.\n"


def test_multiline_secret_is_redacted_in_bundles_and_publish(project, repo, monkeypatch):
    monkeypatch.setenv("API_SECRET", "first-secret-line\nsecond-secret-line")
    (project / "report.md").write_text("Header\nfirst-secret-line\nsecond-secret-line\nFooter\n")
    main(["bundle", "--raw", "no", "--out", "out/b.zip"])
    data = _bundle_names(repo / "out" / "b.zip")["club/report.md"]
    assert b"first-secret-line" not in data and b"second-secret-line" not in data
    assert main(["publish", "--to", "public"]) == 0
    text = (repo / "public" / "report.md").read_text()
    assert "first-secret-line" not in text and "second-secret-line" not in text
