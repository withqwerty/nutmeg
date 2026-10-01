"""Team and user configuration.

The team file `.nutmeg/team.json` lives in the team's repository and changes
through normal review. It sets the floor; user config can only be stricter.
"""
import json
import os
import subprocess
from pathlib import Path

TEAM_FILE = Path(".nutmeg") / "team.json"

DATA_IN_GIT_POLICIES = ("yes", "no", "ask")


class ConfigError(ValueError):
    pass


def load_team(repo_root):
    """The team config as a dict, or {} when the repo has none."""
    path = Path(repo_root) / TEAM_FILE
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"{TEAM_FILE} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        raise ConfigError(f"{TEAM_FILE} must hold a JSON object")
    return data


def data_in_git_policy(team):
    """The team's data-in-git policy: "yes", "no" or "ask" (the default)."""
    policy = team.get("data_in_git", "ask")
    if policy not in DATA_IN_GIT_POLICIES:
        raise ConfigError(f"data_in_git in {TEAM_FILE} must be one of {', '.join(DATA_IN_GIT_POLICIES)}")
    return policy


def user_name(repo_root):
    """The person running nutmeg: git user.name, else $USER, else "unknown"."""
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
