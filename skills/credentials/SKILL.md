---
name: credentials
description: "Manage API keys and data access for football data providers. Use when the user asks about API keys, authentication, setting up access to Opta, StatsBomb, SportMonks, Wyscout, or any football data source. Also use when they ask what data is available for free vs paid."
argument-hint: "[provider name or 'list']"
allowed-tools: ["Read", "Write", "Bash", "AskUserQuestion"]
---

# Credentials

Help the user safely manage API keys and understand what data access they have.

## First: check profile

Read `.nutmeg.user.md`. If it doesn't exist, tell the user to run `/nutmeg:init` first.

## Key management

API keys should NEVER be committed to git. Guide the user to store them in:

1. **`.env` file** (gitignored) for project-level keys
2. **Environment variables** for system-level keys
3. **`.nutmeg.credentials.local`** (gitignored) for nutmeg-specific config

When the user wants to add a key, help them:
- Create/update `.env` with the key
- Verify `.gitignore` includes `.env` and `*.local`
- Test the key works with a minimal API call

## Provider access reference

### Free (no key needed)

| Source | Access method | What you get |
|--------|--------------|--------------|
| StatsBomb open data | GitHub download / statsbombpy | Event data for select competitions (World Cups, FA WSL, some league seasons) |
| FBref | Web scraping (soccerdata) | Season aggregates: passing, shooting, defense, GCA, possession stats |
| Understat | Web scraping (soccerdata) | Per-match xG, shot-level data. Top 5 European leagues |
| ClubElo | HTTP API (no key) | Historical Elo ratings for European clubs |
| football-data.co.uk | CSV download | Historical match results with betting odds |
| Transfermarkt | Web scraping | Transfer values, squad info (fragile, terms may prohibit) |

### Paid / keyed

| Provider | Free tier? | Key type | Env var convention |
|----------|-----------|----------|-------------------|
| SportMonks | Yes (limited) | API token | `SPORTMONKS_API_TOKEN` |
| Opta/Perform | No (unofficial feed key exists) | Feed token | `OPTA_FEED_TOKEN` |
| StatsBomb API | No | API key + password | `STATSBOMB_API_KEY`, `STATSBOMB_API_PASSWORD` |
| Wyscout | No | API key | `WYSCOUT_API_KEY` |

### Data marketplaces

| Source | What to look for |
|--------|-----------------|
| Kaggle | Search "football events", "soccer xG". Check license (many are CC-BY). Verify freshness. |
| GitHub | Search "football data", "soccer analytics". StatsBomb open-data is the gold standard. |
| data.world | Occasional football datasets. Check quality and documentation. |

## When the user asks "what can I access for free?"

Based on their `.nutmeg.user.md` profile, give them a concrete plan:
- **Beginners:** Start with StatsBomb open data. It's the best-documented, highest-quality free source.
- **Python users:** Install `statsbombpy` and `soccerdata` for immediate access to open data + FBref/Understat.
- **R users:** Install `StatsBombR` and `worldfootballR` for similar coverage.
- **JS/TS users:** StatsBomb open data can be fetched directly from GitHub as JSON. FBref requires scraping.

## Warnings

- Scraping websites may violate their terms of service. Advise caution.
- Commercial API keys often prohibit data redistribution. Check the license.
- Free tier rate limits can be very low (SportMonks free: 5 requests/day on some plans).
- Never print or log API keys. Use `process.env` or equivalent.
