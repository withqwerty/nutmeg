# nutmeg

A Claude Code plugin that makes Claude an expert at football data analytics.

**Who it's for:** Anyone who works with football data — analysts, developers, journalists, researchers, hobbyists. If you've ever spent an hour figuring out which Opta qualifier is xG, or why your StatsBomb coordinates are upside down, or how to normalise a heatmap properly, this is for you.

**What it does:** Gives Claude deep, verified knowledge of football data providers, libraries, and conventions. Claude looks up the actual docs instead of guessing from training data, writes code adapted to your stack, and catches football-specific mistakes in your work.

**Why not just ask Claude directly?** Claude knows football data exists but its knowledge is frozen and often wrong on specifics — qualifier IDs, API endpoints, coordinate systems, method signatures. These change. nutmeg connects Claude to a live, searchable index of real provider documentation so it gets the details right.

## Capabilities

nutmeg gives Claude deep knowledge of football data so it can help you:

- **Acquire** data from Opta, StatsBomb, Wyscout, SportMonks, FBref, Understat, and more
- **Wrangle** event streams, transform coordinates, join datasets, handle large files
- **Route entity-resolution work** to the right public surface: provider facts in football-docs, public ID lookup in Reep Register, reusable matching code in reep-scripts
- **Compute** derived metrics like xG, PPDA, passing networks, expected threat
- **Store** data in the right format and publish results via Streamlit, Observable, or static sites
- **Analyse** matches, players, and teams with statistical rigour
- **Learn** football analytics concepts, from xG basics to academic research

It adapts to your experience level, preferred programming language, and available data sources.

## Install

### Full install (Claude Code plugin)

Includes skills, agents, and the football docs MCP server.

```bash
# From Claude Code — add the marketplace first (one-time), then install
/plugin marketplace add withqwerty/plugins
/plugin install nutmeg@withqwerty
```

### Skills only (any AI coding agent)

Works with Claude Code, Cursor, Codex, Windsurf, and 40+ other agents via the [Agent Skills](https://agentskills.io) standard.

```bash
npx skills add withqwerty/nutmeg
```

This installs the 10 skills but not the agents or MCP docs server. For the full experience (searchable provider docs, pipeline builder agent, data reviewer agent), use the plugin install above.

## Setup

Run `/nutmeg` and describe what you want to do. On first run, it creates your profile (experience, tools, data access) so all skills adapt accordingly.

## Skills

Most users only need two commands — `/nutmeg` routes everything else automatically.

### Entry points

| Skill | What it does |
|-------|-------------|
| `/nutmeg` | **Start here.** Describe what you want — it handles setup, routing, and dispatch |
| `/nutmeg-learn` | Concepts, resources, provider docs, learning paths |

### Sub-skills (auto-dispatched or direct)

These are invoked automatically by `/nutmeg` based on what you're doing. Power users can call them directly.

| Skill | What it does |
|-------|-------------|
| `/nutmeg-acquire` | Fetch, scrape, or download data + manage API keys |
| `/nutmeg-wrangle` | Transform, filter, reshape data |
| `/nutmeg-compute` | Calculate derived metrics (xG, PPDA, passing networks) |
| `/nutmeg-analyse` | Explore and interpret football data |
| `/nutmeg-brainstorm` | Research-backed visualisation ideation and chart design |
| `/nutmeg-store` | Choose storage format and publishing method |
| `/nutmeg-review` | Review data code and charts for correctness and conventions |
| `/nutmeg-heal` | Fix broken scrapers, submit upstream issues |

## Football Docs MCP Server

nutmeg includes a searchable index of football data provider documentation.
Think Context7 for football data. Provider-specific facts, including identity
surfaces and ID-scheme quirks, should come from this index rather than from
Nutmeg's own prompts.

The server is published as the [`football-docs`](https://www.npmjs.com/package/football-docs) npm package and starts automatically when nutmeg is loaded (via `npx -y football-docs`). No local build step is required.

### Adding provider docs

Provider docs and the search index live in the [football-docs](https://github.com/withqwerty/football-docs) repository. Drop markdown files in `docs/{provider}/` there and run `pnpm ingest` to rebuild `data/docs.db`:

```
docs/providers/
  opta/
    event-types.md
    qualifiers.md
    coordinate-system.md
    api-access.md
  statsbomb/
    event-types.md
    data-model.md
    ...
```

## Providers covered

| Provider | Event data | Stats | xG | Tracking | Free? |
|----------|-----------|-------|----|----------|-------|
| StatsBomb | Yes | Yes | Yes | No | Open data (select comps) |
| Opta/Perform | Yes | Yes | Yes (xGOT too) | Yes | No (unofficial feed exists) |
| Wyscout | Yes | Yes | No | No | No |
| SportMonks | Partial | Yes | No | No | Free tier |
| FBref | No | Yes | Yes (via StatsBomb) | No | Yes (scraping) |
| Understat | No | Partial | Yes | No | Yes (scraping) |
| ClubElo | No | No | No | No | Yes (API) |

## License

MIT
