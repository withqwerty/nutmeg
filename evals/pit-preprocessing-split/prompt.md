---
tags: [point-in-time, leakage]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(python3:*)]
---

Our sports scientists want to check a simple risk rule before the club uses it: flag a player-week when high-speed
running is above 10 km. Some weeks have no GPS reading, and in production we fill a missing week with the squad
average. data/weeks.csv has player, season, week, hsr_km (blank when missing) and soft_tissue_injury (1 if an
injury followed that week). Treat 2024-25 as the history we have and 2025-26 as the season the rule would have run
in. Write the analysis as analysis.py in this folder (it reads data/ and writes result.json with the 2025-26 accuracy
as "accuracy" and the value used to fill missing weeks as "fill_value"), run it, and tell me how accurate the rule is.
