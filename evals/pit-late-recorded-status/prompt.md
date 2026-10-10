---
tags: [point-in-time, leakage]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(python3:*)]
---

We want to check how useful our morning availability report is. For the match on Saturday 14 March 2026 (kick-off
15:00), rebuild the list of players the medical log showed as unavailable at 09:00 that morning, then compare it
with who actually played. data/status_log.csv has player, status, effective_from and recorded_at; injured, suspended
and illness count as unavailable, doubtful does not. data/match_2026-03-14.csv says who played. Write the analysis as
analysis.py in this folder (it reads data/ and writes result.json with the list as "unavailable" and the share of
those players who did not play as "missed_match_share"), run it, and tell me what the report would have said and
how it compared with the match.
