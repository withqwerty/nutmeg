#!/usr/bin/env bash
# A novice explains the thread well before publishing. The test (over-firing): nutmeg goes ahead to publish and does not demand more explanation.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bash "$here/../_fixtures/signings-xt.sh" novice
