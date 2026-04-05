---
title: Campos — football UI component library (multi-flavour-capable monorepo)
status: draft-v2
date: 2026-04-05
authors: [rahaluha]
revisions:
  - v1 (2026-04-05): initial draft — shadcn-style registry, dual-flavour, 9 components
  - v2 (2026-04-05): restructured after adversarial review — Python-first pip library from a multi-flavour-capable monorepo, one-way dep from nutmeg, risk-first launch, interim measurement tripwires
related:
  - nutmeg (Claude Code plugin — consumes Campos as a PyPI dependency)
  - football-docs (MCP server — architectural sibling, not a dependency)
---

# Campos — design spec (v2)

> Beautiful, battle-tested football UI components. Pythonic today, multi-flavour tomorrow.

## Summary

Campos is a standalone, open-source football UI component library. v1 ships as a Python package (`pip install campos`) with ~8 components + a design system, all rendering via matplotlib and mplsoccer. The source repository is structured as a **multi-flavour-capable monorepo**: components live in language-neutral folders with a JSON Schema contract for data types and a JSON tokens file for theming. v1 populates only the Python flavour. Future web (HTML + CSS + inline SVG) and React flavours can be added file-by-file without forking the project, duplicating schemas, or maintaining separate repositories.

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

**Escape hatch (per F3):** if any single component's 12-axis matrix cannot be closed in 10 working days, that component is cut from v1 and the launch proceeds with the remaining components. No sunk-cost grinding. The 10-day rule is committed *before* building begins and enforced by the author on themselves.

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
- **Output quality:** did the rendered result look like what the user asked for? (Manual rubric, author-scored.)

**Pass criteria:**

- ≥70% of tasks produce working code on first attempt.
- ≥85% of component selections are reasonable (no confabulated components, no obvious mismatches).
- Zero schema hallucinations (agents do not invent fields that don't exist on Campos types).

**If the experiment fails** (below the pass thresholds), the design assumptions in this spec are wrong and the project is paused for a rethink. The entire post-agent-validation plan is conditional on passing this eval.

**Budget:** 1–2 days of author time to build the stubs, write the 20 tasks, run them, and score the results. This runs *before* the full build phase and is the cheapest available falsification of the core thesis.

## Audience validation (the F1 experiment)

Running in parallel with the agent eval:

- **Find 5 existing open-source Python football apps** on GitHub that hand-rolled components Campos proposes to provide.
- **For each, identify the specific component and the gap** — what was hand-written, why wasn't mplsoccer/an existing library sufficient?
- **If you cannot find 5**, the audience is smaller than assumed and the scope should contract (or the project should pause).
- **If the gaps all cluster around Typography/Layout components** (PlayerHero, PercentileRibbon, etc.), the reviewer's scope concern (F8) is validated and Campos can afford to drop the chart components from v1 in favour of a focused ship.
- **If the gaps are chart components** (shot maps, radars, tables), the current scope is validated.

This audit costs ~half a day and is a prerequisite to committing build time.

## Launch plan (risk-first ordering)

| Stage | Content | Gate |
|---|---|---|
| **S0 — Validation** | Agent eval (20 tasks, 3 stub components) + audience audit (5 GitHub apps) | Pass/fail decision before any real implementation begins. |
| **S1 — Risk-first dogfood** | Build ShotMap (hardest) to full 12-axis green. Theme built alongside. | If ShotMap closes in ≤10 days, scope is survivable. If not, re-plan. |
| **S2 — Chart dogfood** | Build RadarChart + PlayerTable to full green. | Confirms chart-heavy components are all achievable. |
| **S3 — Chrome build-out** | Build PlayerHero, PercentileRibbon, PercentileGroup, CategoryScoreCard, RankedList. | Typography/layout components. Should be fastest stage. |
| **S4 — Private beta** | 3–5 friendly users from Python football community install `campos==0.1.0rc1` and attempt to build something. | Interim success metric (see measurement plan). |
| **S5 — Public v1.0** | Announcement, docs site, blog post, nutmeg plugin integration. | Full 8 components + theme green on all 12 axes. |

Each stage has a kill-criterion (see measurement plan). No stage is allowed to start before the previous stage's gate has been passed.

## Measurement plan (interim tripwires)

The v1 (2026-04-05) draft listed 5 success criteria all measured at month 6. That is not a measurement plan; it is an obituary. v2 adds interim tripwires so the project can fail fast if the thesis is wrong.

| Checkpoint | Signal | Kill-criterion |
|---|---|---|
| **End of S0** (~1 week in) | Agent eval ≥70% / ≥85% / 0 hallucinations + audience audit finds ≥5 real gaps | If any fail, pause and rethink the product. Do not proceed to S1. |
| **End of S1** (~3 weeks in) | ShotMap closes 12-axis matrix in ≤10 working days | If it takes >15 days, cut scope by 1–2 chart components. If it takes >20, cut all charts and reassess whether Campos is viable. |
| **End of S3** (~8 weeks in) | All 8 components + theme on main, half with green matrices | If <4 components are green, delay public launch and narrow scope. |
| **End of S4** (~10 weeks in) | ≥1 beta user ships something without direct author help; ≥3 unsolicited feature/bug reports | If neither happens, the audience signal from S0 was false and the library is solving a problem the audience doesn't have. Delay public launch; reconsider target users. |
| **v1.0 launch + 1 month** | ≥5 installs from non-author PyPI downloads; ≥1 external GitHub star from outside the author's network | If either fails, distribution strategy needs rework before investing in v1.1. |
| **v1.0 launch + 6 months** | The original 5 success criteria (see below) | Final check. |

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

## Summary of changes from v1 → v2

The v1 (2026-04-05 earlier-same-day) draft proposed a shadcn-style dual-flavour registry with a CLI, MCP server, scraped adapters, and 9 components each maintained in two flavours. Adversarial review identified 4 blockers and 5 serious findings. v2 responds as follows:

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
