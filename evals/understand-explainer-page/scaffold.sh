#!/usr/bin/env bash
# A novice asks for a shareable explainer they can edit. The test: an editable source and a self-contained page, whose numbers all come from the project's ledger.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bash "$here/../_fixtures/signings-xt.sh" novice
