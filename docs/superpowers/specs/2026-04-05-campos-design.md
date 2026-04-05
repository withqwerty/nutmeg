---
title: Campos — football UI component library (multi-flavour-capable monorepo)
status: draft-v2.1
date: 2026-04-05
authors: [rahaluha]
revisions:
  - v1 (2026-04-05): initial draft — shadcn-style registry, dual-flavour, 9 components
  - v2 (2026-04-05): restructured after adversarial review — Python-first pip library from a multi-flavour-capable monorepo, one-way dep from nutmeg, risk-first launch, interim measurement tripwires
  - v2.1 (2026-04-05): second adversarial review surfaced 1 blocker + 7 serious findings around commitment-device enforcement of kill-criteria. v2.1 adds operational discipline without further restructuring. N3 token-file falsification run inline, architecture claims adjusted for honesty.
related:
  - nutmeg (Claude Code plugin — consumes Campos as a PyPI dependency)
  - football-docs (MCP server — architectural sibling, not a dependency)
---

# Campos — design spec (v2.1)

> Beautiful, battle-tested football UI components. Pythonic today, multi-flavour tomorrow.

## Summary

Campos is a standalone, open-source football UI component library. v1 ships as a Python package (`pip install campos`) with 8 components + a design system, all rendering via matplotlib and mplsoccer. The source repository is structured as a **multi-flavour-capable monorepo**: components live in language-neutral folders with a JSON Schema contract for data types and a JSON tokens file for theming. v1 populates only the Python flavour. Future web (HTML + CSS + inline SVG) and React flavours can be added by authoring new flavour files in the same folders — no fork, no schema duplication, no rewritten generators. Adding a new flavour may require *additive* new optional tokens (e.g., motion, pseudo-states) that were meaningless in the first flavour; this is expected and does not break existing flavours. The "zero rework" claim is bounded to existing components and generators, not to the tokens file itself. See "Theme tokens and cross-flavour expressivity" below for the honest account of what the monorepo structure can and cannot promise.

Campos is a separate project from the `nutmeg` Claude Code plugin, with a one-way dependency: nutmeg lists Campos in its `pyproject.toml` and invokes it from a rendering skill. Campos has no awareness of nutmeg, no scraped adapters, no Claude-specific coupling, and no MCP server in v1. It is a Python library that can be used from any script, notebook, Streamlit app, FastAPI endpoint, or Quarto document — with or without Claude Code.

The differentiator is a **12-axis quality bar** every component must pass before shipping: the full edge-case matrix (empty/sparse/dense/missing/extreme/i18n/responsive/themeable/composable/mpl-hygiene/a11y/tested) made visible per component on the docs site. This is what the project is selling — not breadth, not interactivity, but *production-grade* components in a domain where the status quo is one-off gists.

## Motivation and context

The existing Python football viz ecosystem (mplsoccer, soccerplots, plotnine snippets, bespoke Streamlit apps) is stuck in gist culture. Every scouting dashboard reinvents the same components — player cards, percentile ribbons, radars, shot maps, ranked lists — from scratch, with inconsistent quality, no edge-case handling, and no shared design language. The Scout Lab and Teams Lab apps referenced in the brainstorm are evidence of *how good* this work can be when someone fights hard enough; they're also evidence of *how much fighting* it takes to reach that quality inside a framework (Streamlit) that wasn't built for it.

Campos proposes that the right level of abstraction is a component library, not a framework. It does not compete with Streamlit, Marimo, Jupyter, mplsoccer, or any existing tool. It slots underneath them — import a Campos component, hand it canonical data, get back a rendered artefact that looks good and handles every edge case you didn't have time to think about.

## Goals

1. **Be the default football UI primitives** that Python analysts reach for when they want to ship something that looks finished.
2. **Raise the quality floor**, not just the ceiling. A novice using Campos should get the same rendering quality as a Scout-Lab-level expert, because all 12 axes of the quality bar are handled inside the component, not by the caller.
3. **Preserve the option** to add web (HTML/CSS/SVG) and React flavours later *without* rewriting, forking, or duplicating the schema and design tokens.
4. **Stay a library**, not a framework. No app structure, no opinions about state management, no runtime. Every component is a function that takes data and returns a rendered output.
5. **Be discoverable in the Python ecosystem** (PyPI, pip, standard docs tooling), not locked inside Claude Code.

## Non-goals (v1)

- **Web and React flavours in v1.** The monorepo structure preserves these as zero-rework future additions. v1 ships Python only.
- **A CLI or copy-paste distribution model.** Python users expect `pip install`. A shadcn-style CLI is reserved for later — only if and when multiple flavours exist and fork-and-modify becomes the more idiomatic pattern.
- **An MCP server for agent discovery.** Deferred. v1 relies on standard Python introspection, docstrings, type hints, and the docs site. If the agent validation eval (below) shows this is insufficient, an MCP server can be added without architectural change.
- **Scraped data adapters.** Campos accepts *only* canonical schema objects and never touches raw provider data. Adapters for Opta, WhoScored, StatsBomb, Wyscout, etc. live in nutmeg's `acquire` skill where they belong architecturally.
- **Generic UI primitives** (buttons, dropdowns, navs, dialogs). Agents can scaffold these from Campos's theme tokens; Campos stays football-specific on purpose.
- **Team / match / league components.** v1 is scouting-flow and player-oriented. Match heroes, formation diagrams, league projection tables, xG race charts — all v1.x+.
- **Comparison-dedicated components.** `PlayerHero` renders a single entity; a comparison view is a composition of primitives in v1.x.
- **Interactive cross-chart brushing.** Hover tooltips are allowed inside a single component; cross-component linked selection is not a v1 feature.
- **Scatter-with-label-collision** (the ScatterWithLabels component from the v1 draft). Force-directed label placement is a research problem even in matplotlib and does not fit the quality bar for v1. Deferred to v1.x.

## Target users

All three audiences use AI agents as their primary code-authoring surface. None of them will hand-write Campos calls; agents will compose components into their projects.

1. **The ambitious Python analyst** who already ships Streamlit / Marimo / Quarto apps and loses weeks to visual polish. Scout Lab / Teams Lab authors. Has taste, owns their data, wants the design system their work deserves.
2. **The notebook-native analyst** who lives in Jupyter / Quarto / nbdev and wants publication-quality match reports, scouting PDFs, and social-ready images without a web stack. Uses matplotlib natively; Campos feels like a well-styled extension of what they already do.
3. **The agent-assisted app builder** who describes a football dashboard in natural language and expects an agent to produce working code. May have no football viz background; benefits from Campos transparently because the agent picks it.

Common thread: **every design decision is made with "an agent will read and invoke this" as a primary constraint.** Docstrings, type hints, examples, and error messages must be legible to an LLM that has never seen the project before.

## Architecture

### Monorepo with language-neutral truth, language-specific flavours

The source repository is a single Git monorepo with this shape:

```
campos/                             # repo root — one source of truth
├── schema/                         # language-neutral data contracts
│   ├── player.schema.json
│   ├── club.schema.json
│   ├── shot.schema.json
│   ├── action.schema.json
│   ├── percentile_row.schema.json
│   └── radar_category.schema.json
├── theme/                          # language-neutral design tokens
│   └── tokens.json                 # colours, spacing, typography, motion
├── python/                         # Python flavour — v1 PyPI package lives here
│   ├── pyproject.toml              # package name: campos
│   ├── src/campos/
│   │   ├── __init__.py             # public API re-exports
│   │   ├── schema/                 # pydantic types generated from /schema
│   │   ├── theme/                  # matplotlib rcParams generated from /theme
│   │   └── components/
│   │       ├── player_hero.py
│   │       ├── percentile_ribbon.py
│   │       ├── percentile_group.py
│   │       ├── category_score_card.py
│   │       ├── radar_chart.py
│   │       ├── player_table.py
│   │       ├── ranked_list.py
│   │       └── shot_map.py
│   └── tests/
│       ├── fixtures/               # canonical test data — the 12-axis corpus
│       └── components/             # 12-axis snapshot tests per component
├── web/                            # v2+ web flavour — empty in v1
├── react/                          # vN+ React flavour — empty in v1
├── scripts/
│   ├── generate_python_types.py    # /schema → pydantic (src/campos/schema/)
│   └── generate_python_theme.py    # /theme/tokens.json → rcParams module
├── docs/                           # docs site source (Quarto or similar)
└── README.md
```

**Why this layout**

- `schema/` and `theme/` are the truth. Every flavour *generates* or *consumes* them, never duplicates them. A schema change propagates to every flavour automatically via the generator scripts.
- Each language flavour is a self-contained project in its own top-level folder (`python/`, `web/`, `react/`). A flavour can be developed, tested, versioned, and released without touching the others.
- v1 populates only `python/`. `web/` and `react/` are empty placeholders that document *where future flavours go*, making the path from v1 to v2 a matter of adding files, not restructuring.
- Test fixtures live under each flavour because snapshot formats differ (matplotlib SVGs for Python, Playwright screenshots for web). The *inputs* to those fixtures (canonical data) are the same across flavours and can be shared via symlinks or generators when web/react arrive.
- The repo root has a `pyproject.toml` for monorepo-wide dev tooling (linting, formatting, type checking, schema generation), independent of the `python/pyproject.toml` that defines the publishable package.

### Canonical data schema (JSON Schema as source of truth)

Components accept only canonical Campos types. Provider-specific DataFrames are never passed directly.

The canonical schema is defined in **JSON Schema** at `schema/*.schema.json`. This is the single source of truth for data shapes. Language-specific types are *generated* from it:

- **Python**: `scripts/generate_python_types.py` produces pydantic models at `python/src/campos/schema/*.py`.
- **TypeScript** (future, for web/react): a generator will produce `.d.ts` files at `web/src/schema/` and `react/src/schema/`.

v1 canonical types (conceptual — exact field names finalised during implementation):

| Schema | Purpose |
|---|---|
| `Player` | id, name, photo_url?, club_id?, league_id?, nation?, position?, age?, minutes?, birth_date? |
| `Club` | id, name, crest_url?, league_id?, colour_primary?, colour_secondary? |
| `Shot` | x, y (0–1 normalised), xg, body_part, outcome, minute, player_id? |
| `Action` | start_x, start_y, end_x, end_y (0–1), action_type, xt?, outcome, player_id? |
| `PercentileRow` | stat_id, label, category, value, percentile, comparison_percentile? |
| `RadarCategory` | label, value, comparison_value?, max, reversed? |

**Critical constraints:**

- All pitch coordinates are normalised to 0–1 on both axes, never provider-native (120×80, 100×100, etc.). Normalisation is the job of whoever produces the data (in the Campos+nutmeg pipeline, that's nutmeg's acquire skill).
- Every field that can be absent is explicitly optional in the schema. Components handle missing fields as part of the 12-axis quality bar; no field is "assumed present."
- Schema evolution is versioned. Breaking changes bump a major version on the Campos package. Non-breaking additions (new optional fields) are minor version bumps. Deprecation follows semver conventions.

**Generated files are not hand-edited.** All schema changes happen in `schema/*.schema.json`. Generated type files (`python/src/campos/schema/*.py`, future `web/src/schema/*.ts`, etc.) are regenerated on every build and will overwrite any hand edits. If a constraint cannot be expressed in JSON Schema and requires language-specific logic (e.g., cross-field validation like "`Shot.x` and `Shot.y` must both be present or both absent"), that logic lives in a hand-authored `python/src/campos/schema/validators.py` that wraps the generated types — never in the generated files themselves. This preserves the "single source of truth" claim honestly and makes the boundary between generated and hand-written code enforceable.

**Schema governance.** Schema change decisions are owned by Campos maintainers and follow a uniform process regardless of which consumer surfaces the requirement. A change request is accepted only if: (a) there is a demonstrated use case in at least one public Campos-using project, and (b) at least one Campos component that touches the changed field continues to pass its 12-axis quality matrix after the change. The process makes no mention of nutmeg — if nutmeg surfaces a request, it follows the same rules as any other consumer. This keeps the one-way dependency claim honest at the governance layer, not just at the import-statement layer.

**S0 validation for schema approach.** During S0, validate that at least one cross-field constraint in the canonical schema round-trips through JSON Schema → pydantic generation → runtime validation without requiring post-generation hand editing. If it cannot, the generator approach is wrong and needs adjustment before S1 begins (most likely: JSON Schema for structure + `validators.py` for constraints, as described above).

### Theme tokens and cross-flavour expressivity (tested)

`theme/tokens.json` is the single source of truth for design decisions. Language-specific generators (`scripts/generate_python_theme.py` today; future equivalents for web/react) read the tokens file and produce flavour-appropriate artefacts.

**A sketch-and-stub exercise was run before spec commitment** to validate the "language-neutral tokens" claim. Results were partially positive and partially corrective, and the honest outcome is documented here so the architecture promise matches reality.

**What the exercise found:**

CSS can consume every token category in the sketched tokens file directly: colours, typography (family as fallback chain, weight, size, tracking, transform), spacing, radius, and future additions like motion and pseudo-state variants.

Matplotlib can consume the subset listed below and *cannot* consume the remainder:

| Token category | Matplotlib can express? | Notes |
|---|---|---|
| `color.*` | Yes | Direct rcParam mapping. |
| `typography.*.family` (list) | Yes | `rcParams['font.family']` accepts a fallback list. |
| `typography.*.size` | Yes | `rcParams['font.size']`. |
| `typography.*.weight` | Yes | `rcParams['font.weight']`. |
| `typography.*.tracking` (letter-spacing) | **No** | Matplotlib has no letter-spacing rcParam. Must be applied per-`Text` object in component code, or accepted as a visual limitation. |
| `typography.*.transform: uppercase` | **No** | No rcParam. Component code applies `.upper()` manually or uses a different approach. |
| `spacing.*` (in abstract units) | Partial | Unit ambiguity: matplotlib uses points, inches, or figure fractions depending on context. Component code interprets per use site. |
| `radius.*` | **No (global)** | No global border-radius in matplotlib. Applied per-`FancyBboxPatch` in component code. |
| (future) `motion.*` | No | Static figures; motion is meaningless in matplotlib. |
| (future) `state.hover.*`, `state.focus.*` | No | No pseudo-states in matplotlib. |

**Honest claim:** the tokens file is the single source of truth for *design decisions*, but each flavour consumes the subset it can render. Matplotlib cannot express letter-spacing, text transforms, global border-radius, motion, or pseudo-states. When web and React flavours arrive in the future, they will consume more of the tokens file than Python currently does, and they will likely require **additive new optional tokens** (e.g., motion durations, focus-ring colours, hover-state variants) that were meaningless in v1. Additive tokens do not break the Python flavour.

**What this means for v1:** nothing observable. v1 ships Python only, so there is no cross-flavour divergence to see.

**What this means for v2+ (when web arrives):**

- The CSS generator will express tokens that the Python generator ignores, producing visual refinements in the web flavour that Python cannot match. This is a matplotlib limitation, not a Campos limitation, and is acceptable.
- Adding the web flavour will include "extend `tokens.json` with web-relevant optional fields" as part of the flavour work. This is part of the cost of adding a flavour, not evidence against the monorepo approach.
- The "zero rework" claim is therefore bounded: **zero rework to existing components, existing generators, and existing tokens.** New flavour = new generator + possibly additive optional tokens + new flavour files per component. That is still a much lower bar than forking or maintaining a parallel repo.

**What this exercise rules out:** the stronger claim that any Campos component will render identically across flavours. Python components may have known visual limitations vs web on the axes above. The spec no longer makes the stronger claim.

### Distribution (v1)

**v1 = one PyPI package: `campos`.**

```
pip install campos
```

That's the entire install story. There is no CLI. There is no website copy-paste. There is no registry of files to clone. Users `pip install`, `import`, and call functions. Exactly as idiomatic Python expects.

```python
import campos
import matplotlib.pyplot as plt

campos.use_theme("dark")

fig = campos.player_hero(
    campos.schema.Player(name="Michael Olise", club_id="bayern", ...),
    club=campos.schema.Club(id="bayern", name="Bayern München", crest_url=...),
)
plt.show()
```

Docs site (content in `docs/`, built with Quarto or similar) is hosted on GitHub Pages at launch. PyPI package is published from `python/`. No other distribution surface in v1.

### Relationship with nutmeg (one-way dependency)

nutmeg and Campos are **separate projects with a one-way dependency**: nutmeg imports Campos, Campos does not know nutmeg exists. This is the same architectural relationship nutmeg has with `football-docs` today.

Concretely:

1. `nutmeg/pyproject.toml` (the nutmeg Claude Code plugin) adds `campos>=0.1` as a Python dependency.
2. nutmeg adds a new skill (working name: `render`) that imports `campos` and composes components from the data produced by `acquire → wrangle → compute → analyse`.
3. nutmeg's `acquire` skill is updated to output canonical Campos-schema-shaped data wherever sensible, so the render skill can pass acquired data into Campos components directly.
4. Campos has no knowledge of nutmeg's existence anywhere in its source, docs, issues, or release notes. A non-nutmeg Python user should never encounter nutmeg by installing Campos.

This resolves the earlier spec's "independent siblings" fiction: the projects are not siblings, they are a library and a consumer. The coupling is asymmetric, one-way, and completely honest.

**Adapter location (ownership clarification):** scraped data adapters (Opta, WhoScored, and eventually StatsBomb, Wyscout) live **in nutmeg's acquire skill**, not in Campos. They are an acquisition concern, not a rendering concern. Campos accepts canonical schema only. This removes all scraping, all upstream HTML-change on-call burden, and all ToS exposure from Campos entirely.

## Component inventory — v1 (8 components + theme)

All Python flavour. Ordered here by *build priority* (risk-first), not alphabetically.

| Build order | Component | Purpose | Why this position |
|---|---|---|---|
| 1 | **ShotMap** | Pitch plot with xG colour scale, shot-type shapes, companion distribution bee-swarm. Wraps mplsoccer. | **Riskiest component first** (per F3 in review). If the 12-axis bar is unachievable here, the whole plan reshapes. Dogfoods every hard decision: pitch orientation, dense-state handling, legend layout, bee-swarm composability, mplsoccer wrapping discipline. |
| 2 | **RadarChart** | Football-aware radar with category labels, subject polygon, companion category-score tile grid, reversed-scale support. | Second-hardest. Validates label-collision handling at the 3-to-12-category range and tests the "companion grid" composition pattern also used by ShotMap. |
| 3 | **PlayerTable** | Sortable table with crest+name cells, position pills, colour-scaled metric cells. | Third-hardest. Tests dense-state handling (1000+ rows), pandas-Styler integration, and table typography — a different set of edge cases from charts. |
| 4 | **Theme** | `tokens.json` → rcParams. Dark default + light variant + club rebrand tokens. | Not risky, but every subsequent component depends on the theme being stable. Built alongside component 1 and refined iteratively as components 2–3 reveal gaps. |
| 5 | **PlayerHero** | Photo + name + chip row + team-crest watermark + position pill + season badge. The showcase. | Typography + layout, harder than it looks (missing photos, unicode, long names, gradient fallback). First of the "chrome" components. |
| 6 | **PercentileRibbon** | Single labelled bar with value and percentile fill; supports comparison overlay and P90/Total/padj/raw modes. | Simple visually, complex in mode handling. |
| 7 | **PercentileGroup** | Category header + aggregate score + collapsible nested ribbons. | Pure composition on top of PercentileRibbon. Tests composability axis of the quality bar. |
| 8 | **CategoryScoreCard** | Small tile with category label, subject score, optional comparison score. | Smallest, simplest component. Built last as a sanity check on the theme and to fill out the Scout-Lab-style player card grid. |
| 9 | **RankedList** | Rank + crest + name + subtext + value bar. Used for leaderboards and similarity lists via a `mode` prop. | Last. Composition of typography + bar charts. Validates that the theme supports tabular visual rhythm. |

**Total: 8 components + theme. 9 build units.**

**Explicitly deferred to v1.x:** ScatterWithLabels (force-directed label collision is too hard for v1), PlayerComparisonHero (composition on top of PlayerHero), ActionMap, MultiPitchPanel.

**Explicitly deferred to v2+:** match-level components, team/league components, web flavour, React flavour, MCP server, CLI.

## Quality bar (12 axes, Python flavour)

Every component must pass this checklist before it is considered done. Each axis is a row in the component's `README.md` quality matrix with a green/red indicator and a linked snapshot test.

| # | Axis | Pass criteria |
|---|---|---|
| 1 | **Empty** | `None`, empty list, empty DataFrame → graceful placeholder, never raises. |
| 2 | **Sparse** | 1 data point → legends/axes/tooltips sensible, no broken layout assumptions. |
| 3 | **Dense** | 1000+ rows / 500+ shots / 60 list items → no overflow, deterministic truncation, no performance cliff. |
| 4 | **Missing** | `NaN` numerics, `None` strings, absent photos/crests/positions → every field has a fallback. |
| 5 | **Extreme** | Negative percentiles, >100 percentiles, zero minutes, infinite xG, duplicate ranks → no corruption. |
| 6 | **Text edges** | 30-char names, unicode (Ø, ñ, 张伟, Müller), RTL (عمر مرموش), 2-line names, all-caps → typeset, no clipping. |
| 7 | **Responsive** | Matplotlib figure renders at 400 / 800 / 1200 / 1600 px output widths. Print-to-A4 works. |
| 8 | **Themeable** | Dark + light via theme swap. One-line club rebrand by overriding `--campos-accent` (in the tokens layer) / equivalent rcParam (in the matplotlib layer). |
| 9 | **Composable** | Works inside a matplotlib subplot grid, a Streamlit column, a Quarto figure block. Returns `Figure` or `Axes`, never calls `plt.show()`. |
| 10 | **Matplotlib hygiene** | `campos.use_theme()` does not mutate global rcParams beyond the call scope. No side effects on the user's other plots. |
| 11 | **A11y** | Contrast ratios meet WCAG AA on all theme variants. Alt text in figure metadata. Colour is not the only encoding. |
| 12 | **Tested** | Snapshot tests exist for every row above. Fixtures stored in `python/tests/fixtures/`. Tests reproducible by anyone. |

**The checklist is the product.** It is what distinguishes Campos from gist-level football viz. The docs site displays the matrix prominently for every component; green cells are a promise.

### Scope commitment: 8 components, flexible axes (per N6)

The author has committed to the full 8-component scope. Cutting components is not the primary flex mechanism if the calendar pressures the matrix. Instead:

**Flex dimension: axis count, not component count.** If per-component time during S1 averages more than 2 working days per axis, two axes are candidates for deferral from v1 to v1.x:

1. **Axis 11 (A11y)**. WCAG AA contrast, alt text, non-colour encoding. Remains a long-term target but deferrable to v1.x if the v1 calendar cannot hold it. A v1 that ships without A11y green is honest; a v1 that slips 6 months trying to hit A11y is not.
2. **Axis 7 clause: print-to-A4.** The responsive range (400 / 800 / 1200 / 1600 px) stays. The "print-to-A4" sub-clause is deferrable to v1.x.

All 12 axes remain the long-term target. v1 may ship with 10–12 axes green and 0–2 axes "planned for v1.x". This is a **pre-commitment**, not a decision to be made under pressure. The trigger for flexing is pre-stated and countable; the axes that may flex are named in advance.

**Baseline estimate ritual (S1).** Before S1 starts, the author estimates each axis of ShotMap in working hours and commits the estimate to the repo at `docs/estimates/shotmap.md`. Actuals are tracked during S1. If ShotMap's total time exceeds 150% of the estimate, the axis-flex rule fires automatically — Axis 11 defers to v1.x for all subsequent components without re-litigation. Exceeding 200% fires the second flex (Axis 7 A4 clause). Exceeding 250% triggers a full replan.

### Escape hatch with commitment device (per F3 / N2)

If any single component's in-scope axes (after any flexing above) cannot be closed by end of day on the tenth working day, that component is cut from v1 and becomes a v1.x candidate. **The rule is enforced by a commitment device, not by willpower.**

**On day 1 of each component build, the author creates `docs/component_log/{component}.md` containing:**

1. Component name.
2. Start date (absolute YYYY-MM-DD).
3. Cut date (absolute YYYY-MM-DD, ten working days after start).
4. In-scope axes (initially all 12, minus any deferred by the axis-flex rule).
5. The literal text: **"If this component is not green on all in-scope axes by end of day on the cut date, it is cut from v1. This decision is not re-litigated."**
6. A link to a public declaration of the component's start — a tweet, a GitHub issue on the Campos repo, or a blog post — that records the cut date in the public record.

**On day 11 (regardless of outcome) the author posts the result publicly**: either "green, shipped" or "cut, deferred to v1.x." The public posting is the commitment device. Reversing it requires walking back a public declaration, which is a strong enough disincentive to function as self-enforcement.

**Phrasing discipline:** the rule says "not green by end of day on cut date," not "cannot be closed." The subjective "cannot" is the word sunk cost uses when it means "has not yet." The objective phrasing removes the escape route.

Cut components become v1.x candidates automatically. The v1 launch proceeds with whatever components cleared the gate. The measurement plan's "End of S3" tripwire explicitly allows for a v1 that ships with fewer than 8 components; the launch is *not* delayed waiting for cut components to catch up.

## Agent validation (the most important pre-build experiment)

**The entire product thesis depends on agents being effective at picking, reading, and invoking Campos components from natural-language task descriptions.** This is untested. It will be tested before any component is built beyond the seed.

### Experiment design

**Inputs:**

- Stub implementations of 3 components (PlayerHero, PercentileRibbon, ShotMap) with real docstrings, type hints, and minimal working behaviour.
- Canonical schema pydantic types (real, generated from `schema/*.schema.json`).
- A README that describes Campos at the level an LLM will encounter it in a user's project.
- A representative dataset (StatsBomb Open Data for 1–2 players, pre-adapted to Campos schema).

**Tasks:** 20 natural-language prompts of the form:

1. "Build me a player report for Mohamed Salah using the data in `df`."
2. "Show Olise's shot map alongside his top percentile stats."
3. "Make a one-page scouting card I can share on Twitter."
4. "I want to compare two players' shooting output visually."
5. … (15 more variations covering different phrasings, different player archetypes, different output formats)

**Agents tested:** Claude Code, Cursor, one open-source agent (e.g. Aider or Continue).

**Measures:**

- **Selection accuracy:** did the agent pick components that could plausibly satisfy the task?
- **Schema compliance:** did the agent construct valid canonical-schema objects, or did it confabulate field names?
- **Execution success:** did the generated code run without errors?
- **Output quality:** did the rendered result look like what the user asked for? (Rubric-based — see pre-committed rubric below.)

**Pass criteria (all must hold; no single-metric overrides):**

- ≥70% of tasks produce working code on first attempt.
- ≥85% of component selections are reasonable (no confabulated components, no obvious mismatches).
- Zero schema hallucinations (agents do not invent fields that don't exist on Campos types).
- Output quality: ≥60% of outputs score "acceptable" or better on the pre-committed rubric.

**Pre-committed rubric (per N4).** The output-quality rubric is written and committed to `docs/agent_eval_rubric.md` *before* S0 begins, with anchored example outputs for each of the 20 tasks labelled pass/fail/borderline. Rubric cells cover: (a) did the output answer the task's implicit question, (b) are all the stated entities present and correctly labelled, (c) is the composition sensible, (d) are there obvious visual errors (overlap, clipping, wrong colours). Once the rubric is committed it is frozen for the duration of S0 — retroactive softening is not allowed. If the rubric is wrong, it is revised *after* S0 completes and S0 runs again from scratch with the new rubric.

**"Paused" means paused, not retried (per N4).** If S0 fails on any of the four pass criteria, the project pauses for a **minimum of 2 calendar weeks**. During the pause, at least one spec assumption must be revised — target audience, component set, quality bar definition, architectural approach — not just improvements to the eval stubs. Retries that only iterate the stubs or re-score the same outputs are explicitly not allowed. If three S0 cycles in a row fail, v1 is archived with a public post-mortem and the project does not continue in its current form.

**Budget:** 1–2 days of author time to build the stubs, write the 20 tasks, run them against agents, and score the results. This runs *before* any component build work and is the cheapest available falsification of the core thesis.

## Audience validation (the F1 experiment)

Running in parallel with the agent eval:

- **Find 5 existing open-source Python football apps** on GitHub that hand-rolled components Campos proposes to provide.
- **For each, identify the specific component and measure the gap** against the pre-committed definition below.
- **Record findings** in `docs/audience_audit.md`, committed to the repo.

**Qualifying gap definition (pre-committed per N4).** A qualifying gap is a component in an existing open-source Python football app where the author wrote **≥50 lines of custom matplotlib / styling / layout code** that Campos's proposed API would have replaced with **≤10 lines**. The line counts are measured on the final code as checked in, not on drafts. This definition is pre-committed and will not be softened during the audit. Styling tweaks of <50 lines are not gaps; they are polish, which mplsoccer and existing tools already support.

**Pre-committed audit → build-order mapping (per N10).** The scope remains 8 components regardless of audit outcome (per author decision). The audit's output determines *build order within S1–S3*, not *whether components exist in v1*:

- **If ≥4 of 5 qualifying gaps are in chart components** (shot maps, radars, tables): current build order holds — ShotMap → RadarChart → PlayerTable → Theme → chrome.
- **If ≥4 of 5 qualifying gaps are in chrome components** (hero, ribbons, tiles, lists): **build order reverses** — PlayerHero → PercentileRibbon → PercentileGroup → CategoryScoreCard first, then charts. Chrome becomes the S1 risk gate. ShotMap drops to S2 or S3.
- **If gaps are evenly distributed** (e.g., 2 chart + 2 chrome + 1 other): current build order holds.

This rule fires automatically based on the audit results. The author does not re-evaluate the scope decision in the moment.

**If fewer than 5 qualifying gaps are found:** the audience is smaller than assumed. Per N4's "paused means paused" rule, the project pauses for at least 2 weeks and the target-users section is revised before S1 begins.

This audit costs ~half a day and is a prerequisite to committing build time.

## Launch plan (risk-first ordering)

| Stage | Content | Gate |
|---|---|---|
| **S0 — Validation** | Agent eval (20 tasks, 3 stub components) + audience audit (5 GitHub apps) + JSON-Schema round-trip test + N3 token exercise verification | Pass/fail decision before any real implementation begins. |
| **S1 — Risk-first dogfood** | Build ShotMap (or chrome lead per N10 audit outcome) to full in-scope-axes green. **In parallel, build a PlayerHero stub** — not full-green, but fully typographically styled with a realistic player profile — to force the theme to answer display-typography, unicode, gradient-fallback, and photo-framing questions during theme design rather than discovering the gaps in S3 (per N7). Theme built from the union of both components' requirements. | Component #1 closes its in-scope axes by end of day on cut date. Commitment-device rule (see Quality bar section) applies. |
| **S2 — Chart dogfood (or chart catch-up if chrome-first per audit)** | Build remaining charts to green. | Confirms chart-heavy components are all achievable within the adjusted scope/axis flex. |
| **S3 — Remaining components** | Build whichever components have not yet shipped. | All 8 components + theme on main. |
| **S4 — Private beta** | 3–5 named friendly users from Python football community install `campos==0.1.0rc1` and attempt to build something. | Interim success metric (see measurement plan). |
| **S5 — Public v1.0** | Announcement, docs site, blog post, nutmeg plugin integration. | All 8 components' in-scope axes green + nutmeg acquire readiness gate (see measurement plan). |

Each stage has a kill-criterion (see measurement plan). No stage is allowed to start before the previous stage's gate has been passed.

**N7 rationale:** building the theme by iterating only against charts will produce a charts-theme. PlayerHero's typography needs (display weight at 32px+, unicode handling, gradient backgrounds, photo framing) are not expressed by ShotMap's needs (axis labels, small-caps legends, categorical colour encoding). Building a PlayerHero stub in parallel with ShotMap in S1 forces the theme to answer both sets of questions during theme design. The stub is not counted as a delivered component; its job is to stress-test the theme.

## Measurement plan (interim tripwires)

The v1 (2026-04-05) draft listed 5 success criteria all measured at month 6. That is not a measurement plan; it is an obituary. v2 added interim tripwires; v2.1 tightens them with commitment devices and dependency gates.

| Checkpoint | Signal | Kill-criterion |
|---|---|---|
| **End of S0** (~1 week in) | Agent eval ≥70% / ≥85% / 0 hallucinations / ≥60% rubric-acceptable + audience audit ≥5 qualifying gaps + JSON Schema cross-field constraint round-trips successfully + N3 tokens exercise confirms bounded-multi-flavour claim holds | If any fail: project pauses ≥2 calendar weeks. At least one spec assumption must be revised before retry. Three consecutive S0 failures = public post-mortem and archival. |
| **End of S1** (~3 weeks in) | ShotMap closes in-scope axes by end of its cut date per the commitment device. Actual time tracked against the baseline estimate at `docs/estimates/shotmap.md`. | If actual > 150% of estimate: Axis 11 (A11y) defers to v1.x automatically for all subsequent components. If > 200%: Axis 7's A4 clause also defers. If > 250%: full replan. |
| **End of S3** (~8 weeks in) | All 8 components on main, majority with in-scope axes green | If <5 components are green on in-scope axes, delay public launch and narrow v1 to whatever cleared the gate. |
| **End of S4** (~10 weeks in) | **≥1 beta user publishes a public artefact** (public repo, tweet, blog post, PR to their own project) using Campos, where the only author involvement is via the public record (README, public docs, merged public GitHub issues, public blog posts, public examples). Private DMs, voice/video calls, pair-debugging, and one-on-one code review do **not** count. | If zero public artefacts from beta users meet the strict "public help only" bar, the audience signal from S0 was misleading. Delay public launch; reconsider target users per the N4 "paused" rule. |
| **Pre-S5 nutmeg readiness gate** (per N5) | nutmeg's `acquire` skill can emit Campos-schema-shaped data from **≥1 provider used by ≥3 of the S0 audience-audit apps**. Note: Scout-Lab-type authors typically use FBref / Opta / WhoScored scrapes, not StatsBomb Open Data. If acquire can only produce StatsBomb Open Data, the target-audience coverage at launch is limited. | If nutmeg's acquire is not ready for any provider the target audience actually uses: either delay Campos v1.0 launch, **or** launch explicitly limited to StatsBomb Open Data AND revise the target-users section to match. The mismatch is made visible, not hidden. |
| **v1.0 launch + 1 month** | ≥100 PyPI downloads from non-author sources (measured via PyPI stats) + ≥1 external GitHub star from outside the author's network + ≥1 unsolicited issue or question | If any fail: distribution strategy needs rework before investing in v1.1. Name recognition test (open question #6) runs now if it hasn't already. |
| **v1.0 launch + 3 months** | ≥1 external contribution (bug report, PR, theme variant, or new fixture) | If zero: adoption is shallower than raw install counts suggest. Pause v1.x feature work and investigate. |
| **v1.0 launch + 6 months** | The long-term success criteria (see below) | Final check. |

**Strict phrasing of kill-criteria (per N8).** "Direct author help" in the S4 tripwire is defined negatively above: any content a beta user could have accessed without contacting the author directly counts as "no help." Anything private — DMs, calls, pair-debugging — does not.

## Success criteria (long-term, 6-month terminal)

1. At least one independent developer has shipped a public football app using Campos, without direct help from the author.
2. At least one Claude Code user has asked `/nutmeg` to "build me a scouting dashboard" and received a working Campos-based app.
3. The quality matrix is fully green across the 8 components.
4. At least 5 external contributions (bug reports, PRs, theme variants, new fixtures).
5. At least 100 PyPI downloads per month from non-author sources.

(Vibes metrics like "someone made the camponents joke on football Twitter" have been removed. They were not measurable signals.)

## What this spec explicitly does NOT adopt from shadcn

The previous draft leaned heavily on the shadcn analogy. The adversarial review correctly pointed out that shadcn's preconditions (React monoculture, copy-paste-comfortable audience, primitives not domain objects) don't transfer to Python football viz. v2 takes only the one idea from shadcn that genuinely transfers:

- **Multi-flavour-capable source structure**: the ability to add new language flavours without duplicating schema or forking the repo.

It does **not** adopt:

- The copy-paste distribution model (Python users expect `pip install`).
- The CLI (unnecessary without copy-paste).
- The "you own the source and modify freely" ethos (users modify via theme tokens and component props; deep customisation means forking, same as any library).
- The registry website pattern (the docs site is a docs site, not a source registry).
- The claim that shadcn's success validates Campos's model (it doesn't; Campos is a new pattern in a new domain).

This is a Python library with a monorepo structure that *keeps options open*, not a shadcn clone.

## Open questions

1. **Docs site tooling.** Quarto, MkDocs Material, Sphinx, or something custom? Leaning Quarto because it handles matplotlib figure embedding natively and matches the target audience's existing tooling.
2. **Snapshot testing tooling.** `pytest-mpl` (matplotlib image comparison) for v1. Tolerance thresholds, baseline regeneration workflow, and fixture storage strategy all need to be pinned during S1.
3. **Schema-to-pydantic generator choice.** `datamodel-code-generator` is the obvious pick. Confirm during S0.
4. **Python version floor.** 3.10, 3.11, or 3.12? Leaning 3.10 for compatibility with the Streamlit / Marimo install base.
5. **Matplotlib version floor.** 3.7+ for tight integration with the latest typography features; mplsoccer's own floor will constrain this.
6. **Name final-check.** "Campos" vs distribution-friendlier alternatives (pitchkit, etc.). Reviewer flagged this as identity-over-distribution. Test by describing Campos to 5 Python analysts and measuring recognition before buying a domain.
7. **Licence.** MIT for v1. Contribution-back clause for anyone shipping commercial products on top? Out of scope for v1; flag for v1.x.
8. **nutmeg `render` skill scope.** Is it a new skill, or a capability added to the existing `analyse` skill? Decision belongs in nutmeg's repo, not this spec, but the coupling is worth noting.

## Summary of changes from v1 → v2 → v2.1

The v1 (2026-04-05 earlier-same-day) draft proposed a shadcn-style dual-flavour registry with a CLI, MCP server, scraped adapters, and 9 components each maintained in two flavours. First adversarial review identified 4 blockers and 5 serious findings; v2 restructured the architecture in response. Second adversarial review cleared the structural blockers but surfaced 1 new blocker and 7 serious findings, all clustering around operational discipline — "v2 articulates discipline but doesn't operationalise it into commitment devices." v2.1 adds the commitment devices and tightens definitions without restructuring.

### v1 → v2 (architecture)

| Finding | v1 position | v2 position |
|---|---|---|
| **F1** — Audience evidence asserted, not shown | No evidence | S0 audience audit is a build gate |
| **F2** — Dual-flavour maintenance burden infeasible solo | 9 × 2 × 12 = 216 cells | 8 × 1 × 12 = 96 cells; web flavour deferred but structurally enabled |
| **F3** — Launch order starts with easy components | Seed = PlayerHero, PercentileRibbon, ShotMap | Build order 1 = ShotMap (hardest first); 10-day escape hatch per component |
| **F4** — Scraped adapters = unacknowledged op debt | Adapters in Campos | Adapters moved to nutmeg entirely; Campos accepts canonical schema only |
| **F5** — Agent-first premise unvalidated | Asserted | S0 agent eval (20 tasks, 3 thresholds) is a build gate |
| **F6** — "Independent siblings" fiction | 5 mutual integration points | One-way dependency: nutmeg → campos. Campos has zero nutmeg awareness |
| **F7** — shadcn analogy doesn't transfer | Implicit validation | Explicit rejection of shadcn distribution model; only the monorepo-structure idea is retained |
| **F8** — Scope cuts breadth but kept hardest components | 9 components including ScatterWithLabels | Dropped ScatterWithLabels; kept chart-heavy per author's "complexity is where the value is" call; risk-first ordering + 10-day escape hatch |
| **F9** — "Campos" name is identity-work | Committed | Deferred until docs site decision; recognition test added to open questions |
| **F10** — No interim tripwires | Single 6-month terminal | Six interim checkpoints with explicit kill-criteria |

### v2 → v2.1 (operational discipline)

Second review credited v2 with clearing F4, F6, F7, part of F8, F9, and most of F10. Remaining findings addressed:

| Finding | v2 position | v2.1 position |
|---|---|---|
| **N1** — Schema is a shared contract despite one-way code dep | No governance statement | Schema-governance subsection; uniform process applies to all consumers, nutmeg not named |
| **N2** — 10-day escape hatch has no enforcement mechanism (BLOCKER) | "Enforced by the author on themselves" | `docs/component_log/` start-date + cut-date ritual; public day-1 declaration; mandatory day-11 public posting (green or cut); phrasing changed from "cannot be closed" to "not green by end of day on cut date" |
| **N3** — Tokens file probably Python-shaped; untested | Asserted language-neutral | Sketch-and-stub exercise run inline; findings documented honestly. Tokens file *is* single source of truth for design decisions, but each flavour consumes its expressible subset. Matplotlib cannot express letter-spacing, transforms, global radius, motion, or pseudo-states. "Zero rework" claim bounded to existing components and generators; additive new optional tokens expected when new flavours arrive. |
| **N4** — S0 gates soft on author-scored rubric and undefined "pause" | Author-scored rubric; pause undefined | Pre-committed rubric at `docs/agent_eval_rubric.md` frozen during S0; "pause" = minimum 2 calendar weeks + at least one spec assumption must change; 3 consecutive failures = archival |
| **N5** — Complexity moved to nutmeg still on author's calendar | Deferred as "nutmeg's problem" | Pre-S5 nutmeg readiness gate added to measurement plan: acquire skill must emit Campos-schema data from a provider the target audience uses, or launch is delayed / target audience is revised |
| **N6** — 96-cell timeline vs solo calendar unvalidated | Implicit | Axis-flex rule: if per-axis time during S1 exceeds 2 days average, Axis 11 (A11y) defers to v1.x automatically. Second trigger at 200%: Axis 7 A4 clause defers. Full replan at 250%. Baseline estimate ritual commits time estimates before S1 begins. Per author: scope stays at 8 components; flex is axis count, not component count |
| **N7** — Theme built from charts will misfit chrome | Theme alongside ShotMap only | S1 revised to build ShotMap **and a PlayerHero stub** in parallel. Stub forces theme to answer display-typography, unicode, gradient, and photo-framing questions during theme design |
| **N8** — "Direct author help" undefined | Soft phrase | Strict phrasing: only content accessible via public record (README, public docs, merged public issues, blog posts, public examples) counts as "no help." DMs, calls, pair-debugging, private code review explicitly excluded |
| **N9** — JSON-Schema → pydantic generator untested | Named but unvalidated | "Generated files are not hand-edited" rule committed; S0 cross-field-constraint round-trip test added; fallback approach (JSON Schema + `validators.py`) named in case of generator limitation |
| **N10** — S0 audit has no pre-committed scope-change rule | "Can drop charts" language (permissive, not mandatory) | Scope stays 8 components per author decision. Audit output determines **build order**, not component count: ≥4/5 chrome gaps → reverse build order (chrome first), ≥4/5 chart gaps → current order, mixed → current order. Rule fires automatically |
