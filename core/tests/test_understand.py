import json

import pytest

from nutmeg_core import gate, understand
from nutmeg_core import workspace as workspaces
from nutmeg_core.cli import main
from nutmeg_core.ledger import Ledger
from nutmeg_core.project import parse_choices

WORDS = ["--claim", "Mendes makes us more dangerous than anyone we had",
         "--rests-on", "valuing passes and carries by how close they take the ball to goal",
         "--would-change", "a few big games driving it, or a fuller squad median"]


@pytest.fixture
def project(repo):
    main(["new", "signings", "--data-in-git", "yes"])
    folder = repo / "research" / "signings"
    (folder / "runs" / "R1").mkdir(parents=True)
    (folder / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "status": "ok"}))
    ledger = Ledger(folder / "claims.jsonl")
    for run_id in ("R2", "R3"):
        (folder / "runs" / run_id).mkdir(parents=True)
        (folder / "runs" / run_id / "run.json").write_text(json.dumps({"id": run_id, "status": "ok"}))
    ledger.append({"kind": "computed", "statement": "Mendes adds 0.31 xT per 90", "value": 0.31,
                   "evidence": {"run_id": "R1", "alternatives": [
                       {"run_id": "R2", "choice": "at least 600 minutes", "value": 0.31},
                       {"run_id": "R3", "choice": "squad mean instead of median", "value": 0.31}]},
                   "headline": True})
    ledger.append({"kind": "computed", "statement": "the squad median is 0.14 xT per 90", "value": 0.14,
                   "evidence": {"run_id": "R1"}})
    (folder / "report.md").write_text("Mendes adds 0.31 [C1] against a squad median of 0.14 [C2].\n")
    return folder


def test_publish_refuses_until_the_author_teaches_back(project, capsys):
    assert main(["publish"]) == 2
    err = capsys.readouterr().err
    assert "Test Analyst should be able to defend it" in err and "C1" in err
    assert not (project / "published.json").exists()
    assert main(["teachback", *WORDS]) == 0
    assert main(["publish"]) == 0
    assert (project / "published.json").is_file()


def test_teachback_covers_headline_claims_only(project):
    assert main(["teachback", *WORDS]) == 0
    entry = understand.records(project)[-1]
    assert list(entry["covers"]) == ["C1"] and entry["by"] == "Test Analyst"


def test_without_headline_claims_the_cited_claims_count(project):
    ledger = Ledger(project / "claims.jsonl")
    ledger.update("C1", headline=False)
    assert sorted(understand.needed(project)) == ["C1", "C2"]


def test_a_changed_claim_needs_a_new_teachback(project, capsys):
    assert main(["teachback", *WORDS]) == 0
    ledger = Ledger(project / "claims.jsonl")
    ledger.update("C1", value=0.32, statement="Mendes adds 0.32 xT per 90")
    (project / "report.md").write_text("Mendes adds 0.32 [C1] against a squad median of 0.14 [C2].\n")
    assert main(["publish"]) == 2
    assert "changed since the last talk-through: C1" in capsys.readouterr().err


def test_another_persons_teachback_does_not_count(project, monkeypatch, repo, capsys):
    assert main(["teachback", *WORDS]) == 0
    (repo / "me.json").write_text(json.dumps({"name": "Someone Else"}))
    monkeypatch.setenv("NUTMEG_USER_CONFIG", str(repo / "me.json"))
    assert main(["publish"]) == 2
    assert "Someone Else should be able to defend it" in capsys.readouterr().err


@pytest.mark.parametrize("field,text,message", [
    ("--claim", "Mendes is good", "at least 4"),
    ("--claim", "Mendes adds 0.31 [C1] against a squad median of 0.14 [C2].", "matches report.md"),
])
def test_teachback_rejects_short_or_copied_words(project, capsys, field, text, message):
    words = list(WORDS)
    words[words.index(field) + 1] = text
    assert main(["teachback", *words]) == 2
    assert message in capsys.readouterr().err
    assert not understand.records(project)


def test_teachback_rejects_the_same_answer_three_times(project, capsys):
    same = "Mendes makes us more dangerous than anyone"
    assert main(["teachback", "--claim", same, "--rests-on", same, "--would-change", same]) == 2
    assert "the three answers are the same" in capsys.readouterr().err


def test_publish_card_shows_the_words_and_late_choices(project, repo):
    main(["plan", "choose", "--kind", "method", "--choice", "compare with the squad's worst player",
          "--why", "The user asked for a second comparison.", "--rests-type", "user", "--rests-ref", "'make them look better'",
          "--after-results", "added next to the median comparison at Sam's request, after the results"])
    assert main(["teachback", *WORDS]) == 0
    reason = gate.decide("nutmeg publish", repo, project, repo).reason
    assert "In Test Analyst's own words" in reason and "What would change the answer: a few big games" in reason
    assert "after seeing results: method: compare with the squad's worst player" in reason


def test_after_results_choice_is_recorded_and_needs_a_note(project, capsys):
    base = ["plan", "choose", "--kind", "filter", "--choice", "at least 600 minutes", "--why", "Asked for.",
            "--rests-type", "user", "--rests-ref", "'drop the filter'"]
    assert main(base + ["--after-results", "  "]) == 2
    assert main(base + ["--after-results", "replaces 900 minutes; asked by Sam after seeing the table"]) == 0
    choice = parse_choices((project / "plan.md").read_text())[-1]
    assert choice["after_results"] == "replaces 900 minutes; asked by Sam after seeing the table"
    assert "changed after seeing results" in workspaces.build(project)


def test_explainer_page_is_one_file_with_its_sources(project, repo, capsys):
    assert main(["explain", "new", "why-mendes", "--title", "Why Mendes stands out"]) == 0
    source = project / "explainers" / "why-mendes.md"
    (repo / "chart.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 20)
    source.write_text("# Why Mendes stands out\n\nMendes adds 0.31 xT per 90 [C1], the squad median is 0.14 [C2].\n\n"
                      "![chart](../../../chart.png)\n\n<!-- a note to myself -->\n")
    assert main(["explain", "render", "why-mendes"]) == 0
    page = (project / "explainers" / "why-mendes.html").read_text()
    assert "Content-Security-Policy" in page and "<script" not in page
    assert 'src="data:image/png;base64,' in page
    assert "Where the numbers come from" in page and 'id="n-C1"' in page and 'href="#n-C1"' in page
    assert "a note to myself" not in page
    assert "<title>Why Mendes stands out</title>" in page
    assert understand.page_state(source) == "current"


def test_explainer_numbers_are_checked(project, capsys):
    main(["explain", "new", "why-mendes"])
    (project / "explainers" / "why-mendes.md").write_text("# Why\n\nMendes adds 0.45 xT per 90.\n")
    assert main(["explain", "render", "why-mendes"]) == 1
    assert "0.45" in capsys.readouterr().out


def test_publish_refuses_a_page_older_than_its_source(project, capsys):
    main(["explain", "new", "why-mendes"])
    source = project / "explainers" / "why-mendes.md"
    source.write_text("# Why\n\nMendes adds 0.31 [C1].\n")
    main(["explain", "render", "why-mendes"])
    source.write_text("# Why\n\nMendes adds 0.31 [C1], more than anyone.\n")
    main(["teachback", *WORDS])
    assert main(["publish"]) == 2
    assert "older than its source" in capsys.readouterr().err
    main(["explain", "render"])
    assert main(["publish"]) == 0
    files = [f["source"] for f in json.loads((project / "published.json").read_text())[0]["files"]]
    assert "research/signings/explainers/why-mendes.html" in files


def test_image_outside_the_repository_is_not_embedded(project, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "secret.png"
    outside.write_bytes(b"\x89PNG\r\n\x1a\n")
    main(["explain", "new", "pic"])
    (project / "explainers" / "pic.md").write_text(f"# Pic\n\n![x]({outside})\n")
    main(["explain", "render", "pic"])
    page = (project / "explainers" / "pic.html").read_text()
    assert "base64" not in page and "image not found" in page


def test_render_any_markdown_file_outside_a_project(repo, capsys):
    (repo / "notes.md").write_text("# What is PPDA?\n\nPasses allowed per defensive action.\n")
    assert main(["explain", "render", "--file", "notes.md"]) == 0
    assert "Passes allowed per defensive action." in (repo / "notes.html").read_text()


def test_declined_topics_are_listed(project, capsys):
    assert main(["explain", "decline", "what xT is"]) == 0
    main(["explain", "list"])
    assert "Declined (do not offer again): what xT is" in capsys.readouterr().out


def test_teachback_is_personal_and_never_in_the_repository(project, repo, monkeypatch, tmp_path_factory):
    monkeypatch.setenv("NUTMEG_USER_CONFIG", str(tmp_path_factory.mktemp("home") / "user.json"))
    main(["teachback", *WORDS, "--clarified", "xT values passes and carries, not shots"])
    main(["explain", "decline", "what a median is"])
    store = understand.personal_store(project)
    assert store.is_file() and repo not in store.parents
    for path in repo.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            text = path.read_text(errors="replace")
            assert "a few big games" not in text and "what a median is" not in text, path
    page = workspaces.build(project)
    assert "teach-back" not in page.lower() and "a few big games" not in page


def test_shown_quotes_count_and_the_card_shows_them(project, repo):
    quote = "I chose the squad median because a ranking alone would hide whether anyone improved on what we had"
    assert main(["teachback", "--shown", quote]) == 0
    reason = gate.decide("nutmeg publish", repo, project, repo).reason
    assert "Understanding shown in Test Analyst's own messages" in reason and quote in reason
    assert main(["publish"]) == 0


def test_shown_and_answers_together_are_refused(project, capsys):
    quote = "I chose the squad median because a ranking alone would hide whether anyone improved"
    assert main(["teachback", "--shown", quote, *WORDS]) == 2
    assert "either --shown quotes or the three answers" in capsys.readouterr().err


def test_clarified_points_show_on_the_card(project, repo):
    main(["teachback", *WORDS, "--clarified", "xT values passes and carries, not shots"])
    assert "Cleared up along the way: xT values passes and carries, not shots" in \
        gate.decide("nutmeg publish", repo, project, repo).reason
