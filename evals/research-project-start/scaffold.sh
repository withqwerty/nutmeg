#!/usr/bin/env bash
# Writes a nutmeg profile into the eval workspace so skills skip first-run setup.
set -euo pipefail
cat > .nutmeg.user.md <<'PROFILE'
---
programming_level: competent
languages: [python, sql]
python_stack: pandas
football_data_level: experienced
statistics_level: intermediate
providers: [statsbomb-open, fbref, understat, opta]
goals: [professional, content]
primary_goal: professional
initialized: 2026-09-30
---
PROFILE

mkdir -p data
cat > data/players.csv <<'CSV'
player,team,position,minutes,prog_carries,prog_passes
A. Robertson,Liverpool,LB,2710,88,190
P. Estupinan,Brighton,LB,2398,61,154
M. Lewis-Skelly,Arsenal,LB,1890,55,98
D. Udogie,Tottenham,LB,1622,74,81
V. Kerkez,Bournemouth,LB,3021,93,140
CSV
