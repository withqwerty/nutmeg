"""Team and user configuration.

The team file `.nutmeg/team.json` lives in the team's repository and changes
through normal review. It sets the floor. The user file (`nutmeg/user.json`
in the user's config folder, written by setup) can only be stricter: for
every setting the stricter of the two applies. docs/team-config.md
documents every key.

Autonomy levels, per stage (plan, run, publish):
    L1 suggest: nutmeg shows the card and the user runs things.
    L2 draft: nutmeg asks before each run and each publish.
    L3 execute with checkpoints: as L2, but with run_then_review a run
       goes ahead and its card waits in the review queue.
A lower level is stricter.
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path

TEAM_FILE = Path(".nutmeg") / "team.json"
USER_FILE_ENV = "NUTMEG_USER_CONFIG"

DATA_IN_GIT_POLICIES = ("yes", "no", "ask")
LEVELS = ("L1", "L2", "L3")
STAGES = ("plan", "run", "publish")
PERSONAS = {
    # Persona defaults from the plan (R16): fanalysts L3, club data scientists L2.
    "fanalyst": {"plan": "L3", "run": "L3", "publish": "L3"},
    "club": {"plan": "L2", "run": "L2", "publish": "L2"},
    "company": {"plan": "L2", "run": "L2", "publish": "L2"},
}
DEFAULT_PERSONA = "club"


class ConfigError(ValueError):
    pass


def _read_json(path, label):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"{label} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        raise ConfigError(f"{label} must hold a JSON object")
    return data


def load_team(repo_root):
    """The team config as a dict, or {} when the repo has none. Raises ConfigError for a bad file."""
    path = Path(repo_root) / TEAM_FILE
    if not path.exists():
        return {}
    team = _read_json(path, TEAM_FILE)
    validate_team(team)
    return team


TEAM_TYPES = {
    "max_autonomy": dict, "allow_run_then_review": bool, "persona_default": str, "approved_services": list,
    "approved_ai_providers": list, "licences": dict, "data_in_git": str, "signoff": dict,
}


USER_KEYS = ("persona", "autonomy_plan", "autonomy_run", "autonomy_publish", "run_then_review", "name")


def unknown_keys(team, user):
    """Keys nutmeg does not read, so a typo never passes silently. Returns warning strings."""
    out = []
    for key in sorted(set(team) - set(TEAM_TYPES)):
        out.append(f"{TEAM_FILE} has an unknown key \"{key}\"; nutmeg ignores it "
                   f"(known keys: {', '.join(TEAM_TYPES)})")
    for key in sorted(set(user) - set(USER_KEYS)):
        hint = (" (use autonomy_plan, autonomy_run and autonomy_publish)" if key == "autonomy"
                else f" (known keys: {', '.join(USER_KEYS)})")
        out.append(f"the user config has an unknown key \"{key}\"; nutmeg ignores it{hint}")
    return out


def validate_team(team):
    """Check every known key has the right type, so a malformed value never silently weakens a rule."""
    for key, kind in TEAM_TYPES.items():
        if key in team and not isinstance(team[key], kind):
            raise ConfigError(f"{key} in {TEAM_FILE} must be a {kind.__name__}")
    signoff = team.get("signoff", {})
    if "required" in signoff and not isinstance(signoff["required"], bool):
        raise ConfigError(f"signoff.required in {TEAM_FILE} must be true or false")
    for key in ("approved_services", "approved_ai_providers"):
        if not all(isinstance(v, str) for v in team.get(key, [])):
            raise ConfigError(f"{key} in {TEAM_FILE} must list strings")


def user_config_path():
    if os.environ.get(USER_FILE_ENV):
        return Path(os.environ[USER_FILE_ENV]).expanduser()
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return Path(base) / "nutmeg" / "user.json"


def load_user():
    path = user_config_path()
    if not path.exists():
        return {}
    return _read_json(path, path)


def save_user(values):
    """Write the user config (setup only). Unknown keys are kept."""
    path = user_config_path()
    current = load_user() if path.exists() else {}
    current.update(values)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    return path


def data_in_git_policy(team):
    """The team's data-in-git policy: "yes", "no" or "ask" (the default)."""
    policy = team.get("data_in_git", "ask")
    if policy not in DATA_IN_GIT_POLICIES:
        raise ConfigError(f"data_in_git in {TEAM_FILE} must be one of {', '.join(DATA_IN_GIT_POLICIES)}")
    return policy


def _level(value, where):
    if value is None:
        return None
    if value not in LEVELS:
        raise ConfigError(f"{where} must be one of {', '.join(LEVELS)}")
    return value


def _stricter(a, b):
    """The stricter (lower) of two levels; None means "no limit"."""
    levels = [x for x in (a, b) if x is not None]
    return min(levels, key=LEVELS.index) if levels else None


def effective(team, user):
    """Merge team and user config. Returns a dict with the levels and the reason for each."""
    persona = user.get("persona") or team.get("persona_default") or DEFAULT_PERSONA
    if persona not in PERSONAS:
        raise ConfigError(f"persona must be one of {', '.join(PERSONAS)}")
    team_max = team.get("max_autonomy") or {}
    if not isinstance(team_max, dict):
        raise ConfigError(f"max_autonomy in {TEAM_FILE} must map stages to levels")
    out = {"persona": persona, "levels": {}, "reasons": {}}
    for stage in STAGES:
        own = _level(user.get(f"autonomy_{stage}"), f"autonomy_{stage} in the user config")
        chosen = own or PERSONAS[persona][stage]
        floor = _level(team_max.get(stage), f"max_autonomy.{stage} in {TEAM_FILE}")
        level = _stricter(chosen, floor)
        out["levels"][stage] = level
        out["reasons"][stage] = (f"team limit {floor} applies (you chose {chosen})"
                                 if floor and level == floor and floor != chosen
                                 else "your setting" if own else f"{persona} default")
    team_allows = team.get("allow_run_then_review", True)
    wants = bool(user.get("run_then_review", False))
    out["run_then_review"] = wants and bool(team_allows) and out["levels"]["run"] == "L3"
    if wants and not team_allows:
        out["reasons"]["run_then_review"] = f"the team config ({TEAM_FILE}) does not allow run-then-review"
    elif wants and out["levels"]["run"] != "L3":
        out["reasons"]["run_then_review"] = f"run-then-review needs run level L3; yours is {out['levels']['run']}"
    else:
        out["reasons"]["run_then_review"] = "on" if out["run_then_review"] else "off"
    out["approved_services"] = [str(s).lower() for s in team.get("approved_services", [])]
    out["approved_ai_providers"] = list(team.get("approved_ai_providers", []))
    out["licences"] = dict(team.get("licences", {}))
    signoff = team.get("signoff") or {}
    out["signoff_required"] = bool(signoff.get("required", False))
    out["data_in_git"] = data_in_git_policy(team)
    return out


def team_signoff_required(repo_root):
    """The team's sign-off rule, read from the team file alone (a broken user config cannot turn it off)."""
    return bool(load_team(repo_root).get("signoff", {}).get("required", False))


def load_effective(repo_root):
    team, user = load_team(repo_root), load_user()
    settings = effective(team, user)
    settings["warnings"] = unknown_keys(team, user)
    return settings


def config_hash(repo_root):
    """A hash of the team and user config files, to notice changes between gates."""
    digest = hashlib.sha256()
    for path in (Path(repo_root) / TEAM_FILE, user_config_path()):
        digest.update(str(path).encode("utf-8"))
        digest.update(path.read_bytes() if path.is_file() else b"<none>")
    return digest.hexdigest()[:16]


def service_status(host, approved):
    """'approved by team' or 'not on the team list' (or '' when the team lists none)."""
    if not approved:
        return ""
    host = host.lower()
    ok = any(host == a or host.endswith("." + a) for a in approved)
    return "approved by team" if ok else "not on the team list"


def user_name(repo_root):
    """The person running nutmeg: user config name, git user.name, $USER, else "unknown"."""
    try:
        name = load_user().get("name")
    except ConfigError:
        name = None
    if name:
        return name
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "config", "user.name"],
            capture_output=True, text=True, timeout=5,
        )
        name = result.stdout.strip()
        if name:
            return name
    except (OSError, subprocess.SubprocessError):
        pass
    return os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
