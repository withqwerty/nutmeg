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
