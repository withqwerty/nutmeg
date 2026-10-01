"""The `nutmeg` command.

Skills call it as `python3 "${CLAUDE_PLUGIN_ROOT}/core/nutmeg.py" <command>`.
Messages say what failed and what to do next; they never print secrets.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__, card as cards, check as checks, project as projects, run as runs
from .config import ConfigError, data_in_git_policy, load_team, user_name
from .gate import pending_key
from .ledger import KINDS, REST_TYPES, ClaimError, Ledger
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
    """The project for this command: --project, $NUTMEG_PROJECT, then the active project."""
    chosen = args.project or os.environ.get("NUTMEG_PROJECT")
    if chosen:
        project = Path(chosen).resolve()
        if not project.is_dir():
            raise UsageError(f"research project not found: {chosen}")
        return project
    project = projects.active_project(find_repo_root(Path.cwd()))
    if project is None:
        raise UsageError("no active research project; start one with `nutmeg new <slug>` or pass --project research/<slug>")
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


def cmd_new(args):
    repo = find_repo_root(Path.cwd())
    try:
        policy = data_in_git_policy(load_team(repo))
    except ConfigError as exc:
        raise UsageError(str(exc))
    choice, source = args.data_in_git, "user"
    if policy == "no":
        if choice == "yes":
            raise UsageError("the team policy in .nutmeg/team.json keeps data out of git; drop --data-in-git yes")
        choice, source = "no", "team"
    elif policy == "yes" and choice is None:
        choice, source = "yes", "team"
    if choice is None:
        raise UsageError(
            "no team policy for data in git. Ask the user whether to keep data, run outputs and "
            "figure snapshots out of git, then run again with --data-in-git no (keep out) or --data-in-git yes"
        )
    try:
        folder = projects.create(repo, args.slug, choice, question=args.question or "",
                                 author=user_name(repo), title=args.title, policy_source=source)
    except projects.ProjectError as exc:
        raise UsageError(str(exc))
    kept = "kept out of git" if choice == "no" else "committed with the project"
    print(f"Started research/{args.slug} (active). Data and run outputs are {kept} ({source} choice).")
    print(f"Next: fill in {folder.relative_to(repo)}/question.md, then add plan choices with `nutmeg plan choose`.")
    return 0


def cmd_open(args):
    repo = find_repo_root(Path.cwd())
    try:
        projects.set_active(repo, args.slug)
    except projects.ProjectError as exc:
        raise UsageError(str(exc))
    print(f"research/{args.slug} is now the active project.")
    return 0


def cmd_close(args):
    slug = projects.close(find_repo_root(Path.cwd()))
    print(f"Closed research/{slug}; no project is active." if slug else "No project was active.")
    return 0


def cmd_status(args):
    repo = find_repo_root(Path.cwd())
    project = projects.active_project(repo)
    if project is None:
        print("No active research project.")
        return 0
    claims, problems = Ledger(project / "claims.jsonl").read()
    choices = projects.parse_choices((project / "plan.md").read_text(encoding="utf-8"))
    runs = [p for p in (project / "runs").iterdir() if p.is_dir() and not p.name.startswith(".")] if (project / "runs").is_dir() else []
    print(f"Active project: {project.relative_to(repo)}")
    print(f"  plan choices: {len(choices)}  claims: {len(claims)}  runs: {len(runs)}")
    if problems:
        print(f"  ledger problems: {len(problems)} (run `nutmeg claim list`)")
    return 0


def cmd_plan_choose(args):
    project = resolve_project(args)
    try:
        projects.add_choice(project, args.kind, args.choice, args.why, args.rests_type, args.rests_ref)
    except projects.ProjectError as exc:
        raise UsageError(str(exc))
    print(f"Added {args.kind}: {args.choice} to plan.md")
    return 0


def cmd_plan_check(args):
    project = resolve_project(args)
    choices = projects.parse_choices((project / "plan.md").read_text(encoding="utf-8"))
    problems = projects.check_choices(choices)
    for problem in problems:
        print(problem)
    if not choices:
        print("plan.md has no choices yet.")
    elif not problems:
        print(f"All {len(choices)} plan choices have a reason and what they rest on.")
    return 1 if problems else 0


def _run_args(args):
    return cards.normalise_run_args(args)


def cmd_gate(args):
    """Build and print the gate card without running anything (autonomy level L1)."""
    project = resolve_project(args)
    repo, cwd = find_repo_root(project), Path.cwd()
    run_args = _run_args(args)
    card = cards.build_run_card(run_args, repo, project, cwd)
    cards.save_pending(project, pending_key(cards.run_key(run_args, repo, cwd)), card)
    print(cards.render_text(card))
    return 1 if card["problems"] else 0


def cmd_run(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    try:
        run_id, exit_code, record = runs.execute(_run_args(args), repo, project, Path.cwd())
    except runs.RunError as exc:
        raise UsageError(f"run refused: {exc}")
    note = ""
    if record["gate"]["changed_since_gate"]:
        note = f"; changed after the gate card was shown: {', '.join(record['gate']['changed_since_gate'])}"
    print(f"nutmeg: recorded run {run_id} ({record['status']}, exit {exit_code}) in "
          f"{project.relative_to(repo)}/runs/{run_id}{note}. Cite it as run_id {run_id} in computed claims.",
          file=sys.stderr)
    return exit_code


def cmd_check(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    if args.accept:
        try:
            record = checks.accept(project, args.accept, args.reason, user_name(repo))
        except ValueError as exc:
            raise UsageError(str(exc))
        print(f"Accepted {record['id']}: {record['failure']['message']} (reason recorded in receipts.jsonl)")
    state = checks.check(project)
    files = checks.output_files(project)
    for warning in state.get("warnings", []):
        print(f"warning: {warning}")
    if not state["open"]:
        print(f"No open problems in {len(files)} output file(s) and {project.relative_to(repo)}/claims.jsonl.")
        return 0
    print(f"{len(state['open'])} open problem(s):")
    for failure in state["open"]:
        print(f"- {checks.describe(failure)}")
    print("Fix each one (add the claim with its evidence, or correct the output), or record the user's reason "
          "with `nutmeg check --accept <id> --reason \"...\"`.")
    return 1


def build_parser():
    parser = argparse.ArgumentParser(
        prog="nutmeg",
        description="Record and check the claims, runs and figures in a nutmeg research project.",
    )
    parser.add_argument("--version", action="version", version=f"nutmeg {__version__}")
    parser.add_argument("--project", help="research project folder (default: the active project)")
    commands = parser.add_subparsers(dest="command", metavar="<command>")

    new = commands.add_parser("new", help="start a research project and make it active")
    new.add_argument("slug", help="short name, for example shortlist-lb")
    new.add_argument("--question", help="the question, in one sentence")
    new.add_argument("--title", help="a readable title (default: from the slug)")
    new.add_argument("--data-in-git", choices=("yes", "no"),
                     help="commit data and run outputs (yes) or keep them out of git (no)")
    new.set_defaults(handler=cmd_new)

    opener = commands.add_parser("open", help="make an existing project active")
    opener.add_argument("slug")
    opener.set_defaults(handler=cmd_open)

    commands.add_parser("close", help="clear the active project").set_defaults(handler=cmd_close)
    commands.add_parser("status", help="show the active project").set_defaults(handler=cmd_status)

    plan = commands.add_parser("plan", help="add or check plan choices")
    plan_commands = plan.add_subparsers(dest="plan_command", metavar="<action>")
    choose = plan_commands.add_parser("choose", help="add a choice with its reason to plan.md")
    choose.add_argument("--kind", required=True, choices=projects.CHOICE_KINDS)
    choose.add_argument("--choice", required=True, help="what was chosen, for example 'npxG per 90'")
    choose.add_argument("--why", required=True, help="one sentence: why this was chosen")
    choose.add_argument("--rests-type", required=True, choices=REST_TYPES, help="what the reason rests on")
    choose.add_argument("--rests-ref", required=True,
                        help="the reference: a football-docs page, rule, paper, claim ID or the user's words")
    choose.set_defaults(handler=cmd_plan_choose)
    plan_commands.add_parser("check", help="check every choice has a reason").set_defaults(handler=cmd_plan_check)

    run = commands.add_parser("run", help="run a .py, .R or .sql file and record it")
    cards.add_run_arguments(run)
    run.set_defaults(handler=cmd_run)

    gate = commands.add_parser("gate", help="show the gate card for a run without running it")
    cards.add_run_arguments(gate)
    gate.set_defaults(handler=cmd_gate)

    check = commands.add_parser("check", help="check that every number, citation and fact in the outputs traces to the ledger")
    check.add_argument("--accept", metavar="ID", help="close an open problem with the user's reason")
    check.add_argument("--reason", help="why the problem is accepted (required with --accept)")
    check.set_defaults(handler=cmd_check)

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
    argv = list(sys.argv[1:] if argv is None else argv)
    argv, script_args = cards.split_script_args(argv)
    args = parser.parse_args(argv)
    args.script_args = script_args
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0 if args.command is None else 2
    try:
        return handler(args)
    except UsageError as exc:
        print(f"nutmeg: {exc}", file=sys.stderr)
        return 2
