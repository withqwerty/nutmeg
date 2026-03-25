---
name: nutmeg-init
description: "Set up your football data profile. Use when the user first installs nutmeg, says 'set up nutmeg', 'configure nutmeg', 'nutmeg init', or when any other nutmeg skill detects that .nutmeg.user.md does not exist."
argument-hint: ""
allowed-tools: ["Read", "Write", "AskUserQuestion"]
---

# Nutmeg Init

Set up the user's football data profile so all other nutmeg skills can adapt to their experience, tools, and goals.

## When to run

- First time using nutmeg
- When the user says "nutmeg init", "set up nutmeg", or "configure nutmeg"
- When any other nutmeg skill detects that `.nutmeg.user.md` does not exist in the project root

## Process

### 1. Check for existing profile

Read `.nutmeg.user.md` in the project root. If it exists, show the user their current profile and ask if they want to update it. If not, proceed with setup.

### 2. Ask questions using AskUserQuestion

Ask these in sequence, ONE AT A TIME. Wait for each answer before proceeding. Use `multiSelect: true` where indicated.

#### Q1: Programming experience (single select)

"How experienced are you with programming?"

- **Beginner** - Learning to code, or only done simple scripts
- **Competent** - Comfortable writing programs, using libraries, debugging
- **Advanced** - Architect systems, write production code, contribute to open source

#### Q2: Programming languages (multi-select)

"Which programming languages do you use?"

- **Python** - pandas, polars, Jupyter, matplotlib
- **R** - tidyverse, ggplot2, Shiny
- **JavaScript / TypeScript** - Node.js, D3.js, web frameworks
- **SQL** - Database queries, data warehousing

If Python selected, follow up (single select): "Which Python data stack do you prefer?"
- **pandas** - The standard, most tutorials use it
- **polars** - Faster, Rust-backed, growing ecosystem
- **Both / no preference**

#### Q3: Football analytics experience (single select)

"How experienced are you with football data and analytics?"

- **New** - Know what xG means but haven't worked with match data
- **Familiar** - Used FBref or Understat, made some charts, read analytics content
- **Experienced** - Built pipelines, computed derived metrics, published analysis
- **Expert** - Professional analyst, deep statistical knowledge, domain authority

#### Q4: Statistics / data science experience (single select)

"How comfortable are you with statistics and data analysis?"

- **Basic** - Averages, percentages, simple comparisons
- **Intermediate** - Distributions, correlation, regression, hypothesis testing
- **Advanced** - Bayesian methods, causal inference, ML models, experimental design

#### Q5: Data providers (multi-select)

"Which data sources do you have access to or plan to use?"

Group A - Free (no key needed):
- **StatsBomb open data** - Free event data for select competitions (World Cups, FA WSL, some leagues)
- **FBref** - Free season stats (powered by StatsBomb). Web scraping
- **Understat** - Free xG and shot data for top 5 leagues. Web scraping

Group B - Free with API key:
- **SportMonks** - REST API, free tier available (limited requests)
- **Football-data.org** - Free tier, match results and standings
- **FPL (Fantasy Premier League)** - Free unofficial API, player stats and prices
- **TheSportsDB** - Free tier, match metadata and images
- **ClubElo** - Free, no key needed, Elo ratings

Group C - Commercial (paid):
- **Opta / Stats Perform** - Commercial feeds or theanalyst.com unofficial access
- **StatsBomb API** - Commercial event + 360 data
- **Wyscout** - Commercial event data and video
- **API-Football (RapidAPI)** - Pay-per-request via RapidAPI marketplace

Group D - Marketplaces and other:
- **Kaggle** - Community datasets, variable quality
- **GitHub datasets** - Open data repos (StatsBomb, Metrica, SkillCorner)

Present all groups together as a single multi-select. The groups are for your reference when generating warnings.

#### Q6: Goals (multi-select)

"What do you want to do with football data? Select all that apply."

- **Explore and learn** - Curiosity-driven, build understanding
- **Create content** - Charts, blog posts, social media, data journalism
- **Academic research** - Papers, thesis, structured analysis
- **Build a product** - App, website, or tool using football data
- **Professional analysis** - Scouting, match analysis, club or media work

If more than one selected, follow up (single select): "Which of these is your primary goal?"

### 3. Generate warnings and caveats

Based on their answers, include relevant warnings in the profile.

**If using scraped sources (FBref, Understat, WhoScored):**
- Scrapers break when sites change. Pin versions of scraping libraries.
- Respect rate limits. FBref: max ~10 req/min. Understat: ~1-2 req/sec.
- Check terms of service. Some sites prohibit automated access.
- Cache aggressively. Don't re-fetch data you already have.

**If new to football data:**
- Start with StatsBomb open data. It's free, well-documented, and has a large community.
- Don't trust xG models blindly. Different providers (StatsBomb, Understat, Opta) give different values for the same shots.
- Football data has inherent noise. Don't draw conclusions from fewer than 10 matches (team) or 900 minutes (player).

**If using commercial APIs (Opta, Wyscout, StatsBomb API):**
- These cost money. Understand your tier limits before building pipelines.
- Data redistribution is usually prohibited. Check your license before publishing raw data.
- API keys are secrets. Never commit them to git. Use `.env` files.

**If using free-with-key APIs (SportMonks, Football-data.org, FPL):**
- Free tiers have strict rate limits. Cache responses locally.
- FPL API is unofficial and undocumented. It can change without notice.
- SportMonks free tier may limit to 5-100 requests/day depending on plan.

**If building a product:**
- Data licensing is complex. Commercial use often requires separate agreements with providers.
- Consider data freshness requirements (live vs hourly vs daily).
- Plan for provider outages. Don't depend on a single source.

**If doing academic research:**
- Document your data sources and methodology. Reproducibility matters.
- Be explicit about which xG model you're using and why.
- Small sample sizes are the biggest trap in football analytics.

**If basic statistics level:**
- Start with simple counts and comparisons. Build up to per-90 normalisation.
- Be cautious about "correlation vs causation" claims.
- Learn about sample size before publishing findings.

### 4. Write the profile

Write `.nutmeg.user.md` in the project root with this structure:

```markdown
---
programming_level: beginner | competent | advanced
languages: [python, r, javascript, sql]
python_stack: pandas | polars | both
football_data_level: new | familiar | experienced | expert
statistics_level: basic | intermediate | advanced
providers: [statsbomb-open, fbref, understat, sportmonks, opta, ...]
goals: [explore, content, academic, product, professional]
primary_goal: content
has_api_keys: true | false
initialized: YYYY-MM-DD
---

# Nutmeg User Profile

## Warnings

[Generated warnings based on their setup]

## Available Skills

- `/nutmeg-init` - Update this profile
- `/nutmeg-credentials` - Manage API keys and data access
- `/nutmeg-providers` - Search provider documentation and compare data availability
- `/nutmeg-acquire` - Fetch, scrape, or download football data
- `/nutmeg-heal` - Fix broken scrapers, submit upstream issues
- `/nutmeg-wrangle` - Transform, filter, reshape, and join data
- `/nutmeg-compute` - Calculate derived metrics (xG, PPDA, passing networks, etc.)
- `/nutmeg-store` - Choose storage format and location for your data
- `/nutmeg-analyse` - Explore and interpret football data
- `/nutmeg-learn` - Glossary, papers, courses, and community resources
```

### 5. Next steps

Based on their profile, suggest what to do next:

**If they selected any provider that requires an API key** (SportMonks, Opta, StatsBomb API, Wyscout, API-Football, Football-data.org):
- Tell them to run `/nutmeg-credentials` to set up their API keys safely.

**Then, based on football data experience:**
- **New:** "Run `/nutmeg-learn` to get oriented, then `/nutmeg-acquire` to grab some StatsBomb open data."
- **Familiar:** "Run `/nutmeg-providers` to search for the specific data you need, then `/nutmeg-acquire` to fetch it."
- **Experienced/Expert:** "You're all set. All nutmeg skills will adapt to your setup. Use `/nutmeg-providers` to search across provider docs."

### 6. Do NOT ask about publishing or storage

Publishing format and storage decisions depend on the specific project and pipeline. These will be addressed by `/nutmeg-store` when the user is working on a concrete output. Asking about them during init is premature.
