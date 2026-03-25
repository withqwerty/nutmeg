---
name: nutmeg-init
description: "Set up your football data profile. Use when the user first installs nutmeg, says 'set up nutmeg', 'configure nutmeg', 'nutmeg init', or when any other nutmeg skill detects that .user.md does not exist."
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

Ask these questions ONE AT A TIME. Wait for each answer before proceeding.

**Experience level:**
- "What's your experience with football data analytics? (new to it / done some exploration / work with it regularly / professional analyst)"

**Programming:**
- "What programming language(s) do you prefer? (Python, R, JavaScript/TypeScript, SQL, or tell me what you're comfortable with)"
- If Python: "Do you use pandas, polars, or both?"

**Data access:**
- "Which data providers do you have access to? (Pick all that apply: StatsBomb API, Opta/Perform feeds, Wyscout, SportMonks, or just free sources like FBref/Understat/StatsBomb open data)"

**Goals:**
- "What are you trying to do with football data? (explore for fun / academic research / content creation / professional analysis / building a product)"

**Publishing:**
- "Do you want to publish or share your work? If so, how? (Streamlit app / web page / Jupyter notebooks / blog posts / social media charts / not sure yet)"

### 3. Generate warnings and caveats

Based on their answers, include relevant warnings in the profile:

**If using scraped sources (FBref, WhoScored, Understat):**
- Scrapers break when sites change. Pin versions of scraping libraries.
- Respect rate limits. Cache aggressively.
- Check terms of service. Some sites prohibit automated access.

**If new to football data:**
- Start with StatsBomb open data. It's free, well-documented, and has a large community.
- Don't trust xG models blindly. Understand what goes into them.
- Football data has inherent noise. Small samples are misleading.

**If using commercial APIs (Opta, Wyscout, StatsBomb API):**
- These cost money. Understand your tier limits.
- Data redistribution is usually prohibited. Check your license.
- API keys are secrets. Never commit them to git.

**If building a product:**
- Data licensing is complex. Commercial use often requires separate agreements.
- Consider data freshness requirements. Live vs batch.

### 4. Write the profile

Write `.nutmeg.user.md` in the project root with this structure:

```markdown
---
experience: beginner | intermediate | advanced | professional
languages: [python, r, javascript, sql]
python_stack: pandas | polars | both
providers: [statsbomb-open, fbref, understat, opta, sportmonks, wyscout]
goals: exploration | academic | content | professional | product
publishing: streamlit | web | notebooks | blog | social | none
initialized: 2026-03-25
---

# Nutmeg User Profile

## Warnings

[Generated warnings based on their setup]

## Available Skills

- `/nutmeg:init` - Update this profile
- `/nutmeg:credentials` - Manage API keys and data access
- `/nutmeg:providers` - Search provider documentation and compare data availability
- `/nutmeg:acquire` - Fetch, scrape, or download football data
- `/nutmeg:heal` - Fix broken scrapers, submit upstream issues
- `/nutmeg:wrangle` - Transform, filter, reshape, and join data
- `/nutmeg:compute` - Calculate derived metrics (xG, PPDA, passing networks, etc.)
- `/nutmeg:store` - Choose storage format and location for your data
- `/nutmeg:analyse` - Explore and interpret football data
- `/nutmeg:learn` - Glossary, papers, courses, and community resources
```

### 5. Confirm

Tell the user their profile is saved and suggest what to do next based on their experience level:

- **Beginners:** "Run `/nutmeg:learn` to get oriented, then `/nutmeg:acquire` to grab some StatsBomb open data."
- **Intermediate:** "Run `/nutmeg:providers` to search for the data you need, then `/nutmeg:acquire` to fetch it."
- **Advanced/Professional:** "You're all set. All nutmeg skills will adapt to your setup. Use `/nutmeg:providers` to search across provider docs."
