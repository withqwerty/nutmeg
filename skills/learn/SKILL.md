---
name: nutmeg-learn
description: "Learn about football analytics concepts and explore provider documentation. Use when the user asks what a metric means (xG, PPDA, expected threat, xT), wants learning resources, papers, or courses, is new to football analytics, or wants a learning path. Also use when the user asks about data provider documentation — qualifier IDs, coordinate systems, event types, API schemas, field mappings — or wants to compare providers, look something up in the docs, or find out what data a provider offers."
argument-hint: "[concept, 'getting started', or provider query]"
allowed-tools: ["Read", "mcp__football-docs__search_docs", "mcp__football-docs__list_providers", "mcp__football-docs__compare_providers"]
---

# Learn

Teach football analytics concepts, recommend resources, provide a learning path, and answer questions about data provider documentation — all adapted to the user's level.

## Accuracy

Read and follow `docs/accuracy-guardrail.md` before answering any question about provider-specific facts (IDs, endpoints, schemas, coordinates, rate limits). Always use `search_docs` — never guess from training data.

## First: check profile

Read `.nutmeg.user.md`. If it doesn't exist, tell the user to run `/nutmeg` first.

## Glossary of core concepts

### Chance quality metrics

| Metric | What it means | Intuition |
|--------|--------------|-----------|
| xG (Expected Goals) | Probability a shot results in a goal (0-1) | "How good was the chance?" |
| xGOT (xG on Target) | xG adjusted for shot placement in the goal | "How good was the finish?" |
| xA (Expected Assists) | xG of the shot that resulted from a pass | "How good was the chance created?" |
| xT (Expected Threat) | Value added by moving the ball to a more dangerous area | "How much did this pass/carry increase goal threat?" |
| PSxG (Post-Shot xG) | Same as xGOT. StatsBomb terminology. |

### Possession and pressing

| Metric | What it means |
|--------|--------------|
| PPDA | Passes allowed per defensive action. Lower = more pressing |
| High press | Defensive actions in the opponent's defensive third |
| Counterpressure | Immediate defensive reaction after losing the ball |
| Build-up | How a team progresses the ball from defence to attack |
| Possession value | How much each action contributes to scoring probability |

### Passing

| Metric | What it means |
|--------|--------------|
| Progressive pass | Pass that moves the ball significantly toward the opponent's goal |
| Key pass | Pass directly leading to a shot |
| Assist | Pass directly leading to a goal |
| Through ball | Pass played into space behind the defence |
| Switch of play | Long pass crossing the centre of the pitch |
| Pass completion % | Successful passes / total passes (misleading in isolation) |

### Shooting

| Metric | What it means |
|--------|--------------|
| Shots per 90 | Shot volume normalised by playing time |
| Conversion rate | Goals / shots (noisy, small sample issues) |
| Big chance | High-xG opportunity (typically xG > 0.3) |
| Shot on target % | Shots on target / total shots |

### Defensive

| Metric | What it means |
|--------|--------------|
| Tackles won | Successful tackle attempts |
| Interceptions | Reading and intercepting opponent passes |
| Clearances | Defensive clearances (often under pressure) |
| Blocks | Blocking shots or passes |
| Aerial duels won | Headers contested and won |

### Per-90 normalisation

Always normalise player stats per 90 minutes, not per match:
```
per_90 = (raw_stat / minutes_played) * 90
```

Why: a player with 2 goals in 180 minutes (per 90: 1.0) is performing the same as one with 1 goal in 90 minutes. Per-match stats penalise part-time players.

**Minimum sample:** ~900 minutes (10 full matches) before per-90 stats are meaningful.

## Learning path

### Stage 1: Getting started

1. **Read:** "The Numbers Game" by Chris Anderson and David Sally. Accessible introduction to football analytics.
2. **Watch:** Tifo Football YouTube channel for visual explainers of tactical and analytical concepts.
3. **Do:** Load StatsBomb open data and make a shot map. Just plot the x,y coordinates of shots, colour by goal/no goal.
4. **Understand:** What xG is and isn't. Read StatsBomb's public xG methodology.

### Stage 2: Building skills

1. **Read:** "Soccermatics" by David Sumpter. Mathematical modelling applied to football.
2. **Learn:** How to make pass networks and xG timelines.
3. **Practice:** Analyse a full match. Write up what happened and what the data shows.
4. **Explore:** FBref for season-level stats. Compare teams across multiple dimensions.
5. **Tool up:** Learn pandas/polars (Python), tidyverse (R), or D3.js (JavaScript) for data manipulation and visualisation.

### Stage 3: Going deeper

1. **Read key papers:**
   - Decroos et al. (2019) "Actions Speak Louder than Goals" (VAEP model)
   - Fernandez & Bornn (2018) "Wide Open Spaces" (pitch control)
   - Karun Singh (2018) "Introducing Expected Threat" (xT)
   - Spearman (2018) "Beyond Expected Goals" (pitch control + off-ball)
2. **Build a model:** Train your own xG model. Compare with provider xG.
3. **Tracking data:** If you can access it, explore player positioning data.
4. **Community:** Join football analytics Twitter/X, attend OptaPro Forum or StatsBomb Conference talks (many are free online).

### Stage 4: Professional level

1. **Statistical rigour:** Learn about confidence intervals, effect sizes, Bayesian methods.
2. **Causal inference:** Understanding what data can and can't tell you about cause and effect.
3. **Communication:** Presenting findings to non-technical audiences (coaches, scouts, journalists).
4. **Domain expertise:** The best analysts combine data skills with deep football knowledge. Watch matches, understand tactics.

## Community resources

| Resource | What it is |
|----------|-----------|
| StatsBomb open data | Free event data, best starting point |
| Friends of Tracking (YouTube) | University-level video lectures on football analytics |
| McKay Johns (YouTube) | Python football analytics tutorials |
| FBref | Free season stats, powered by StatsBomb data |
| The Athletic | Journalism with analytics focus |
| OptaPro Forum | Annual analytics conference (talks online) |
| StatsBomb Conference | Annual conference with published research |
| r/socceranalytics | Reddit community |
| Football Analytics Slack | Community workspace |

## Common misconceptions

1. **"More possession = better."** Possession without purpose is meaningless. Quality of chances matters more.
2. **"xG is a prediction."** xG is a description of chance quality, not a prediction of future performance.
3. **"This player has 0.8 xG per 90, so they'll score 30 goals."** Small samples, regression to the mean, context all matter.
4. **"Data analytics replaces scouting."** It complements it. Data finds candidates; humans evaluate fit, personality, potential.
5. **"All xG models are the same."** They vary significantly by input features, training data, and methodology.

## Provider documentation

When the user asks about provider-specific details — event types, qualifier IDs, coordinate systems, API schemas, field mappings — use the football-docs MCP tools.

### Answering specific questions

Use `search_docs` with the user's query. Add a `provider` filter if they're asking about a specific provider.

Examples:
- "What qualifier ID is a headed goal in Opta?" → `search_docs(query="headed goal qualifier", provider="opta")`
- "How does StatsBomb represent xG?" → `search_docs(query="xG expected goals", provider="statsbomb")`
- "What free data sources have shot-level data?" → `search_docs(query="shot data free", provider="free-sources")`

### Comparing providers

Use `compare_providers` when the user wants to understand differences.

Examples:
- "How do Opta and StatsBomb represent passes differently?" → `compare_providers(topic="pass event types", providers=["opta", "statsbomb"])`
- "Which providers have xG data?" → `compare_providers(topic="xG expected goals")`

### Discovering what's available

Use `list_providers` to show what documentation is indexed and its coverage.

### Cross-referencing with kloppy

When comparing providers, also search for kloppy's mapping documentation. kloppy defines how each provider's events map to a canonical model, which helps the user understand what maps cleanly between providers, what information is lost in translation, and what becomes a GenericEvent (unmapped).

### Response format

1. Give the direct answer first (the qualifier ID, the field name, etc.)
2. Add context about how it works in practice
3. If relevant, mention how other providers handle the same concept
4. Adapt technical depth to the user's experience level
