---
title: Campos — football UI component registry
status: draft
date: 2026-04-05
authors: [rahaluha]
related:
  - nutmeg (Claude Code plugin, sibling project)
  - football-docs (MCP server, reference architecture for Campos MCP)
---

# Campos — design spec

> Beautiful, battle-tested football UI components. Shadcn for football.

## Summary

Campos is a copy-paste component registry for football data applications. It ships production-quality, football-specific UI components — player heroes, percentile ribbons, radar charts, shot maps, scouting tables — in two flavours per component: a **Python** flavour (matplotlib / mplsoccer) and a **web** flavour (framework-agnostic HTML + CSS + inline SVG). It is MIT-licensed, open source, and distributed as a shadcn-style registry: users copy source files into their own projects via a CLI, own the code, and modify freely.

Campos is a sibling to the `nutmeg` Claude Code plugin. nutmeg helps agents *acquire, wrangle, compute, and analyse* football data; Campos helps agents *render* it. Together they form a complete agent-driven football analytics pipeline, but each can be adopted independently.

## Goals

1. **Raise the ceiling of what a Python football analyst can ship visually**, without asking them to learn React, fight Streamlit CSS, or hire a designer.
2. **Be the default UI vocabulary for agent-generated football apps.** When an LLM writes football code, Campos is what it reaches for.
3. **Meet a production quality bar**, not a demo quality bar. Every component handles every edge case. No loose ends.
4. **Stay complementary to the existing Python football ecosystem** (matplotlib, mplsoccer, Streamlit, Marimo, Jupyter, Quarto, FastAPI). Never compete with it. Slot into any of them.
5. **Ship a visibly complete scouting dashboard** in v1 — enough components to build a Scout-Lab-quality player-oriented app end-to-end.

## Non-goals (v1)

- **Generic UI primitives** (buttons, dropdowns, navs, dialogs). Agents can scaffold these from the theme tokens; Campos stays football-specific on purpose.
- **A React flavour.** Framework-agnostic HTML+CSS+SVG works inside React, Vue, Astro, Streamlit, Quarto, and email. A React flavour is v2+ if demand materialises.
- **A hosted service.** Campos is a registry and a CLI. No accounts, no servers, no billing.
- **Team / match / league-level components.** v1 is scouting-dashboard-shaped and player-oriented. Match heros, formation diagrams, league projection tables, xG race charts — all v2.
- **Comparison views** as standalone components. `PlayerHero` handles a single entity; a comparison is a v2 composition on top.
- **Interactive brushing / linked views** across components. Hover tooltips are acceptable; cross-chart selection is not a v1 feature.

## Target users

Campos serves three overlapping audiences, all using AI agents to write their code:

1. **The Python analyst who already ships Streamlit apps** (the Scout Lab / Teams Lab authors). They have taste, they know their data, they lose weeks to custom CSS and HTML component workarounds. Campos gives them the design system their apps already deserve, without the fight.
2. **The notebook-native analyst** who works in Jupyter / Quarto / nbdev and wants publication-quality artefacts (match reports, scouting PDFs, social-ready cards) without learning a web stack. They use the Python flavour exclusively.
3. **The app builder** who is scaffolding a football dashboard with an AI agent. They may not have any football viz background at all — the agent handles that. They benefit from Campos without knowing they are using it, because the agent picks it.

Common thread: **none of them will write Campos code by hand.** They will describe what they want, and an agent (Claude Code, Cursor, Copilot) will compose Campos components into their project. Every design decision below is made with "an agent will read this" as the primary constraint.

## Architecture

### Two flavours per component

Every component ships in two parallel implementations:

| Flavour | Output | Primary use |
|---|---|---|
| **`python`** | Returns a matplotlib `Figure` (or `Axes` for composables) | Notebooks, scripts, Quarto, static exports, PDF reports, Twitter posts |
| **`web`** | Returns an HTML string (inline SVG for charts, CSS variables for theming, optional vanilla JS for hover) | Streamlit `st.html()`, Marimo, FastAPI responses, Astro, Quarto HTML, email, any web framework |

The web flavour is **framework-agnostic**. No React, no build step, no npm install. HTML that any framework can drop in trivially.

Component authors write both flavours and maintain them in parallel. The quality bar (below) applies independently to each.

### Canonical data schema (S1)

Components accept **only** a canonical Campos schema, never provider-specific DataFrames. Messiness is isolated to adapters.

```python
# conceptual — exact types TBD in implementation plan
campos.schema.Player        # id, name, photo_url, club_id, league_id, nation, position, age, minutes
campos.schema.Club          # id, name, crest_url, league_id, colour_primary, colour_secondary
campos.schema.Shot          # x, y (normalised 0-1), xg, body_part, outcome, minute, player_id
campos.schema.Action        # start_x, start_y, end_x, end_y, action_type, xt, outcome, player_id
campos.schema.PercentileRow # stat_id, label, category, value, percentile, comparison_percentile?
campos.schema.RadarCategory # label, value, comparison_value?, max
```

Coordinates are always normalised to 0–1 (both axes) so pitch plots are provider-agnostic. Adapters do the conversion.

### Adapters

v1 ships **two adapters**, deliberately chosen for the widest reach at launch: both are Opta-lineage and both are scrapable by end users, so no paid API access is required to use Campos.

| Adapter | Schema source | Notes |
|---|---|---|
| **Opta** | Scraped theanalyst.com feeds — event stream + f9 season stats + qualifier taxonomy | Schema reference lives in [`withqwerty/www`](file:///Volumes/WQ/projects/www): `docs/OPTA-DATA-ATLAS.md`, `data/opta-definitions/opta-events.json`, `opta-f9-stats.json`, `opta-qualifiers.json`. Coordinate system normalises to 0–1; qualifier codes map to Campos action types. |
| **WhoScored** | Scraped WhoScored match centre data | Also Opta-sourced downstream, so schema overlap with the Opta adapter is substantial — much of the adapter code is shared. Slightly different event taxonomy and a coarser qualifier set; adapter handles the translation. |

Both adapters deliberately target **scrapable** sources. Paid-tier adapters (StatsBomb, Wyscout, Stats Perform Opta Sports API) are explicit v2 candidates, added once the core registry is proven. This keeps v1's addressable audience as wide as possible — any hobbyist with a Python script and a bit of patience can use Campos.

Adapters live at `campos.adapters.<provider>` and expose a flat API:

```python
campos.adapters.opta.to_shots(df) -> list[Shot]
campos.adapters.opta.to_players(df) -> list[Player]
campos.adapters.whoscored.to_actions(df) -> list[Action]
# etc.
```

Because both v1 adapters share Opta lineage, Campos can ship a shared `campos.adapters._opta_base` module that handles the common qualifier translation, with thin provider-specific wrappers on top. This keeps the battle-testing burden manageable — the hardest transformation logic is written and tested once.

The nutmeg plugin's `acquire` skill can return data pre-adapted to Campos schema, so the common end-to-end agent flow is: *acquire → canonical → Campos component → rendered output* with no manual mapping.

### Registry structure

Campos is distributed as a GitHub repository with a registry layout modelled on shadcn:

```
campos/
├── registry/
│   ├── components/
│   │   ├── player-hero/
│   │   │   ├── python.py          # matplotlib Figure
│   │   │   ├── web.html           # HTML + inline SVG + CSS
│   │   │   ├── meta.json          # name, description, deps, props, flavours, tags
│   │   │   └── README.md          # usage, examples, edge cases, quality matrix
│   │   ├── percentile-ribbon/
│   │   └── ...
│   ├── theme/
│   │   ├── dark.css               # CSS variables
│   │   ├── light.css
│   │   └── rcparams.py            # matplotlib rcParams
│   ├── schema/
│   └── adapters/
├── cli/
│   └── campos                     # Python CLI (campos add, campos list, campos init)
├── site/                          # registry website (Astro or similar, static)
└── mcp/                           # MCP server exposing the registry to agents
```

### CLI

```bash
campos init                         # sets up theme in user's project
campos add player-hero              # agent-detects flavour, copies file in
campos add player-hero --flavour web
campos list                         # lists available components
campos list --flavour python
campos doctor                       # checks theme is installed correctly
```

The CLI is Python (`pip install campos`) so it works in any Python project. For pure-web projects without Python, users copy files directly from the registry site.

### MCP server (agent-native discovery)

An MCP server exposes the component registry to agents directly, the same way `football-docs` exposes provider documentation to nutmeg today:

```
mcp__campos__list_components()
mcp__campos__search_components(query: str)   # "show player progression over seasons"
mcp__campos__get_component(name, flavour)    # returns source + README + props
mcp__campos__get_theme_tokens()
```

This is the primary agent integration surface. The CLI is for humans; MCP is for agents. In practice agents will use MCP to discover and read components, then call the CLI (via Bash tool) to install them.

## Component inventory — v1 (9 components + theme)

All components exist in both `python` and `web` flavours unless noted.

| # | Component | Purpose | Hardest edge cases |
|---|---|---|---|
| 0 | **Theme** | CSS variables + matplotlib rcParams. Dark default, light variant, token-based rebrand. | Collision with user's existing matplotlib rcParams; CSS specificity inside Streamlit iframes. |
| 1 | **PlayerHero** | Photo + name + chip row (nation / league / club / age / mins) + team-crest watermark + position pill. The centrepiece. | Missing photo (fallback initials); very long names; unicode; RTL names; missing crest; missing position; 2-line name; gradient fallback when no crest colour known. |
| 2 | **PercentileRibbon** | Single labelled bar: stat name + value + percentile fill. | `NaN` percentile; negative values; values >100; zero minutes; comparison overlay; P90 vs Total mode; padj vs raw toggle. |
| 3 | **PercentileGroup** | Collapsible category header with aggregate score + nested ribbons. | Single-ribbon group; 20-ribbon group; missing aggregate; categories with zero eligible stats. |
| 4 | **CategoryScoreCard** | Small tile: category label + subject score (+ optional comparison score). Grid-composable. | Missing comparison; score >100; negative deltas; narrow viewport reflow. |
| 5 | **RadarChart** | Football-aware radar: category labels around edge, subject polygon, optional comparison polygon, percentile rings, companion category-score tile grid. | 3 categories (minimum); 12 categories (maximum, label collision); missing categories; ties; reversed scales (lower=better stats like xGA). |
| 6 | **PlayerTable** | Sortable football-flavoured table: crest+name cell, position pill cell, colour-scaled metric cells, minutes cell, alternating row treatment. | 1000+ rows (virtualisation in web flavour); missing crests; tied values; mixed data types; column sorting state; column overflow. |
| 7 | **RankedList** | Rank + crest + name + subtext (club, pos) + value bar. Reused for leaderboards *and* similarity via a `mode` prop. | Tied ranks; 100 rows; very short value ranges; missing crests; subtext overflow. |
| 8 | **ShotMap** | Hex-binned or point-based shot map with xG colour scale, shot-type shape encoding, legend, companion distribution bee-swarm ("you are here"). Python flavour wraps mplsoccer. | 0 shots; 1 shot; 500 shots; missing xG; shot on top of shot; pitch orientation (attack L→R or R→L); mirrored for away view. |
| 9 | **ScatterWithLabels** | Scatter plot with top-N player annotations, league-colour legend, highlight list, optional quadrant lines. | Label overlap (force-directed layout in web, adjustText in python); very clustered data; missing values; highlight of non-existent player; log-scale axes. |

Explicitly **not** in v1: PlayerComparisonHero, ActionMap, MultiPitchPanel, MatchHero, TrendLine, XGRace, PassNetwork, FormationDiagram, LeagueHeatmapTable, SeasonProjectionTable.

## Quality bar

Every component, in every flavour, must pass this 12-axis state-coverage checklist before it ships. Each axis is a row in the component's README quality matrix, with a green/red indicator and a linked snapshot test.

| # | Axis | What "pass" means |
|---|---|---|
| 1 | **Empty** | `None` / empty DataFrame / empty list renders a graceful placeholder with explanatory text. Never raises. |
| 2 | **Sparse** | 1 data point works without broken layouts (legends, gridlines, axes, tooltips all render sensibly). |
| 3 | **Dense** | 1000+ rows / 500+ shots / 60 list items renders without overflow, label collision, or performance issues. Deterministic truncation where needed. |
| 4 | **Missing** | `NaN` numerics, `None` strings, missing photos/crests/positions all have fallbacks. Every field has a defined empty-state. |
| 5 | **Extreme values** | Negative percentiles, >100 percentiles, zero minutes, infinite xG, duplicate ranks: handled without corruption. |
| 6 | **Text edges** | 30-character names, unicode (Ø, ñ, 张伟, Müller), RTL (عمر مرموش), 2-line names, all-caps: typeset correctly, no clipping. |
| 7 | **Responsive** | Renders at 400px (mobile), 800px (embed), 1200px+ (dashboard). Print-to-A4 works for static outputs. |
| 8 | **Theming** | Dark + light via CSS variables. One-line club rebrand by swapping `--campos-accent` and `--campos-surface`. |
| 9 | **Composability** | Works inside a CSS grid, flex column, scroll container, Streamlit column, Quarto callout. No fixed positioning. |
| 10 | **Matplotlib hygiene** | Python flavour respects `campos.use_theme()` without polluting the user's other plots. Figure is returned, never shown. |
| 11 | **A11y** | Semantic HTML, alt text on images, `aria-label` on SVG, keyboard focus order, WCAG AA contrast. |
| 12 | **Tested** | Snapshot tests exist for every row above. Fixtures stored in the registry so anyone can reproduce. |

**This checklist is the product.** It is the single biggest differentiator versus the status quo (where football viz components are one-off gists with no edge-case handling). The registry site displays the quality matrix for every component prominently.

## Integration with nutmeg

Campos is a sibling, not a dependency, but the two integrate deeply:

1. **The `nutmeg` plugin ships a `render` skill** that knows how to call Campos. When an agent completes an `acquire → wrangle → compute → analyse` flow, `render` composes Campos components into the user's project.
2. **The MCP server from Campos is declared in nutmeg's `.mcp.json`** alongside football-docs. Agents using nutmeg automatically have component discovery.
3. **`acquire` skill output is pre-adapted** to Campos schema where possible, so the agent can pass data directly into components without manual mapping.
4. **Cross-linking on both landing pages.** nutmeg's site has a "render with Campos" section; Campos's site has a "get your data with nutmeg" section.
5. **Shared design language.** The Campos website uses Campos components to demo itself; nutmeg-site (existing Astro project) will adopt Campos theme tokens for visual consistency across the brand family.

## Distribution

| Channel | Purpose |
|---|---|
| **GitHub repository** (`withqwerty/campos`) | Source of truth, issue tracker, contribution surface, MIT license |
| **PyPI package** (`campos`) | CLI + schema + adapters; `pip install campos` |
| **Registry website** (`campos.football` or similar — see open questions) | Browse components, see live examples, read quality matrix, copy source directly |
| **MCP server** (bundled with package, declared in `.mcp.json`) | Agent-native component discovery |
| **Plugin marketplace link** from nutmeg | Discoverability for Claude Code users |

Launch order:
1. GitHub repo with 3 components (PlayerHero, PercentileRibbon, ShotMap) — both flavours, both tested, both documented with quality matrix. Internal dogfood.
2. Remaining 6 components + theme + adapters. Private beta with 3–5 friendly users from the football Python community.
3. Registry website launch. Public announcement. Twitter thread with camponents pun.
4. MCP server + nutmeg plugin integration.
5. v1.0 tag once all 9 components have full green quality matrices.

## Open questions

1. **Adapter list confirmation.** Spec currently reflects author's 2026-04-05 revision: v1 ships **Opta + WhoScored** (both scrapable, both Opta-lineage), with StatsBomb + Wyscout deferred to v2. This replaces an earlier proposal of Opta/StatsBomb/Wyscout. Confirm during spec review.
2. **Domain name.** `campos.dev`, `campos.football`, `camponents.dev`, `getcampos.com`. Check availability. Leaning `campos.football` for on-brand signalling.
3. **MCP server packaging.** Ship as part of the `campos` Python package, or as a separate `@campos/mcp` npm package like football-docs? If the CLI is Python, bundling is simpler, but cross-ecosystem discoverability may favour npm.
4. **Snapshot testing strategy.** Python flavour: pytest + matplotlib image comparison (mpl-testing). Web flavour: Playwright visual regression? Something lighter? Needs a decision before the quality-bar tests can be written.
5. **Theme token naming.** `--campos-*` prefix is safest but verbose. `--cmp-*` is tight but collides with common abbreviations. Bikeshed during implementation.
6. **Contribution model.** PRs welcome from v1, or closed during the battle-testing phase? Leaning closed until v1.0, then opened with a strict quality matrix requirement for any new component.
7. **Pricing / sustainability.** MIT open source and free forever for the registry itself. Optional paid tier later for private component registries, club-branded theme packs, or commercial support? Out of scope for this spec but worth noting as a future lever.

## Success criteria

Campos v1 is successful if, 6 months after launch:

1. At least one independent developer has shipped a public football app using Campos components, without direct help from the author.
2. At least one Claude Code user has asked `/nutmeg` to "build me a scouting dashboard" and received a working Campos-based app.
3. The quality matrix has zero red cells across the 9 components.
4. There are at least 5 external contributions (bug reports, PRs, theme variants, new adapters).
5. Someone on football Twitter has made the "camponents" joke without being prompted.
