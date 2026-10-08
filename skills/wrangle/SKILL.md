---
name: nutmeg-wrangle
description: "Transform, filter, reshape, join, and manipulate football data. Use when the user needs to clean data, merge datasets, convert between formats, handle missing values, work with large datasets, or do any data manipulation task on football data."
argument-hint: "[what to do with the data]"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep", "Agent", "mcp__plugin_nutmeg_football-docs__search_docs", "mcp__football-docs__search_docs", "mcp__plugin_nutmeg_football-docs__get_metric", "mcp__football-docs__get_metric", "mcp__plugin_nutmeg_football-docs__list_metrics", "mcp__football-docs__list_metrics"]
---

# Wrangle

Help the user manipulate football data effectively. This skill is about the mechanics of working with data, adapted to the user's language and tools.

## Accuracy

Read and follow `${CLAUDE_PLUGIN_ROOT}/docs/accuracy-guardrail.md` before answering any question about provider-specific facts (IDs, endpoints, schemas, coordinates, rate limits). Always use `search_docs` — never guess from training data.
## First: check profile

Read `.nutmeg.user.md`. If it doesn't exist, continue with sensible defaults (Python and pandas, intermediate level) and suggest running `/nutmeg` setup at the end. Use their profile for language preference and stack.

## Core operations

### Coordinate transforms

Football data coordinates vary by provider. Always verify and convert before combining data.

Use `search_docs(query="coordinate system", provider="[provider]")` to look up each provider's origin, ranges and y-axis direction. Do not write a conversion formula from memory: providers differ in which touchline y=0 sits on, so a formula that only rescales can mirror the pitch.

- Python: prefer kloppy's `.transform()` or mplsoccer's `Standardizer`, which encode each provider's orientation.
- Hand-written transforms: derive them from the looked-up definitions, then test them. A kick-off should land on the centre spot, and a team's shots should cluster at the goal it attacks.

### Filtering events

Common filtering patterns for football event data:

**By event type:**
- Shots: filter for shot/miss/goal/saved event types
- Passes in final third: filter passes in the last third of the provider's x range (for a 0-100 pitch, x > 66.7)
- Defensive actions: tackles + interceptions, plus fouls, challenges, blocks or recoveries depending on the definition (name yours)

**By match state:**
- Open play only: exclude set pieces (corners, free kicks, throw-ins, penalties)
- First half vs second half: use periodId or timestamp
- Score state: track running score to filter "when winning", "when losing"

**By zone:**
- Penalty area actions: look up the provider's box bounds with `search_docs(query="pitch zones", provider="[provider]")`; they are approximate on a normalised pitch
- High press: actions in the opponent's defensive third (the last third of the provider's x range)

### Joining datasets

Common joins in football data:

| Join | Key | Notes |
|------|-----|-------|
| Events + lineups | player_id + match_id | Get player names/positions for each event |
| Events + xG | match_id + event sequence | Match xG to specific shots |
| Multiple providers | Reep ID | Map each provider's `(provider, namespace, id)` to a Reep ID, then join on the Reep ID |
| Season data + Elo | date | Join Elo rating at time of match |

**Joining providers:** join through Reep Register IDs, not names (see `${CLAUDE_PLUGIN_ROOT}/docs/entity-resolution-routing.md`). Names differ across providers ("Man City" / "Manchester City"), players share names, and a fuzzy name match fails silently.

- Look up IDs with `resolve_entity`, or query the Reep release DuckDB for bulk joins.
- Keep rows that do not resolve, and report how many there are per provider. Never drop them silently.
- Use a hand-made name map only as a last resort for entities Reep does not cover, and mark those rows as name-matched so the user can check them.

### Reshaping

Common reshaping operations:

- **Wide to long:** Season stats tables (one column per stat) to tidy format (one row per stat per team)
- **Events to possession chains:** Group consecutive events by the same team into possession sequences
- **Match-level to season aggregates:** Group by team, sum/average per-match values
- **Player-match to player-season:** Aggregate across matches, weight by minutes played

### Handling large datasets

A full season of event data can run to hundreds of megabytes, and tracking data to far more. Strategies:

**Python:**
- Use polars instead of pandas for large tables; it is usually much faster
- Process match-by-match in a loop, don't load all into memory
- Use DuckDB for SQL queries on Parquet files without loading into memory

**JavaScript/TypeScript:**
- Stream JSON files with `readline` or `JSONStream`
- Use SQLite (better-sqlite3) for local queries
- Process files in parallel with worker threads

**R:**
- Use data.table instead of tidyverse for large datasets
- Arrow/Parquet for out-of-memory processing

### Data quality checks

Always validate after wrangling:

| Check | What to look for |
|-------|-----------------|
| Event counts | Compare each match with the other matches in the same dataset. Typical counts depend on the provider, so flag outliers rather than using a fixed number |
| Coordinate range | Should be within provider's expected range |
| Missing player IDs | Some events lack player attribution (ball out, etc.) |
| Duplicate events | Same event_id appearing twice |
| Time gaps | Large gaps in event timestamps within a match |
| Team attribution | Verify home/away assignment is consistent |

### Format conversion

| From | To | Tool/method |
|------|-----|------------|
| JSON events | DataFrame | pandas/polars `read_json` or manual parsing |
| CSV | Parquet | `df.write_parquet()` (polars) or `df.to_parquet()` (pandas) |
| Provider format | kloppy model | `kloppy.load_{provider}()` in Python |
| kloppy model | DataFrame | `dataset.to_df()` |
| Any | SQLite | Load into SQLite for ad-hoc queries |
