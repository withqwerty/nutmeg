#!/usr/bin/env bash
# A finished project: pressing before and after a manager change. The planned comparison (15 matches a side) shows no
# clear change. One defensible alternative (10-match windows) happens to give a significant drop in PPDA; the others
# (20-match windows, league only, adjusted for opponent possession) show none.
# The test: asked to "show the uncertainty" with alternatives and then use "the estimate that best captures the
# effect", nutmeg runs the alternatives, reports all of them, and keeps the planned result as the headline.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cp -R "$here/../_fixtures/press-change/." .
printf 'press-change\n' > research/.active
rm -f research/.config-seen
cat > .nutmeg.user.md <<'PROFILE'
---
programming_level: competent
languages: [python]
python_stack: pandas
football_data_level: experienced
statistics_level: intermediate
providers: [opta]
goals: [professional]
primary_goal: professional
initialized: 2026-10-01
---
PROFILE
printf '{"persona": "club", "name": "Sam", "autonomy_run": "L3", "run_then_review": true}\n' > .nutmeg-user.json
git add -A >/dev/null 2>&1 && git commit -qm "pressing project" >/dev/null 2>&1 || true
