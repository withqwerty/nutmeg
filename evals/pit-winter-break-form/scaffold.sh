#!/usr/bin/env bash
# Writes a nutmeg profile (run-then-review on) and a simulated league: results, the club's own rating snapshots and
# betting-market probabilities published the evening before each match. The test: "what we expected as of the winter
# break" must come from what was known at the break, not from market prices published later.
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
