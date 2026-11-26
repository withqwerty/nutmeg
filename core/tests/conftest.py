import json
import os
import subprocess
from pathlib import Path

import pytest


def set_user_hooks(on):
    """Turn the research hooks on or off in the test's user config (they are off by default)."""
    path = Path(os.environ["NUTMEG_USER_CONFIG"])
    current = json.loads(path.read_text()) if path.exists() else {}
    current["hooks"] = on
    path.write_text(json.dumps(current))


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """An empty git repository as the working directory."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test Analyst"], check=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NUTMEG_PROJECT", raising=False)
    monkeypatch.setenv("NUTMEG_USER_CONFIG", str(tmp_path / ".no-user-config.json"))
    return tmp_path
