"""Decide what the PreToolUse gate does with a Bash command.

Inside an active research project the gate:

- shows a gate card and asks before a single `nutmeg run` (either form:
  `nutmeg run ...` or `python3 ".../core/nutmeg.py" run ...`);
- asks with a "not recorded" card before a direct interpreter or query call
  (python, python3, Rscript, duckdb, sqlite3, psql, bq);
- asks, with no card, before a compound command that contains either of
  those, because the card could not describe everything that will run;
- leaves every other command to Claude Code's normal permission flow.

Outside an active project it never decides anything.
"""
import hashlib
import json
import os
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path

INTERPRETERS = ("python", "python3", "Rscript", "duckdb", "sqlite3", "psql", "bq")
GATED_SUBCOMMANDS = ("run",)
# Runners that start the next word as the real command.
WRAPPERS = ("uv", "poetry", "pipenv", "conda", "env", "time", "nohup")
OPERATORS = {";", "&&", "||", "|", "&", "(", ")", "<", ">", ">>", "<<", ">&", "<&", "|&", ";;", "&>"}


@dataclass
class Parsed:
    """What a Bash command is, as far as the gate cares."""

    kind: str  # "nutmeg", "interpreter", "compound", "other"
    tokens: list = field(default_factory=list)
    subcommand: str = ""
    args: list = field(default_factory=list)  # nutmeg args after the global options
    global_args: list = field(default_factory=list)
    reason: str = ""


def _is_python(token):
    return re.fullmatch(r"python(3(\.\d+)?)?", os.path.basename(token)) is not None


def _nutmeg_args(tokens):
    """The nutmeg arguments if `tokens` call the nutmeg command, else None."""
    if not tokens:
        return None
    head = tokens[0]
    if os.path.basename(head) == "nutmeg":
        return tokens[1:]
    if _is_python(head) and len(tokens) > 1 and tokens[1].replace("\\", "/").endswith("core/nutmeg.py"):
        return tokens[2:]
    return None


def _strip_wrappers(tokens):
    """Drop leading VAR=value assignments and runners such as `uv run`."""
    rest = list(tokens)
    while rest:
        word = rest[0]
        if "=" in word and not word.startswith("=") and word.split("=", 1)[0].replace("_", "").isalnum():
            rest = rest[1:]
        elif word in WRAPPERS:
            rest = rest[2:] if len(rest) > 1 and rest[1] in ("run", "exec") else rest[1:]
        else:
            break
    return rest


def _split_global(args):
    """Split nutmeg's global options (--project X) from the subcommand."""
    head = []
    rest = list(args)
    while rest and rest[0].startswith("--"):
        option = rest.pop(0)
        head.append(option)
        if option == "--project" and rest:
            head.append(rest.pop(0))
    return head, rest


def parse(command):
    """Classify a Bash command string."""
    text = command.strip()
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError as exc:
        return Parsed("compound", reason=f"nutmeg could not read this command ({exc})")
    # A trailing 2>&1 only merges stderr into stdout; it does not change what runs.
    if tokens[-3:] == ["2", ">&", "1"]:
        tokens = tokens[:-3]

    def mentions_gated(words):
        return any(_is_python(w) or os.path.basename(w) in INTERPRETERS or os.path.basename(w) == "nutmeg"
                   or w.endswith("core/nutmeg.py") for w in words)

    multi_line = "\n" in text
    substitution = "`" in text or "$(" in text
    has_operator = any(t in OPERATORS or (t and set(t) <= set(";&|<>()")) for t in tokens)
    if multi_line or substitution or has_operator:
        if mentions_gated(tokens) or "nutmeg.py" in text:
            return Parsed("compound", tokens=tokens,
                          reason="this command chains, redirects or substitutes other commands; nothing has run yet")
        return Parsed("other", tokens=tokens)

    words = _strip_wrappers(tokens)
    args = _nutmeg_args(words)
    if args is not None:
        global_args, rest = _split_global(args)
        sub = rest[0] if rest else ""
        return Parsed("nutmeg", tokens=words, subcommand=sub, args=rest[1:], global_args=global_args)
    if words and (_is_python(words[0]) or os.path.basename(words[0]) in INTERPRETERS):
        return Parsed("interpreter", tokens=words)
    return Parsed("other", tokens=words)


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


def pending_key(run_args):
    """A stable key for a run's arguments, shared by the gate and `nutmeg run`."""
    blob = json.dumps(run_args, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def decide(command, repo_root, project, cwd=None):
    """Return a Decision, or None to leave the command to normal permissions."""
    from . import card as cards  # local import keeps the parser light

    if project is None:
        return None
    cwd = Path(cwd or repo_root)
    parsed = parse(command)

    if parsed.kind == "compound":
        return Decision(
            "ask",
            "nutmeg research gate: " + parsed.reason + ", so nutmeg cannot show what it will run or record it. "
            "Approve only if you have read the whole command; to record a run, call `nutmeg run <file>` on its own.",
        )
    if parsed.kind == "interpreter":
        built = cards.build_direct_card(parsed.tokens, repo_root, project, cwd)
        return Decision("ask", cards.render_text(built), built)
    if parsed.kind == "nutmeg" and parsed.subcommand in GATED_SUBCOMMANDS:
        try:
            run_args = cards.parse_run_args(parsed.args)
        except cards.CardError as exc:
            return Decision("ask", f"nutmeg research gate: {exc}. nutmeg run will refuse this command.")
        target = cards.project_from_global(parsed.global_args, cwd) or project
        built = cards.build_run_card(run_args, repo_root, target, cwd)
        cards.save_pending(target, pending_key(cards.run_key(run_args, repo_root, cwd)), built)
        return Decision("ask", cards.render_text(built), built)
    return None
