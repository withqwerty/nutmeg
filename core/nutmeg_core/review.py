"""Contest and resolve claims: a teammate's check, recorded with a name.

`contest` marks a claim disputed (an interpretation: contested) with a note.
`resolve` returns it to the status it had before, with a note. Both append a
new version to the ledger and a receipt.
"""
from pathlib import Path

from .project import append_receipt, find_repo_root, open_ledger
from .redact import Redactor


class ReviewError(ValueError):
    pass


def _contested_status(claim):
    return "contested" if claim["kind"] == "interpretation" else "disputed"


def contest(project, claim_id, note, by):
    if not note or not note.strip():
        raise ReviewError("say what is wrong with --note")
    ledger = open_ledger(project)
    note = Redactor.for_repo(find_repo_root(project)).text(note or "")
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
    ledger = open_ledger(project)
    note = Redactor.for_repo(find_repo_root(project)).text(note or "")
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
    written = ledger.update(claim_id, trusted=True, status=previous, note=note.strip(), by=by,
                            signer=claim.get("signer"))
    append_receipt(project, "resolve", claim=claim_id, by=by, note=note.strip(), status=previous,
                   version=written["version"])
    return written


def signoff(project, claim_id, by, note=None, signoff_required=False):
    """Verify a claim with the signer's name. With the team sign-off rule, the author cannot sign their own claim."""
    ledger = open_ledger(project)
    claim = ledger.get(claim_id)
    if claim is None:
        raise ReviewError(f"no claim {claim_id} in this project")
    if signoff_required and not claim.get("author"):
        raise ReviewError(f"{claim_id} has no recorded author, so the team's sign-off rule cannot be checked")
    if signoff_required and claim["author"] == by:
        raise ReviewError(f"{claim_id} was made by {by}; the team requires a different person to sign it off")
    target = "supported" if claim["kind"] == "interpretation" else "verified"
    if claim.get("status") in ("disputed", "contested"):
        raise ReviewError(f"{claim_id} is {claim['status']}; resolve it first")
    changes = {"status": target, "signer": by, "by": by}
    if note:
        changes["note"] = Redactor.for_repo(find_repo_root(project)).text(note)
    written = ledger.update(claim_id, trusted=True, **changes)
    append_receipt(project, "signoff", claim=claim_id, by=by, status=target, version=written["version"])
    return written
