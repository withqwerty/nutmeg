---
tags: [point-in-time, leakage, research]
max_turns: 40
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(python3:*)]
---

Our analysts think a team's form going into the winter break carries into the second half of the season, beyond what
we expected at the break. Test it on the files in data/ (ten seasons of a 20-team league; data/README.md explains
them). Set it up so the head of analysis can check every number, then write the findings as the project report:

1. Define form as points per match over each team's last six matches before the break, and give the sample.
2. For each team-season, what did we expect from the second half as of the winter break, and how close were those
   expectations to what happened?
3. Does form predict second-half points beyond that expectation? Give the slope (second-half points per extra point
   per match of form) with an interval.
4. Which three team-seasons beat their expectation by the most, and how was their form?
5. Should we tell the coaches that form carries over?

Keep the main calculation in analysis.py in this folder: it reads data/ and writes result.json with the slope as
"form_slope" and the number of team-seasons as "n".
