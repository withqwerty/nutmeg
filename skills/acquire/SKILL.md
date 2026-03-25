---
name: acquire
description: "Fetch, scrape, or download football data from any source. Use when the user wants to get data from StatsBomb, Opta, FBref, Understat, SportMonks, Wyscout, Kaggle, or any football data source. Also use when they ask how to get specific data like 'Premier League xG data' or 'match events for a game'."
argument-hint: "[what data to get]"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep", "Agent", "mcp__football-docs__search_docs"]
---

# Acquire

Help the user get football data from any source into their local environment.

## First: check profile

Read `.nutmeg.user.md`. If it doesn't exist, tell the user to run `/nutmeg:init` first. Use their profile to determine preferred language and available providers.

## Decision tree

When the user asks for data, determine the best source:

### 1. What data do they need?

| Need | Best free source | Best paid source |
|------|-----------------|-----------------|
| Match events (pass-by-pass) | StatsBomb open data | Opta, StatsBomb API, Wyscout |
| Season stats (aggregates) | FBref | SportMonks |
| xG / shot data | Understat, StatsBomb open | Opta (matchexpectedgoals), StatsBomb API |
| Tracking data (player positions) | None free | Second Spectrum, SkillCorner, Tracab |
| Historical results | football-data.co.uk | SportMonks |
| Elo ratings | ClubElo (free API) | - |
| Player valuations | Transfermarkt (scraping) | - |

### 2. Write acquisition code

Adapt to the user's language preference from `.nutmeg.user.md`.

**Python patterns:**

```python
# StatsBomb open data
from statsbombpy import sb
events = sb.events(match_id=3788741)

# FBref via soccerdata
import soccerdata as sd
fbref = sd.FBref('ENG-Premier League', '2024')
stats = fbref.read_team_season_stats()

# Understat via soccerdata
understat = sd.Understat('ENG-Premier League', '2024')
shots = understat.read_shot_events()
```

**R patterns:**

```r
# StatsBomb
library(StatsBombR)
events <- get.matchFree(Matches) %>% allclean()

# FBref
library(worldfootballR)
stats <- fb_season_team_stats("ENG", "M", 2024, "standard")
```

**JavaScript/TypeScript:**

```typescript
// StatsBomb open data (direct from GitHub)
const resp = await fetch('https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{match_id}.json');
const events = await resp.json();
```

### 3. Data validation

After acquiring data, always:
- Check row/event counts are sensible (PL match should have ~1500-2000 events)
- Verify key fields are present (coordinates, player IDs, timestamps)
- Check for missing data (some providers have gaps for certain competitions)
- Warn about coordinate system differences if combining sources

## Self-discovery

If the user asks for data from an unfamiliar source:
1. Search the football-docs index: `search_docs(query="[source name]")`
2. If not found, search the web for "[source] football data API" or "[source] football dataset"
3. Evaluate: is it free? What format? What coverage? Any rate limits?
4. Guide the user through access

## Caching

Always recommend caching fetched data locally:
- API responses: save as JSON files with metadata (fetch date, parameters)
- Scraped data: save with timestamps so stale data is identifiable
- Suggest a directory structure: `data/{source}/{competition}/{season}/`

## Rate limiting

Remind users about rate limits:
- FBref: 10 requests/minute recommended
- Understat: no official limit but be respectful
- SportMonks: varies by plan (check with `/nutmeg:credentials`)
- StatsBomb open data: no limit (static files on GitHub)
