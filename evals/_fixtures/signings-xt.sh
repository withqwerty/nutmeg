#!/usr/bin/env bash
# Shared scaffold: a finished research project (signings-xt) with a clean `nutmeg check`, and a user profile.
# Usage: bash signings-xt.sh novice|expert   (run from the eval workspace)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cp -R "$here/signings-xt/." .
printf 'signings-xt\n' > research/.active
case "${1:-novice}" in
  novice)
    cat > .nutmeg.user.md <<'PROFILE'
---
programming_level: beginner
languages: [python]
python_stack: pandas
football_data_level: new
statistics_level: basic
providers: []
goals: [content]
primary_goal: content
initialized: 2026-10-01
---
PROFILE
    printf '{"persona": "fanalyst", "name": "Sam"}\n' > .nutmeg-user.json ;;
  expert)
    cat > .nutmeg.user.md <<'PROFILE'
---
programming_level: advanced
languages: [python, sql]
python_stack: pandas
football_data_level: expert
statistics_level: advanced
providers: [statsbomb-open, opta, wyscout]
goals: [professional, content]
primary_goal: professional
initialized: 2026-10-01
---
PROFILE
    printf '{"persona": "fanalyst", "name": "Sam"}\n' > .nutmeg-user.json ;;
esac
git add -A >/dev/null 2>&1 && git commit -qm "project so far" >/dev/null 2>&1 || true
