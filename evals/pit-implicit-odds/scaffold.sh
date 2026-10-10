#!/usr/bin/env bash
# Writes a nutmeg profile (run-then-review on) and a simulated league in the football-data.co.uk format: results and
# pre-match odds on every match row, with no time the odds were set. The bookmakers price each match from the teams'
# strength that week, and strength drifts during a season. The test: the market's view once every team has played 12
# matches must come from the odds known by then, not from the odds of later matches, which carry later form.
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
printf '{"persona": "fanalyst", "run_then_review": true, "name": "Eval Analyst"}\n' > .nutmeg-user.json
mkdir -p .nutmeg data
printf '{"data_in_git": "no"}\n' > .nutmeg/team.json
cp "$here"/data/*.csv "$here"/data/README.md data/
