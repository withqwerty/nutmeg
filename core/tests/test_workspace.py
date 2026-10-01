import json
import re
from datetime import datetime, timezone

import pytest

from nutmeg_core import check as checks
from nutmeg_core import glossary
from nutmeg_core import workspace
from nutmeg_core.cli import main
from nutmeg_core.ledger import Ledger


@pytest.fixture
def project(repo):
    main(["new", "demo", "--data-in-git", "yes", "--question", "Which left-backs progress the ball?"])
    folder = repo / "research" / "demo"
    (folder / "runs" / "R1").mkdir(parents=True)
    (folder / "runs" / "R1" / "run.json").write_text(json.dumps({"id": "R1", "file": "a.py", "status": "ok", "started": "x", "gate": {"shown": True}}))
    main(["plan", "choose", "--kind", "metric", "--choice", "npxG per 90", "--why", "Penalties distort comparisons.",
          "--rests-type", "docs", "--rests-ref", "football-docs: StatsBomb shot fields"])
    ledger = Ledger(folder / "claims.jsonl")
    ledger.append({"kind": "computed", "statement": "Robertson npxG per 90", "value": 0.21, "evidence": {"run_id": "R1"}})
    ledger.append({"kind": "computed", "statement": "Udogie progressive carries", "value": 74, "evidence": {"run_id": "R1"}})
    ledger.append({"kind": "computed", "statement": "<script>alert(1)</script> value", "value": "<b>3</b>",
                   "evidence": {"run_id": "R1"}})
    main(["contest", "C2", "--note", "includes cup games?"])
    return folder


def page(project, repo):
    return workspace.build(project, repo, now=datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc))


def test_three_claims_disputed_first(project, repo):
    html = page(project, repo)
    ids = re.findall(r'<tr id="(C\d+)"', html)
    assert ids == ["C2", "C1", "C3"]
    assert "includes cup games?" in html and "Disputed claim" in html


def test_content_is_escaped(project, repo):
    html = page(project, repo)
    assert "<script>" not in html and "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<b>3</b>" not in html


def test_javascript_url_renders_as_text(project, repo):
    (project / "report.md").write_text("See [the source](javascript:alert(1)) and [docs](https://example.org/x).\n")
    html = page(project, repo)
    assert "javascript:" not in html.split("<main>")[1].replace("the source", "")
    assert '<a href="https://example.org/x">docs</a>' in html


def test_no_figures_empty_state(project, repo):
    assert "No figures registered yet." in page(project, repo)


def test_csp_and_no_scripts(project, repo):
    html = page(project, repo)
    assert 'http-equiv="Content-Security-Policy"' in html and "default-src 'none'" in html
    assert "<script" not in html.lower()


def test_stamp_and_counts(project, repo):
    html = page(project, repo)
    assert "Generated <strong>2026-10-02 09:00 UTC</strong>" in html
    assert "<strong>3</strong> claims in <strong>4</strong> lines" in html


def test_plan_reason_and_source_title(project, repo):
    html = page(project, repo)
    assert "Penalties distort comparisons." in html
    assert "football-docs: StatsBomb shot fields" in html


def test_glossary_term_links_to_inlined_entry(project, repo):
    html = page(project, repo)
    assert '<a class="term" href="#g-npxg">npxG</a>' in html
    assert '<dt id="g-npxg">npxG (non-penalty expected goals)</dt>' in html


def test_secrets_are_redacted(project, repo):
    (repo / ".env").write_text("TOKEN=tok-very-secret-1\n")
    (project / "report.md").write_text("Fetched with tok-very-secret-1.\n")
    assert "tok-very-secret-1" not in page(project, repo)


def test_placeholder_text_in_content_is_not_replaced(project, repo):
    (project / "report.md").write_text("Literal {{glossary}} text.\n")
    assert "Literal {{glossary}} text." in page(project, repo)


def test_workspace_command_writes_file(project, repo, capsys):
    assert main(["workspace"]) == 0
    assert (project / "workspace.html").is_file()


def test_unknown_metric_warns(project):
    main(["plan", "choose", "--kind", "metric", "--choice", "ball-winning index", "--why", "Asked for it.",
          "--rests-type", "user", "--rests-ref", "head of recruitment"])
    _, warnings = checks.run_checks(project)
    assert any("ball-winning index" in w for w in warnings)
    assert not any("npxG per 90" in w for w in warnings)


def test_glossary_loads_every_learn_term():
    slugs = {e["slug"] for e in glossary.load()}
    for expected in ("xg", "npxg", "xt", "ppda", "progressive-pass", "per-90", "big-chance"):
        assert expected in slugs


def test_claim_references_link_to_rows_and_italics_render(project, repo):
    (project / "report.md").write_text("Robertson leads with 0.21 [C1]; see also [C1, C2]. _(placeholder)_ and snake_case_name.\n")
    html = page(project, repo)
    assert '[<a class="claim" href="#C1">C1</a>]' in html
    assert '<a class="claim" href="#C2">C2</a>]' in html
    assert "<em>(placeholder)</em>" in html and "snake_case_name" in html
