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

mkdir -p research/lb-shortlist/runs research/lb-shortlist/figures research/lb-shortlist/data
printf 'lb-shortlist\n' > research/.active
printf '.active\n.python-warned\n*/runs/.pending/\n' > research/.gitignore
printf 'claims.jsonl merge=union\nreceipts.jsonl merge=union\n' > research/.gitattributes
cat > research/lb-shortlist/project.json <<'JSON'
{"slug": "lb-shortlist", "title": "Left-back shortlist", "author": "Analyst", "created": "2026-09-30T09:00:00Z", "data_in_git": "no"}
JSON
cat > research/lb-shortlist/question.md <<'MD'
# Left-back shortlist

**Question:** Which Premier League left-backs progress the ball best, for Friday's recruitment meeting?
MD
cat > research/lb-shortlist/plan.md <<'MD'
# Plan: Left-back shortlist

## Choices

### filter: at least 900 league minutes
- why: Per-90 rates from fewer minutes swing too much to rank players on.
- rests_on: rule nutmeg metric-misuse checks: per 90 needs a minimum-minutes filter

### metric: progressive carries and progressive passes per 90
- why: The recruitment brief asks for ball progression, and these two count it directly.
- rests_on: user brief from the head of recruitment, 29 September
MD
: > research/lb-shortlist/claims.jsonl
: > research/lb-shortlist/receipts.jsonl
printf '{"files": []}\n' > research/lb-shortlist/data/manifest.json

mkdir -p queries
cat > queries/progression.sql <<'SQL'
SELECT player, team, minutes,
       ROUND((prog_carries + prog_passes) * 90.0 / minutes, 2) AS prog_actions_p90
FROM players
WHERE position = 'LB' AND minutes >= 900
ORDER BY prog_actions_p90 DESC
LIMIT 3;
SQL
cat > analysis.py <<'PY'
import csv
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE players (player, team, position, minutes INT, prog_carries INT, prog_passes INT)")
with open("data/players.csv") as handle:
    rows = list(csv.DictReader(handle))
con.executemany("INSERT INTO players VALUES (?, ?, ?, ?, ?, ?)",
                [(r["player"], r["team"], r["position"], int(r["minutes"]), int(r["prog_carries"]), int(r["prog_passes"])) for r in rows])
for row in con.execute(open("queries/progression.sql").read()):
    print(row)
PY
mkdir -p data
cat > data/players.csv <<'CSV'
player,team,position,minutes,prog_carries,prog_passes
A. Robertson,Liverpool,LB,2710,88,190
P. Estupinan,Brighton,LB,2398,61,154
M. Lewis-Skelly,Arsenal,LB,1890,55,98
D. Udogie,Tottenham,LB,1622,74,81
V. Kerkez,Bournemouth,LB,3021,93,140
CSV
