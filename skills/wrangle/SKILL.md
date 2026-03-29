---
name: nutmeg-wrangle
description: "Transform, filter, reshape, join, and manipulate football data. Use when the user needs to clean data, merge datasets, convert between formats, handle missing values, work with large datasets, or do any data manipulation task on football data."
argument-hint: "[what to do with the data]"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep", "Agent", "mcp__football-docs__search_docs"]
---

# Wrangle

Help the user manipulate football data effectively. This skill is about the mechanics of working with data, adapted to the user's language and tools.

## Accuracy

Read and follow `docs/accuracy-guardrail.md` before answering any question about provider-specific facts (IDs, endpoints, schemas, coordinates, rate limits). Always use `search_docs` — never guess from training data.
## First: check profile

Read `.nutmeg.user.md`. If it doesn't exist, tell the user to run `/nutmeg` first. Use their profile for language preference and stack.

## Core operations

### Coordinate transforms

Football data coordinates vary by provider. Always verify and convert before combining data.

Use `search_docs(query="coordinate system", provider="[provider]")` to look up the specific system. Key conversions:

- Opta (0-100) to StatsBomb (120x80): `x * 1.2`, `y * 0.8`
- Wyscout to Opta: `x` stays, `y = 100 - y` (invert Y)
- Any to kloppy normalised: use kloppy's `.transform()` in Python

### Filtering events

Common filtering patterns for football event data:

**By event type:**
- Shots: filter for shot/miss/goal/saved event types
- Passes in final third: filter passes where x > 66.7 (Opta coords)
- Defensive actions: tackles + interceptions + ball recoveries

**By match state:**
- Open play only: exclude set pieces (corners, free kicks, throw-ins, penalties)
- First half vs second half: use periodId or timestamp
- Score state: track running score to filter "when winning", "when losing"

**By zone:**
- Penalty area actions: x > 83, 21 < y < 79 (Opta coords)
- High press: actions in opponent's defensive third (x > 66.7)

### Joining datasets

Common joins in football data:

| Join | Key | Notes |
|------|-----|-------|
| Events + lineups | player_id + match_id | Get player names/positions for each event |
| Events + xG | match_id + event sequence | Match xG to specific shots |
| Multiple providers | match date + team names | Fuzzy matching often needed |
| Season data + Elo | date | Join Elo rating at time of match |

**Fuzzy team name matching** is a constant pain. Build a mapping table:
```python
TEAM_MAP = {
    'Man City': 'Manchester City',
    'Man United': 'Manchester United',
    'Spurs': 'Tottenham Hotspur',
    'Wolves': 'Wolverhampton Wanderers',
    # ...
}
```

### Reshaping

Common reshaping operations:

- **Wide to long:** Season stats tables (one column per stat) to tidy format (one row per stat per team)
- **Events to possession chains:** Group consecutive events by the same team into possession sequences
- **Match-level to season aggregates:** Group by team, sum/average per-match values
- **Player-match to player-season:** Aggregate across matches, weight by minutes played

### Handling large datasets

Full event data for a PL season is ~500MB+ (380 matches x ~1700 events). Strategies:

**Python:**
- Use polars instead of pandas for 5-10x speed improvement
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
| Event counts | ~1500-2000 events per PL match. Much less = data issue |
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
