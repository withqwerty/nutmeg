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
