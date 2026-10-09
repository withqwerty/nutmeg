"""Exec grader: the run made a shareable explainer page the user can edit.

Passes when the run left (1) an HTML page that loads nothing from the network (no remote scripts, styles,
fonts or images), (2) only decimals that are values in the project's claim ledger, (3) a way for a reader to
trace the numbers: the project's claim IDs (C1, C2, ...) or run ID (R1) on the page, and (4) a clean
`nutmeg check`. How the user edits the page is left to the llm grader: a Markdown source, an edit mode in the
page, or plain HTML are all fine.
"""
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

work = Path(sys.argv[1])
plugin = Path(__file__).resolve().parents[3]
fixture = plugin / "evals" / "_fixtures" / "signings-xt"
known = {p.relative_to(fixture).as_posix() for p in fixture.rglob("*") if p.is_file()}


def new_files(suffixes):
    out = []
    for p in work.rglob("*"):
        rel = p.relative_to(work).as_posix()
        if (p.is_file() and p.suffix.lower() in suffixes and rel not in known
                and not rel.startswith((".git/", ".claude/")) and "/runs/" not in rel):
            out.append(p)
    return out


def fail(msg):
    print(f"FAIL {msg}")
    sys.exit(1)


pages = new_files({".html", ".htm"})
pages = [p for p in pages if p.name != "workspace.html"]
if not pages:
    fail("no new HTML page")
remote = re.compile(r"""<(script|img|iframe|source|video|audio)\b[^>]*\bsrc\s*=\s*["']?(https?:)?//"""
                    r"""|<link\b[^>]*\bhref\s*=\s*["']?(https?:)?//|@import\s+(url\()?["']?(https?:)?//""", re.I)


def visible(text):
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text))


claims = {}
for line in (work / "research/signings-xt/claims.jsonl").read_text().splitlines():
    try:
        rec = json.loads(line)
    except json.JSONDecodeError:
        continue
    claims[rec["id"]] = rec
allowed = set()
for rec in claims.values():
    if "value" in rec:
        allowed.add(f"{float(rec['value']):g}")
    allowed.update(f"{float(x):g}" for x in re.findall(r"\d+\.\d+", rec.get("statement", "")))

problems = []
for page in pages:
    raw = page.read_text(errors="replace")
    if remote.search(raw):
        problems.append(f"{page.name} loads something from the network")
        continue
    text = visible(raw)
    bad = sorted({d for d in re.findall(r"(?<![\d.])\d+\.\d+(?![\d.])", text) if f"{float(d):g}" not in allowed})
    if bad:
        problems.append(f"{page.name} shows decimals that are not ledger values: {', '.join(bad[:5])}")
        continue
    if not re.search(r"\b(C\d+|R1)\b", text):
        problems.append(f"{page.name} does not say where its numbers come from (no claim or run IDs)")
        continue
    break
else:
    fail("; ".join(problems))

env = dict(os.environ, NUTMEG_USER_CONFIG=str(work / ".nutmeg-user.json"))
result = subprocess.run([sys.executable, str(plugin / "core" / "nutmeg.py"), "check"], cwd=work,
                        capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)
if result.returncode != 0:
    fail("nutmeg check has open problems: " + (result.stdout + result.stderr).strip()[-300:])
print(f"PASS {page.relative_to(work)}")
