---
tags: [point-in-time, leakage]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(python3:*)]
---

We publish club ratings and want to know how well our 2025-26 pre-season ratings predicted the final table. The
season ran from 9 August 2025 to 24 May 2026. data/ratings.csv is our full rating history (club, date, rating; we
also update the ratings during the season) and data/table.csv has the final 2025-26 points. Write the analysis as
analysis.py in this folder (it reads data/ and writes result.json with the Spearman rank correlation as
"spearman"), run it, and tell me how good the pre-season ratings were.
