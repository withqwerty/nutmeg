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

cat > fbref_players.csv <<'CSV'
fbref_id,player,squad,minutes,xg
dc7f8a28,Cole Palmer,Chelsea,3180,16.1
1f44ac21,Erling Haaland,Manchester City,2890,22.4
bc7dc64d,Bukayo Saka,Arsenal,2690,11.2
CSV
cat > tm_values.csv <<'CSV'
tm_id,name,club,market_value_eur
568177,Cole Palmer,Chelsea FC,130000000
418560,Erling Haaland,Man City,180000000
433177,Bukayo Saka,Arsenal FC,140000000
CSV
