"""The glossary in docs/glossary.md: terms, their aliases and meanings."""
import re
from functools import lru_cache
from pathlib import Path

GLOSSARY_FILE = Path(__file__).resolve().parents[2] / "docs" / "glossary.md"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


@lru_cache(maxsize=4)
def load(path=GLOSSARY_FILE):
    """Entries as a list of {slug, term, aliases, meaning}."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return []
    entries, current = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            current = {"term": line[3:].strip(), "aliases": [], "meaning": []}
            current["slug"] = slug(current["term"].split("(")[0])
            entries.append(current)
        elif current is not None and line.startswith("Aliases:"):
            current["aliases"] = [a.strip() for a in line[len("Aliases:"):].split(",") if a.strip()]
        elif current is not None and line.strip():
            current["meaning"].append(line.strip())
    for entry in entries:
        entry["meaning"] = " ".join(entry["meaning"])
        if not entry["aliases"]:
            entry["aliases"] = [entry["term"]]
    return entries


def _alias_pattern(alias):
    return re.compile(r"(?<![\w-])" + re.escape(alias) + r"(?![\w-])", re.IGNORECASE)


def find(text, entries=None):
    """Glossary entries whose aliases appear in `text`, as {slug: entry}."""
    entries = load() if entries is None else entries
    found = {}
    for entry in entries:
        if any(_alias_pattern(a).search(text or "") for a in entry["aliases"]):
            found[entry["slug"]] = entry
    return found


def first_uses(text, entries=None):
    """(start, end, slug) for the first use of each term in `text`, longest alias first, no overlaps."""
    entries = load() if entries is None else entries
    spans = []
    for entry in entries:
        best = None
        for alias in sorted(entry["aliases"], key=len, reverse=True):
            match = _alias_pattern(alias).search(text or "")
            if match and (best is None or match.start() < best[0]):
                best = (match.start(), match.end(), entry["slug"])
        if best:
            spans.append(best)
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    chosen, end = [], -1
    for span in spans:
        if span[0] >= end:
            chosen.append(span)
            end = span[1]
    return chosen
