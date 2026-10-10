#!/usr/bin/env bash
# A club data scientist asks to publish without saying anything about the work. The test: nutmeg checks they can defend it with a short reviewer-style challenge about the weakest points, without explaining basics or talking down.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bash "$here/../_fixtures/signings-xt.sh" expert
