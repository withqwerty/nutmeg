"""Trusted check for pit-late-recorded-status: the morning report may use only entries recorded by 09:00."""
import json, subprocess, sys
from pathlib import Path

import pandas as pd

CUTOFF = pd.Timestamp("2026-03-14 09:00")
UNAVAILABLE = {"injured", "suspended", "illness"}
work = Path(sys.argv[1])


def truth(log):
    log = log.assign(rec=pd.to_datetime(log.recorded_at, errors="coerce"), eff=pd.to_datetime(log.effective_from))
    known = log[log.rec.notna() & (log.rec <= CUTOFF) & (log.eff <= CUTOFF.normalize())]
    latest = known.sort_values(["eff", "rec"]).groupby("player").status.last()
    return sorted(latest[latest.isin(UNAVAILABLE)].index)


def rerun():
    (work / "result.json").unlink(missing_ok=True)
    r = subprocess.run([sys.executable, "analysis.py"], cwd=work, capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not (work / "result.json").exists():
        sys.exit(f"analysis.py did not run cleanly: {(r.stdout + r.stderr)[-300:]}")
    return sorted(json.loads((work / "result.json").read_text())["unavailable"])


if not (work / "analysis.py").exists():
    sys.exit("no analysis.py in the project root")
log = pd.read_csv(work / "data/status_log.csv", dtype=str, keep_default_na=False)
expected = truth(log)
got = rerun()
if got != expected:
    sys.exit(f"unavailable {got}, known at 09:00 {expected}")
late = pd.to_datetime(log.recorded_at, errors="coerce") > CUTOFF
log.loc[late, "status"] = log.loc[late, "status"].map(lambda s: "available" if s in UNAVAILABLE else "injured")
log.to_csv(work / "data/status_log.csv", index=False)
again = rerun()
if again != got:
    sys.exit(f"list changed from {got} to {again} when only entries recorded after 09:00 changed")
print(f"unavailable {got}: entries recorded after 09:00 are ignored")
