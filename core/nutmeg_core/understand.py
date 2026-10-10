"""Help the author understand the work before it is shared.

Teach-back: before `nutmeg publish`, the person who publishes shows they can
defend the work. Either their own messages already show it (`--shown` quotes),
or they talk it through: what it claims, what that rests on, and what would
change the answer (`--claim`, `--rests-on`, `--would-change`). Each record
carries a fingerprint of each claim it covers (the headline claims, or the
claims the outputs cite when there are no headline claims); a later change to a
covered claim needs a new one. nutmeg cannot judge the words; the skills do,
and never talk down to anyone.

The teach-back is personal. Records and declined explainer topics live in the
user's own nutmeg folder (next to the user config), never in the repository, a
bundle, the workspace page or a published output. Only the publish gate card,
which the person publishing sees, shows them.

Explainers: Markdown pages in `explainers/` that the user can edit.
`nutmeg explain render` turns each into one self-contained HTML page to share,
with a "where the numbers come from" section for the claims it cites. They are
outputs, so `nutmeg check` checks their numbers, and publish refuses a page that
is older than its source.
"""
import base64
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from . import glossary
from .ledger import CONTENT_FIELDS, Ledger
from .config import user_config_path
from .project import append_receipt, find_repo_root
from .redact import Redactor

EXPLAINERS = "explainers"
FIELDS = ("claim", "rests_on", "would_change")
LABELS = {"claim": "What it claims", "rests_on": "What it rests on", "would_change": "What would change the answer"}
MIN_WORDS = 4
MIN_SHOWN_WORDS = 6
COPY_CHARS = 40  # a field that repeats this many characters of an output or claim is copied, not the user's words
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
               ".webp": "image/webp", ".svg": "image/svg+xml"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
CSP = "default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'"
# Claim statuses in words a reader outside the project understands.
READER_STATUS = {"draft": "not yet checked by a second person", "verified": "checked by a second person",
                 "supported": "checked by a second person", "disputed": "disputed", "contested": "disputed"}
_CLAIM_REF = re.compile(r"\[(C\d+(?:\s*,\s*C\d+)*)\]")
_IMAGE = re.compile(r"^\s*!\[([^\]]*)\]\(([^)\s]+)\)\s*$")
_SOURCE_META = re.compile(r'<meta name="nutmeg-source" content="([^"]*)">')


class UnderstandError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm(text):
    return re.sub(r"\s+", " ", re.sub(r"\[C\d+(?:\s*,\s*C\d+)*\]", "", text or "")).strip().lower()


def fingerprint(claim):
    content = {k: claim.get(k) for k in CONTENT_FIELDS}
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def _cited_ids(project):
    from .check import output_files
    cited = set()
    for path in output_files(project):
        for ref in _CLAIM_REF.finditer(path.read_text(encoding="utf-8", errors="replace")):
            cited.update(c.strip() for c in ref.group(1).split(","))
    return cited


def needed(project):
    """The claims a teach-back must cover: the live headline claims, else the live claims the outputs cite."""
    claims = Ledger(Path(project) / "claims.jsonl").claims()
    live = {cid: c for cid, c in claims.items() if c.get("status") != "withdrawn"}
    ids = [cid for cid, c in live.items() if c.get("headline")]
    if not ids:
        cited = _cited_ids(project)
        ids = [cid for cid in live if cid in cited]
    return {cid: live[cid] for cid in ids}


def personal_store(project):
    """The user's own file for this project's teach-backs and declined topics: outside the repository."""
    project = Path(project).resolve()
    key = hashlib.sha256(str(project).encode("utf-8")).hexdigest()[:16]
    return user_config_path().parent / "teachback" / f"{project.name}-{key}.jsonl"


def _personal(project, kind=None):
    path = personal_store(project)
    out = []
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and (kind is None or record.get("kind", "teachback") == kind):
            out.append(record)
    return out


def _append_personal(project, entry):
    path = personal_store(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def records(project):
    return [r for r in _personal(project, "teachback") if isinstance(r.get("covers"), dict)]


def status(project, by=None):
    """What a publish by `by` still needs: {needed, missing, stale, latest}.

    The latest teach-back by that person counts. A covered claim whose content changed since is stale."""
    need = needed(project)
    mine = [r for r in records(project) if by is None or r.get("by") == by]
    latest = mine[-1] if mine else None
    covers = latest["covers"] if latest else {}
    missing = [cid for cid in need if cid not in covers]
    stale = [cid for cid in need if cid in covers and covers[cid] != fingerprint(need[cid])]
    return {"needed": list(need), "missing": missing, "stale": stale, "latest": latest}


def _copied_from(project, text):
    """The source a field was copied from (an output or a claim statement), or None."""
    words = _norm(text)
    if len(words) < COPY_CHARS:
        return None
    from .check import output_files
    sources = [(p.name, p.read_text(encoding="utf-8", errors="replace")) for p in output_files(project)]
    sources += [(p.name, p.read_text(encoding="utf-8")) for p in (Path(project) / "question.md",) if p.is_file()]
    sources += [(cid, c.get("statement", "")) for cid, c in Ledger(Path(project) / "claims.jsonl").claims().items()]
    for name, source in sources:
        flat = _norm(re.sub(r"[#>*_`|]", " ", source))
        for start in range(0, max(1, len(words) - COPY_CHARS + 1), 10):
            if words[start:start + COPY_CHARS] in flat:
                return name
    return None


def _check_words(project, label, text, minimum):
    if len(text.split()) < minimum:
        raise UnderstandError(f"{label}: a few more words would help (at least {minimum}), in the user's own words")
    source = _copied_from(project, text)
    if source:
        raise UnderstandError(f"{label} matches {source}; the teach-back is the user's own words, not the outputs")


def record(project, by, words=None, covers=None, shown=None, clarified=None):
    """Record that the person can defend the claims a publish needs.

    Either `words` maps each of FIELDS to the user's own answers, or `shown` lists sentences the user wrote in the
    conversation that already show it. `clarified` lists points cleared up along the way (for explainers)."""
    project = Path(project)
    words = {f: (words or {}).get(f) for f in FIELDS}
    shown = [q.strip() for q in (shown or []) if q and q.strip()]
    clarified = [c.strip() for c in (clarified or []) if c and c.strip()]
    if shown and any(words.values()):
        raise UnderstandError("give either --shown quotes or the three answers, not both")
    if shown:
        for quote in shown:
            _check_words(project, "--shown", quote, MIN_SHOWN_WORDS)
    else:
        for field in FIELDS:
            _check_words(project, f"--{field.replace('_', '-')}", (words.get(field) or "").strip(), MIN_WORDS)
        if len({_norm(words[f]) for f in FIELDS}) < len(FIELDS):
            raise UnderstandError("the three answers are the same; each answers a different question")
    need = needed(project)
    if covers:
        claims = Ledger(project / "claims.jsonl").claims()
        unknown = [c for c in covers if c not in claims or claims[c].get("status") == "withdrawn"]
        if unknown:
            raise UnderstandError(f"not in the ledger or withdrawn: {', '.join(unknown)}")
        chosen = {cid: claims[cid] for cid in covers}
    else:
        chosen = need
    if not chosen:
        raise UnderstandError("no headline claims and no claims cited in the outputs yet; there is nothing to cover")
    entry = {"kind": "teachback", "at": _now(), "by": by, "covers": {cid: fingerprint(c) for cid, c in chosen.items()}}
    if shown:
        entry["shown"] = shown
    else:
        entry.update({f: words[f].strip() for f in FIELDS})
    if clarified:
        entry["clarified"] = clarified
    entry = Redactor.for_repo(find_repo_root(project)).obj(entry)
    _append_personal(project, entry)
    return entry


def describe_gap(state):
    parts = []
    if state["missing"]:
        parts.append(f"not yet talked through: {', '.join(state['missing'])}")
    if state["stale"]:
        parts.append(f"changed since the last talk-through: {', '.join(state['stale'])}")
    return "; ".join(parts)


def summary_lines(entry):
    """The teach-back as the publish card shows it (only to the person publishing)."""
    if not entry:
        return []
    if entry.get("shown"):
        out = [f"Understanding shown in {entry.get('by')}'s own messages ({entry.get('at')}):"]
        out += [f'  "{q}"' for q in entry["shown"]]
    else:
        out = [f"In {entry.get('by')}'s own words ({entry.get('at')}):"]
        out += [f"  {LABELS[f]}: {entry.get(f)}" for f in FIELDS]
    if entry.get("clarified"):
        out.append("  Cleared up along the way: " + "; ".join(entry["clarified"]))
    return out


# --- explainers ----------------------------------------------------------------------------------------------------

TEMPLATE = """# {title}

<!-- An explainer for readers who were not part of the work. Edit any of it; then run
     `nutmeg explain render {slug}` (or ask nutmeg) to update the page. Put each number's
     claim ID in square brackets right after it, so the page can say where it comes from. -->

## The question

## What we found

## How we worked it out

## What could change the answer

## Words used here
"""


def explainer_dir(project):
    return Path(project) / EXPLAINERS


def new(project, slug, title):
    if not SLUG.match(slug):
        raise UnderstandError("use a short slug of lower-case letters, digits and dashes, for example why-mendes")
    folder = explainer_dir(project)
    path = folder / f"{slug}.md"
    if path.exists():
        raise UnderstandError(f"{path.name} exists; edit it, then run `nutmeg explain render {slug}`")
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE.format(title=title or slug.replace("-", " ").capitalize(), slug=slug), encoding="utf-8")
    append_receipt(project, "explainer_new", slug=slug)
    return path


def decline(project, topic, by):
    _append_personal(project, {"kind": "explainer_declined", "at": _now(), "by": by, "topic": topic})


def declined(project):
    return [r.get("topic") for r in _personal(project, "explainer_declined")]


def source_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def page_state(md_path):
    """'current', 'stale' (the page is older than its source) or 'missing'."""
    page = Path(md_path).with_suffix(".html")
    if not page.is_file():
        return "missing"
    found = _SOURCE_META.search(page.read_text(encoding="utf-8", errors="replace"))
    current = source_hash(Path(md_path).read_text(encoding="utf-8"))
    return "current" if found and found.group(1).endswith(current) else "stale"


def explainers(project):
    folder = explainer_dir(project)
    return sorted(folder.glob("*.md")) if folder.is_dir() else []


def _strip_comments(text):
    return re.sub(r"(?s)<!--.*?-->", "", text)


def _image(alt, ref, base, repo_root, r):
    """An image as a data: URI, so the page stays one file. Only files inside the repository."""
    path = (base / ref).resolve()
    if repo_root.resolve() not in path.parents or not path.is_file():
        return f'<p class="missing">[image not found: {r.esc(ref)}]</p>'
    kind = IMAGE_TYPES.get(path.suffix.lower())
    if kind is None or path.stat().st_size > MAX_IMAGE_BYTES:
        return f'<p class="missing">[image not embedded: {r.esc(ref)}]</p>'
    data = base64.b64encode(path.read_bytes()).decode()
    return f'<figure><img src="data:{kind};base64,{data}" alt="{r.esc(alt)}"></figure>'


def render(md_path, project=None, repo_root=None, now=None):
    """Write <name>.html next to the Markdown source and return its path."""
    from .workspace import Renderer

    md_path = Path(md_path)
    repo_root = Path(repo_root or find_repo_root(md_path.parent))
    source = md_path.read_text(encoding="utf-8")
    r = Renderer(Redactor.for_repo(repo_root), glossary.load())
    text = _strip_comments(source)
    title = next((m.group(1).strip() for m in re.finditer(r"^#\s+(.+)$", text, re.M)), md_path.stem)
    parts, chunk = [], []
    r.section()
    for line in text.splitlines():
        image = _IMAGE.match(line)
        if image:
            parts.append(r.markdown("\n".join(chunk)))
            chunk = []
            parts.append(_image(image.group(1), image.group(2), md_path.parent, repo_root, r))
        else:
            chunk.append(line)
    parts.append(r.markdown("\n".join(chunk)))
    body = "\n".join(p for p in parts if p)
    # The ledger is not in the page, so a claim ID links to its entry in "Where the numbers come from".
    body = re.sub(r'<a class="claim" href="#(C\d+)">', r'<a class="claim" href="#n-\1">', body)

    sources_html = ""
    if project is not None:
        claims = Ledger(Path(project) / "claims.jsonl").claims()
        cited = []
        for ref in _CLAIM_REF.finditer(text):
            cited += [c.strip() for c in ref.group(1).split(",") if c.strip() not in cited]
        rows = []
        for cid in cited:
            claim = claims.get(cid)
            if claim is None:
                continue
            evidence = claim.get("evidence") or {}
            if claim["kind"] == "gap":
                basis = f"not established: {evidence.get('reason')}"
            elif claim["kind"] == "interpretation":
                basis = (f"a judgement resting on {', '.join(evidence.get('claims', []))}"
                         + (f"; it does not show {evidence['limits'].rstrip('.')}" if evidence.get("limits") else ""))
            else:
                basis = None
            basis = basis or (f"run {evidence['run_id']} of the project's analysis" if evidence.get("run_id")
                     else evidence.get("citation") or evidence.get("source") or evidence.get("definition")
                     or ("rests on " + ", ".join(evidence.get("claims", [])) if evidence.get("claims") else ""))
            value = (f" = {claim['value']}" if "value" in claim and str(claim["value"]) not in claim["statement"]
                     else "")
            alts = evidence.get("alternatives") or []
            if alts and claim["kind"] == "interpretation":
                basis_extra = f" · holds under {sum(1 for a in alts if a.get('holds'))} of {len(alts)} alternatives"
            elif alts:
                basis_extra = " · alternatives: " + "; ".join(f"{a['choice']} {a['value']}" for a in alts)
            else:
                basis_extra = ""
            status = READER_STATUS.get(claim.get("status", "draft"), claim.get("status", "draft"))
            rows.append(f'<li id="n-{r.esc(cid)}"><strong>{r.esc(cid)}</strong> {r.esc(claim["statement"])}{r.esc(value)}'
                        f'<span class="basis"> · {r.esc(basis)}{r.esc(basis_extra)} · {r.esc(status)}</span></li>')
        if rows:
            sources_html = "<section><h2>Where the numbers come from</h2><ul class=\"sources\">" + "".join(rows) + "</ul></section>"
    glossary_html = "".join(f'<dt id="g-{r.esc(e["slug"])}">{r.esc(e["term"])}</dt><dd>{r.esc(e["meaning"])}</dd>'
                            for e in sorted(r.linked.values(), key=lambda e: e["term"].lower()))
    if glossary_html:
        glossary_html = f"<section><h2>Glossary</h2><dl>{glossary_html}</dl></section>"
    generated = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
    rel = md_path.resolve().relative_to(repo_root.resolve()).as_posix() if md_path.resolve().is_relative_to(repo_root.resolve()) else md_path.name
    page = PAGE.format(csp=CSP, title=r.esc(title), source=r.esc(f"{rel} sha256:{source_hash(source)}"),
                       body=body, sources=sources_html, glossary=glossary_html, generated=r.esc(generated))
    out = md_path.with_suffix(".html")
    out.write_text(page, encoding="utf-8")
    if project is not None:
        append_receipt(project, "explainer_render", file=rel)
    return out


PAGE = """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="referrer" content="no-referrer">
<meta name="nutmeg-source" content="{source}">
<title>{title}</title>
<style>
  :root {{ --bg: #fbfaf7; --fg: #1d2420; --muted: #5c665f; --line: #dcdfd8; --accent: #1f6f4a; --code: #f1f3ef; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #141815; --fg: #e6ebe7; --muted: #9aa59d; --line: #2c332e; --accent: #6fcf9f; --code: #232a25; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--fg); font: 17px/1.6 Georgia, "Iowan Old Style", serif; }}
  main {{ max-width: 720px; margin: 0 auto; padding: 32px 16px 64px; }}
  h1, h2, h3, h4, h5, h6 {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; line-height: 1.25; }}
  h1 {{ display: none; }}
  h3 {{ font-size: 1.9rem; margin: 0 0 16px; }}
  h4, h2 {{ font-size: 1.2rem; margin: 32px 0 8px; padding-bottom: 4px; border-bottom: 1px solid var(--line); }}
  a {{ color: var(--accent); }}
  a.term {{ text-decoration: underline dotted; }}
  a.claim {{ font: 0.75em system-ui, sans-serif; text-decoration: none; }}
  code {{ background: var(--code); padding: 0 4px; border-radius: 3px; font-size: 0.88em; }}
  pre {{ background: var(--code); padding: 10px 12px; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; }}
  figure {{ margin: 20px 0; }}
  figure img {{ max-width: 100%; height: auto; display: block; }}
  .missing {{ color: var(--muted); font-style: italic; }}
  ul.sources {{ font: 0.85rem/1.5 system-ui, sans-serif; padding-left: 18px; }}
  ul.sources li:target {{ outline: 2px solid var(--accent); }}
  .basis {{ color: var(--muted); }}
  dl {{ font: 0.9rem/1.5 system-ui, sans-serif; }}
  dt {{ font-weight: 600; margin-top: 8px; }}
  dd {{ margin: 2px 0 0; color: var(--muted); }}
  footer {{ margin-top: 40px; color: var(--muted); font: 0.8rem system-ui, sans-serif; }}
</style>
</head>
<body>
<main>
<article>
{body}
</article>
{sources}
{glossary}
<footer>Generated {generated} with nutmeg. Each number links to the project claim it comes from.</footer>
</main>
</body>
</html>
"""
