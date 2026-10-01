import json
import shutil

import pytest

from nutmeg_core.cli import main
from nutmeg_core.ledger import Ledger
from nutmeg_core.why import trace_lines, why_lines

pytestmark = pytest.mark.skipif(shutil.which("python3") is None, reason="needs python3 on PATH")


@pytest.fixture
def project(repo):
    main(["new", "demo", "--data-in-git", "yes"])
    folder = repo / "research" / "demo"
    (repo / "data").mkdir()
    (repo / "data" / "events.csv").write_text("player,xg\nA,0.4\nB,0.3\n")
    (repo / "analysis.py").write_text(
        "import csv, os, shutil\n"
        "rows = list(csv.DictReader(open('data/events.csv')))\n"
        "total = sum(float(r['xg']) for r in rows)\n"
        "shutil.copy('data/events.csv', os.path.join(os.environ['NUTMEG_OUTPUT_DIR'], 'rows.csv'))\n"
        "print(round(total, 2))\n")
    main(["run", "analysis.py", "--input", "data/events.csv"])
    return folder


def add(project, **claim):
    return Ledger(project / "claims.jsonl").append(claim)


def test_computed_claim_card(project, repo):
    add(project, kind="computed", statement="Total xG 0.7", value=0.7, why="Sum of shot xG.",
        rests_on={"type": "docs", "ref": "football-docs statsbomb shot xg"},
        evidence={"run_id": "R1", "metric": "xG (StatsBomb)", "n": 2, "filters": {"season": "2025/26"},
                  "code_lines": "analysis.py:2-3", "snapshot": "research/demo/runs/R1/outputs/rows.csv"})
    text = "\n".join(why_lines(project, repo, "C1"))
    for expected in ("C1 · computed · draft", "Value: 0.7", "Definition: xG (StatsBomb)",
                     "run R1: analysis.py with python3 · ok", "input: data/events.csv",
                     "   3 | total = sum(float(r['xg']) for r in rows)", "Filters: season = 2025/26", "n: 2",
                     "player | xg", "A | 0.4", "Why: Sum of shot xG.", "Rests on: docs · football-docs statsbomb shot xg",
                     "v1"):
        assert expected in text, expected


def test_five_sample_rows_at_most(project, repo):
    (repo / "big.csv").write_text("a\n" + "".join(f"{i}\n" for i in range(20)))
    add(project, kind="computed", statement="x", value=1, evidence={"run_id": "R1", "snapshot": "big.csv"})
    text = "\n".join(why_lines(project, repo, "C1"))
    assert "first 5 of big.csv" in text and "  4" in text and "  5" not in text


def test_identity_and_provider_fact(project, repo):
    add(project, kind="identity", statement="Bukayo Saka", evidence={"reep_id": "reep_p1a2b3", "release": "v1 (2026-09-01)",
                                                                       "provider_ids": {"opta": "p223340"}})
    add(project, kind="provider_fact", statement="Opta x runs 0-100",
        evidence={"provider": "opta", "source": "football-docs: opta coordinates"})
    identity = "\n".join(why_lines(project, repo, "C1"))
    assert "Reep ID: reep_p1a2b3 · release v1 (2026-09-01)" in identity and "opta: p223340" in identity
    assert "docs source: football-docs: opta coordinates" in "\n".join(why_lines(project, repo, "C2"))


def test_literature_card(project, repo):
    add(project, kind="literature", statement="Singh introduced xT",
        evidence={"citation": "Singh (2019)", "source_id": "web:karun.in/blog/expected-threat.html",
                  "match": "normalised", "quote": "expected threat"})
    text = "\n".join(why_lines(project, repo, "C1"))
    assert "citation: Singh (2019)" in text and "quote match: normalised" in text and "“expected threat”" in text


def test_interpretation_lists_what_it_rests_on(project, repo):
    add(project, kind="computed", statement="Total xG 0.7", value=0.7, evidence={"run_id": "R1"})
    add(project, kind="interpretation", statement="They create little", evidence={"claims": ["C1"]})
    text = "\n".join(why_lines(project, repo, "C2"))
    assert "C1 · computed · draft · Total xG 0.7" in text


def test_unknown_claim_exits_non_zero(project, capsys):
    assert main(["why", "C99"]) == 2
    assert "no claim C99" in capsys.readouterr().err


def test_trace_tree(project, repo):
    add(project, kind="computed", statement="Total xG 0.7", value=0.7, evidence={"run_id": "R1"})
    add(project, kind="definition", statement="xG", evidence={"definition": "chance quality"})
    add(project, kind="interpretation", statement="They create little", evidence={"claims": ["C1"]})
    text = "\n".join(trace_lines(project, repo))
    assert "R1 analysis.py · ok" in text
    assert "prov:used data/events.csv" in text
    assert "prov:wasGeneratedBy C1 Total xG 0.7 = 0.7" in text
    assert "C2 definition" in text
    assert "C3 They create little · draft  prov:wasDerivedFrom C1" in text
