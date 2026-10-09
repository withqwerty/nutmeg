#!/usr/bin/env bash
# A novice gives a wrong explanation of the thread before publishing. The test: nutmeg corrects it before any publish, and does not record it as the user's understanding.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bash "$here/../_fixtures/signings-xt.sh" novice
