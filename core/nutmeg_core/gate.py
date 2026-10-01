"""Decide what the PreToolUse gate does with a Bash command.

Inside an active research project the gate:

- shows a gate card and asks before a single `nutmeg run` (either form:
  `nutmeg run ...` or `python3 ".../core/nutmeg.py" run ...`, also behind
  wrappers such as `env`, `uv run` or `conda run`), and before `nutmeg
  publish` and `nutmeg bundle`;
- asks with a "not recorded" card before a direct interpreter or query call
  (python, python3, Rscript, duckdb, sqlite3, psql, bq);
- asks, with no card, before a compound command (chains, pipes, redirects,
  substitutions, comments) that contains either of those, and before any
  command it cannot read with certainty, because a card could not describe
  everything that will run;
- leaves every other command to Claude Code's normal permission flow.

Outside an active project it never decides anything. The gate parses nutmeg
arguments with the same parser as the nutmeg command, so the card describes
the run that will happen.
"""
import hashlib
import json
import os
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path

from . import config
from .redact import Redactor

INTERPRETERS = ("python", "python3", "Rscript", "duckdb", "sqlite3", "psql", "bq")
GATED_SUBCOMMANDS = ("run", "publish", "bundle")
OPERATORS = {";", "&&", "||", "|", "&", "(", ")", "<", ">", ">>", "<<", ">&", "<&", "|&", ";;", "&>"}
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

# Commands that start the next word as the real command, and their options that take a value.
SIMPLE_WRAPPERS = {
    "env": ("-u", "--unset", "-C", "--chdir"),
    "command": (),
    "exec": ("-a",),
    "nice": ("-n", "--adjustment"),
    "nohup": (),
    "time": ("-f", "--format", "-o", "--output"),
    "timeout": ("-s", "--signal", "-k", "--kill-after"),
    "caffeinate": ("-t", "-w"),
    "sudo": ("-u", "-g", "-C", "-D", "-h", "-p", "-r", "-t", "-U"),
    "xvfb-run": ("-a", "-n", "-s", "-f", "-e"),
}
RUNNERS = {
    "uv": ("--project", "--directory", "--with", "--with-requirements", "--with-editable", "--python", "-p",
           "--env-file", "--extra", "--group", "--package", "--from", "--index", "--index-url", "--only-group"),
    "uvx": ("--from", "--with", "--python", "-p"),
    "poetry": ("-C", "--directory", "-P", "--project"),
    "pipenv": (),
    "conda": ("-n", "--name", "-p", "--prefix", "--cwd"),
    "mamba": ("-n", "--name", "-p", "--prefix", "--cwd"),
    "micromamba": ("-n", "--name", "-p", "--prefix", "--cwd"),
    "pixi": ("-e", "--environment", "--manifest-path"),
    "pdm": ("-p", "--project"),
    "hatch": ("-e", "--env"),
    "rye": (),
}


@dataclass
class Parsed:
    """What a Bash command is, as far as the gate cares."""

    kind: str  # "nutmeg", "interpreter", "compound", "other"
    tokens: list = field(default_factory=list)
    subcommand: str = ""
    namespace: object = None  # the nutmeg command's parsed arguments
    env: dict = field(default_factory=dict)  # command-local VAR=value assignments
    reason: str = ""


def _is_python(token):
    return re.fullmatch(r"python(3(\.\d+)?)?", os.path.basename(token)) is not None


def _is_interpreter(token):
    return _is_python(token) or os.path.basename(token) in INTERPRETERS


def _is_nutmeg_word(token):
    return os.path.basename(token) == "nutmeg" or token.replace("\\", "/").endswith("core/nutmeg.py")


def _nutmeg_args(tokens):
    """The nutmeg arguments if `tokens` call the nutmeg command, else None."""
    if not tokens:
        return None
    if os.path.basename(tokens[0]) == "nutmeg":
        return tokens[1:]
    if _is_python(tokens[0]) and len(tokens) > 1 and tokens[1].replace("\\", "/").endswith("core/nutmeg.py"):
        return tokens[2:]
    return None


def _skip_options(rest, with_value):
    while rest and rest[0].startswith("-") and rest[0] != "-":
        option = rest.pop(0)
        if option == "--":
            break
        if "=" not in option and option in with_value and rest:
            rest.pop(0)
    return rest


def _strip_wrappers(tokens):
    """Drop VAR=value assignments and wrappers such as `env`, `uv run` or `conda run -n x`.

    Returns (remaining tokens, assignments, whether a wrapper was seen, whether it could be read).
    """
    rest, env, wrapped = list(tokens), {}, False
    while rest:
        word = rest[0]
        base = os.path.basename(word)
        if _ASSIGNMENT.match(word):
            name, value = word.split("=", 1)
            env[name] = value
            rest = rest[1:]
        elif base in SIMPLE_WRAPPERS:
            wrapped = True
            rest = rest[1:]
            if base == "env" and any(t in ("-S", "--split-string") or t.startswith("-S") for t in rest[:4]):
                return rest, env, wrapped, False
            rest = _skip_options(rest, SIMPLE_WRAPPERS[base])
            if base == "timeout" and rest:
                rest = rest[1:]  # the duration
        elif base in RUNNERS:
            wrapped = True
            rest = rest[1:]
            rest = _skip_options(rest, RUNNERS[base])
            if rest and rest[0] in ("run", "exec", "tool"):
                rest = rest[1:]
                if rest and rest[0] == "run":  # uv tool run
                    rest = rest[1:]
            rest = _skip_options(rest, RUNNERS[base])
        else:
            break
    return rest, env, wrapped, True


def _tokenise(text):
    lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""  # bash starts a comment only at the start of a word; checked below
    return list(lexer)


def parse(command):
    """Classify a Bash command string."""
    text = command.strip()
    try:
        tokens = _tokenise(text)
    except ValueError as exc:
        return Parsed("compound", reason=f"nutmeg could not read this command ({exc})")
    # A trailing 2>&1 only merges stderr into stdout; it does not change what runs.
    if tokens[-3:] == ["2", ">&", "1"]:
        tokens = tokens[:-3]

    gated_words = any(_is_interpreter(t) or _is_nutmeg_word(t) for t in tokens)
    unsafe = (
        "\n" in text
        or "`" in text
        or "$(" in text
        or "<(" in text
        or ">(" in text
        or any(t.startswith("#") for t in tokens)
        or any(t in OPERATORS or (t and set(t) <= set(";&|<>()")) for t in tokens)
    )
    if unsafe:
        if gated_words:
            return Parsed("compound", tokens=tokens,
                          reason="this command chains, redirects, substitutes or comments other commands; nothing has run yet")
        return Parsed("other", tokens=tokens)

    words, env, wrapped, readable = _strip_wrappers(tokens)
    if not readable:
        return Parsed("compound", tokens=tokens, env=env,
                      reason="nutmeg could not tell exactly what this wrapper runs; nothing has run yet")
    args = _nutmeg_args(words)
    if args is not None:
        return _parse_nutmeg(args, words, env)
    if words and _is_interpreter(words[0]):
        return Parsed("interpreter", tokens=words, env=env)
    if wrapped and any(_is_interpreter(w) or _is_nutmeg_word(w) for w in words):
        return Parsed("compound", tokens=tokens, env=env,
                      reason="nutmeg could not tell exactly what this wrapper runs; nothing has run yet")
    return Parsed("other", tokens=words, env=env)


def _parse_nutmeg(args, words, env):
    from . import card as cards
    from .cli import build_parser

    own, script_args = cards.split_script_args(args)
    parser = build_parser(parser_class=cards.RaisingParser)
    try:
        namespace = parser.parse_args(own)
    except cards.CardError as exc:
        return Parsed("nutmeg", tokens=words, subcommand="?", env=env, reason=str(exc))
    except SystemExit:  # --help or --version: prints and exits, runs nothing
        return Parsed("other", tokens=words, env=env)
    namespace.script_args = script_args
    return Parsed("nutmeg", tokens=words, subcommand=namespace.command or "", namespace=namespace, env=env)


@dataclass
class Decision:
    decision: str  # "ask" or "allow"
    reason: str
    card: dict = None

    def hook_output(self):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": self.decision,
                "permissionDecisionReason": self.reason,
            }
        }


def pending_key(run_key):
    """A stable key for a run's resolved arguments, shared by the gate and `nutmeg run`."""
    blob = json.dumps(run_key, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _target_project(parsed, cwd, active):
    """The project the nutmeg command will use: --project, then NUTMEG_PROJECT, then the active one."""
    chosen = getattr(parsed.namespace, "project", None) or parsed.env.get("NUTMEG_PROJECT")
    if chosen:
        return (Path(cwd) / Path(chosen).expanduser()).resolve()
    return active


def decide(command, repo_root, project, cwd=None):
    """Return a Decision, or None to leave the command to normal permissions."""
    if project is None:
        return None
    decision = _decide(command, repo_root, project, Path(cwd or repo_root))
    if decision is not None:
        decision.reason = Redactor.for_repo(repo_root).text(decision.reason)
    return decision


def _decide(command, repo_root, project, cwd):
    from . import card as cards

    parsed = parse(command)
    if parsed.kind == "compound":
        return Decision(
            "ask",
            "nutmeg research gate: " + parsed.reason + ". nutmeg cannot show what it will run or record it. "
            "Approve only if you have read the whole command; to record a run, call `nutmeg run <file>` on its own.",
        )
    if parsed.kind == "interpreter":
        built = cards.build_direct_card(parsed.tokens, repo_root, project, cwd)
        return Decision("ask", cards.render_text(built), built)
    if parsed.kind != "nutmeg":
        return None
    if parsed.subcommand == "?":
        return Decision("ask", f"nutmeg research gate: {parsed.reason}. nutmeg will refuse this command; nothing has run yet.")
    if parsed.subcommand not in GATED_SUBCOMMANDS:
        return None

    target = _target_project(parsed, cwd, project)
    if target is None or not Path(target).is_dir():
        return Decision("ask", f"nutmeg research gate: research project not found ({target}); nutmeg will refuse this command.")
    try:
        settings = config.load_effective(repo_root)
    except config.ConfigError as exc:
        return Decision("ask", f"nutmeg research gate: the team or user config is broken ({exc}), so the strictest "
                               "gate applies. Fix the config file, then try again.")
    changed = settings_changed(repo_root, settings)
    if parsed.subcommand == "run":
        run_args = cards.normalise_run_args(parsed.namespace)
        built = cards.build_run_card(run_args, repo_root, target, cwd, approved=settings["approved_services"])
        level = settings["levels"]["run"]
        allow = settings["run_then_review"] and not changed and not built["problems"]
        built["review"] = "queued" if allow else "asked"
        cards.save_pending(target, pending_key(cards.run_key(run_args, repo_root, cwd)), built)
        text = cards.render_text(built)
        if changed:
            text = changed + "\n\n" + text
        elif level == "L1":
            text = ("Your run level is L1 (suggest): nutmeg shows the card and you run the code yourself. "
                    "Approve only if you want nutmeg to run it now.\n\n" + text)
        if allow:
            return Decision("allow", "run-then-review: this run goes ahead and its card waits in the review queue "
                                     "(`nutmeg queue`).\n\n" + text, built)
        return Decision("ask", text, built)
    decision = _decide_release(parsed, repo_root, target)
    if changed:
        decision.reason = changed + "\n\n" + decision.reason
    return decision


SEEN_FILE = ".config-seen"


def settings_changed(repo_root, settings):
    """A message if the team or user config changed since the last gate, else ''. Records the change."""
    from .project import active_project, append_receipt, ensure_research_files, research_root

    ensure_research_files(repo_root)
    seen_path = research_root(repo_root) / SEEN_FILE
    current = config.config_hash(repo_root)
    try:
        previous = seen_path.read_text(encoding="utf-8").strip()
    except OSError:
        previous = ""
    if previous == current:
        return ""
    try:
        seen_path.write_text(current + "\n", encoding="utf-8")
    except OSError:
        pass
    if not previous:
        return ""  # first gate on this machine: nothing to compare with
    levels = ", ".join(f"{stage} {settings['levels'][stage]}" for stage in config.STAGES)
    project = active_project(repo_root)
    if project is not None:
        append_receipt(project, "gate_settings_changed", levels=settings["levels"],
                       run_then_review=settings["run_then_review"])
    return (f"Gate settings changed since the last gate (team or user config). Now: {levels}; "
            f"run-then-review {settings['reasons']['run_then_review']}. This step asks again.")


def _decide_release(parsed, repo_root, target):
    """Publish and bundle: show what will be released."""
    label = Path(target).relative_to(repo_root).as_posix() if Path(target).is_relative_to(repo_root) else str(target)
    if parsed.subcommand == "bundle":
        from . import bundle as bundling
        return Decision("ask", bundling.render_preview(target, repo_root, parsed.namespace, label))
    from . import publish as publishing
    return Decision("ask", publishing.render_preview(publishing.preview(target, repo_root), label))
