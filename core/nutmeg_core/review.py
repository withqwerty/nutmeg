"""Contest and resolve claims: a teammate's check, recorded with a name.

`contest` marks a claim disputed (an interpretation: contested) with a note.
`resolve` returns it to the status it had before, with a note. Both append a
new version to the ledger and a receipt.
"""
from pathlib import Path

from .ledger import Ledger
from .project import append_receipt


class ReviewError(ValueError):
    pass


def _contested_status(claim):
    return "contested" if claim["kind"] == "interpretation" else "disputed"


def contest(project, claim_id, note, by):
    if not note or not note.strip():
        raise ReviewError("say what is wrong with --note")
    ledger = Ledger(Path(project) / "claims.jsonl")
    claim = ledger.get(claim_id)
    if claim is None:
        raise ReviewError(f"no claim {claim_id} in this project")
    target = _contested_status(claim)
    if claim.get("status") == target:
        raise ReviewError(f"{claim_id} is already {target}; add to it with `nutmeg resolve` or a new contest later")
    written = ledger.update(claim_id, status=target, note=note.strip(), by=by,
                            previous_status=claim.get("status", "draft"))
    append_receipt(project, "contest", claim=claim_id, by=by, note=note.strip(), version=written["version"])
    return written


def resolve(project, claim_id, note, by):
    if not note or not note.strip():
        raise ReviewError("say how it was resolved with --note")
    ledger = Ledger(Path(project) / "claims.jsonl")
    claim = ledger.get(claim_id)
    if claim is None:
        raise ReviewError(f"no claim {claim_id} in this project")
    if claim.get("status") != _contested_status(claim):
        raise ReviewError(f"{claim_id} is {claim.get('status')}, not {_contested_status(claim)}; nothing to resolve")
    previous = "draft"
    for version in reversed(ledger.history(claim_id)):
        if version.get("previous_status"):
            previous = version["previous_status"]
            break
    written = ledger.update(claim_id, status=previous, note=note.strip(), by=by)
    append_receipt(project, "resolve", claim=claim_id, by=by, note=note.strip(), status=previous,
                   version=written["version"])
    return written
