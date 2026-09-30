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

cat > goals_by_team.py <<'PY'
import json
from collections import Counter

# Opta match events for one fixture (matchevent feed)
events = json.load(open("match_events.json"))["liveData"]["event"]

goals = Counter()
for e in events:
    if e["typeId"] == 16:  # goal
        goals[e["contestantId"]] += 1

for team, n in goals.items():
    print(team, n)
PY
