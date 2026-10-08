#!/usr/bin/env bash
# Writes a nutmeg profile and a fictional league's rating history (published before and during the season) and
# final table. The test: an evaluation of pre-season ratings must use only ratings published before the season.
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
