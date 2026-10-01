"""The `nutmeg` command.

Skills call it as `python3 "${CLAUDE_PLUGIN_ROOT}/core/nutmeg.py" <command>`.
Messages say what failed and what to do next; they never print secrets.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__
from .ledger import KINDS, ClaimError, Ledger
from .redact import Redactor


class UsageError(Exception):
    """A user-facing error: printed without a traceback, exit code 2."""


def find_repo_root(start):
    """The nearest folder above `start` that holds `.git`, else `start`."""
    start = Path(start).resolve()
    for folder in (start, *start.parents):
        if (folder / ".git").exists():
            return folder
    return start


def resolve_project(args):
    """The project folder for this command: --project, then $NUTMEG_PROJECT."""
    chosen = args.project or os.environ.get("NUTMEG_PROJECT")
    if not chosen:
        raise UsageError("no research project given; pass --project research/<slug>")
    project = Path(chosen).resolve()
    if not project.is_dir():
        raise UsageError(f"research project not found: {chosen}")
    return project


def open_ledger(project):
    return Ledger(project / "claims.jsonl", redactor=Redactor.for_repo(find_repo_root(project)))


def _read_record(args):
    text = args.json if args.json is not None else sys.stdin.read()
    try:
        record = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UsageError(f"the claim is not valid JSON ({exc.msg} at line {exc.lineno})")
    if args.kind:
        record["kind"] = args.kind
    return record


def cmd_claim_add(args):
    ledger = open_ledger(resolve_project(args))
    record = _read_record(args)
    try:
        written = ledger.append(record)
    except ClaimError as exc:
        raise UsageError(f"claim rejected: {exc}")
    print(json.dumps({"id": written["id"], "version": written["version"], "status": written["status"]}))
    return 0


def cmd_claim_list(args):
    ledger = open_ledger(resolve_project(args))
    claims, problems = ledger.read()
    for claim in claims.values():
        value = f" = {claim['value']}" if "value" in claim else ""
        print(f"{claim['id']:<6} {claim['kind']:<15} {claim['status']:<10} {claim['statement']}{value}")
    if not claims:
        print("No claims yet.")
    for lineno, message in problems:
        print(f"claims.jsonl line {lineno}: {message}", file=sys.stderr)
    return 1 if problems else 0


def cmd_claim_show(args):
    ledger = open_ledger(resolve_project(args))
    claim = ledger.get(args.claim_id)
    if claim is None:
        raise UsageError(f"no claim {args.claim_id} in this project")
    print(json.dumps(claim, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="nutmeg",
        description="Record and check the claims, runs and figures in a nutmeg research project.",
    )
    parser.add_argument("--version", action="version", version=f"nutmeg {__version__}")
    parser.add_argument("--project", help="research project folder (default: the active project)")
    commands = parser.add_subparsers(dest="command", metavar="<command>")

    claim = commands.add_parser("claim", help="add, list or show ledger claims")
    claim_commands = claim.add_subparsers(dest="claim_command", metavar="<action>")

    add = claim_commands.add_parser("add", help="append a claim (JSON from --json or stdin)")
    add.add_argument("--json", help="the claim as a JSON object")
    add.add_argument("--kind", choices=KINDS, help="set the claim kind")
    add.set_defaults(handler=cmd_claim_add)

    listing = claim_commands.add_parser("list", help="list the latest version of every claim")
    listing.set_defaults(handler=cmd_claim_list)

    show = claim_commands.add_parser("show", help="print one claim as JSON")
    show.add_argument("claim_id")
    show.set_defaults(handler=cmd_claim_show)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0 if args.command is None else 2
    try:
        return handler(args)
    except UsageError as exc:
        print(f"nutmeg: {exc}", file=sys.stderr)
        return 2
