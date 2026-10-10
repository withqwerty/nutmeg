#!/usr/bin/env bash
# The signings-xt project on event-level data (about 1,500 rows), after its run R1. Then the event feed is refreshed:
# it now includes four of Okafor's matches the first pull missed. Nothing else says so.
# The test: asked to check the thread, nutmeg notices the run's input changed after the run, so Okafor's 0.13 and
# "no step up yet" are out of date (he is at 0.18, above the squad median).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cp -R "$here/../_fixtures/signings-events/." .
printf 'signings-xt\n' > research/.active
cat > .nutmeg.user.md <<'PROFILE'
---
programming_level: advanced
languages: [python, sql]
python_stack: pandas
football_data_level: expert
statistics_level: advanced
providers: [statsbomb-open, opta, wyscout]
goals: [professional]
primary_goal: professional
initialized: 2026-10-01
---
PROFILE
printf '{"persona": "club", "name": "Sam"}\n' > .nutmeg-user.json
git add -A >/dev/null 2>&1 && git commit -qm "project so far" >/dev/null 2>&1 || true
cp "$here/data/events_refreshed.csv" data/events.csv
git add -A >/dev/null 2>&1 && git commit -qm "refresh event data" >/dev/null 2>&1 || true
