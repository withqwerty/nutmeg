#!/usr/bin/env bash
# Writes a nutmeg profile and a fictional squad's weekly high-speed running loads (some missing) and
# injury labels for two seasons. The test: missing loads must be filled from the history season only.
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
