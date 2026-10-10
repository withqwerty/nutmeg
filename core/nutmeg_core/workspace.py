"""`nutmeg workspace`: a view-only, self-contained HTML page for a project.

The page shows, in order: when it was generated and how big the ledger is,
the review queue (open check problems, runs waiting for review, disputed
claims, headline claims waiting for sign-off, explainer pages older than
their source; the teach-back is personal and never shown here), the question, the plan with
its reasons, the ledger (disputed and failing claims first, each with its
`why` card), the figures with their footnotes, the runs, and the glossary
entries the page links to.

It is static: no scripts, a Content-Security-Policy that allows none, only
http, https and relative links, and every value escaped and redacted.
Statuses are words, so the page reads without colour. Approvals still happen
in Claude Code.
"""
import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from . import check as checks
from . import glossary, understand
from .config import ConfigError, team_signoff_required
from .figure import load_all as load_figures
from .ledger import Ledger
from .project import deviation_lines, find_repo_root, parse_choices
from .redact import Redactor
from .run import review_queue
from .why import why_lines

TEMPLATE = Path(__file__).parent / "templates" / "workspace.html"
CSP = "default-src 'none'; style-src 'unsafe-inline'; img-src 'self' file: data:; base-uri 'none'; form-action 'none'"
STATUS_ORDER = {"disputed": 0, "contested": 0}

_INLINE = re.compile(r"(`[^`]+`)|(\[([^\]]+)\]\(([^)\s]+)\))")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<![\w*])[_*](?![_*\s])(.+?)(?<![_*\s])[_*](?![\w*])")
_CLAIM_REF = re.compile(r"\[(C\d+(?:\s*,\s*C\d+)*)\]")


def safe_href(url):
    """The URL if it is http, https or relative; otherwise None."""
    url = (url or "").strip()
    if re.match(r"^https?://", url, re.I):
        return url
    if url.startswith("//") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", url):
        return None
    return url or None


class Renderer:
    """Escapes and redacts text, and links glossary terms on their first use per section."""

    def __init__(self, redactor, entries):
        self.redactor = redactor
        self.entries = entries
        self.linked = {}  # slug -> entry, for the inlined glossary
        self.used = set()  # terms already linked in the current section

    def section(self):
        self.used = set()

    def esc(self, value):
        return html.escape(self.redactor.text("" if value is None else str(value)), quote=True)

    def terms(self, text):
        """Escape plain text and link the first use of each glossary term in this section."""
        text = self.redactor.text(text)
        out, pos = [], 0
        for start, end, slug in glossary.first_uses(text, self.entries):
            if slug in self.used:
                continue
            self.used.add(slug)
            self.linked[slug] = next(e for e in self.entries if e["slug"] == slug)
            out.append(html.escape(text[pos:start]))
            out.append(f'<a class="term" href="#g-{slug}">{html.escape(text[start:end])}</a>')
            pos = end
        out.append(html.escape(text[pos:]))
        rendered = _ITALIC.sub(r"<em>\1</em>", _BOLD.sub(r"<strong>\1</strong>", "".join(out)))
        # [C3] or [C3, C5]: link each claim ID to its ledger row.
        return _CLAIM_REF.sub(lambda m: "[" + ", ".join(
            f'<a class="claim" href="#{c.strip()}">{c.strip()}</a>' for c in m.group(1).split(",")) + "]", rendered)

    def inline(self, text):
        out, pos = [], 0
        for match in _INLINE.finditer(text):
            out.append(self.terms(text[pos:match.start()]))
            if match.group(1):
                out.append(f"<code>{self.esc(match.group(1)[1:-1])}</code>")
            else:
                label, href = match.group(3), safe_href(match.group(4))
                out.append(f'<a href="{self.esc(href)}">{self.esc(label)}</a>' if href else self.esc(label))
            pos = match.end()
        out.append(self.terms(text[pos:]))
        return "".join(out)

    def markdown(self, text):
        """A small, safe subset: headings, paragraphs, lists, code blocks, bold, code and links."""
        html_out, para, items, list_tag, code = [], [], [], None, None

        def flush():
            nonlocal para, items, list_tag
            if para:
                html_out.append(f"<p>{self.inline(' '.join(para))}</p>")
                para = []
            if items:
                html_out.append(f"<{list_tag}>" + "".join(f"<li>{self.inline(i)}</li>" for i in items) + f"</{list_tag}>")
                items, list_tag = [], None

        for line in (text or "").splitlines():
            if code is not None:
                if line.strip().startswith("```"):
                    html_out.append(f"<pre>{self.esc(chr(10).join(code))}</pre>")
                    code = None
                else:
                    code.append(line)
                continue
            if line.strip().startswith("```"):
                flush()
                code = []
                continue
            heading = re.match(r"^(#{1,6})\s+(.*)", line)
            bullet = re.match(r"^\s*[-*]\s+(.*)", line)
            number = re.match(r"^\s*\d+[.)]\s+(.*)", line)
            if heading:
                flush()
                level = min(6, len(heading.group(1)) + 2)
                html_out.append(f"<h{level}>{self.inline(heading.group(2))}</h{level}>")
            elif bullet or number:
                tag = "ul" if bullet else "ol"
                if para or (list_tag and list_tag != tag):
                    flush()
                list_tag = tag
                items.append((bullet or number).group(1))
            elif not line.strip():
                flush()
            else:
                if items:
                    flush()
                para.append(line.strip())
        if code is not None:
            html_out.append(f"<pre>{self.esc(chr(10).join(code))}</pre>")
        flush()
        return "\n".join(html_out)


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""


def build(project, repo_root=None, now=None):
    project = Path(project)
    repo_root = Path(repo_root or find_repo_root(project))
    r = Renderer(Redactor.for_repo(repo_root), glossary.load())
    ledger = Ledger(project / "claims.jsonl")
    claims, problems = ledger.read()
    line_count = len([l for l in _read(project / "claims.jsonl").splitlines() if l.strip()])
    state = checks.check(project)
    failing = {f.get("claim") for f in state["open"] if f.get("claim")}
    try:
        signoff_required = team_signoff_required(repo_root)
    except ConfigError:
        signoff_required = True
    meta = json.loads(_read(project / "project.json") or "{}")
    title = meta.get("title") or project.name
    generated = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M UTC")

    # Review queue
    queue = []
    for failure in state["open"]:
        queue.append(f"<li><strong>Open problem</strong> {r.esc(checks.describe(failure))}</li>")
    for run in review_queue(project):
        queue.append(f"<li><strong>Run waiting for review</strong> {r.esc(run['id'])} {r.esc(run.get('file'))} "
                     f"({r.esc(run.get('status'))}); card in <code>runs/{r.esc(run['id'])}/gate.json</code></li>")
    for claim in claims.values():
        if claim.get("status") in ("disputed", "contested"):
            queue.append(f"<li><strong>{r.esc(claim['status'].capitalize())} claim</strong> "
                         f'<a href="#{r.esc(claim["id"])}">{r.esc(claim["id"])}</a> '
                         f"{r.esc(claim['statement'])}: {r.esc(claim.get('note'))} ({r.esc(claim.get('by'))})</li>")
        if signoff_required and claim.get("headline") and not claim.get("signer"):
            queue.append(f'<li><strong>Waiting for sign-off</strong> <a href="#{r.esc(claim["id"])}">'
                         f"{r.esc(claim['id'])}</a> {r.esc(claim['statement'])}</li>")
    for source in understand.explainers(project):
        state = understand.page_state(source)
        if state != "current":
            queue.append(f"<li><strong>Explainer page {r.esc(state)}</strong> <code>explainers/{r.esc(source.name)}"
                         "</code>; run <code>nutmeg explain render</code></li>")
    queue_html = "<ul>" + "".join(queue) + "</ul>" if queue else '<p class="empty">Nothing waits for review.</p>'

    # Question
    r.section()
    question_html = r.markdown(_read(project / "question.md")) or '<p class="empty">No question card.</p>'

    # Plan with reasons
    r.section()
    rows = []
    for choice in parse_choices(_read(project / "plan.md")):
        rests = (choice.get("rests_on") or "").split(None, 1)
        rests_type = rests[0] if rests else ""
        rests_ref = rests[1] if len(rests) > 1 else ""
        after = (f' <span class="tag">changed after seeing results</span> {r.inline(choice["after_results"])}'
                 if choice.get("after_results") else "")
        rows.append(f"<tr><td>{r.esc(choice.get('kind') or '?')}</td><td>{r.inline(choice['choice'])}{after}</td>"
                    f"<td>{r.inline(choice.get('why') or 'no reason given')}</td>"
                    f"<td><span class=\"tag\">{r.esc(rests_type)}</span> {r.inline(rests_ref)}</td></tr>")
    plan_html = ("<table><thead><tr><th>Kind</th><th>Choice</th><th>Why</th><th>Rests on</th></tr></thead><tbody>"
                 + "".join(rows) + "</tbody></table>") if rows else '<p class="empty">No plan choices yet.</p>'
    plan_html += "<ul>" + "".join(f"<li>{r.esc(line.lstrip('- '))}</li>" for line in deviation_lines(project)) + "</ul>"

    # Ledger
    r.section()
    def order(claim):
        number = int(claim["id"][1:]) if claim["id"][1:].isdigit() else 0
        return (STATUS_ORDER.get(claim.get("status"), 1 if claim["id"] in failing else 2), number)
    ledger_rows = []
    for claim in sorted(claims.values(), key=order):
        status = claim.get("status", "draft")
        flag = " · open problem" if claim["id"] in failing else ""
        value = f"<td class=\"num\">{r.esc(claim.get('value'))}</td>" if "value" in claim else "<td></td>"
        card = r.esc("\n".join(why_lines(project, repo_root, claim["id"])))
        ledger_rows.append(
            f'<tr id="{r.esc(claim["id"])}" class="status-{r.esc(status)}"><td>{r.esc(claim["id"])}</td>'
            f"<td>{r.esc(claim['kind'])}</td><td><span class=\"status\">{r.esc(status)}{flag}</span></td>"
            f"<td>{r.inline(claim['statement'])}<details><summary>Evidence and history</summary><pre>{card}</pre>"
            f"</details></td>{value}</tr>")
    ledger_html = ("<table><thead><tr><th>ID</th><th>Kind</th><th>Status</th><th>Claim</th><th>Value</th></tr>"
                   "</thead><tbody>" + "".join(ledger_rows) + "</tbody></table>") if ledger_rows else \
        '<p class="empty">No claims yet.</p>'
    if problems:
        ledger_html += "<p><strong>Ledger lines nutmeg could not read:</strong></p><ul>" + "".join(
            f"<li>line {n}: {r.esc(m)}</li>" for n, m in problems) + "</ul>"

    # Report
    r.section()
    report_text = _read(project / "report.md")
    report_html = r.markdown(report_text) if report_text else '<p class="empty">No report yet.</p>'

    # Figures
    figure_parts = []
    for prov in load_figures(project):
        if prov.get("error"):
            figure_parts.append(f"<figure><figcaption>{r.esc(prov['figure'])}: {r.esc(prov['error'])}</figcaption></figure>")
            continue
        image_html = ""
        image = prov.get("image")
        if image:
            path = (repo_root / image).resolve()
            if path.is_file() and repo_root.resolve() in path.parents:
                rel = os.path.relpath(path, project.resolve())
                image_html = f'<img src="{r.esc(Path(rel).as_posix())}" alt="{r.esc(prov["figure"])}">'
        figure_parts.append(
            f"<figure>{image_html}<figcaption><strong>{r.esc(prov['figure'])}</strong><br>{r.esc(prov.get('footnote'))}"
            f"<details><summary>Provenance</summary><pre>{r.esc(prov.get('footnote_long'))}</pre></details>"
            f"</figcaption></figure>")
    figures_html = "".join(figure_parts) or '<p class="empty">No figures registered yet.</p>'

    # Runs
    run_rows = []
    runs_dir = project / "runs"
    if runs_dir.is_dir():
        for folder in sorted((p for p in runs_dir.iterdir() if p.name[1:].isdigit()), key=lambda p: int(p.name[1:])):
            run = json.loads(_read(folder / "run.json") or "{}")
            if not run:
                continue
            gate = run.get("gate", {})
            gate_text = "queued for review" if gate.get("queued_for_review") else ("approved" if gate.get("shown") else "no gate card shown")
            run_rows.append(f"<tr><td>{r.esc(run.get('id'))}</td><td><code>{r.esc(run.get('file'))}</code></td>"
                            f"<td>{r.esc(run.get('status'))}</td><td>{r.esc(gate_text)}</td><td>{r.esc(run.get('started'))}</td></tr>")
    runs_html = ("<table><thead><tr><th>Run</th><th>File</th><th>Status</th><th>Gate</th><th>Started</th></tr></thead>"
                 "<tbody>" + "".join(run_rows) + "</tbody></table>") if run_rows else '<p class="empty">No runs yet.</p>'

    # Glossary entries the page linked
    glossary_html = "".join(
        f'<dt id="g-{r.esc(e["slug"])}">{r.esc(e["term"])}</dt><dd>{r.esc(e["meaning"])}</dd>'
        for e in sorted(r.linked.values(), key=lambda e: e["term"].lower()))
    glossary_html = f"<dl>{glossary_html}</dl>" if glossary_html else '<p class="empty">No glossary terms on this page.</p>'

    values = {
        "csp": CSP,
        "title": r.esc(title),
        "generated": r.esc(generated),
        "line_count": str(line_count),
        "claim_count": str(len(claims)),
        "open_count": str(len(state["open"])),
        "queue": queue_html,
        "question": question_html,
        "plan": plan_html,
        "ledger": ledger_html,
        "report": report_html,
        "figures": figures_html,
        "runs": runs_html,
        "glossary": glossary_html,
    }
    # One pass, so text inside a value is never read as a placeholder.
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values.get(m.group(1), m.group(0)), TEMPLATE.read_text(encoding="utf-8"))


def write(project, repo_root=None):
    page = build(project, repo_root)
    path = Path(project) / "workspace.html"
    path.write_text(page, encoding="utf-8")
    return path
