from pathlib import Path

import pytest

from nutmeg_core import card as cards
from nutmeg_core.cli import main


@pytest.fixture
def project(repo):
    main(["new", "club", "--data-in-git", "no"])
    return repo / "research" / "club"


def args(file, **extra):
    base = {"file": file, "sql": [], "input": [], "db": None, "sends": [], "interpreter": None, "script_args": []}
    base.update(extra)
    return base


def test_helper_module_is_named_not_inspected(project, repo):
    (repo / "helpers.py").write_text("import requests\ndef push(df):\n    requests.post('https://api.scout.io/v1', json=df)\n")
    (repo / "analysis.py").write_text(
        "import json\nimport pandas as pd\nfrom helpers import push\n"
        "df = pd.read_csv('https://data.example.org/players.csv')\npush(df)\n")
    card = cards.build_run_card(args("analysis.py", sends=["api.scout.io:player_id,minutes"]), repo, project, repo)
    services = card["services"]
    assert services["local_modules"] == ["helpers.py"]
    assert services["packages"] == ["pandas"]
    assert services["detected"] == ["data.example.org"]
    assert services["declared"] == [{"host": "api.scout.io", "columns": ["player_id", "minutes"]}]
    text = cards.render_text(card)
    assert "not inspected (local code): helpers.py" in text
    assert "detected: data.example.org" in text
    assert "AI provider" in text
    # The card lists services in order: data sent first, then inputs, then code.
    assert text.index("Data sent and services") < text.index("Inputs") < text.index("Code: analysis.py")


def test_r_dependencies(project, repo):
    (repo / "model.R").write_text('library(dplyr)\nsource("utils.R")\nx <- worldfootballR::fb_match_urls()\n')
    card = cards.build_run_card(args("model.R"), repo, project, repo)
    assert card["services"]["packages"] == ["dplyr", "worldfootballR"]
    assert card["services"]["local_modules"] == ["utils.R"]
    assert card["interpreter"] == "Rscript"


def test_inputs_are_hashed_with_columns(project, repo):
    (repo / "data").mkdir()
    (repo / "data" / "events.csv").write_text("match_id,player_id,xg\n1,2,0.1\n")
    (repo / "a.py").write_text("print(1)\n")
    card = cards.build_run_card(args("a.py", input=["data/events.csv"]), repo, project, repo)
    item = card["inputs"][0]
    assert item["path"] == "data/events.csv" and len(item["sha256"]) == 64
    assert item["columns"] == ["match_id", "player_id", "xg"]


def test_input_outside_repo_is_a_problem(project, repo):
    (repo / "a.py").write_text("print(1)\n")
    card = cards.build_run_card(args("a.py", input=["~/.aws/credentials"]), repo, project, repo)
    assert any("outside the repository" in p for p in card["problems"])


def test_secrets_are_redacted_on_the_card(project, repo):
    (repo / ".env").write_text("SPORTMONKS_API_TOKEN=tok_abcdef123456\n")
    (repo / "a.py").write_text("URL = 'https://api.sportmonks.com/v3?api_token=tok_abcdef123456'\n")
    card = cards.build_run_card(args("a.py"), repo, project, repo)
    assert "tok_abcdef123456" not in cards.render_text(card)


def test_long_code_is_truncated_in_text(project, repo):
    (repo / "a.py").write_text("".join(f"x{i} = {i}\n" for i in range(200)))
    text = cards.render_text(cards.build_run_card(args("a.py"), repo, project, repo))
    assert "more lines in the card file" in text
    assert "x199" not in text


def test_sql_uses_duckdb_or_sqlite(repo, monkeypatch):
    monkeypatch.setattr(cards.shutil, "which", lambda name: "/usr/bin/duckdb" if name == "duckdb" else None)
    argv, name, stdin = cards.choose_interpreter(Path("q.sql"))
    assert name == "duckdb" and stdin == Path("q.sql")
    monkeypatch.setattr(cards.shutil, "which", lambda name: None)
    argv, name, stdin = cards.choose_interpreter(Path("q.sql"), db="x.db")
    assert argv == ["sqlite3", "x.db"]


def test_unsupported_extension(repo):
    with pytest.raises(cards.CardError):
        cards.choose_interpreter(Path("a.ipynb"))
