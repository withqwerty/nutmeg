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
        elif base in SIMPLE_WRAPPERS or base in RUNNERS:
            wrapped = True
            options = SIMPLE_WRAPPERS.get(base, RUNNERS.get(base))
            rest = rest[1:]
            # A wrapper that splits a string into a command, or changes the directory, runs
            # something the card cannot describe exactly.
            rest, readable = _wrapper_options(rest, options, base)
            if not readable:
                return rest, env, wrapped, False
            if base in RUNNERS and rest and rest[0] in ("run", "exec", "tool"):
                rest = rest[1:]
                if rest and rest[0] == "run":  # uv tool run
                    rest = rest[1:]
                rest, readable = _wrapper_options(rest, options, base)
                if not readable:
                    return rest, env, wrapped, False
            if base == "timeout" and rest:
                rest = rest[1:]  # the duration
        else:
            break
    return rest, env, wrapped, True


# Options that make a wrapper split a string into a command or change the working directory.
UNREADABLE_BY_WRAPPER = {
    "env": ("-S", "--split-string", "-C", "--chdir"),
    "sudo": ("-D", "--chdir", "-s", "--shell", "-i", "--login"),
    "uv": ("--directory",),
    "uvx": ("--directory",),
    "poetry": ("-C", "--directory"),
    "conda": ("--cwd",),
    "mamba": ("--cwd",),
    "micromamba": ("--cwd",),
}


def _unreadable_option(token, wrapper):
    names = UNREADABLE_BY_WRAPPER.get(wrapper, ())
    if token.split("=", 1)[0] in names:
        return True
    # Attached short options: -Csub, -Spython3 ...
    return any(len(n) == 2 and token.startswith(n) and len(token) > 2 and not token.startswith("--") for n in names)


def _wrapper_options(rest, with_value, wrapper=""):
    """Skip a wrapper's own options. Returns (the rest, whether nutmeg can read what runs)."""
    rest = list(rest)
    while rest and rest[0].startswith("-") and rest[0] != "-":
        option = rest.pop(0)
        if option == "--":
            break
        if _unreadable_option(option, wrapper):
            return rest, False
        if "=" not in option and option in with_value and rest:
            rest.pop(0)
    return rest, True



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

    unsafe = (
        "\n" in text
        or "`" in text
        or "$(" in text
        or "<(" in text
        or ">(" in text
        or any(t.startswith("#") for t in tokens)
        or any(_is_operator(t) for t in tokens)
    )
    if unsafe:
        segments = []
        for line in text.splitlines() or [text]:
            try:
                segments += _segments(_tokenise(line))
            except ValueError:
                segments.append(tokens)  # a quote spans lines: judge the whole command
        segments = segments or _segments(tokens)
        if any(_executes_gated(seg) for seg in segments) or ("`" in text and any(_mentions_gated(t) for t in tokens)):
            return Parsed("compound", tokens=tokens,
                          reason="this command chains, redirects, substitutes or comments other commands; nothing has run yet")
        return Parsed("other", tokens=tokens)

    while tokens and tokens[0] in SHELL_KEYWORDS:  # "! python3 a.py" runs python3
        tokens = tokens[1:]
    bare = _drop_assignments(tokens)
    head = os.path.basename(bare[0]) if bare else ""
    if (head in SHELLS or head in EXECUTORS) and any(_mentions_gated(t) for t in bare[1:]):
        return Parsed("compound", tokens=tokens,
                      reason=f"`{head}` runs a command from a string, a file or its input that nutmeg cannot inspect; "
                             "nothing has run yet")
    words, env, wrapped, readable = _strip_wrappers(tokens)
    if not readable:
        splits = any(_unreadable_option(t, w) and t.lstrip("-")[:1] == "S" or t.startswith("--split-string")
                     for t in tokens for w in ("env",))
        if splits or any(_mentions_gated(t) for t in tokens):
            return Parsed("compound", tokens=tokens, env=env,
                          reason="this wrapper changes the directory or splits a string into a command, so nutmeg "
                                 "cannot tell exactly what runs; nothing has run yet")
        return Parsed("other", tokens=tokens, env=env)
    args = _nutmeg_args(words)
    if args is not None:
        return _parse_nutmeg(args, words, env)
    if words and _is_interpreter(words[0]):
        return Parsed("interpreter", tokens=words, env=env)
    if wrapped and (_executes_gated(words) or any(_is_interpreter(w) or _is_nutmeg_word(w) for w in words)):
        return Parsed("compound", tokens=tokens, env=env,
                      reason="this command starts an interpreter or nutmeg in a way nutmeg cannot inspect; nothing has run yet")
    return Parsed("other", tokens=words, env=env)


# Commands that run other commands from a string, a file or their input.
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "mksh", "ash", "csh", "tcsh", "fish", "pwsh", "powershell", "eval",
          "source", ".", "su", "script", "busybox", "expect", "osascript"}
EXECUTORS = {"find", "xargs", "parallel", "watch", "entr", "flock", "stdbuf", "ionice", "taskset", "doas", "chronic",
             "unbuffer"}
_GATED_TEXT = re.compile(r"(?<![\w.-])(python(3(\.\d+)?)?|Rscript|duckdb|sqlite3|psql|bq|nutmeg(\.py)?)(?![\w-])")


def _is_operator(token):
    return token in OPERATORS or bool(token and set(token) <= set(";&|<>()"))


def _segments(tokens):
    """Split tokens into simple commands at operators."""
    segments, current = [], []
    for token in tokens:
        if _is_operator(token):
            if current:
                segments.append(current)
            current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments


# Shell words that can come before the command itself: if true; then python3 a.py; fi
SHELL_KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}", "time", "coproc", "fi",
                  "done", "esac"}


def _drop_assignments(tokens):
    rest = list(tokens)
    while rest and (_ASSIGNMENT.match(rest[0]) or rest[0] in SHELL_KEYWORDS):
        rest = rest[1:]
    return rest


def _executes_gated(words):
    """Whether a simple command would start an interpreter or nutmeg (not just mention one in its arguments)."""
    rest = _drop_assignments(words)
    if not rest:
        return False
    if _is_interpreter(rest[0]) or _is_nutmeg_word(rest[0]):
        return True
    head = os.path.basename(rest[0])
    if head in SHELLS or head in EXECUTORS or head in SIMPLE_WRAPPERS or head in RUNNERS:
        return any(_mentions_gated(t) for t in rest[1:])
    return False


def _mentions_gated(token):
    return bool(_GATED_TEXT.search(token))


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
    chosen = (getattr(parsed.namespace, "project", None) or parsed.env.get("NUTMEG_PROJECT")
              or os.environ.get("NUTMEG_PROJECT"))
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
    from .project import find_repo_root
    # The command runs in the target project's repository, with that repository's team floor.
    repo_root = find_repo_root(target)
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


def acknowledge_settings(repo_root):
    """Record the current config as approved. Called by run, publish and bundle, which only
    run after the user approved the gate (or under run-then-review with unchanged settings)."""
    from .project import ensure_research_files, research_root

    ensure_research_files(repo_root)
    try:
        (research_root(repo_root) / SEEN_FILE).write_text(config.config_hash(repo_root) + "\n", encoding="utf-8")
    except OSError:
        pass


def settings_changed(repo_root, settings):
    """A message if the team or user config changed since the last approved step, else ''.

    The new settings count as acknowledged only once an approved step runs, so denying the
    prompt and retrying asks again.
    """
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
    if not previous:
        acknowledge_settings(repo_root)
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
