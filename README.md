# nutmeg

A Claude Code plugin that makes Claude an expert at football data analytics.

**Who it's for:** Anyone who works with football data — analysts, developers, journalists, researchers, hobbyists. If you've ever spent an hour figuring out which Opta qualifier is xG, or why your StatsBomb coordinates are upside down, or how to normalise a heatmap properly, this is for you.

**What it does:** Gives Claude deep, verified knowledge of football data providers, libraries, and conventions. Claude looks up the actual docs instead of guessing from training data, writes code adapted to your stack, and catches football-specific mistakes in your work.

**Why not just ask Claude directly?** Claude knows football data exists but its knowledge is frozen and often wrong on specifics — qualifier IDs, API endpoints, coordinate systems, method signatures. These change. nutmeg connects Claude to a live, searchable index of real provider documentation so it gets the details right.

## Capabilities

nutmeg gives Claude deep knowledge of football data so it can help you:

- **Acquire** data from Opta, StatsBomb, Wyscout, SportMonks, FBref, Understat, and more
- **Wrangle** event streams, transform coordinates, join datasets, handle large files
- **Compute** derived metrics like xG, PPDA, passing networks, expected threat
- **Store** data in the right format and publish results via Streamlit, Observable, or static sites
- **Analyse** matches, players, and teams with statistical rigour
- **Learn** football analytics concepts, from xG basics to academic research

It adapts to your experience level, preferred programming language, and available data sources.

## Install

### Full install (Claude Code plugin)

Includes skills, agents, and the football docs MCP server.

```bash
# From Claude Code
/plugin install nutmeg@withqwerty/nutmeg
```

### Skills only (any AI coding agent)

Works with Claude Code, Cursor, Codex, Windsurf, and 40+ other agents via the [Agent Skills](https://agentskills.io) standard.

```bash
npx skills add withqwerty/nutmeg
```

This installs the 10 skills but not the agents or MCP docs server. For the full experience (searchable provider docs, pipeline builder agent, data reviewer agent), use the plugin install above.

## Setup

Run `/nutmeg-init` to create your profile. This tells nutmeg about your experience, tools, and data access so all skills adapt accordingly.

## Skills

| Skill | What it does |
|-------|-------------|
| `/nutmeg-init` | Set up your profile |
| `/nutmeg-credentials` | Manage API keys and data access |
| `/nutmeg-providers` | Search provider documentation (Opta qualifiers, StatsBomb event types, etc.) |
| `/nutmeg-acquire` | Fetch, scrape, or download football data |
| `/nutmeg-heal` | Fix broken scrapers, submit upstream issues |
| `/nutmeg-wrangle` | Transform, filter, reshape data |
| `/nutmeg-compute` | Calculate derived metrics (xG, PPDA, passing networks) |
| `/nutmeg-store` | Choose storage format and publishing method |
| `/nutmeg-analyse` | Explore and interpret football data |
| `/nutmeg-learn` | Glossary, papers, courses, community resources |
| `/nutmeg-brainstorm` | Research-backed visualisation ideation and chart design |
| `/nutmeg-review` | Review data code and charts for correctness, conventions, and edge cases |

## Football Docs MCP Server

nutmeg includes a searchable index of football data provider documentation. Think Context7 for football data.

```bash
# Build the docs index
cd mcp/football-docs-server
npm install
npm run ingest

# The MCP server starts automatically when nutmeg is loaded
```

### Adding provider docs

Drop markdown files in `docs/providers/{provider}/` and re-run `npm run ingest`:

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
