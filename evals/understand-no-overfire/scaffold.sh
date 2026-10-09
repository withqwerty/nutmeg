#!/usr/bin/env bash
# An expert asks a routine lookup. The test (over-firing): nutmeg answers without offering an explainer or asking for a teach-back.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bash "$here/../_fixtures/signings-xt.sh" expert
