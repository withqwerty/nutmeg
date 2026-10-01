import subprocess

import pytest


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """An empty git repository as the working directory."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test Analyst"], check=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NUTMEG_PROJECT", raising=False)
    monkeypatch.setenv("NUTMEG_USER_CONFIG", str(tmp_path / ".no-user-config.json"))
    return tmp_path
