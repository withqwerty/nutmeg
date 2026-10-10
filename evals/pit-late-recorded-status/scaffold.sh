#!/usr/bin/env bash
# Writes a nutmeg profile and a fictional medical status log (with the date each status applies and when it was logged) and
# a match sheet. The test: a report "as of" a time must use only entries logged by then, not backdated ones.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cat > .nutmeg.user.md <<'PROFILE'
---
programming_level: competent
languages: [python]
python_stack: pandas
football_data_level: experienced
statistics_level: intermediate
providers: []
goals: [professional]
primary_goal: professional
initialized: 2026-10-08
---
PROFILE
mkdir -p data
cp "$here"/data/*.csv data/
