"""The `nutmeg` command.

Skills call it as `python3 "${CLAUDE_PLUGIN_ROOT}/core/nutmeg.py" <command>`.
Messages say what failed and what to do next; they never print secrets.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__, card as cards, check as checks, figure as figures, project as projects, publish as publishing
from . import bundle as bundling, provenance, review, run as runs, understand, why as whys, workspace as workspaces
from .config import (LEVELS, PERSONAS, STAGES, ConfigError, data_in_git_policy, load_effective, load_team,
                     save_user, team_signoff_required, user_config_path, user_name)
from .gate import acknowledge_settings, pending_key
from .ledger import KINDS, REST_TYPES, ClaimError, Ledger
from .redact import Redactor


class UsageError(Exception):
    """A user-facing error: printed without a traceback, exit code 2."""


find_repo_root = projects.find_repo_root


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


open_ledger = projects.open_ledger


def _read_record(args):
    text = args.json if args.json is not None else sys.stdin.read()
    try:
        record = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UsageError(f"the claim is not valid JSON ({exc.msg} at line {exc.lineno})")
    if args.kind:
        record["kind"] = args.kind
    if isinstance(record, dict) and args.headline:
        record["headline"] = True
    return record


def cmd_claim_add(args):
    project = resolve_project(args)
    ledger = open_ledger(project)
    record = _read_record(args)
    if isinstance(record, dict) and (not record.get("id") or not ledger.history(record["id"])):
        record["author"] = user_name(find_repo_root(project))
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
        projects.add_choice(project, args.kind, args.choice, args.why, args.rests_type, args.rests_ref,
                            after_results=args.after_results)
    except projects.ProjectError as exc:
        raise UsageError(str(exc))
    marked = " (marked as made after seeing the results)" if args.after_results is not None else ""
    print(f"Added {args.kind}: {args.choice} to plan.md{marked}")
    if projects.plan_locks(project):
        print("The plan was locked at the first run, so this choice is listed as a deviation on the publish card. "
              "Keep the locked choice as the primary result unless the user decides otherwise.")
    return 0


def cmd_plan_lock(args):
    project = resolve_project(args)
    if not args.reason:
        raise UsageError("say why you lock again with --reason, for example 'phase 2: opponent analysis'")
    lock = projects.lock_plan(project, reason=args.reason, by=user_name(find_repo_root(project)))
    print(f"Locked {len(lock['choices'])} plan choice(s) ({lock['hash']}).")
    return 0


def cmd_plan_diff(args):
    print("\n".join(projects.deviation_lines(resolve_project(args))))
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
    acknowledge_settings(repo)
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


def cmd_why(args):
    project = resolve_project(args)
    try:
        lines = whys.why_lines(project, find_repo_root(project), args.claim_id)
    except KeyError:
        raise UsageError(f"no claim {args.claim_id} in {project.name}; `nutmeg claim list` shows the IDs")
    print(Redactor.for_repo(find_repo_root(project)).text("\n".join(lines)))
    return 0


def cmd_trace(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    print(Redactor.for_repo(repo).text("\n".join(whys.trace_lines(project, repo))))
    return 0


def cmd_contest(args):
    project = resolve_project(args)
    try:
        written = review.contest(project, args.claim_id, args.note, user_name(find_repo_root(project)))
    except review.ReviewError as exc:
        raise UsageError(str(exc))
    print(f"{written['id']} is now {written['status']} ({written['by']}: {written['note']})")
    return 0


def cmd_claim_withdraw(args):
    project = resolve_project(args)
    try:
        written = review.withdraw(project, args.claim_id, args.note, user_name(find_repo_root(project)))
    except review.ReviewError as exc:
        raise UsageError(str(exc))
    print(f"{written['id']} is now withdrawn ({written['by']}: {written['note']}); "
          "outputs that still cite it will fail `nutmeg check`")
    return 0


def cmd_resolve(args):
    project = resolve_project(args)
    try:
        written = review.resolve(project, args.claim_id, args.note, user_name(find_repo_root(project)))
    except review.ReviewError as exc:
        raise UsageError(str(exc))
    print(f"{written['id']} is now {written['status']} ({written['by']}: {written['note']})")
    return 0


def cmd_figure_register(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    claims = [c.strip() for c in (args.claims or "").split(",") if c.strip()]
    try:
        # Paths are relative to where the command runs, like every other nutmeg path argument.
        data = str(Path.cwd() / args.data) if args.data else None
        image = None
        if args.image:
            image_path = (Path.cwd() / args.image).resolve()
            image = image_path.relative_to(repo).as_posix() if image_path.is_relative_to(repo) else args.image
        prov = figures.register(project, repo, args.name, data, args.source, claims, n=args.n,
                                competition_season=args.season, filters=args.filters, metric=args.metric,
                                uncertainty=args.uncertainty, run_id=args.run, image=image, panels=args.panel)
    except figures.FigureError as exc:
        raise UsageError(str(exc))
    print(f"Footnote (put it under the chart): {prov['footnote']}")
    print(f"Provenance: {project.relative_to(repo)}/figures/{prov['figure']}.prov.json")
    return 0


def cmd_publish(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    try:
        record = publishing.publish(project, repo, user_name(repo), to=str(Path.cwd() / args.to) if args.to else None)
    except publishing.PublishError as exc:
        raise UsageError(f"publish refused: {exc}")
    acknowledge_settings(repo)
    where = f" and copied to {record['to']}" if record["to"] else ""
    print(f"Published {len(record['files'])} file(s) with {len(record['figures'])} figure(s){where}; "
          f"recorded in {project.relative_to(repo)}/published.json.")
    return 0


def cmd_teachback(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    by = user_name(repo)
    words = {"claim": args.claim, "rests_on": args.rests_on, "would_change": args.would_change}
    if not args.show:
        if not args.shown and not all(words.values()):
            raise UsageError("give --shown quotes from the user's messages, or --claim, --rests-on and --would-change "
                             "in their own words (or --show)")
        covers = [c.strip() for c in (args.covers or "").split(",") if c.strip()] or None
        try:
            entry = understand.record(project, by, words=words, covers=covers,
                                      shown=args.shown, clarified=args.clarified)
        except understand.UnderstandError as exc:
            raise UsageError(f"not recorded yet: {exc}")
        print(f"Recorded for {', '.join(sorted(entry['covers']))}, in your own nutmeg folder (not the repository). "
              "Only your publish card shows it.")
    state = understand.status(project, by)
    gap = understand.describe_gap(state)
    if args.show and state["latest"]:
        print("\n".join(understand.summary_lines(state["latest"])))
    if gap:
        print(f"Before publishing, {by} still needs to talk through: {gap}")
        return 1
    if args.show:
        print(f"Ready to publish: it covers {', '.join(state['needed']) or 'nothing yet'}.")
    return 0


def cmd_explain_new(args):
    project = resolve_project(args)
    try:
        path = understand.new(project, args.slug, args.title)
    except understand.UnderstandError as exc:
        raise UsageError(str(exc))
    print(f"Wrote {path.relative_to(find_repo_root(project))}. Fill it in, then run `nutmeg explain render {args.slug}`.")
    return 0


def cmd_explain_render(args):
    if args.file:
        source = (Path.cwd() / args.file).resolve()
        if not source.is_file() or source.suffix.lower() != ".md":
            raise UsageError(f"not a Markdown file: {args.file}")
        repo = find_repo_root(source.parent)
        active = projects.active_project(repo)
        project = active if active is not None and active.resolve() in source.parents else None
        sources = [source]
    else:
        project = resolve_project(args)
        repo = find_repo_root(project)
        sources = understand.explainers(project)
        if args.slug:
            sources = [s for s in sources if s.stem == args.slug]
            if not sources:
                raise UsageError(f"no explainers/{args.slug}.md in {project.name}; `nutmeg explain new {args.slug}` starts one")
        if not sources:
            raise UsageError("no explainers yet; `nutmeg explain new <slug>` starts one")
    for source in sources:
        page = understand.render(source, project=project, repo_root=repo)
        shown = page.relative_to(repo) if page.is_relative_to(repo) else page
        print(f"Wrote {shown} (one file, no network needed). Edit {source.name} and render again to change it.")
    if project is not None:
        state = checks.check(project)
        mine = [f for f in state["open"] if str(f.get("file", "")).startswith(understand.EXPLAINERS + "/")]
        for failure in mine:
            print(f"- {checks.describe(failure)}")
        if mine:
            print(f"{len(mine)} number(s) in the explainers do not trace to the ledger; fix them before sharing.")
            return 1
    return 0


def cmd_explain_list(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    sources = understand.explainers(project)
    for source in sources:
        print(f"{source.relative_to(repo)} · page {understand.page_state(source)}")
    if not sources:
        print("No explainers yet.")
    declined = understand.declined(project)
    if declined:
        print("Declined (do not offer again): " + ", ".join(declined))
    return 0


def cmd_explain_decline(args):
    project = resolve_project(args)
    understand.decline(project, args.topic, user_name(find_repo_root(project)))
    print(f"Recorded: do not offer an explainer on {args.topic!r} again in this project.")
    return 0


def cmd_data_add(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    try:
        entry = provenance.add(project, repo, str(Path.cwd() / args.file), args.source, user_name(repo),
                               licence=args.licence, retrieved=args.retrieved, note=args.note)
    except provenance.ProvenanceError as exc:
        raise UsageError(str(exc))
    prof = entry.get("profile") or {}
    size = f"{prof['rows']} rows, {len(prof.get('columns', []))} columns; " if prof else ""
    print(f"Recorded {entry['path']} ({size}sha256 {entry['sha256'][:12]}) from {entry['source']}.")
    for concern in provenance.concerns(entry):
        print(f"- look at this before analysis: {concern}")
    return 0


def cmd_data_list(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    files = provenance.load(project)["files"]
    if not files:
        print("No data files recorded yet; `nutmeg data add <file> --source ...` records one.")
    for entry in files:
        print(f"{entry['path']} · {provenance.state(repo, entry)} · from {entry.get('source')}"
              f"{' · licence ' + entry['licence'] if entry.get('licence') else ''}")
        for concern in provenance.concerns(entry):
            print(f"  - {concern}")
    return 0


def cmd_signoff(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    try:
        written = review.signoff(project, args.claim_id, user_name(repo), note=args.note,
                                 signoff_required=team_signoff_required(repo))
    except (review.ReviewError, ConfigError) as exc:
        raise UsageError(str(exc))
    print(f"{written['id']} is now {written['status']}, signed off by {written['signer']}.")
    return 0


def cmd_config_show(args):
    repo = find_repo_root(Path.cwd())
    try:
        settings = load_effective(repo)
    except ConfigError as exc:
        raise UsageError(str(exc))
    print(f"Persona: {settings['persona']}")
    for stage in STAGES:
        print(f"  {stage}: {settings['levels'][stage]} - {settings['reasons'][stage]}")
    print(f"  run-then-review: {settings['reasons']['run_then_review']}")
    print(f"Sign-off required for headline claims: {'yes' if settings['signoff_required'] else 'no'}")
    print(f"Data in git: {settings['data_in_git']}")
    if settings["approved_services"]:
        print(f"Team-approved services: {', '.join(settings['approved_services'])}")
    print(f"User config: {user_config_path()}")
    for warning in settings.get("warnings", []):
        print(f"warning: {warning}")
    return 0


def cmd_config_set(args):
    values = {}
    if args.persona:
        values["persona"] = args.persona
    for stage in STAGES:
        level = getattr(args, f"autonomy_{stage}")
        if level:
            values[f"autonomy_{stage}"] = level
    if args.run_then_review:
        values["run_then_review"] = args.run_then_review == "yes"
    if args.name:
        values["name"] = args.name
    if not values:
        raise UsageError("nothing to set; see `nutmeg config set --help`")
    path = save_user(values)
    project = projects.active_project(find_repo_root(Path.cwd()))
    if project is not None:
        projects.append_receipt(project, "config_changed", values=values, file=str(path))
    print(f"Saved {', '.join(sorted(values))} to {path}.")
    return cmd_config_show(args)


def cmd_queue(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    if args.done:
        known = {r["id"] for r in runs.review_queue(project)}
        if args.done not in known:
            raise UsageError(f"{args.done} is not in the review queue")
        projects.append_receipt(project, "run_reviewed", run_id=args.done, by=user_name(repo), note=args.note)
        print(f"Marked {args.done} as reviewed.")
    queue = runs.review_queue(project)
    if not queue:
        print("The review queue is empty.")
        return 0
    print(f"{len(queue)} run(s) went ahead under run-then-review and wait for review:")
    for record in queue:
        print(f"- {record['id']} {record.get('file')} · {record.get('status')} · {record.get('started')}"
              f" (card: {project.relative_to(repo)}/runs/{record['id']}/gate.json)")
    return 0


def cmd_bundle(args):
    project = resolve_project(args)
    repo = find_repo_root(project)
    try:
        target, manifest = bundling.bundle(project, repo, args.raw, user_name(repo), out=args.out)
    except bundling.BundleError as exc:
        raise UsageError(f"bundle refused: {exc}")
    acknowledge_settings(repo)
    raw = "with raw data" if manifest["raw_data"] else f"without raw data ({len(manifest['raw_omitted'])} file(s) by hash)"
    shown = target.relative_to(repo) if target.is_relative_to(repo) else target
    print(f"Wrote {shown}: {len(manifest['files'])} file(s), {raw}.")
    return 0


def cmd_workspace(args):
    project = resolve_project(args)
    path = workspaces.write(project, find_repo_root(project))
    print(f"Wrote {path.relative_to(find_repo_root(project))}. Open it in a browser; it is view-only.")
    return 0


def build_parser(parser_class=cards.NutmegParser):
    parser = parser_class(
        prog="nutmeg",
        description="Record and check the claims, runs and figures in a nutmeg research project.",
    )
    parser.add_argument("--version", action="version", version=f"nutmeg {__version__}")
    parser.add_argument("--project", help="research project folder (default: the active project)")
    commands = parser.add_subparsers(dest="command", metavar="<command>", parser_class=parser_class)

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
    choose.add_argument("--after-results", metavar="NOTE",
                        help="this choice was made after the results were seen: say what it replaces (the method, not the person)")
    choose.set_defaults(handler=cmd_plan_choose)
    plan_commands.add_parser("check", help="check every choice has a reason").set_defaults(handler=cmd_plan_check)
    locker = plan_commands.add_parser("lock", help="lock the plan again for a new phase (it locks at the first run)")
    locker.add_argument("--reason", help="why, for example 'phase 2: opponent analysis'")
    locker.set_defaults(handler=cmd_plan_lock)
    plan_commands.add_parser("diff", help="show changes since the plan was locked").set_defaults(handler=cmd_plan_diff)

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

    figure = commands.add_parser("figure", help="register a chart's data and provenance")
    figure_commands = figure.add_subparsers(dest="figure_command", metavar="<action>")
    register = figure_commands.add_parser("register", help="write <name>.prov.json and print the footnote")
    register.add_argument("name", help="figure name, for example shot-map")
    register.add_argument("--data", help="CSV or JSON of the rows the chart plots (required)")
    register.add_argument("--source", action="append", default=[], help="a data source (repeat for each)")
    register.add_argument("--panel", action="append", default=[], help="the panel each --source feeds, in order")
    register.add_argument("--claims", help="claim IDs the chart shows, comma-separated")
    register.add_argument("--n", type=int, help="sample size (default: rows in --data)")
    register.add_argument("--season", help="competition and season, for example 'Premier League 2025/26'")
    register.add_argument("--filters", help="filters, for example 'min 900 minutes'")
    register.add_argument("--metric", help="the metric plotted")
    register.add_argument("--uncertainty", help="uncertainty shown, for example 'bootstrap 95%% CI'")
    register.add_argument("--run", help="the run that produced the data")
    register.add_argument("--image", help="the chart file")
    register.set_defaults(handler=cmd_figure_register)

    bundle = commands.add_parser("bundle", help="package the project for someone else to check")
    bundle.add_argument("--raw", choices=("yes", "no"),
                        help="include raw data (yes; check its licence) or list it by hash only (no); required")
    bundle.add_argument("--out", help="the zip file to write (default: research/<slug>/bundles/)")
    bundle.set_defaults(handler=cmd_bundle)

    publish = commands.add_parser("publish", help="publish the outputs (refuses while checks have open problems or the teach-back is missing)")
    publish.add_argument("--to", help="also copy the outputs to this folder in the repository")
    publish.set_defaults(handler=cmd_publish)

    commands.add_parser("workspace", help="write workspace.html: question, plan, ledger, figures, review queue"
                        ).set_defaults(handler=cmd_workspace)

    why = commands.add_parser("why", help="show a claim's value, evidence, reason and history")
    why.add_argument("claim_id")
    why.set_defaults(handler=cmd_why)

    commands.add_parser("trace", help="show inputs, runs, claims and figures as a tree").set_defaults(handler=cmd_trace)

    contest = commands.add_parser("contest", help="mark a claim disputed, with a note")
    contest.add_argument("claim_id")
    contest.add_argument("--note", required=True, help="what is wrong or unclear")
    contest.set_defaults(handler=cmd_contest)

    resolve = commands.add_parser("resolve", help="resolve a disputed claim, with a note")
    resolve.add_argument("claim_id")
    resolve.add_argument("--note", required=True, help="how it was resolved")
    resolve.set_defaults(handler=cmd_resolve)

    queue = commands.add_parser("queue", help="list runs waiting for review (run-then-review)")
    queue.add_argument("--done", metavar="RUN", help="mark a run as reviewed")
    queue.add_argument("--note", help="what you checked")
    queue.set_defaults(handler=cmd_queue)

    teachback = commands.add_parser("teachback", help="record that you can defend the work before publishing "
                                    "(kept in your own nutmeg folder, never in the repository)")
    teachback.add_argument("--shown", action="append", default=[],
                           help="a sentence from the user's own messages that shows they understand (repeat)")
    teachback.add_argument("--clarified", action="append", default=[],
                           help="a point cleared up along the way, for explainers (repeat)")
    teachback.add_argument("--claim", help="what the work claims, in the user's words")
    teachback.add_argument("--rests-on", help="what that rests on (the main assumption or evidence), in their words")
    teachback.add_argument("--would-change", help="what would change the answer, in their words")
    teachback.add_argument("--covers", help="claim IDs it covers (default: the headline claims, else the cited claims)")
    teachback.add_argument("--show", action="store_true", help="show the latest teach-back and what publish still needs")
    teachback.set_defaults(handler=cmd_teachback)

    explain = commands.add_parser("explain", help="write, render and list explainer pages the user can edit and share")
    explain_commands = explain.add_subparsers(dest="explain_command", metavar="<action>")
    explain_new = explain_commands.add_parser("new", help="start explainers/<slug>.md from a short outline")
    explain_new.add_argument("slug", help="short name, for example why-mendes")
    explain_new.add_argument("--title", help="the page title")
    explain_new.set_defaults(handler=cmd_explain_new)
    explain_render = explain_commands.add_parser("render", help="write a self-contained HTML page from each explainer")
    explain_render.add_argument("slug", nargs="?", help="one explainer (default: all)")
    explain_render.add_argument("--file", help="any Markdown file, also outside a research project")
    explain_render.set_defaults(handler=cmd_explain_render)
    explain_commands.add_parser("list", help="list explainers and declined topics").set_defaults(handler=cmd_explain_list)
    explain_decline = explain_commands.add_parser("decline", help="record that the user declined an explainer topic")
    explain_decline.add_argument("topic")
    explain_decline.set_defaults(handler=cmd_explain_decline)

    data = commands.add_parser("data", help="record where each input file came from (data/manifest.json)")
    data_commands = data.add_subparsers(dest="data_command", metavar="<action>")
    data_add = data_commands.add_parser("add", help="record a file's source, licence, hash and a short profile")
    data_add.add_argument("file")
    data_add.add_argument("--source", required=True, help="where it came from: a URL, a provider and product, or a person")
    data_add.add_argument("--licence", help="the licence or terms, if known")
    data_add.add_argument("--retrieved", help="when it was retrieved, for example 2026-10-09")
    data_add.add_argument("--note", help="anything else a reader should know")
    data_add.set_defaults(handler=cmd_data_add)
    data_commands.add_parser("list", help="list recorded files and whether they changed").set_defaults(handler=cmd_data_list)

    signoff = commands.add_parser("signoff", help="verify a claim with your name (a teammate's check)")
    signoff.add_argument("claim_id")
    signoff.add_argument("--note", help="what you checked")
    signoff.set_defaults(handler=cmd_signoff)

    config = commands.add_parser("config", help="show or set your persona and autonomy levels")
    config_commands = config.add_subparsers(dest="config_command", metavar="<action>")
    config_commands.add_parser("show", help="show the settings in force and why").set_defaults(handler=cmd_config_show)
    setter = config_commands.add_parser("set", help="change your user settings (the team floor still applies)")
    setter.add_argument("--persona", choices=sorted(PERSONAS))
    for stage in STAGES:
        setter.add_argument(f"--autonomy-{stage}", choices=LEVELS, dest=f"autonomy_{stage}")
    setter.add_argument("--run-then-review", choices=("yes", "no"))
    setter.add_argument("--name", help="your name for sign-offs and notes (default: git user.name)")
    setter.set_defaults(handler=cmd_config_set)

    claim = commands.add_parser("claim", help="add, list, show or withdraw ledger claims")
    claim_commands = claim.add_subparsers(dest="claim_command", metavar="<action>")

    add = claim_commands.add_parser("add", help="append a claim (JSON from --json or stdin)")
    add.add_argument("--json", help="the claim as a JSON object")
    add.add_argument("--kind", choices=KINDS, help="set the claim kind")
    add.add_argument("--headline", action="store_true", help="mark a headline claim (needs sign-off when the team requires it)")
    add.set_defaults(handler=cmd_claim_add)

    listing = claim_commands.add_parser("list", help="list the latest version of every claim")
    listing.set_defaults(handler=cmd_claim_list)

    show = claim_commands.add_parser("show", help="print one claim as JSON")
    show.add_argument("claim_id")
    show.set_defaults(handler=cmd_claim_show)

    withdraw = claim_commands.add_parser("withdraw", help="take a claim out of use, with a note")
    withdraw.add_argument("claim_id")
    withdraw.add_argument("--note", required=True, help="why, for example 'replaced by C23-C26'")
    withdraw.set_defaults(handler=cmd_claim_withdraw)

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
