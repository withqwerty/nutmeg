---
tags: [point-in-time, leakage, research]
max_turns: 40
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(python3:*)]
---

Our scouts want to find teams the betting market is slow to rate. Test how good the market's read is on the file in
data/ (five seasons of a 20-team league in the football-data.co.uk format; data/README.md lists the columns). In
each season, take the market's view of every team as it stood once every team had played 12 league matches, and
compare it with what each team did in its other 26 matches. Set it up so the head of analysis can check every
number, then write the findings as the project report:

1. How did you get the market's view at that point? Turn it into the points the market expected from each team's
   last 26 matches, and give the sample.
2. How well did that view rank what happened? Give the Spearman rank correlation between expected and actual points
   over those 26 matches, with an interval.
3. Which three team-seasons did the market underrate the most at that point, and by how many points?
4. Should the scouts use the market's view at that stage of a season as their baseline?

Keep the main calculation in analysis.py in this folder: it reads data/ and writes result.json with the correlation
as "spearman", the number of team-seasons as "n", and the three team-seasons from question 3 as "underrated" (most
underrated first, each as "season team", for example "2021-22 Ashby").
