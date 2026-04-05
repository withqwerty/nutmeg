# Campos S0 Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute S0 of the Campos v1 launch plan: scaffold a minimal Campos monorepo, build the schema/theme generators, create stub implementations of 3 components, run an agent-effectiveness evaluation with a pre-committed rubric, run an audience audit against 5 GitHub apps, and produce a go/no-go decision document. Everything in S0 is a gate before any real component work begins.

**Architecture:** Campos is a standalone Python library (to live at `~/Work/campos` as its own git repo, not inside nutmeg). Monorepo layout with language-neutral `schema/` (JSON Schema) and `theme/` (tokens) folders, plus a `python/` flavour folder containing the PyPI package. Type files and theme rcParams are generated from the language-neutral sources by scripts, never hand-edited. This plan produces the scaffolding, the generators, the stubs, and the evidence artefacts — not any finished components. If S0 passes its four kill-criteria, a separate Plan 2 will handle real component builds.

**Tech Stack:** Python 3.10+, pydantic v2, `datamodel-code-generator` (JSON Schema → pydantic), matplotlib 3.7+, mplsoccer, pytest, git. Reference: `/Users/rahulkeerthi/Work/nutmeg/docs/superpowers/specs/2026-04-05-campos-design.md` (spec v2.1) for architecture, kill-criteria, and rubric requirements.

**Context for an engineer with no prior knowledge:**
- Campos is a football UI component library. It consumes canonical data (a Shot, a Player, etc.) and produces matplotlib figures. See the spec for full motivation.
- "S0" is the validation phase from the spec's launch plan — the pre-build gate. S0 produces evidence (did agents pick the right stubs? does the audience exist?), not finished products.
- "Green on all in-scope axes" is spec language for "a component passed every row in its 12-axis quality matrix." S0 doesn't produce any green components; it produces stubs that are intentionally minimal.
- The spec's "N3 token exercise" was run inline during brainstorming and found that matplotlib cannot express letter-spacing, text transforms, global border-radius, motion, or pseudo-states. Plan 1 verifies this finding programmatically as part of S0.

---

## File Structure

Files created by this plan, grouped by responsibility:

**Root / git:**
- `~/Work/campos/` — new git repo
- `~/Work/campos/README.md` — minimal README
- `~/Work/campos/.gitignore` — Python + venv + generated files
- `~/Work/campos/LICENSE` — MIT

**Language-neutral sources of truth:**
- `schema/player.schema.json`
- `schema/club.schema.json`
- `schema/shot.schema.json`
- `schema/action.schema.json`
- `schema/percentile_row.schema.json`
- `schema/radar_category.schema.json`
- `theme/tokens.json`

**Generator scripts:**
- `scripts/generate_python_types.py` — JSON Schema → pydantic
- `scripts/generate_python_theme.py` — tokens.json → rcParams module

**Python flavour package (`python/` subdirectory):**
- `python/pyproject.toml`
- `python/src/campos/__init__.py` — public API re-exports
- `python/src/campos/schema/__init__.py` — re-exports generated types
- `python/src/campos/schema/_generated.py` — generated pydantic types (DO NOT HAND-EDIT)
- `python/src/campos/schema/validators.py` — hand-authored cross-field validators
- `python/src/campos/theme/__init__.py`
- `python/src/campos/theme/_rcparams.py` — generated rcParams dict (DO NOT HAND-EDIT)
- `python/src/campos/theme/api.py` — `use_theme()` function
- `python/src/campos/components/__init__.py`
- `python/src/campos/components/player_hero.py` — stub
- `python/src/campos/components/percentile_ribbon.py` — stub
- `python/src/campos/components/shot_map.py` — stub
- `python/tests/__init__.py`
- `python/tests/test_schema.py`
- `python/tests/test_theme.py`
- `python/tests/test_stubs.py`

**Evidence artefacts (S0 outputs):**
- `docs/agent_eval_rubric.md` — frozen pre-committed rubric
- `docs/agent_eval_tasks.md` — 20 natural-language prompts
- `docs/audience_audit.md` — methodology + findings
- `docs/n3_token_verification.md` — programmatic verification of the N3 finding
- `docs/s0_results/claude_code.md` — raw agent eval results
- `docs/s0_results/cursor.md` — raw agent eval results (if available)
- `docs/s0_results/aider.md` — raw agent eval results (if available)
- `docs/s0_results/scored.md` — results scored against the frozen rubric
- `docs/s0_decision.md` — final go/no-go decision

---

## Task 1: Create the Campos repo

**Files:**
- Create: `~/Work/campos/` (new directory)
- Create: `~/Work/campos/.gitignore`
- Create: `~/Work/campos/README.md`
- Create: `~/Work/campos/LICENSE`

- [ ] **Step 1: Create the directory and initialise git**

```bash
mkdir -p ~/Work/campos
cd ~/Work/campos
git init
```

Expected: `Initialized empty Git repository in /Users/.../Work/campos/.git/`

- [ ] **Step 2: Create `.gitignore`**

Create `~/Work/campos/.gitignore` with:

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
*.egg
.pytest_cache/
.venv/
venv/
env/
build/
dist/

# Generated files are committed, but editor artefacts are not
*.swp
*.swo
.DS_Store
.idea/
.vscode/

# Test artefacts
.coverage
htmlcov/

# Snapshot test baselines go in python/tests/fixtures/ and ARE committed
```

- [ ] **Step 3: Create `README.md`**

Create `~/Work/campos/README.md` with:

```markdown
# Campos

> Beautiful, battle-tested football UI components. Pythonic today, multi-flavour tomorrow.

Campos is a Python library of production-quality, football-specific UI components:
player heroes, percentile ribbons, radar charts, shot maps, and more. It accepts
canonical football data and returns matplotlib figures that look good without the
caller having to write styling code.

**Status:** S0 validation phase. This repo is not ready for use.

**Design spec:** See `docs/` in this repo, or the original spec at
`withqwerty/nutmeg:docs/superpowers/specs/2026-04-05-campos-design.md`.

**Licence:** MIT.
```

- [ ] **Step 4: Create `LICENSE` (MIT)**

Create `~/Work/campos/LICENSE` with the standard MIT licence text, substituting the current year and "withqwerty" as the copyright holder. Use the canonical text from https://opensource.org/licenses/MIT — do not paraphrase.

- [ ] **Step 5: Initial commit**

```bash
cd ~/Work/campos
git add .gitignore README.md LICENSE
git commit -m "chore: initialise Campos repository"
```

Expected: commit succeeds, `git log --oneline` shows one commit.

---

## Task 2: Establish the monorepo directory structure

**Files:**
- Create: `~/Work/campos/schema/.gitkeep`
- Create: `~/Work/campos/theme/.gitkeep`
- Create: `~/Work/campos/python/.gitkeep`
- Create: `~/Work/campos/web/.gitkeep`
- Create: `~/Work/campos/react/.gitkeep`
- Create: `~/Work/campos/scripts/.gitkeep`
- Create: `~/Work/campos/docs/.gitkeep`
- Create: `~/Work/campos/web/README.md`
- Create: `~/Work/campos/react/README.md`

- [ ] **Step 1: Create all the top-level folders**

```bash
cd ~/Work/campos
mkdir -p schema theme python web react scripts docs
touch schema/.gitkeep theme/.gitkeep python/.gitkeep scripts/.gitkeep docs/.gitkeep
```

- [ ] **Step 2: Create placeholder READMEs for empty flavour folders**

Create `~/Work/campos/web/README.md` with:

```markdown
# Web flavour

This folder is reserved for a future HTML + CSS + inline SVG flavour of Campos
components. It is intentionally empty in v1.

When this flavour is added, components will live at `web/components/<name>.html`
(or similar), consuming the same `schema/` and `theme/` sources as the Python
flavour. See the spec section "Theme tokens and cross-flavour expressivity" for
the known limitations on what matplotlib can express relative to CSS.
```

Create `~/Work/campos/react/README.md` with:

```markdown
# React flavour

This folder is reserved for a future React + TypeScript flavour of Campos
components. It is intentionally empty in v1.

When this flavour is added, components will live at `react/src/components/<Name>.tsx`,
with TypeScript types generated from `schema/*.schema.json` via
`json-schema-to-typescript`.
```

- [ ] **Step 3: Commit the structure**

```bash
cd ~/Work/campos
git add .
git commit -m "chore: establish monorepo directory structure"
```

Expected: commit succeeds, `tree -L 2` shows schema/, theme/, python/, web/, react/, scripts/, docs/.

---

## Task 3: Write the canonical JSON Schema for `Player`

**Files:**
- Create: `~/Work/campos/schema/player.schema.json`

- [ ] **Step 1: Create `player.schema.json`**

Create `~/Work/campos/schema/player.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://campos.football/schema/player.schema.json",
  "title": "Player",
  "description": "A football player. Required fields are id and name; every other field is optional and components must handle missing values.",
  "type": "object",
  "required": ["id", "name"],
  "additionalProperties": false,
  "properties": {
    "id": {
      "type": "string",
      "description": "Stable identifier for this player within the data source. Not assumed to be globally unique across sources."
    },
    "name": {
      "type": "string",
      "description": "Display name. May be full or short form. Unicode and multi-script names must be supported."
    },
    "photo_url": {
      "type": ["string", "null"],
      "format": "uri",
      "description": "Optional portrait photo URL. Components must fall back to initials if null or unreachable."
    },
    "club_id": {
      "type": ["string", "null"],
      "description": "Optional club identifier matching a Club.id."
    },
    "league_id": {
      "type": ["string", "null"],
      "description": "Optional league identifier."
    },
    "nation": {
      "type": ["string", "null"],
      "description": "Optional ISO 3166 alpha-3 country code (e.g. FRA, BRA, ENG)."
    },
    "position": {
      "type": ["string", "null"],
      "description": "Optional position label. Free-form, provider-dependent (e.g. 'Att Mid/Winger', 'LB', 'CF')."
    },
    "age": {
      "type": ["integer", "null"],
      "minimum": 0,
      "maximum": 60,
      "description": "Age in years at the reference date."
    },
    "minutes": {
      "type": ["integer", "null"],
      "minimum": 0,
      "description": "Total minutes played in the reference period."
    },
    "birth_date": {
      "type": ["string", "null"],
      "format": "date",
      "description": "ISO 8601 date (YYYY-MM-DD)."
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
cd ~/Work/campos
git add schema/player.schema.json
git commit -m "feat(schema): add Player JSON Schema"
```

---

## Task 4: Write the canonical JSON Schema for `Club`

**Files:**
- Create: `~/Work/campos/schema/club.schema.json`

- [ ] **Step 1: Create `club.schema.json`**

Create `~/Work/campos/schema/club.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://campos.football/schema/club.schema.json",
  "title": "Club",
  "description": "A football club. Required fields are id and name.",
  "type": "object",
  "required": ["id", "name"],
  "additionalProperties": false,
  "properties": {
    "id": {
      "type": "string",
      "description": "Stable club identifier within the data source."
    },
    "name": {
      "type": "string",
      "description": "Display name (e.g. 'Bayern München', 'Manchester City')."
    },
    "crest_url": {
      "type": ["string", "null"],
      "format": "uri",
      "description": "Optional club crest image URL."
    },
    "league_id": {
      "type": ["string", "null"],
      "description": "Optional league identifier."
    },
    "colour_primary": {
      "type": ["string", "null"],
      "pattern": "^#[0-9A-Fa-f]{6}$",
      "description": "Primary club colour as 6-digit hex (e.g. '#DC052D'). Optional."
    },
    "colour_secondary": {
      "type": ["string", "null"],
      "pattern": "^#[0-9A-Fa-f]{6}$",
      "description": "Secondary club colour as 6-digit hex. Optional."
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
cd ~/Work/campos
git add schema/club.schema.json
git commit -m "feat(schema): add Club JSON Schema"
```

---

## Task 5: Write the canonical JSON Schema for `Shot`

**Files:**
- Create: `~/Work/campos/schema/shot.schema.json`

This schema includes the cross-field constraint that exercises N9 during Task 15: `x` and `y` must both be present or both be absent. Standard JSON Schema cannot express this directly (it requires a dependency between two nullable fields). The generator test in Task 15 will verify whether the chosen generator (`datamodel-code-generator`) can round-trip this via `dependentRequired` or whether it needs the `validators.py` fallback.

- [ ] **Step 1: Create `shot.schema.json`**

Create `~/Work/campos/schema/shot.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://campos.football/schema/shot.schema.json",
  "title": "Shot",
  "description": "A single shot attempt. Coordinates are normalised to [0, 1] on both axes where (0, 0) is the attacking team's defensive corner and (1, 1) is the attacking corner of the goal being attacked. If x or y is present, the other must also be present (enforced at runtime in validators.py).",
  "type": "object",
  "required": ["id", "xg"],
  "additionalProperties": false,
  "properties": {
    "id": {
      "type": "string",
      "description": "Stable shot identifier."
    },
    "x": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 1,
      "description": "Normalised X coordinate (attacking direction). Must be present if y is present."
    },
    "y": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 1,
      "description": "Normalised Y coordinate (width). Must be present if x is present."
    },
    "xg": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Expected-goals value for this shot."
    },
    "body_part": {
      "type": ["string", "null"],
      "enum": ["foot", "head", "other", null],
      "description": "Body part used. Free-form 'other' covers chest, shoulder, unusual cases."
    },
    "outcome": {
      "type": ["string", "null"],
      "enum": ["goal", "saved", "blocked", "off_target", "post", "own_goal", null],
      "description": "Shot outcome."
    },
    "minute": {
      "type": ["integer", "null"],
      "minimum": 0,
      "maximum": 200,
      "description": "Match minute (covers 90 + max stoppage)."
    },
    "player_id": {
      "type": ["string", "null"],
      "description": "Optional Player.id of the shot taker."
    }
  },
  "dependentRequired": {
    "x": ["y"],
    "y": ["x"]
  }
}
```

- [ ] **Step 2: Commit**

```bash
cd ~/Work/campos
git add schema/shot.schema.json
git commit -m "feat(schema): add Shot JSON Schema with coordinate cross-field constraint"
```

---

## Task 6: Write the remaining canonical schemas

**Files:**
- Create: `~/Work/campos/schema/action.schema.json`
- Create: `~/Work/campos/schema/percentile_row.schema.json`
- Create: `~/Work/campos/schema/radar_category.schema.json`

- [ ] **Step 1: Create `action.schema.json`**

Create `~/Work/campos/schema/action.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://campos.football/schema/action.schema.json",
  "title": "Action",
  "description": "A ball-progression action (pass, carry, cross, dribble). Coordinates normalised to [0, 1].",
  "type": "object",
  "required": ["id", "start_x", "start_y", "end_x", "end_y", "action_type"],
  "additionalProperties": false,
  "properties": {
    "id": { "type": "string" },
    "start_x": { "type": "number", "minimum": 0, "maximum": 1 },
    "start_y": { "type": "number", "minimum": 0, "maximum": 1 },
    "end_x":   { "type": "number", "minimum": 0, "maximum": 1 },
    "end_y":   { "type": "number", "minimum": 0, "maximum": 1 },
    "action_type": {
      "type": "string",
      "enum": ["pass", "carry", "cross", "dribble", "take_on", "clearance", "recovery"]
    },
    "xt": {
      "type": ["number", "null"],
      "description": "Expected threat delta for this action. May be negative."
    },
    "outcome": {
      "type": ["string", "null"],
      "enum": ["success", "fail", null]
    },
    "player_id": {
      "type": ["string", "null"]
    }
  }
}
```

- [ ] **Step 2: Create `percentile_row.schema.json`**

Create `~/Work/campos/schema/percentile_row.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://campos.football/schema/percentile_row.schema.json",
  "title": "PercentileRow",
  "description": "A single stat with its raw value and percentile rank vs a peer group. Used by PercentileRibbon and PercentileGroup.",
  "type": "object",
  "required": ["stat_id", "label", "value", "percentile"],
  "additionalProperties": false,
  "properties": {
    "stat_id": {
      "type": "string",
      "description": "Stable stat identifier (e.g. 'npxg_p90')."
    },
    "label": {
      "type": "string",
      "description": "Display label (e.g. 'Non-penalty xG per 90')."
    },
    "category": {
      "type": ["string", "null"],
      "description": "Optional category grouping (e.g. 'Shooting', 'Creation')."
    },
    "value": {
      "type": "number",
      "description": "Raw stat value."
    },
    "percentile": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Percentile rank within the peer group."
    },
    "comparison_percentile": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 100,
      "description": "Optional second percentile for a comparison player."
    }
  }
}
```

- [ ] **Step 3: Create `radar_category.schema.json`**

Create `~/Work/campos/schema/radar_category.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://campos.football/schema/radar_category.schema.json",
  "title": "RadarCategory",
  "description": "A single axis on a radar chart.",
  "type": "object",
  "required": ["label", "value", "max"],
  "additionalProperties": false,
  "properties": {
    "label": { "type": "string" },
    "value": { "type": "number" },
    "comparison_value": {
      "type": ["number", "null"],
      "description": "Optional value for a comparison player."
    },
    "max": {
      "type": "number",
      "description": "Axis maximum for normalisation. Usually the 99th percentile of the peer group."
    },
    "reversed": {
      "type": ["boolean", "null"],
      "description": "If true, lower raw values render further from centre (for stats like xGA where lower is better)."
    }
  }
}
```

- [ ] **Step 4: Commit all three**

```bash
cd ~/Work/campos
git add schema/action.schema.json schema/percentile_row.schema.json schema/radar_category.schema.json
git commit -m "feat(schema): add Action, PercentileRow, and RadarCategory JSON Schemas"
```

---

## Task 7: Create the Python package skeleton

**Files:**
- Create: `~/Work/campos/python/pyproject.toml`
- Create: `~/Work/campos/python/src/campos/__init__.py`
- Create: `~/Work/campos/python/src/campos/components/__init__.py`

- [ ] **Step 1: Create `python/pyproject.toml`**

Create `~/Work/campos/python/pyproject.toml` with:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "campos"
version = "0.0.0"
description = "Beautiful, battle-tested football UI components for Python."
readme = "../README.md"
license = { text = "MIT" }
authors = [{ name = "withqwerty" }]
requires-python = ">=3.10"
classifiers = [
    "Development Status :: 1 - Planning",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Visualization",
]
dependencies = [
    "matplotlib>=3.7",
    "mplsoccer>=1.2",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-mpl>=0.16",
    "datamodel-code-generator>=0.25",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create `python/src/campos/__init__.py`**

Create `~/Work/campos/python/src/campos/__init__.py` with:

```python
"""Campos — beautiful, battle-tested football UI components for Python.

This is S0-stage code. APIs are not stable, components are stubs, and nothing
in this package is suitable for production use.
"""

__version__ = "0.0.0.s0"
```

- [ ] **Step 3: Create `python/src/campos/components/__init__.py`**

Create `~/Work/campos/python/src/campos/components/__init__.py` with:

```python
"""Campos component implementations (Python flavour)."""
```

- [ ] **Step 4: Install the package in editable mode and verify the import**

```bash
cd ~/Work/campos/python
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -c "import campos; print(campos.__version__)"
```

Expected output: `0.0.0.s0`

- [ ] **Step 5: Commit**

```bash
cd ~/Work/campos
git add python/pyproject.toml python/src/campos/__init__.py python/src/campos/components/__init__.py
git commit -m "feat(python): scaffold Python flavour package"
```

---

## Task 8: Build the JSON Schema → pydantic generator script

**Files:**
- Create: `~/Work/campos/scripts/generate_python_types.py`
- Create: `~/Work/campos/python/src/campos/schema/__init__.py`

- [ ] **Step 1: Create the generator script**

Create `~/Work/campos/scripts/generate_python_types.py` with:

```python
#!/usr/bin/env python
"""Generate pydantic types from Campos JSON Schemas.

Reads every *.schema.json in ../schema/ and produces a single
python/src/campos/schema/_generated.py containing pydantic BaseModel
classes for each schema.

This file is executed by hand or via CI — generated output is committed
to the repository and NEVER hand-edited.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schema"
OUTPUT_FILE = REPO_ROOT / "python" / "src" / "campos" / "schema" / "_generated.py"


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    schema_files = sorted(SCHEMA_DIR.glob("*.schema.json"))
    if not schema_files:
        raise SystemExit(f"No *.schema.json files found in {SCHEMA_DIR}")

    # datamodel-code-generator can take multiple inputs via a directory.
    cmd = [
        "datamodel-codegen",
        "--input",
        str(SCHEMA_DIR),
        "--input-file-type",
        "jsonschema",
        "--output",
        str(OUTPUT_FILE),
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--target-python-version",
        "3.10",
        "--use-standard-collections",
        "--use-union-operator",
        "--field-constraints",
        "--use-schema-description",
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # Prepend a "do not edit" banner to the generated file.
    banner = (
        "# DO NOT HAND-EDIT.\n"
        "# This file is generated from schema/*.schema.json by\n"
        "# scripts/generate_python_types.py. Re-running the generator will\n"
        "# overwrite any local changes.\n"
        "# If you need to add logic that JSON Schema cannot express\n"
        "# (e.g. cross-field validation), add it to validators.py instead.\n\n"
    )
    content = OUTPUT_FILE.read_text()
    OUTPUT_FILE.write_text(banner + content)

    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create the `campos.schema` package `__init__.py` that re-exports generated types**

Create `~/Work/campos/python/src/campos/schema/__init__.py` with:

```python
"""Campos canonical data types.

These types are GENERATED from schema/*.schema.json via
scripts/generate_python_types.py. Do not hand-edit _generated.py.

Hand-authored cross-field validators live in validators.py.
"""

from campos.schema._generated import (  # noqa: F401
    Player,
    Club,
    Shot,
    Action,
    PercentileRow,
    RadarCategory,
)
```

- [ ] **Step 3: Run the generator**

```bash
cd ~/Work/campos
python scripts/generate_python_types.py
```

Expected: prints `Wrote .../python/src/campos/schema/_generated.py` and the file exists.

- [ ] **Step 4: Verify the generated types import and instantiate**

```bash
cd ~/Work/campos
source python/.venv/bin/activate
python -c "
from campos.schema import Player, Club, Shot
p = Player(id='olise', name='Michael Olise')
print(p)
c = Club(id='bayern', name='Bayern München')
print(c)
s = Shot(id='s1', xg=0.42)
print(s)
"
```

Expected: each line prints a pydantic model repr without error.

- [ ] **Step 5: Commit generator and generated file**

```bash
cd ~/Work/campos
git add scripts/generate_python_types.py python/src/campos/schema/__init__.py python/src/campos/schema/_generated.py
git commit -m "feat(schema): add JSON Schema → pydantic generator and initial types"
```

---

## Task 9: Write a failing test for cross-field constraint, then the validator

**Files:**
- Create: `~/Work/campos/python/tests/__init__.py`
- Create: `~/Work/campos/python/tests/test_schema.py`
- Create: `~/Work/campos/python/src/campos/schema/validators.py`

Purpose: exercise the N9 finding. If `datamodel-code-generator` propagated the `dependentRequired` constraint from `shot.schema.json` into the pydantic class directly, the test passes with the generated code alone. If it didn't, we write the constraint into `validators.py` and wrap the generated `Shot` type with it.

- [ ] **Step 1: Create `tests/__init__.py`**

Create `~/Work/campos/python/tests/__init__.py` as an empty file:

```bash
cd ~/Work/campos
touch python/tests/__init__.py
```

- [ ] **Step 2: Write a failing test for the Shot cross-field constraint**

Create `~/Work/campos/python/tests/test_schema.py` with:

```python
"""Schema tests — especially the cross-field constraints that JSON Schema
cannot always express natively.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from campos.schema import Shot


class TestShotCoordinateConstraint:
    """If x is present, y must be present (and vice versa)."""

    def test_shot_with_both_coordinates_is_valid(self) -> None:
        shot = Shot(id="s1", xg=0.3, x=0.85, y=0.5)
        assert shot.x == 0.85
        assert shot.y == 0.5

    def test_shot_with_neither_coordinate_is_valid(self) -> None:
        shot = Shot(id="s1", xg=0.3)
        assert shot.x is None
        assert shot.y is None

    def test_shot_with_only_x_raises(self) -> None:
        with pytest.raises(ValidationError):
            Shot(id="s1", xg=0.3, x=0.85)

    def test_shot_with_only_y_raises(self) -> None:
        with pytest.raises(ValidationError):
            Shot(id="s1", xg=0.3, y=0.5)
```

- [ ] **Step 3: Run the test — expected to fail**

```bash
cd ~/Work/campos
source python/.venv/bin/activate
cd python
pytest tests/test_schema.py -v
```

Expected: the first two tests pass, the last two fail with a `pydantic.ValidationError` NOT being raised. (If `datamodel-code-generator` did propagate `dependentRequired`, all four tests pass — in which case skip to Step 6 with a note in the commit message.)

- [ ] **Step 4: Add the validator in `validators.py`**

Create `~/Work/campos/python/src/campos/schema/validators.py` with:

```python
"""Hand-authored cross-field validators layered over the generated types.

JSON Schema cannot cleanly express some constraints (e.g. 'if x is present,
y must also be present'). These validators live here and wrap the generated
types when imported via `campos.schema`.

Rule (per spec N9): generated files are not hand-edited. This file is.
"""
from __future__ import annotations

from pydantic import model_validator

from campos.schema._generated import Shot as _GeneratedShot


class Shot(_GeneratedShot):
    """Shot with the x/y paired-coordinate constraint enforced at runtime."""

    @model_validator(mode="after")
    def _validate_coordinate_pair(self) -> "Shot":
        x_set = self.x is not None
        y_set = self.y is not None
        if x_set != y_set:
            raise ValueError(
                "Shot: x and y must both be present or both be absent "
                f"(got x={self.x!r}, y={self.y!r})."
            )
        return self
```

- [ ] **Step 5: Update `schema/__init__.py` to re-export the wrapped `Shot`**

Edit `~/Work/campos/python/src/campos/schema/__init__.py` to:

```python
"""Campos canonical data types.

Generated types live in _generated.py (DO NOT HAND-EDIT) and are produced
from schema/*.schema.json by scripts/generate_python_types.py.

Cross-field validators that JSON Schema cannot express are layered on top
in validators.py and re-exported here. Consumers should always import from
campos.schema (not from _generated directly).
"""

# Wrapped types with cross-field validators
from campos.schema.validators import Shot  # noqa: F401

# Types that need no additional validation come straight from the generated file
from campos.schema._generated import (  # noqa: F401
    Player,
    Club,
    Action,
    PercentileRow,
    RadarCategory,
)
```

- [ ] **Step 6: Re-run the test — expected to pass**

```bash
cd ~/Work/campos/python
pytest tests/test_schema.py -v
```

Expected: all four tests pass.

- [ ] **Step 7: Commit**

```bash
cd ~/Work/campos
git add python/tests/__init__.py python/tests/test_schema.py python/src/campos/schema/validators.py python/src/campos/schema/__init__.py
git commit -m "feat(schema): add Shot coordinate-pair validator (N9 constraint)"
```

---

## Task 10: Write the tokens.json and the Python theme generator

**Files:**
- Create: `~/Work/campos/theme/tokens.json`
- Create: `~/Work/campos/scripts/generate_python_theme.py`
- Create: `~/Work/campos/python/src/campos/theme/__init__.py`
- Create: `~/Work/campos/python/src/campos/theme/api.py`

- [ ] **Step 1: Create `theme/tokens.json`**

Create `~/Work/campos/theme/tokens.json` with:

```json
{
  "$comment": "Campos design tokens. This file is the single source of truth for design decisions. Each flavour consumes the subset it can express — see the spec section 'Theme tokens and cross-flavour expressivity' for what matplotlib cannot express.",
  "color": {
    "surface": {
      "base":  "#0a0a0b",
      "hero":  "#12141a",
      "chip":  "#1c1f27"
    },
    "text": {
      "primary":   "#f5f5f7",
      "secondary": "#9ea3ad"
    },
    "accent": {
      "primary":   "#7cd3a3",
      "secondary": "#a78bfa"
    },
    "border": {
      "hairline": "#2a2e38"
    }
  },
  "typography": {
    "display": {
      "family": ["Inter", "DejaVu Sans", "sans-serif"],
      "weight": 800,
      "size":   48,
      "tracking": -0.02
    },
    "body": {
      "family": ["Inter", "DejaVu Sans", "sans-serif"],
      "weight": 400,
      "size":   14,
      "tracking": 0
    },
    "label": {
      "family": ["Inter", "DejaVu Sans", "sans-serif"],
      "weight": 500,
      "size":   10,
      "tracking": 0.08,
      "transform": "uppercase"
    }
  },
  "spacing": {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32
  },
  "radius": {
    "sm": 6,
    "md": 12,
    "lg": 20
  }
}
```

- [ ] **Step 2: Create the theme generator**

Create `~/Work/campos/scripts/generate_python_theme.py` with:

```python
#!/usr/bin/env python
"""Generate a matplotlib rcParams module from theme/tokens.json.

Matplotlib cannot express every token (notably: letter-spacing, text-transform,
global border-radius, motion, pseudo-states). This generator consumes only the
tokens matplotlib natively supports and writes them to
python/src/campos/theme/_rcparams.py as a module-level dict literal.

The generated file is committed and DO NOT HAND-EDIT. Downstream code reads
it from campos.theme.api.use_theme().
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOKENS_FILE = REPO_ROOT / "theme" / "tokens.json"
OUTPUT_FILE = REPO_ROOT / "python" / "src" / "campos" / "theme" / "_rcparams.py"


def build_rcparams(tokens: dict) -> dict[str, object]:
    """Translate the language-neutral tokens file into matplotlib rcParams.

    Tokens that matplotlib cannot express (tracking, transform, radius) are
    deliberately ignored here. See spec section "Theme tokens and cross-flavour
    expressivity" for the full list and rationale.
    """
    color = tokens["color"]
    typography = tokens["typography"]

    return {
        # Figure + axes colours
        "figure.facecolor": color["surface"]["base"],
        "axes.facecolor":   color["surface"]["hero"],
        "savefig.facecolor": color["surface"]["base"],

        # Text colours
        "text.color":       color["text"]["primary"],
        "axes.labelcolor":  color["text"]["secondary"],
        "axes.edgecolor":   color["border"]["hairline"],
        "xtick.color":      color["text"]["secondary"],
        "ytick.color":      color["text"]["secondary"],

        # Font family (list so matplotlib falls back if the first is missing)
        "font.family":      typography["body"]["family"],
        "font.size":        typography["body"]["size"],
        "font.weight":      typography["body"]["weight"],

        # Grid / spines
        "axes.grid":        False,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
    }


def main() -> None:
    tokens = json.loads(TOKENS_FILE.read_text())
    rcparams = build_rcparams(tokens)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    banner = (
        '"""Generated matplotlib rcParams for Campos.\n\n'
        "DO NOT HAND-EDIT. This file is regenerated from theme/tokens.json by\n"
        'scripts/generate_python_theme.py.\n"""\n\n'
        "from __future__ import annotations\n\n"
    )

    body = f"RCPARAMS: dict[str, object] = {rcparams!r}\n"

    OUTPUT_FILE.write_text(banner + body)
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the generator**

```bash
cd ~/Work/campos
python scripts/generate_python_theme.py
```

Expected: prints `Wrote .../python/src/campos/theme/_rcparams.py` and the file contains an `RCPARAMS` dict.

- [ ] **Step 4: Create `theme/__init__.py` and `theme/api.py`**

Create `~/Work/campos/python/src/campos/theme/__init__.py` with:

```python
"""Campos theme — generated from theme/tokens.json."""

from campos.theme.api import use_theme  # noqa: F401
```

Create `~/Work/campos/python/src/campos/theme/api.py` with:

```python
"""Public theme API for Campos.

Applies the generated rcParams to matplotlib without mutating global state
beyond the expected surface area. Respect user rcParams by only setting
keys that Campos actually owns.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import matplotlib as mpl

from campos.theme._rcparams import RCPARAMS


def use_theme(name: str = "dark") -> None:
    """Apply the Campos theme globally.

    Args:
        name: Theme variant. v1 ships only "dark"; "light" is planned for v1.x.

    Raises:
        ValueError: if the requested theme variant is not supported.
    """
    if name != "dark":
        raise ValueError(
            f"Unknown theme '{name}'. v1 ships only 'dark'. "
            "Light variant is planned for v1.x."
        )
    mpl.rcParams.update(RCPARAMS)


@contextmanager
def theme(name: str = "dark") -> Iterator[None]:
    """Context manager equivalent of use_theme — reverts rcParams on exit."""
    with mpl.rc_context(RCPARAMS):
        yield
```

- [ ] **Step 5: Commit**

```bash
cd ~/Work/campos
git add theme/tokens.json scripts/generate_python_theme.py python/src/campos/theme/__init__.py python/src/campos/theme/api.py python/src/campos/theme/_rcparams.py
git commit -m "feat(theme): add token generator and matplotlib theme API"
```

---

## Task 11: Write the theme test

**Files:**
- Create: `~/Work/campos/python/tests/test_theme.py`

- [ ] **Step 1: Write tests for `use_theme()` and the context manager**

Create `~/Work/campos/python/tests/test_theme.py` with:

```python
"""Theme tests — verify use_theme applies rcParams and the context manager reverts them."""
from __future__ import annotations

import matplotlib as mpl
import pytest

from campos.theme import use_theme
from campos.theme.api import theme
from campos.theme._rcparams import RCPARAMS


def test_use_theme_sets_figure_facecolor() -> None:
    # Reset first so the test is order-independent.
    mpl.rcdefaults()
    use_theme("dark")
    assert mpl.rcParams["figure.facecolor"] == RCPARAMS["figure.facecolor"]


def test_use_theme_unknown_variant_raises() -> None:
    with pytest.raises(ValueError, match="Unknown theme"):
        use_theme("midnight")


def test_theme_context_manager_reverts_on_exit() -> None:
    mpl.rcdefaults()
    original = mpl.rcParams["figure.facecolor"]
    with theme("dark"):
        assert mpl.rcParams["figure.facecolor"] == RCPARAMS["figure.facecolor"]
    assert mpl.rcParams["figure.facecolor"] == original
```

- [ ] **Step 2: Run the tests**

```bash
cd ~/Work/campos/python
pytest tests/test_theme.py -v
```

Expected: all three tests pass.

- [ ] **Step 3: Commit**

```bash
cd ~/Work/campos
git add python/tests/test_theme.py
git commit -m "test(theme): verify use_theme applies rcParams and context manager reverts"
```

---

## Task 12: Verify the N3 tokens exercise finding programmatically

**Files:**
- Create: `~/Work/campos/docs/n3_token_verification.md`
- Create: `~/Work/campos/scripts/verify_n3_exercise.py`

Purpose: the spec states that matplotlib cannot express letter-spacing, text transforms, global border-radius, motion, or pseudo-states. Verify this programmatically so the claim is tested, not asserted.

- [ ] **Step 1: Create the verification script**

Create `~/Work/campos/scripts/verify_n3_exercise.py` with:

```python
#!/usr/bin/env python
"""Programmatic verification of the N3 token-expressivity finding.

Per the spec (section "Theme tokens and cross-flavour expressivity"),
matplotlib cannot express:
  - letter-spacing (tracking)
  - text-transform: uppercase
  - global border-radius
  - motion / transitions
  - pseudo-states (hover, focus)

This script checks matplotlib's actual rcParams namespace for any key
that could plausibly express each of those concepts. If any unexpected
key is found, the spec's claim is falsified and needs revision.
"""
from __future__ import annotations

import matplotlib as mpl

# Keys we claim matplotlib does NOT have. If matplotlib's rcParams
# contains any key matching these patterns, our claim is wrong.
UNEXPECTED_KEY_PATTERNS: dict[str, list[str]] = {
    "letter-spacing / tracking": ["letter", "tracking", "spacing.letter"],
    "text-transform": ["transform", "case"],
    "global border-radius": ["radius", "border.radius", "corner"],
    "motion / transitions": ["transition", "duration", "animation"],
    "pseudo-states (hover/focus)": ["hover", "focus", "active", "disabled"],
}


def main() -> None:
    rcparam_keys = list(mpl.rcParams.keys())
    print(f"Checking {len(rcparam_keys)} matplotlib rcParams keys...")
    print()

    all_findings: dict[str, list[str]] = {}
    for category, patterns in UNEXPECTED_KEY_PATTERNS.items():
        found = [k for k in rcparam_keys if any(p in k.lower() for p in patterns)]
        all_findings[category] = found

    falsified_categories = []
    for category, found in all_findings.items():
        if found:
            print(f"[UNEXPECTED] {category}: {found}")
            falsified_categories.append(category)
        else:
            print(f"[CONFIRMED ]  {category}: no matching rcParams (as expected)")

    print()
    if falsified_categories:
        print(f"FALSIFIED: {len(falsified_categories)} spec claims need revision:")
        for c in falsified_categories:
            print(f"  - {c}")
        raise SystemExit(1)
    print("All N3 claims confirmed: matplotlib does not natively express any of the listed concepts.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the verification**

```bash
cd ~/Work/campos
source python/.venv/bin/activate
python scripts/verify_n3_exercise.py
```

Expected: prints "All N3 claims confirmed..." and exits 0. If it exits 1, the spec needs revision — stop and escalate.

- [ ] **Step 3: Create the results document**

Create `~/Work/campos/docs/n3_token_verification.md` with:

```markdown
# N3 Token-Expressivity Verification

**Purpose:** Programmatically verify the spec claim that matplotlib cannot
express letter-spacing, text-transform, global border-radius, motion, or
pseudo-states via its rcParams system.

**Verification method:** `scripts/verify_n3_exercise.py` inspects every key in
`matplotlib.rcParams` and checks whether any key matches the patterns
associated with each unexpected concept.

**Outcome (2026-04-05 run):** All five claims confirmed.

- letter-spacing / tracking: no matching rcParams ✓
- text-transform: no matching rcParams ✓
- global border-radius: no matching rcParams ✓
- motion / transitions: no matching rcParams ✓
- pseudo-states (hover / focus / active / disabled): no matching rcParams ✓

**Implication:** the spec's "Theme tokens and cross-flavour expressivity"
section is accurate. Python components render the subset of tokens that
matplotlib supports. When a web flavour arrives in the future, tokens in
these categories will be exposed via CSS generators only; the Python flavour
will ignore them or implement them manually per component.

**Re-run:** `python scripts/verify_n3_exercise.py` — should exit 0. If it
exits 1, matplotlib has added rcParams in a version the spec didn't anticipate
and the claim needs revision.
```

- [ ] **Step 4: Commit**

```bash
cd ~/Work/campos
git add scripts/verify_n3_exercise.py docs/n3_token_verification.md
git commit -m "test(theme): verify N3 token-expressivity claim programmatically"
```

---

## Task 13: Stub the PlayerHero component

**Files:**
- Create: `~/Work/campos/python/src/campos/components/player_hero.py`

- [ ] **Step 1: Write a failing test for PlayerHero**

Add to `~/Work/campos/python/tests/test_stubs.py` (create the file if it doesn't exist):

```python
"""Tests for component stubs. Stubs are intentionally minimal — these tests
verify that the signatures accept canonical schema types and return a matplotlib
Figure, not that the outputs look correct. Real quality tests are in Plan 2.
"""
from __future__ import annotations

import matplotlib.figure
import pytest

from campos.components.player_hero import player_hero
from campos.schema import Player, Club


class TestPlayerHeroStub:
    def test_returns_figure(self) -> None:
        player = Player(id="olise", name="Michael Olise")
        club = Club(id="bayern", name="Bayern München")
        fig = player_hero(player, club=club)
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_accepts_missing_club(self) -> None:
        player = Player(id="olise", name="Michael Olise")
        fig = player_hero(player, club=None)
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_player_name_appears_in_figure_suptitle(self) -> None:
        player = Player(id="olise", name="Michael Olise")
        fig = player_hero(player, club=None)
        # The stub puts the name in the suptitle for easy agent inspection.
        assert fig._suptitle is not None
        assert "Michael Olise" in fig._suptitle.get_text()
```

- [ ] **Step 2: Run the test — expected to fail**

```bash
cd ~/Work/campos/python
pytest tests/test_stubs.py -v
```

Expected: ImportError because `campos.components.player_hero` doesn't exist.

- [ ] **Step 3: Write the stub**

Create `~/Work/campos/python/src/campos/components/player_hero.py` with:

```python
"""PlayerHero component — stub implementation.

This is S0-stage code. The stub renders a minimal matplotlib Figure that
is enough for an agent eval to verify selection and schema usage. It is
NOT a finished component. Real implementation with the 12-axis quality
matrix happens in Plan 2.

The public signature MUST NOT change between this stub and the real
implementation, because the agent eval (Task 17) relies on it.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from campos.schema import Player, Club


def player_hero(
    player: Player,
    *,
    club: Club | None = None,
    season_label: str | None = None,
) -> Figure:
    """Render a player hero card.

    Args:
        player: The subject player. Required.
        club: Optional club context for crest + name. If None, the hero
            renders without club chrome.
        season_label: Optional season label (e.g. "2025/26"). If None, no
            season is shown.

    Returns:
        A matplotlib Figure. The caller owns it and should decide whether
        to display, save, or embed it.
    """
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.axis("off")
    title = player.name
    if club is not None:
        title = f"{title} — {club.name}"
    if season_label is not None:
        title = f"{title} ({season_label})"
    fig.suptitle(title, fontsize=24, fontweight="bold", y=0.75)

    if player.position:
        ax.text(0.5, 0.3, player.position, ha="center", va="center", fontsize=12)

    return fig
```

- [ ] **Step 4: Re-run the test — expected to pass**

```bash
cd ~/Work/campos/python
pytest tests/test_stubs.py::TestPlayerHeroStub -v
```

Expected: all three tests pass.

- [ ] **Step 5: Commit**

```bash
cd ~/Work/campos
git add python/src/campos/components/player_hero.py python/tests/test_stubs.py
git commit -m "feat(components): add PlayerHero stub"
```

---

## Task 14: Stub the PercentileRibbon component

**Files:**
- Create: `~/Work/campos/python/src/campos/components/percentile_ribbon.py`

- [ ] **Step 1: Write a failing test**

Append to `~/Work/campos/python/tests/test_stubs.py`:

```python
# (append at the end of the file)

from campos.components.percentile_ribbon import percentile_ribbon


class TestPercentileRibbonStub:
    def test_returns_figure(self) -> None:
        from campos.schema import PercentileRow
        rows = [
            PercentileRow(stat_id="npxg", label="Non-penalty xG", value=0.54, percentile=97),
            PercentileRow(stat_id="xa",   label="Expected Assists", value=0.31, percentile=88),
        ]
        fig = percentile_ribbon(rows)
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_empty_list_returns_figure(self) -> None:
        fig = percentile_ribbon([])
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_single_row_returns_figure(self) -> None:
        from campos.schema import PercentileRow
        rows = [PercentileRow(stat_id="npxg", label="npxG", value=0.4, percentile=85)]
        fig = percentile_ribbon(rows)
        assert isinstance(fig, matplotlib.figure.Figure)
```

- [ ] **Step 2: Run the test — expected to fail**

```bash
cd ~/Work/campos/python
pytest tests/test_stubs.py::TestPercentileRibbonStub -v
```

Expected: ImportError.

- [ ] **Step 3: Write the stub**

Create `~/Work/campos/python/src/campos/components/percentile_ribbon.py` with:

```python
"""PercentileRibbon component — stub implementation.

S0-stage: renders a minimal horizontal-bar chart showing percentile fills
for a list of PercentileRow objects. Real 12-axis implementation in Plan 2.
"""
from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from campos.schema import PercentileRow


def percentile_ribbon(rows: Sequence[PercentileRow]) -> Figure:
    """Render a stack of labelled percentile bars.

    Args:
        rows: Ordered list of stats to display. Empty list renders a
            placeholder figure — this stub never raises.

    Returns:
        A matplotlib Figure.
    """
    n = max(len(rows), 1)
    fig, ax = plt.subplots(figsize=(8, 0.6 * n + 0.8))

    if not rows:
        ax.text(0.5, 0.5, "(no data)", ha="center", va="center", transform=ax.transAxes)
        ax.axis("off")
        return fig

    for i, row in enumerate(reversed(rows)):
        ax.barh(i, row.percentile, color="#7cd3a3", height=0.6)
        ax.text(-1, i, row.label, ha="right", va="center", fontsize=10)
        ax.text(row.percentile + 1, i, f"{row.value:.2f}", ha="left", va="center", fontsize=9)

    ax.set_xlim(0, 105)
    ax.set_ylim(-0.5, len(rows) - 0.5)
    ax.axis("off")
    return fig
```

- [ ] **Step 4: Re-run the test — expected to pass**

```bash
cd ~/Work/campos/python
pytest tests/test_stubs.py::TestPercentileRibbonStub -v
```

Expected: all three tests pass.

- [ ] **Step 5: Commit**

```bash
cd ~/Work/campos
git add python/src/campos/components/percentile_ribbon.py python/tests/test_stubs.py
git commit -m "feat(components): add PercentileRibbon stub"
```

---

## Task 15: Stub the ShotMap component

**Files:**
- Create: `~/Work/campos/python/src/campos/components/shot_map.py`

- [ ] **Step 1: Write a failing test**

Append to `~/Work/campos/python/tests/test_stubs.py`:

```python
# (append at the end of the file)

from campos.components.shot_map import shot_map


class TestShotMapStub:
    def test_returns_figure_with_shots(self) -> None:
        from campos.schema import Shot
        shots = [
            Shot(id="s1", xg=0.42, x=0.85, y=0.5, outcome="goal"),
            Shot(id="s2", xg=0.11, x=0.78, y=0.3, outcome="saved"),
        ]
        fig = shot_map(shots)
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_empty_shots_returns_figure(self) -> None:
        fig = shot_map([])
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_shot_without_coordinates_is_skipped_silently(self) -> None:
        from campos.schema import Shot
        # Shot with no coordinates is valid per the schema; the stub should
        # not crash when it encounters one.
        shots = [Shot(id="s1", xg=0.3)]
        fig = shot_map(shots)
        assert isinstance(fig, matplotlib.figure.Figure)
```

- [ ] **Step 2: Run the test — expected to fail**

```bash
cd ~/Work/campos/python
pytest tests/test_stubs.py::TestShotMapStub -v
```

Expected: ImportError.

- [ ] **Step 3: Write the stub**

Create `~/Work/campos/python/src/campos/components/shot_map.py` with:

```python
"""ShotMap component — stub implementation.

S0-stage: draws a minimal scatter of shots on a pitch using mplsoccer.
Real 12-axis implementation (hex binning, shape encoding, companion
bee-swarm distribution) happens in Plan 2. The signature here is the
public signature that the real implementation will honour.
"""
from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from mplsoccer import VerticalPitch

from campos.schema import Shot


def shot_map(shots: Sequence[Shot]) -> Figure:
    """Render a shot map on a vertical half-pitch.

    Args:
        shots: Shots to display. Shots with missing coordinates are
            silently skipped (per schema, x/y are optional but must
            be paired when present).

    Returns:
        A matplotlib Figure.
    """
    pitch = VerticalPitch(
        pitch_type="custom",
        pitch_length=100,
        pitch_width=100,
        half=True,
        pitch_color="#12141a",
        line_color="#9ea3ad",
    )
    fig, ax = pitch.draw(figsize=(6, 6))

    plottable = [s for s in shots if s.x is not None and s.y is not None]
    if not plottable:
        ax.text(
            50, 50, "(no shots with coordinates)",
            ha="center", va="center", color="#9ea3ad", fontsize=10,
        )
        return fig

    # Convert from 0-1 normalised to the custom 0-100 pitch coordinates.
    xs = [s.x * 100 for s in plottable]
    ys = [s.y * 100 for s in plottable]
    sizes = [max(50, s.xg * 600) for s in plottable]
    colours = ["#7cd3a3" if s.outcome == "goal" else "#a78bfa" for s in plottable]

    pitch.scatter(xs, ys, s=sizes, c=colours, ax=ax, edgecolors="white", linewidths=0.5)
    return fig
```

- [ ] **Step 4: Re-run the test — expected to pass**

```bash
cd ~/Work/campos/python
pytest tests/test_stubs.py::TestShotMapStub -v
```

Expected: all three tests pass.

- [ ] **Step 5: Run the full test suite to verify nothing regressed**

```bash
cd ~/Work/campos/python
pytest -v
```

Expected: every test passes (schema + theme + stubs).

- [ ] **Step 6: Commit**

```bash
cd ~/Work/campos
git add python/src/campos/components/shot_map.py python/tests/test_stubs.py
git commit -m "feat(components): add ShotMap stub using mplsoccer"
```

---

## Task 16: Re-export stubs from the top-level `campos` namespace

**Files:**
- Modify: `~/Work/campos/python/src/campos/__init__.py`

Purpose: agents will typically import `campos.player_hero` or `from campos import player_hero` rather than the fully-qualified path. Re-export the stubs (and the theme API) from the top-level package.

- [ ] **Step 1: Edit `campos/__init__.py` to add re-exports**

Replace the contents of `~/Work/campos/python/src/campos/__init__.py` with:

```python
"""Campos — beautiful, battle-tested football UI components for Python.

This is S0-stage code. APIs are not stable, components are stubs, and nothing
in this package is suitable for production use.
"""

from campos.components.player_hero import player_hero
from campos.components.percentile_ribbon import percentile_ribbon
from campos.components.shot_map import shot_map
from campos.theme import use_theme

__all__ = [
    "player_hero",
    "percentile_ribbon",
    "shot_map",
    "use_theme",
]
__version__ = "0.0.0.s0"
```

- [ ] **Step 2: Verify top-level imports work**

```bash
cd ~/Work/campos/python
python -c "
import campos
from campos.schema import Player, Club, Shot, PercentileRow
campos.use_theme('dark')
fig = campos.player_hero(Player(id='x', name='Test'), club=Club(id='y', name='Club'))
print('OK:', type(fig).__name__)
"
```

Expected: `OK: Figure`

- [ ] **Step 3: Commit**

```bash
cd ~/Work/campos
git add python/src/campos/__init__.py
git commit -m "feat(api): re-export stubs and use_theme from top-level campos"
```

---

## Task 17: Write the pre-committed agent evaluation rubric

**Files:**
- Create: `~/Work/campos/docs/agent_eval_rubric.md`

Purpose: the rubric must be written and committed BEFORE S0 runs. Per the spec's N4 fix, once committed it is frozen for the duration of S0 and retroactive softening is not allowed.

- [ ] **Step 1: Write the rubric**

Create `~/Work/campos/docs/agent_eval_rubric.md` with:

```markdown
# Campos S0 Agent Evaluation Rubric (FROZEN)

**Purpose:** Pre-committed rubric for scoring agent outputs on the 20 S0 eval tasks. Per spec v2.1 N4, this rubric is frozen once committed and cannot be softened retroactively during scoring.

**Status:** FROZEN as of the commit that introduces this file. Any change requires a new S0 cycle from scratch.

## Scoring metrics (all four apply independently)

### M1. Selection accuracy
Did the agent select Campos components that could plausibly satisfy the task?
- **Pass (1 point):** Every component the agent selected is one of `player_hero`, `percentile_ribbon`, `shot_map`, and the selections are reasonable given the task wording (e.g. a "shot map" task uses `shot_map`, not `percentile_ribbon`).
- **Fail (0 points):** The agent selected a component that does not exist in Campos v1 (e.g. invented `campos.radar_chart`), or selected a component that is clearly wrong for the task (e.g. used `percentile_ribbon` for a task asking to plot shot locations).

### M2. Schema compliance
Did the agent construct valid canonical schema objects?
- **Pass (1 point):** All instances of `Player`, `Club`, `Shot`, `PercentileRow` use only fields that exist on the schema (per `schema/*.schema.json`). No invented fields, no wrong types.
- **Fail (0 points):** The agent invented at least one field (e.g. `player.jersey_number`, `shot.location` as a tuple), used a wrong type (e.g. passed a dict where a pydantic model is expected), or made up an enum value (e.g. `shot.outcome='nice'`).

### M3. Execution success
Did the generated code run without errors?
- **Pass (1 point):** Copying the agent's code into a Python file and running it under the Campos venv produces a matplotlib Figure without exceptions (other than matplotlib font-warning-level messages).
- **Fail (0 points):** The code raises any exception — ImportError, AttributeError, ValidationError, TypeError.

### M4. Output quality (rubric-scored per task, see below)
Does the rendered result make sense for the task? Each task has an anchor example below.

## Per-task output-quality anchors

Each of the 20 tasks has three anchor categories:
- **PASS:** the agent produced something that visibly answers the task.
- **BORDERLINE:** the agent produced something related but with a meaningful omission or wrong emphasis.
- **FAIL:** the agent's output does not address the task, contains obvious visual errors, or is empty.

### Task 1 — "Build me a player report for Mohamed Salah using the data in `df`."

| Anchor | Example |
|---|---|
| PASS | Agent calls `campos.player_hero(Player(...))` *and* `campos.percentile_ribbon([...])`, producing a figure with Salah's name visible and at least 3 percentile bars. |
| BORDERLINE | Agent calls only `player_hero` with Salah's name, no stats at all. Or calls only `percentile_ribbon` without a hero. |
| FAIL | Agent calls no Campos components, or calls `shot_map` only (wrong component for a "report"), or produces a figure with a different player's name. |

### Task 2 — "Show Olise's shot map alongside his top percentile stats."

| Anchor | Example |
|---|---|
| PASS | Both `shot_map` and `percentile_ribbon` called, composed into a single figure or paired adjacent figures. |
| BORDERLINE | Only one of the two called, or both called but the stats shown are not "top" (e.g. alphabetical, unsorted). |
| FAIL | Neither called; or used wrong data (not Olise). |

### Task 3 — "Make a one-page scouting card I can share on Twitter."

| Anchor | Example |
|---|---|
| PASS | `player_hero` + `percentile_ribbon` composed into a single figure sized for sharing (portrait or square, not extreme aspect ratios). |
| BORDERLINE | Components present but output is a 2000x500 horizontal strip unsuitable for Twitter. |
| FAIL | No Campos components used; agent tried to build from scratch with raw matplotlib. |

### Task 4 — "I want to compare two players' shooting output visually."

| Anchor | Example |
|---|---|
| PASS | Two `shot_map` calls side by side, or two `percentile_ribbon` calls comparing shooting stats. Labels identify both players. |
| BORDERLINE | One component with both players' data overlaid (comparison not visually clear). |
| FAIL | Only one player shown, or no Campos components used. |

### Task 5 — "I've got a list of shots from StatsBomb. Make a shot map."

| Anchor | Example |
|---|---|
| PASS | `shot_map` called with `Shot` objects derived from the StatsBomb data. Coordinates normalised (not raw 120×80). |
| BORDERLINE | `shot_map` called but coordinates left in raw StatsBomb space (visible on the pitch but wrong scale). |
| FAIL | `shot_map` not called, or called with invalid `Shot` objects (e.g. invented fields). |

### Task 6 — "Visualise how many shots each team took in this match."

| Anchor | Example |
|---|---|
| PASS | Agent recognises that v1 Campos has no team-level or match-level component and either (a) declines politely and suggests composing primitives, or (b) calls `shot_map` twice (once per team). |
| BORDERLINE | Agent calls `percentile_ribbon` with shot counts (awkward but technically works). |
| FAIL | Agent invents `campos.team_summary` or `campos.match_report`. |

### Task 7 — "Can you make a chart of Olise's top stats vs Saka's top stats?"

| Anchor | Example |
|---|---|
| PASS | `percentile_ribbon` called with `comparison_percentile` populated for each row, or two `percentile_ribbon` calls labelled. |
| BORDERLINE | Only one player shown. |
| FAIL | Invented comparison component. |

### Task 8 — "Give me the player card for this DataFrame row." (`df.iloc[0]`)

| Anchor | Example |
|---|---|
| PASS | Agent constructs a `Player` object from the row (mapping obvious columns to schema fields) and calls `player_hero`. |
| BORDERLINE | Agent passes the DataFrame row directly to `player_hero` (which would fail — the stub expects `Player`). |
| FAIL | Agent invents a `campos.from_dataframe()` helper. |

### Task 9 — "I need a percentile chart but the data has NaN values in some cells."

| Anchor | Example |
|---|---|
| PASS | Agent filters NaN rows before constructing `PercentileRow` objects, or writes the code to skip them. |
| BORDERLINE | Agent passes NaN through to `PercentileRow` (which may or may not raise depending on validator). |
| FAIL | Agent crashes or invents error-handling that doesn't match Campos's behaviour. |

### Task 10 — "Plot the expected goals distribution for Bayern München in a way that's clean for a blog post."

| Anchor | Example |
|---|---|
| PASS | `shot_map` called for Bayern's shots, with `use_theme()` applied, output dimensions reasonable for blog embedding. |
| BORDERLINE | `shot_map` called without `use_theme`, so output uses matplotlib defaults. |
| FAIL | Non-Campos approach used. |

### Tasks 11–20

Tasks 11–20 follow the same structure and will be enumerated in `docs/agent_eval_tasks.md` (Task 18 of this plan). Each task has PASS / BORDERLINE / FAIL anchors that reference component selection, schema usage, and visual output.

## Scoring

- **M1 (Selection accuracy):** count of tasks where M1=pass. Threshold ≥85%.
- **M2 (Schema compliance):** count of tasks with zero invented fields across all 20 runs. Threshold = 100% (zero hallucinations).
- **M3 (Execution success):** count of tasks where M3=pass. Threshold ≥70%.
- **M4 (Output quality):** tasks scored PASS or BORDERLINE count as 1; FAIL counts as 0. Threshold ≥60% (PASS-or-BORDERLINE).

**S0 passes iff all four thresholds are met across the full 20-task eval, averaged over the agents tested.**

## Rules (per spec N4)

1. This rubric is frozen for the duration of S0.
2. If the rubric turns out to be wrong, it is revised *after* S0 completes and S0 is rerun from scratch with the new rubric.
3. Borderline cases within a task are scored FAIL, not PASS, absent an explicit anchor that maps the case to PASS.
4. The scorer is the author; scoring happens in one sitting for reproducibility.
```

- [ ] **Step 2: Commit (and note the freeze)**

```bash
cd ~/Work/campos
git add docs/agent_eval_rubric.md
git commit -m "docs(s0): freeze pre-committed agent eval rubric

Per spec v2.1 N4, this rubric cannot be softened retroactively. Any
change requires a new S0 cycle from scratch."
```

---

## Task 18: Write the 20 agent evaluation task prompts

**Files:**
- Create: `~/Work/campos/docs/agent_eval_tasks.md`

- [ ] **Step 1: Write the 20 task prompts**

Create `~/Work/campos/docs/agent_eval_tasks.md` with:

```markdown
# Campos S0 Agent Evaluation — Task Prompts

**Purpose:** 20 natural-language prompts for testing whether AI coding agents can pick, read, and invoke Campos v1 stub components correctly.

**Protocol:** For each prompt, present the agent with:
1. A clean Python project containing Campos installed (`pip install -e ~/Work/campos/python`).
2. The repo's top-level README and `python/src/campos/` source tree available to read.
3. The prompt text verbatim as a user message.

Record:
- The agent's final code output.
- Any tool calls the agent makes (read / search / list files).
- Whether the code runs (M3).
- Component selections (M1) and schema usage (M2).
- Visual output saved as PNG for M4 scoring.

## Prompts

### 1. Player report
> Build me a player report for Mohamed Salah using the data in `df`. Use whatever is in `df` — just make something that looks like a scouting one-pager.

(Provide a `df` with columns `player_name`, `team`, `position`, `minutes`, `npxg_p90`, `xa_p90`, `progressive_passes_p90`, `shots_on_target_pct`.)

### 2. Shot map with percentiles
> Show Olise's shot map alongside his top percentile stats. Make it look clean.

(Provide `shots_df` and `stats_df`.)

### 3. Twitter-ready card
> Make a one-page scouting card I can share on Twitter. Player is Florian Wirtz.

### 4. Player comparison
> I want to compare two players' shooting output visually. Use Haaland and Mbappé. Shots data is in `shots_df`.

### 5. StatsBomb shots
> I've got a list of shots from StatsBomb. Make a shot map. The DataFrame columns are `shot_id`, `location_x`, `location_y`, `shot_statsbomb_xg`, `shot_outcome_name`, `player_id`.

(Coordinates in 0–120 / 0–80 — tests whether the agent normalises to 0–1 before passing to the Campos schema.)

### 6. Match-level shot count
> Visualise how many shots each team took in this match. Data has `team_id`, `shot_id`, `shot_statsbomb_xg`.

### 7. Two-player stat comparison
> Can you make a chart of Olise's top stats vs Saka's top stats? Use the percentile columns in `df`.

### 8. DataFrame row → card
> Give me the player card for this DataFrame row. `row = df.iloc[0]`.

### 9. NaN handling
> I need a percentile chart but the data has NaN values in some cells. Handle them sensibly. Columns: `stat`, `value`, `percentile`.

### 10. Blog-post xG
> Plot the expected goals distribution for Bayern München in a way that's clean for a blog post. Shots are in `shots_df`.

### 11. Minimal example
> Show me the minimum code to make a player hero card with just a name.

### 12. Dark theme
> Apply the Campos dark theme and make me a shot map for Haaland's season.

### 13. Save to file
> Make a player hero for Erling Haaland and save it as `haaland.png` at 300 DPI.

### 14. Multiple players on one figure
> I want three player cards in one figure — Salah, De Bruyne, Saka. Vertical stack.

### 15. Large ribbon
> Show me 15 percentile rows for Trent Alexander-Arnold, grouped by attack / defend / passing. (Provide data with a `category` column.)

### 16. Goalkeeper
> Make a scouting card for a goalkeeper. Alisson Becker, Liverpool. I've got save stats and distribution stats.

### 17. Missing data
> This player has no photo and no club crest. Make the hero work anyway.

### 18. Wrong player name
> Make a shot map. The player name is `"Ødegaard"` (with the Ø).

### 19. Full workflow
> Given this DataFrame (player stats) and this shots DataFrame, build me a full scouting report as a single figure. Player: Cole Palmer.

### 20. Edge case
> Make a shot map but the shots list is empty.

## Protocol for scoring

1. For each prompt, capture the agent's code output.
2. Run the code under the Campos venv.
3. Capture the rendered figure (if the code ran).
4. Score against the rubric (M1, M2, M3, M4) for each agent.
5. Record raw results in `docs/s0_results/<agent>.md`.
6. Compute aggregate pass rate against the four thresholds.
```

- [ ] **Step 2: Commit**

```bash
cd ~/Work/campos
git add docs/agent_eval_tasks.md
git commit -m "docs(s0): add 20 agent eval task prompts"
```

---

## Task 19: Write the audience audit methodology and template

**Files:**
- Create: `~/Work/campos/docs/audience_audit.md`

- [ ] **Step 1: Write the methodology doc with a blank findings template**

Create `~/Work/campos/docs/audience_audit.md` with:

```markdown
# Campos S0 Audience Audit

**Purpose:** Verify that the target audience (Python football analysts building Streamlit/Quarto/notebook apps) is actually hand-rolling components that Campos proposes to provide.

**Per spec v2.1 N4 (qualifying gap definition):** A qualifying gap is a component in an existing open-source Python football app where the author wrote **≥50 lines of custom matplotlib / styling / layout code** that Campos's proposed API would have replaced with **≤10 lines**. Line counts measured on final checked-in code, not drafts. Styling tweaks of <50 lines are not gaps; they are polish.

## Search methodology

1. Search GitHub for repositories matching combinations of these terms:
   - `football xG streamlit`
   - `football scouting python matplotlib`
   - `soccer analysis notebook`
   - `"mplsoccer" language:python`
   - `football dashboard quarto`
2. For each repo found, skim the rendered outputs (if any) for player cards, percentile charts, radars, shot maps, or ranked lists.
3. For each candidate component, check the source: count the lines of custom matplotlib / styling / layout code.
4. Apply the qualifying gap definition. Record findings below.
5. Stop when 5 qualifying gaps have been found, OR when the search is reasonably exhausted (~10 repos examined) — whichever comes first.

## Findings

Fill in during the audit. Each entry should be a real repo and a real file link.

### Gap 1
- **Repo:** <URL>
- **File:** <path/to/file.py>
- **Component type:** <player hero / percentile ribbon / radar / shot map / ranked list / other>
- **Lines of custom code:** <count>
- **What Campos would replace with:** <code snippet, ≤10 lines>
- **Counts as qualifying gap?** <yes/no, with reasoning>

### Gap 2
...

### Gap 3
...

### Gap 4
...

### Gap 5
...

## Summary

- **Qualifying gaps found:** <count out of target 5>
- **Gap cluster:** <charts / chrome / mixed>
- **Per N10 pre-committed rule:**
  - If ≥4 of 5 gaps are in chart components → current build order holds (ShotMap first in Plan 2).
  - If ≥4 of 5 gaps are in chrome components → reverse build order, chrome first in Plan 2.
  - If mixed (2+2+1 or similar) → current build order holds.
- **Build order decision for Plan 2:** <record decision here>

## If fewer than 5 qualifying gaps are found

Per spec v2.1 N4, the project pauses for a minimum of 2 calendar weeks. At least one spec assumption (target users, component set, quality bar, architecture) must be revised before Plan 2 is written. Stub improvements alone are not sufficient.

Record the pause decision and the revised assumption here if this case applies.
```

- [ ] **Step 2: Commit**

```bash
cd ~/Work/campos
git add docs/audience_audit.md
git commit -m "docs(s0): add audience audit methodology and findings template"
```

---

## Task 20: Run the agent evaluation against available agents

**Files:**
- Create: `~/Work/campos/docs/s0_results/claude_code.md`
- Create: `~/Work/campos/docs/s0_results/cursor.md` (if available)
- Create: `~/Work/campos/docs/s0_results/aider.md` (if available)

This task is manual — it requires running real agents against the 20 task prompts. The sub-steps here are the recording protocol.

- [ ] **Step 1: Set up the eval environment**

```bash
cd ~/Work/campos
mkdir -p docs/s0_results
```

Prepare a scratch directory for each agent's eval session:

```bash
mkdir -p /tmp/campos_eval_claude_code
cd /tmp/campos_eval_claude_code
python -m venv .venv
source .venv/bin/activate
pip install -e ~/Work/campos/python
```

Create two small test DataFrames that tasks 1–5 reference (save as `/tmp/campos_eval_claude_code/data.py`):

```python
"""Fixture data for the Campos agent eval. Used across the 20 tasks."""
import pandas as pd

df = pd.DataFrame([
    {"player_name": "Mohamed Salah", "team": "Liverpool", "position": "RW",
     "minutes": 2450, "npxg_p90": 0.41, "xa_p90": 0.28,
     "progressive_passes_p90": 5.2, "shots_on_target_pct": 48.1},
    {"player_name": "Michael Olise",  "team": "Bayern München", "position": "RW",
     "minutes": 1970, "npxg_p90": 0.38, "xa_p90": 0.31,
     "progressive_passes_p90": 4.9, "shots_on_target_pct": 42.5},
])

shots_df = pd.DataFrame([
    {"shot_id": "s1", "location_x": 100, "location_y": 40,
     "shot_statsbomb_xg": 0.42, "shot_outcome_name": "Goal", "player_id": "p1"},
    {"shot_id": "s2", "location_x": 94, "location_y": 25,
     "shot_statsbomb_xg": 0.11, "shot_outcome_name": "Saved", "player_id": "p1"},
])
```

- [ ] **Step 2: Run tasks 1–20 against Claude Code**

For each of the 20 task prompts in `docs/agent_eval_tasks.md`:
1. Start a fresh Claude Code session in `/tmp/campos_eval_claude_code/`.
2. Paste the prompt text verbatim.
3. Let the agent explore the Campos source if it asks to.
4. Capture the agent's final code output.
5. Run the code: `python <filename>.py`.
6. If the code produced a figure, save it: `plt.savefig(f"task_{N}.png")`.
7. Record M1, M2, M3, M4 per the rubric.

Record results in `~/Work/campos/docs/s0_results/claude_code.md` using this template:

```markdown
# Campos S0 Agent Eval — Claude Code

**Date:** <ISO date>
**Agent version:** <Claude Code version / model ID>
**Rubric:** Per frozen `docs/agent_eval_rubric.md`.

## Task 1 — Player report

**Prompt:** (copy from agent_eval_tasks.md task 1)

**Agent's code:**
```python
# paste agent's final code here
```

**Ran?** <yes/no, with error if no>
**Components selected:** <list>
**Invented fields?** <yes/no, with examples if yes>
**Visual output:** task_01.png (attached)
**Rubric scoring:**
- M1 (Selection): <pass/fail>
- M2 (Schema): <pass/fail>
- M3 (Execution): <pass/fail>
- M4 (Quality): <PASS/BORDERLINE/FAIL>

## Task 2 — Shot map with percentiles

... (repeat for all 20 tasks)

## Aggregate

- M1 pass rate: X/20 = Y%
- M2 pass rate: X/20 = Y% (must be 100% to clear threshold)
- M3 pass rate: X/20 = Y%
- M4 PASS+BORDERLINE rate: X/20 = Y%
```

- [ ] **Step 3: Run tasks 1–20 against Cursor (if available)**

Same protocol. Record in `docs/s0_results/cursor.md`. If Cursor is not available, note "not tested" in the final scoring document.

- [ ] **Step 4: Run tasks 1–20 against one open-source agent (Aider or Continue)**

Same protocol. Record in `docs/s0_results/aider.md`. If neither is available locally, note the omission in the final scoring document and proceed with Claude Code + Cursor (or just Claude Code if that's the only one available).

- [ ] **Step 5: Commit raw results**

```bash
cd ~/Work/campos
git add docs/s0_results/
git commit -m "test(s0): capture raw agent eval results

Covers: <list of agents tested>
Tasks: 20 of 20 per docs/agent_eval_tasks.md"
```

---

## Task 21: Run the audience audit

**Files:**
- Modify: `~/Work/campos/docs/audience_audit.md`

- [ ] **Step 1: Search GitHub for candidate repos**

Use the search methodology from `docs/audience_audit.md`. Candidate search terms:

- `football xG streamlit`
- `football scouting python matplotlib`
- `"mplsoccer" language:python`
- `football dashboard quarto`
- `"player percentile" python`

Record ~10 candidate repos in a scratch list.

- [ ] **Step 2: Examine each candidate and apply the qualifying gap definition**

For each candidate:
1. Find the rendered outputs (README, demo gifs, deployed apps).
2. Identify hand-rolled components that match Campos's v1 set.
3. Count lines of custom matplotlib / styling / layout code for that component.
4. Apply the ≥50 lines / ≤10 lines test.

- [ ] **Step 3: Fill in the Findings section of `docs/audience_audit.md`**

For each qualifying gap, complete the entry template. Stop at 5 gaps OR at 10 repos examined, whichever comes first.

- [ ] **Step 4: Fill in the Summary section**

Apply the N10 pre-committed rule to the gap cluster:
- ≥4/5 chart gaps → current build order holds.
- ≥4/5 chrome gaps → reverse build order (chrome first).
- Mixed → current build order holds.

Record the build-order decision explicitly.

- [ ] **Step 5: If fewer than 5 qualifying gaps are found, STOP and do not proceed to Task 22**

Per spec v2.1 N4, the project pauses for at least 2 weeks and a spec assumption must be revised. Do not proceed to the S0 decision document.

- [ ] **Step 6: Commit the filled audit**

```bash
cd ~/Work/campos
git add docs/audience_audit.md
git commit -m "docs(s0): complete audience audit

Qualifying gaps found: <count>
Gap cluster: <charts / chrome / mixed>
Build order decision for Plan 2: <hold / reverse>"
```

---

## Task 22: Score agent eval results against the frozen rubric

**Files:**
- Create: `~/Work/campos/docs/s0_results/scored.md`

- [ ] **Step 1: Aggregate the raw results**

Open every `docs/s0_results/<agent>.md` file. Transcribe the M1/M2/M3/M4 scores for each task, per agent.

- [ ] **Step 2: Compute per-agent aggregates**

For each agent tested:
- M1 pass rate: count(M1=pass) / 20
- M2 pass rate: count(M2=pass) / 20 (must hit 100% for zero hallucinations)
- M3 pass rate: count(M3=pass) / 20
- M4 (PASS + BORDERLINE) rate: count(M4∈{PASS,BORDERLINE}) / 20

- [ ] **Step 3: Compute cross-agent aggregates**

Average each metric across all agents tested. If only one agent was tested, the average equals the single agent's rate; note the limitation explicitly.

- [ ] **Step 4: Apply the thresholds**

- M1 ≥ 85%?
- M2 = 100% (every task, every agent — a single hallucinated field fails M2)?
- M3 ≥ 70%?
- M4 ≥ 60%?

- [ ] **Step 5: Write the scored document**

Create `~/Work/campos/docs/s0_results/scored.md` with:

```markdown
# Campos S0 Agent Eval — Scored Results

**Rubric:** `docs/agent_eval_rubric.md` (frozen)
**Raw results:** `docs/s0_results/{claude_code,cursor,aider}.md`
**Date scored:** <ISO date>

## Per-agent aggregates

| Agent | M1 (Selection) | M2 (Schema) | M3 (Execution) | M4 (Quality) |
|---|---|---|---|---|
| Claude Code | X/20 (Y%) | X/20 (Y%) | X/20 (Y%) | X/20 (Y%) |
| Cursor | X/20 (Y%) | X/20 (Y%) | X/20 (Y%) | X/20 (Y%) |
| Aider | X/20 (Y%) | X/20 (Y%) | X/20 (Y%) | X/20 (Y%) |

## Cross-agent averages

| Metric | Average | Threshold | Pass? |
|---|---|---|---|
| M1 (Selection accuracy) | Y% | ≥85% | <yes/no> |
| M2 (Schema compliance) | Y% | 100% | <yes/no> |
| M3 (Execution success) | Y% | ≥70% | <yes/no> |
| M4 (Output quality PASS+BORDERLINE) | Y% | ≥60% | <yes/no> |

## S0 agent eval verdict

**All four thresholds met?** <yes / no>

**Per spec v2.1:**
- If yes → proceed to the S0 decision document (Task 23).
- If no → project pauses for ≥2 calendar weeks and at least one spec assumption must be revised before retry.
```

- [ ] **Step 6: Commit**

```bash
cd ~/Work/campos
git add docs/s0_results/scored.md
git commit -m "docs(s0): score agent eval results against frozen rubric"
```

---

## Task 23: Produce the S0 go/no-go decision document

**Files:**
- Create: `~/Work/campos/docs/s0_decision.md`

- [ ] **Step 1: Write the decision document**

Create `~/Work/campos/docs/s0_decision.md` with:

```markdown
# Campos S0 Decision

**Date:** <ISO date>
**Spec version:** v2.1 (2026-04-05)

## Gates summary

| Gate | Source | Outcome |
|---|---|---|
| Agent eval — M1 selection ≥85% | `docs/s0_results/scored.md` | <pass/fail> |
| Agent eval — M2 schema = 100% | `docs/s0_results/scored.md` | <pass/fail> |
| Agent eval — M3 execution ≥70% | `docs/s0_results/scored.md` | <pass/fail> |
| Agent eval — M4 quality ≥60% | `docs/s0_results/scored.md` | <pass/fail> |
| Audience audit — ≥5 qualifying gaps | `docs/audience_audit.md` | <pass/fail> |
| JSON Schema cross-field constraint round-trip | `python/tests/test_schema.py` | <pass/fail> |
| N3 token exercise verification | `docs/n3_token_verification.md` | <pass/fail> |

## Decision

**All 7 gates pass:** proceed to Plan 2 (infrastructure + S1 first component).

**Any gate fails:** project pauses for a minimum of 2 calendar weeks per spec v2.1 N4. At least one spec assumption must be revised before retry. Stub improvements alone are not sufficient. Three consecutive S0 failures = public post-mortem and project archival.

**Actual outcome:** <proceed / pause / archive>

## If proceeding

Build order for Plan 2 per audience audit N10 rule: <hold / reverse>

Specifically:
- If hold: Plan 2 builds ShotMap first (risk-first, chart-dominant).
- If reverse: Plan 2 builds PlayerHero + PercentileRibbon first (chrome-first per audit).

## If pausing

Spec assumption(s) to revise: <list>
Pause end date: <date>
Retry conditions: <what must change before S0 runs again>

## If archiving

Link to public post-mortem: <URL>
Reason for archival: <which gate failed and why>
```

- [ ] **Step 2: Fill in each row of the gates summary from the preceding artefacts**

Read every source file listed in the gates summary table and fill in pass/fail for each row.

- [ ] **Step 3: Record the decision**

Based on the gates, pick one of: proceed, pause, archive. Fill in the relevant section at the bottom of the document.

- [ ] **Step 4: Commit the decision**

```bash
cd ~/Work/campos
git add docs/s0_decision.md
git commit -m "docs(s0): S0 go/no-go decision

Verdict: <proceed / pause / archive>
Build order for Plan 2: <hold / reverse / n/a>"
```

- [ ] **Step 5: Tag the commit**

If the decision is "proceed":

```bash
cd ~/Work/campos
git tag s0-complete -m "S0 validation passed. Plan 2 proceeds."
```

If the decision is "pause":

```bash
cd ~/Work/campos
git tag s0-paused -m "S0 paused per spec v2.1 N4. Retry after ≥2 weeks with revised assumption."
```

If the decision is "archive":

```bash
cd ~/Work/campos
git tag s0-archived -m "S0 failed terminally. Project archived."
```

---

## Self-review checklist (run before declaring the plan complete)

- [ ] **Spec coverage:** Every item from the spec's "S0 — Validation" stage has a corresponding task in this plan (monorepo scaffolding, schema generator, theme generator, N3 token verification, 3 component stubs, agent eval rubric frozen, 20 task prompts, audience audit methodology, run the evals, run the audit, score, decide).
- [ ] **Placeholder scan:** No "TBD", "TODO", "implement later", "add appropriate error handling", or "similar to Task N" phrases anywhere in this plan. Every code block is complete.
- [ ] **Type consistency:** Function names (`player_hero`, `percentile_ribbon`, `shot_map`, `use_theme`), class names (`Player`, `Club`, `Shot`, `PercentileRow`, `RadarCategory`, `Action`), and file paths are identical wherever they appear.
- [ ] **Commit cadence:** Every task ends with a commit step. Tasks are sized to produce one focused commit each (or two for the test-then-implement tasks).
- [ ] **Gates enforceable:** Every kill-criterion in the spec's S0 measurement plan is testable from the artefacts this plan produces.
