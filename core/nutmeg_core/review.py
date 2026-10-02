"""Contest and resolve claims: a teammate's check, recorded with a name.

`contest` marks a claim disputed (an interpretation: contested) with a note.
`resolve` returns it to the status it had before, with a note. Both append a
new version to the ledger and a receipt.
"""
from pathlib import Path

from .ledger import CONTENT_FIELDS
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
    claim = ledger.get(claim_id)
    if claim is None:
        raise ReviewError(f"no claim {claim_id} in this project")
    target = _contested_status(claim)
    if claim.get("status") == target:
        raise ReviewError(f"{claim_id} is already {target}; add to it with `nutmeg resolve` or a new contest later")
    note = Redactor.for_repo(find_repo_root(project)).text(note)
    written = ledger.update(claim_id, trusted=True, status=target, note=note.strip(), by=by,
                            previous_status=claim.get("status", "draft"), previous_signer=claim.get("signer"))
    append_receipt(project, "contest", claim=claim_id, by=by, note=note.strip(), version=written["version"])
    return written


def withdraw(project, claim_id, note, by):
    """Take a claim out of use (for example one replaced by finer claims). Outputs that cite it then fail the check."""
    if not note or not note.strip():
        raise ReviewError("say why it is withdrawn with --note, for example 'replaced by C23-C26'")
    ledger = open_ledger(project)
    claim = ledger.get(claim_id)
    if claim is None:
        raise ReviewError(f"no claim {claim_id} in this project")
    if claim.get("status") == "withdrawn":
        raise ReviewError(f"{claim_id} is already withdrawn")
    note = Redactor.for_repo(find_repo_root(project)).text(note)
    written = ledger.update(claim_id, status="withdrawn", note=note.strip(), by=by)
    append_receipt(project, "withdraw", claim=claim_id, by=by, note=note.strip(), version=written["version"])
    return written


def resolve(project, claim_id, note, by):
    if not note or not note.strip():
        raise ReviewError("say how it was resolved with --note")
    ledger = open_ledger(project)
    claim = ledger.get(claim_id)
    if claim is None:
        raise ReviewError(f"no claim {claim_id} in this project")
    if claim.get("status") != _contested_status(claim):
        raise ReviewError(f"{claim_id} is {claim.get('status')}, not {_contested_status(claim)}; nothing to resolve")
    note = Redactor.for_repo(find_repo_root(project)).text(note)
    # The version that opened the dispute holds the status and sign-off from before it. Restore them only if
    # the claim's content has not changed since; otherwise the claim goes back to draft.
    history = ledger.history(claim_id)
    opened = next((v for v in reversed(history) if v.get("status") == _contested_status(claim)
                   and "previous_status" in v), None)
    previous, signer = "draft", None
    if opened is not None and all(opened.get(k) == claim.get(k) for k in CONTENT_FIELDS):
        previous, signer = opened.get("previous_status") or "draft", opened.get("previous_signer")
    changes = {"status": previous, "note": note.strip(), "by": by}
    if signer:
        changes["signer"] = signer
    written = ledger.update(claim_id, trusted=True, **changes)
    append_receipt(project, "resolve", claim=claim_id, by=by, note=note.strip(), status=written["status"],
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
