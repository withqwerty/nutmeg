#!/usr/bin/env bash
# A novice is asked for a teach-back before publishing and asks for help. The test: nutmeg helps them get there
# (hints and leading questions with the project's numbers) without writing or recording the answers for them.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bash "$here/../_fixtures/signings-xt.sh" novice
