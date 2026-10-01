# nutmeg

A Claude Code plugin that makes Claude an expert at football data analytics.

**Who it's for:** Anyone who works with football data — analysts, developers, journalists, researchers, hobbyists. If you've ever spent an hour figuring out which Opta qualifier is xG, or why your StatsBomb coordinates are upside down, or how to normalise a heatmap properly, this is for you.

**What it does:** Gives Claude deep, verified knowledge of football data providers, libraries, and conventions. Claude looks up the actual docs instead of guessing from training data, writes code adapted to your stack, and catches football-specific mistakes in your work.

**Why not just ask Claude directly?** Claude knows football data exists but its knowledge is frozen and often wrong on specifics — qualifier IDs, API endpoints, coordinate systems, method signatures. These change. nutmeg connects Claude to a live, searchable index of real provider documentation so it gets the details right.

## Capabilities

nutmeg gives Claude deep knowledge of football data so it can help you:

- **Acquire** data from Opta, StatsBomb, Wyscout, SportMonks, FBref, Understat, and more
- **Wrangle** event streams, transform coordinates, join datasets, handle large files
- **Route entity-resolution work** to the right public surface: provider facts in football-docs, public ID lookup in Reep Register, reusable matching guidance in reep-toolkit
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

Nutmeg looks up provider facts in the football-docs MCP server, which this install does not include. Add it to your agent as well (Node.js 22.13 or newer):

```bash
claude mcp add football-docs -- npx -y football-docs@0.15.0
```

For other agents, add the same command (`npx -y football-docs@0.15.0`) as an MCP server in their settings. Without it, nutmeg says it cannot check provider facts, and labels anything it answers from memory as unverified.

This installs the 11 skills but not the agents or MCP docs server. For the full experience (searchable provider docs, pipeline builder agent, data reviewer agent), use the plugin install above.

## Setup

Run `/nutmeg` and describe what you want to do. On first run, it creates your profile (experience, tools, data access) so all skills adapt accordingly.

## Skills

Most users only need two commands — `/nutmeg` routes everything else automatically.

### Entry points

| Skill | What it does |
|-------|-------------|
| `/nutmeg` | **Start here.** Describe what you want — it handles setup, routing, and dispatch |
| `/nutmeg:learn` | Concepts, resources, provider docs, learning paths |
| `/nutmeg:research` | Run analysis you will publish or decide on as a research project: a question card, a plan with reasons, and a claim ledger that ties every number to its evidence |

Research projects need Python 3.10 or newer (`python3`). Without it, everything else in nutmeg works as before.

### Sub-skills (auto-dispatched or direct)

These are invoked automatically by `/nutmeg` based on what you're doing. Power users can call them directly.

| Skill | What it does |
|-------|-------------|
| `/nutmeg:acquire` | Fetch, scrape, or download data + manage API keys |
| `/nutmeg:wrangle` | Transform, filter, reshape data |
| `/nutmeg:compute` | Calculate derived metrics (xG, PPDA, passing networks) |
| `/nutmeg:analyse` | Explore and interpret football data |
| `/nutmeg:brainstorm` | Research-backed visualisation ideation and chart design |
| `/nutmeg:store` | Choose storage format and publishing method |
| `/nutmeg:review` | Review data code and charts for correctness and conventions |
| `/nutmeg:heal` | Fix broken scrapers, submit upstream issues |

## Football Docs MCP Server

nutmeg includes a searchable index of football data provider documentation.
Think Context7 for football data. Provider-specific facts, including identity
surfaces and ID-scheme quirks, should come from this index rather than from
Nutmeg's own prompts.

The server is published as the [`football-docs`](https://www.npmjs.com/package/football-docs) npm package and starts automatically when nutmeg is loaded (via `npx -y football-docs@0.15.0`; nutmeg pins the version it was tested with). No local build step is required. It needs Node.js 22.13 or newer.

### Adding provider docs

Provider docs and the search index live in the [football-docs](https://github.com/withqwerty/football-docs) repository. Drop markdown files in `docs/{provider}/` there and run `pnpm ingest` to rebuild `data/docs.db`:

```
docs/
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

Nutmeg does not keep its own provider facts. Coverage, fields, IDs, access terms and rate limits come from football-docs, which indexes 26 providers and tools, including Opta, StatsBomb, Wyscout, SkillCorner, Sportradar, SportMonks, Impect, FBref, Understat, kloppy, socceraction, mplsoccer and databallpy. Ask nutmeg "which providers do you cover?" or call `list_providers` for the current list.

Cross-provider player, team and match IDs come from the [Reep Register](https://reep.football) (CC0), through the `resolve_entity` tool.

## Evals

`evals/` holds a behaviour suite for `claude plugin eval`: provider-fact grounding, abstention, Reep joins, common stat misuses and 2026 source changes. A replay mock stands in for the football-docs server, so runs do not depend on the live index.

```bash
claude plugin eval . --runs 2 --scaffold --no-publish --model sonnet --judge-model haiku
```

`--scaffold` runs each case's `scaffold.sh`, which writes a nutmeg profile into the sandbox. To refresh the mock after football-docs changes, run `evals/_scaffold/record_football_docs.py`. Keep the agent on Sonnet so scores stay comparable; Haiku as the judge (it also runs the mock) keeps each pass of the suite (one run per case) to about $9. `evals/_scaffold/adopt_replays.py` checks a run's mock answers against the real server.

## License

MIT
