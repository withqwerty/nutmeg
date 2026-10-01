import json

import pytest

from nutmeg_core.ledger import ClaimError, Ledger, validate
from nutmeg_core.redact import Redactor


def computed(**extra):
    record = {
        "kind": "computed",
        "statement": "npxG/90 rose to 1.78",
        "value": 1.78,
        "evidence": {"run_id": "R3", "metric": "npxG/90", "n": 34, "filters": {"season": "2025/26"}},
        "why": "npxG/90 removes penalties, which distort per-player comparisons.",
        "rests_on": {"type": "docs", "ref": "football-docs:statsbomb/xg"},
    }
    record.update(extra)
    return record


@pytest.fixture
def ledger(tmp_path):
    return Ledger(tmp_path / "claims.jsonl")


def test_computed_claim_round_trips(ledger):
    written = ledger.append(computed())
    read = ledger.get(written["id"])
    assert read == written
    for key, value in computed().items():
        assert read[key] == value
    assert read["id"] == "C1" and read["version"] == 1 and read["status"] == "draft"


def test_computed_claim_without_run_id_is_rejected(ledger):
    record = computed()
    del record["evidence"]["run_id"]
    with pytest.raises(ClaimError) as exc:
        ledger.append(record)
    assert exc.value.field == "evidence.run_id"
    assert not ledger.path.exists()


def test_computed_claim_without_value_is_rejected(ledger):
    record = computed()
    del record["value"]
    with pytest.raises(ClaimError) as exc:
        ledger.append(record)
    assert exc.value.field == "value"


def test_unknown_kind_is_rejected():
    with pytest.raises(ClaimError) as exc:
        validate(computed(kind="vibe", id="C1"))
    assert exc.value.field == "kind"


def test_interpretation_needs_linked_claims(ledger):
    record = {"kind": "interpretation", "statement": "He is the better pressing forward", "evidence": {"claims": []}}
    with pytest.raises(ClaimError) as exc:
        ledger.append(record)
    assert exc.value.field == "evidence.claims"


def test_interpretation_cannot_be_verified(ledger):
    ledger.append(computed())
    record = {"kind": "interpretation", "statement": "He is the better pressing forward",
              "evidence": {"claims": ["C1"]}, "status": "verified"}
    with pytest.raises(ClaimError) as exc:
        ledger.append(record)
    assert exc.value.field == "status"
    assert "never verified" in str(exc.value)
    written = ledger.append({**record, "status": "supported"})
    assert written["status"] == "supported"


def test_each_kind_needs_its_evidence(ledger):
    cases = {
        "provider_fact": ({"provider": "statsbomb", "source": "football-docs:statsbomb/events"}, "provider"),
        "identity": ({"reep_id": "reep_p123", "release": "v1"}, "release"),
        "literature": ({"citation": "Singh (2019), Introducing Expected Threat"}, "citation"),
        "definition": ({"definition": "Non-penalty xG per 90 minutes"}, "definition"),
    }
    for kind, (evidence, required) in cases.items():
        record = {"kind": kind, "statement": f"a {kind} claim", "evidence": dict(evidence)}
        assert ledger.append(record)["kind"] == kind
        del record["evidence"][required]
        with pytest.raises(ClaimError) as exc:
            ledger.append(record)
        assert exc.value.field == f"evidence.{required}"


def test_same_id_returns_latest_version(ledger):
    first = ledger.append(computed())
    ledger.append({**first, "value": 1.81, "statement": "npxG/90 rose to 1.81"})
    latest = ledger.get(first["id"])
    assert latest["value"] == 1.81 and latest["version"] == 2
    assert [v["value"] for v in ledger.history(first["id"])] == [1.78, 1.81]
    assert len(ledger.path.read_text().splitlines()) == 2


def test_update_appends_a_version(ledger):
    first = ledger.append(computed())
    ledger.update(first["id"], status="disputed", note="excludes extra time?")
    assert ledger.get(first["id"])["status"] == "disputed"
    assert ledger.get(first["id"])["version"] == 2


def test_next_id_counts_up(ledger):
    assert ledger.append(computed())["id"] == "C1"
    assert ledger.append(computed())["id"] == "C2"


def test_malformed_line_is_reported_and_valid_lines_survive(ledger):
    ledger.append(computed())
    with ledger.path.open("a") as handle:
        handle.write("{not json\n")
        handle.write(json.dumps({"id": "C9", "kind": "computed", "statement": "x", "value": 1, "evidence": {}}) + "\n")
    ledger.append(computed(statement="xG per shot 0.12", value=0.12))
    claims, problems = ledger.read()
    assert sorted(claims) == ["C1", "C2"]
    assert [lineno for lineno, _ in problems] == [2, 3]
    assert "not valid JSON" in problems[0][1]
    assert "evidence" in problems[1][1]


def test_reason_must_be_one_line(ledger):
    with pytest.raises(ClaimError) as exc:
        ledger.append(computed(why="First reason.\nSecond reason."))
    assert exc.value.field == "why"


def test_rests_on_needs_type_and_ref(ledger):
    with pytest.raises(ClaimError) as exc:
        ledger.append(computed(rests_on={"type": "vibes", "ref": "x"}))
    assert exc.value.field == "rests_on"


def test_append_redacts_secrets(tmp_path):
    ledger = Ledger(tmp_path / "claims.jsonl", redactor=Redactor(["sk-live-abcdef123456"]))
    written = ledger.append(computed(note="fetched with key sk-live-abcdef123456"))
    assert "sk-live" not in ledger.path.read_text()
    assert written["note"] == "fetched with key [REDACTED]"
