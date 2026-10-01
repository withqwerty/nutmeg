"""Keep API keys and tokens out of everything nutmeg writes.

Run records, gate cards, the workspace page and bundles pass their text
through `Redactor` before it reaches disk. Secret values come from `.env`,
`.nutmeg.credentials.local` and key-like environment variables; URL query
parameters named like a token, key or secret are masked whatever their value.
"""
import os
import re
from pathlib import Path

PLACEHOLDER = "[REDACTED]"

SECRET_FILES = (".env", ".nutmeg.credentials.local")

# Environment variables whose names look like credentials.
_SECRET_NAME = re.compile(r"(TOKEN|KEY|SECRET|PASSWORD|PASSWD|CREDENTIAL)", re.IGNORECASE)

# ?api_token=abc, &key=abc, &client_secret=abc ...
_URL_PARAM = re.compile(
    r"([?&][A-Za-z0-9_.-]*(?:token|key|secret|password|signature)[A-Za-z0-9_.-]*=)[^&\s#\"']+",
    re.IGNORECASE,
)

# Short values (for example "1" or "true") would mask ordinary text.
MIN_SECRET_LENGTH = 6


def parse_env_file(path):
    """Return the values set in a KEY=VALUE (or KEY: VALUE) file."""
    values = {}
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return values
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        for sep in ("=", ":"):
            if sep in line:
                name, value = line.split(sep, 1)
                break
        else:
            continue
        value = _env_value(value.strip())
        if name.strip() and value:
            values[name.strip()] = value
    return values


def _env_value(raw):
    """A dotenv value without its quotes or trailing comment. Nothing is evaluated."""
    if raw[:1] in ("'", '"'):
        quote = raw[0]
        end = raw.find(quote, 1)
        while quote == '"' and end > 0 and raw[end - 1] == "\\":
            end = raw.find(quote, end + 1)
        value = raw[1:end] if end > 0 else raw[1:]
        return value.replace('\\"', '"') if quote == '"' else value
    # Unquoted: a comment starts at " #".
    for marker in (" #", "\t#"):
        if marker in raw:
            raw = raw.split(marker, 1)[0]
    return raw.strip()


class Redactor:
    """Replace known secret values and secret-like URL parameters."""

    def __init__(self, secrets=()):
        unique = {s for s in secrets if s and len(s) >= MIN_SECRET_LENGTH}
        # Longest first, so a secret that contains another is masked whole.
        self.secrets = sorted(unique, key=len, reverse=True)

    @classmethod
    def for_repo(cls, repo_root, environ=None):
        environ = os.environ if environ is None else environ
        secrets = []
        for name in SECRET_FILES:
            secrets.extend(parse_env_file(Path(repo_root) / name).values())
        secrets.extend(v for k, v in environ.items() if _SECRET_NAME.search(k))
        return cls(secrets)

    def text(self, value):
        if not isinstance(value, str) or not value:
            return value
        for secret in self.secrets:
            value = value.replace(secret, PLACEHOLDER)
        return _URL_PARAM.sub(lambda m: m.group(1) + PLACEHOLDER, value)

    def obj(self, value):
        """Redact every string inside a JSON-like value."""
        if isinstance(value, str):
            return self.text(value)
        if isinstance(value, dict):
            return {k: self.obj(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.obj(v) for v in value]
        return value


def inside_repo(path, repo_root):
    """Return the resolved path if it is inside the repo, else raise ValueError."""
    root = Path(repo_root).resolve()
    resolved = (root / Path(path).expanduser()).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"{path} is outside the repository ({root}); nutmeg only reads files inside it")
    return resolved
