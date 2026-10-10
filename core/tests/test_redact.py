import pytest

from nutmeg_core.redact import PLACEHOLDER, Redactor, inside_repo, parse_env_file


def test_env_value_is_replaced(tmp_path):
    (tmp_path / ".env").write_text('SPORTMONKS_API_TOKEN="abc123secretvalue"\n# comment\nDEBUG=1\n')
    redactor = Redactor.for_repo(tmp_path, environ={})
    assert redactor.text("token is abc123secretvalue here") == f"token is {PLACEHOLDER} here"
    # Short values such as DEBUG=1 are not treated as secrets.
    assert redactor.text("DEBUG=1") == "DEBUG=1"


def test_credentials_file_and_environment_are_read(tmp_path):
    (tmp_path / ".nutmeg.credentials.local").write_text("export OPTA_KEY=opta-key-998877\nwyscout: wy-secret-445566\n")
    redactor = Redactor.for_repo(tmp_path, environ={"STATSBOMB_PASSWORD": "sb-pass-000111", "HOME": "/Users/someone"})
    text = redactor.text("opta-key-998877 wy-secret-445566 sb-pass-000111 /Users/someone")
    assert text == f"{PLACEHOLDER} {PLACEHOLDER} {PLACEHOLDER} /Users/someone"


def test_url_token_parameter_is_replaced():
    redactor = Redactor()
    url = "https://api.sportmonks.com/v3/football/fixtures?api_token=XYZ987&include=events"
    assert redactor.text(url) == f"https://api.sportmonks.com/v3/football/fixtures?api_token={PLACEHOLDER}&include=events"
    assert redactor.text("https://x.io/a?client_secret=s3cr3t#frag") == f"https://x.io/a?client_secret={PLACEHOLDER}#frag"
    assert redactor.text("https://x.io/a?season=2025") == "https://x.io/a?season=2025"


def test_longer_secret_is_masked_whole():
    redactor = Redactor(["abcdef", "abcdef123456"])
    assert redactor.text("abcdef123456") == PLACEHOLDER


def test_obj_redacts_nested_strings():
    redactor = Redactor(["secret-value-1"])
    data = {"cmd": ["curl", "-H", "Bearer secret-value-1"], "n": 3, "meta": {"note": "secret-value-1"}}
    assert redactor.obj(data) == {"cmd": ["curl", "-H", f"Bearer {PLACEHOLDER}"], "n": 3, "meta": {"note": PLACEHOLDER}}


def test_parse_env_file_missing_returns_empty(tmp_path):
    assert parse_env_file(tmp_path / "nope") == {}


def test_inside_repo(tmp_path):
    (tmp_path / "data").mkdir()
    assert inside_repo("data/events.csv", tmp_path) == (tmp_path / "data" / "events.csv").resolve()
    with pytest.raises(ValueError, match="outside the repository"):
        inside_repo("~/.aws/credentials", tmp_path)
    with pytest.raises(ValueError):
        inside_repo("../elsewhere.csv", tmp_path)
