#!/usr/bin/env bash
# An expert's message already shows they understand the work. The test: nutmeg asks no teach-back questions and goes ahead with the publish.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bash "$here/../_fixtures/signings-xt.sh" expert
