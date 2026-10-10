#!/usr/bin/env bash
# Writes a nutmeg profile (run-then-review on) and a simulated league: results and betting-market probabilities
# published the evening before each match. The test: "what the market expected as of the winter break" must come
# from prices published by the break, not from prices published later.
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
