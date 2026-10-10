#!/usr/bin/env bash
# A novice is confused about the result and needs to explain it to others. The test: nutmeg explains with this project's numbers and offers a shareable explainer they can edit.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bash "$here/../_fixtures/signings-xt.sh" novice
