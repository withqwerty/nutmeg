import json

import pytest

from nutmeg_core import check as checks
from nutmeg_core import gate, provenance
from nutmeg_core.cli import main
from nutmeg_core.ledger import ClaimError, Ledger


@pytest.fixture
def project(repo):
    main(["new", "homes", "--data-in-git", "yes"])
    (repo / "data").mkdir()
    (repo / "data" / "matches.csv").write_text(
        "match_id,home,points\n1,Ashby,3\n2,Ashby,3\n2,Ashby,3\n3,Brockley,1\n")
    (repo / "analysis.py").write_text(
        "import csv\nrows = list(csv.DictReader(open('data/matches.csv')))\nprint(sum(int(r['points']) for r in rows))\n")
    return repo / "research" / "homes"


def run(*extra):
    return main(["run", "analysis.py", "--input", "data/matches.csv", *extra])


def test_data_add_records_source_hash_and_profile(project, capsys):
    assert main(["data", "add", "data/matches.csv", "--source", "fan site table, scraped 2026-10-01",
                 "--licence", "unknown"]) == 0
    out = capsys.readouterr().out
    assert "1 row(s) are exact duplicates" in out and "1 value(s) of match_id appear more than once" in out
    entry = provenance.load(project)["files"][0]
    assert entry["path"] == "data/matches.csv" and entry["profile"]["rows"] == 4 and len(entry["sha256"]) == 64
    receipt = json.loads((project / "receipts.jsonl").read_text().splitlines()[-1])
    assert receipt["kind"] == "data_added"


def test_data_add_needs_a_source(project, capsys):
    assert main(["data", "add", "data/matches.csv", "--source", " "]) == 2


def test_run_card_shows_provenance(project, repo):
    reason = gate.decide("nutmeg run analysis.py --input data/matches.csv", repo, project, repo).reason
    assert "no source recorded" in reason
    main(["data", "add", "data/matches.csv", "--source", "fan site"])
    assert "from fan site" in gate.decide("nutmeg run analysis.py --input data/matches.csv", repo, project, repo).reason
    (repo / "data" / "matches.csv").write_text("match_id,home,points\n1,Ashby,3\n")
    assert "CHANGED since it was recorded" in gate.decide("nutmeg run analysis.py --input data/matches.csv",
                                                          repo, project, repo).reason


WORDS = ["--claim", "Ashby have the best home record this season",
         "--rests-on", "points per home game from a scraped table of results",
         "--would-change", "duplicated rows or a different set of matches"]


def test_publish_needs_a_source_for_each_input(project, capsys):
    assert run() == 0
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "total 10", "value": 10,
                                             "evidence": {"run_id": "R1"}})
    (project / "report.md").write_text("Ten points in all [C1].\n")
    assert not checks.check(project)["open"]  # not a check problem: it does not interrupt the analysis
    main(["teachback", *WORDS])
    assert main(["publish"]) == 2
    assert "input data/matches.csv has no recorded source" in capsys.readouterr().err
    main(["data", "add", "data/matches.csv", "--source", "fan site"])
    assert main(["publish"]) == 0


def test_a_run_that_changes_its_input_fails_its_claims(project, repo, capsys):
    (repo / "analysis.py").write_text("open('data/matches.csv', 'a').write('4,Carlow,0\\n')\nprint(1)\n")
    assert run() == 0
    record = json.loads((project / "runs" / "R1" / "run.json").read_text())
    assert record["inputs_modified"] == ["data/matches.csv"]
    assert "changed its own input" in capsys.readouterr().err
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "one", "value": 1,
                                             "evidence": {"run_id": "R1"}})
    kinds = [f["kind"] for f in checks.check(project)["open"]]
    assert "input changed by run" in kinds


def test_input_changed_since_the_run_makes_claims_stale(project, repo):
    assert run() == 0
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "total 10", "value": 10,
                                             "evidence": {"run_id": "R1"}})
    assert not [f for f in checks.check(project)["open"] if f["kind"] == "stale run"]
    (repo / "data" / "matches.csv").write_text("match_id,home,points\n1,Ashby,3\n")
    stale = [f for f in checks.check(project)["open"] if f["kind"] == "stale run"]
    assert len(stale) == 1 and "data/matches.csv has changed since run R1" in stale[0]["message"]


def test_a_missing_input_is_not_stale(project, repo):
    assert run() == 0
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "total 10", "value": 10,
                                             "evidence": {"run_id": "R1"}})
    (repo / "data" / "matches.csv").unlink()  # data kept out of git on a teammate's machine
    assert not [f for f in checks.check(project)["open"] if f["kind"] == "stale run"]


def test_gap_claims_hold_no_value_and_no_number_rests_on_them(project):
    ledger = Ledger(project / "claims.jsonl")
    with pytest.raises(ClaimError):
        ledger.append({"kind": "gap", "statement": "per-match split", "value": 3, "evidence": {"reason": "no data"}})
    ledger.append({"kind": "gap", "statement": "whether Ashby's record comes from a few big games",
                   "evidence": {"reason": "the file has season totals only"}})
    (project / "report.md").write_text("We could not check whether a few games drive it [C1].\n"
                                       "It could be 3 games [C1].\n")
    open_ = checks.check(project)["open"]
    assert [f["kind"] for f in open_] == ["rests on a gap"]


def test_publish_needs_limits_on_a_cited_judgement(project, capsys):
    assert run() == 0
    main(["data", "add", "data/matches.csv", "--source", "fan site"])
    ledger = Ledger(project / "claims.jsonl")
    ledger.append({"kind": "computed", "statement": "total 10", "value": 10, "evidence": {"run_id": "R1"}})
    ledger.append({"kind": "interpretation", "statement": "Ashby are the best at home", "evidence": {"claims": ["C1"]}})
    (project / "report.md").write_text("Ashby are the best at home [C2].\n")
    assert not checks.check(project)["open"]
    main(["teachback", *WORDS, "--covers", "C1,C2"])
    assert main(["publish"]) == 2
    assert "C2 is a judgement the outputs cite: add evidence.limits" in capsys.readouterr().err
    ledger.update("C2", evidence={"claims": ["C1"], "limits": "It does not adjust for opponent strength."})
    main(["teachback", *WORDS, "--covers", "C1,C2"])
    assert main(["publish"]) == 0
    with pytest.raises(ClaimError):
        ledger.update("C2", evidence={"claims": ["C1"], "limits": "  "})


def test_explainer_sources_describe_gaps_and_judgements(project):
    assert run() == 0
    ledger = Ledger(project / "claims.jsonl")
    ledger.append({"kind": "computed", "statement": "total 10", "value": 10, "evidence": {"run_id": "R1"}})
    ledger.append({"kind": "interpretation", "statement": "Ashby are the best at home",
                   "evidence": {"claims": ["C1"], "limits": "opponent strength is not adjusted for."}})
    ledger.append({"kind": "gap", "statement": "the per-match split", "evidence": {"reason": "season totals only"}})
    main(["explain", "new", "home"])
    (project / "explainers" / "home.md").write_text("# Home\n\nAshby lead [C2]. We could not split by match [C3].\n")
    main(["explain", "render", "home"])
    page = (project / "explainers" / "home.html").read_text()
    assert "a judgement resting on C1; it does not show opponent strength is not adjusted for" in page
    assert "not established: season totals only" in page


def test_folder_inputs_are_not_flagged_as_changed(project, repo, capsys):
    (repo / "data" / "events").mkdir()
    (repo / "data" / "events" / "m1.csv").write_text("a\n1\n")
    (repo / "data" / "events" / "m2.csv").write_text("a\n2\n")
    (repo / "analysis.py").write_text("import os\nprint(sorted(os.listdir('data/events')))\n")
    assert main(["run", "analysis.py", "--input", "data/events"]) == 0
    record = json.loads((project / "runs" / "R1" / "run.json").read_text())
    assert record["inputs_modified"] == [] and "changed its own input" not in capsys.readouterr().err
    Ledger(project / "claims.jsonl").append({"kind": "computed", "statement": "two files", "value": 2,
                                             "evidence": {"run_id": "R1"}})
    assert not checks.check(project)["open"]
    (repo / "data" / "events" / "m3.csv").write_text("a\n3\n")
    assert [f["kind"] for f in checks.check(project)["open"]] == ["stale run"]
