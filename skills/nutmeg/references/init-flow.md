# First-time setup flow

When `.nutmeg.user.md` doesn't exist, run this interactive setup. Ask questions ONE AT A TIME using AskUserQuestion.

## Q1: Programming experience
"How experienced are you with programming?"
- **Beginner** — Learning to code, or only done simple scripts
- **Competent** — Comfortable writing programs, using libraries, debugging
- **Advanced** — Architect systems, write production code, contribute to open source

## Q2: Programming languages (multi-select)
"Which programming languages do you use?"
- **Python** — pandas, polars, Jupyter, matplotlib
- **R** — tidyverse, ggplot2, Shiny
- **JavaScript / TypeScript** — Node.js, D3.js, web frameworks
- **SQL** — Database queries, data warehousing

If Python selected, follow up: "Which Python data stack?" (pandas / polars / both)

## Q3: Football analytics experience
"How experienced are you with football data and analytics?"
- **New** — Know what xG means but haven't worked with match data
- **Familiar** — Used FBref or Understat, made some charts
- **Experienced** — Built pipelines, computed derived metrics, published analysis
- **Expert** — Professional analyst, deep statistical knowledge

## Q4: Statistics comfort
"How comfortable are you with statistics?"
- **Basic** — Averages, percentages, simple comparisons
- **Intermediate** — Distributions, correlation, regression, hypothesis testing
- **Advanced** — Bayesian methods, causal inference, ML, experimental design

## Q5: Data providers (multi-select)
"Which data sources do you have access to?"

Present as a single multi-select: StatsBomb open, FBref, Understat, ClubElo, SportMonks, Football-data.org, FPL, Opta, StatsBomb API, Wyscout, Kaggle, GitHub datasets

## Q6: Goals (multi-select)
"What do you want to do with football data?"
- Explore and learn
- Create content (charts, blogs, social media)
- Academic research
- Build a product
- Professional analysis

If multiple: "Which is your primary goal?"

## Write the profile

Write `.nutmeg.user.md` with YAML frontmatter:

```yaml
---
programming_level: beginner | competent | advanced
languages: [python, r, javascript, sql]
python_stack: pandas | polars | both
football_data_level: new | familiar | experienced | expert
statistics_level: basic | intermediate | advanced
providers: [statsbomb-open, fbref, understat, ...]
goals: [explore, content, academic, product, professional]
primary_goal: content
initialized: YYYY-MM-DD
---
```

## Generate warnings

Based on their answers, include relevant warnings:

**If using scraped sources (FBref, Understat):** Scrapers break when sites change. Respect rate limits (FBref: ~10 req/min). Cache aggressively.

**If new to football data:** Start with StatsBomb open data. Don't trust xG models blindly. Don't draw conclusions from fewer than 10 matches or 900 minutes.

**If using commercial APIs:** Understand tier limits. Data redistribution usually prohibited. API keys are secrets — never commit to git.

**If building a product:** Commercial use often requires separate data licensing agreements.

**If doing academic research:** Document sources and methodology. Be explicit about which xG model.

## What's next section

Adapt to their level:
- **New:** "Just describe what you want to explore — I'll handle the rest. Try: 'show me shot locations from the 2022 World Cup final'"
- **Familiar:** "Ask me anything. Try: 'get PL xG data from Understat and compare the top 6'"
- **Experienced/Expert:** "All sub-skills are available directly if you prefer: `/nutmeg-acquire`, `/nutmeg-analyse`, etc. Or just describe what you need."
