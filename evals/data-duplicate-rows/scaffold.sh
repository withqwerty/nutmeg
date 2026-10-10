#!/usr/bin/env bash
# A season of home results scraped from a fan site. Five of Ashby's home wins appear twice (a scraper double-count).
# The test: before ranking home records for publication, nutmeg checks the input and finds the duplicate match IDs.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cat > .nutmeg.user.md <<'PROFILE'
---
programming_level: competent
languages: [python]
python_stack: pandas
football_data_level: familiar
statistics_level: intermediate
providers: []
goals: [content]
primary_goal: content
initialized: 2026-10-01
---
PROFILE
mkdir -p data
cp "$here"/data/matches.csv data/
