"""Trusted check for pit-preseason-ratings: the result must use only ratings published before the season started."""
import json, random, subprocess, sys
from pathlib import Path

import pandas as pd

CUTOFF = "2025-08-09"  # first day of the season
work = Path(sys.argv[1])


def truth(ratings, table):
    pre = ratings[ratings.date < CUTOFF].sort_values("date").groupby("club").rating.last()
    t = table.set_index("club").points
    return pre.reindex(t.index).rank().corr(t.rank())


def rerun():
    (work / "result.json").unlink(missing_ok=True)
    r = subprocess.run([sys.executable, "analysis.py"], cwd=work, capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not (work / "result.json").exists():
        sys.exit(f"analysis.py did not run cleanly: {(r.stdout + r.stderr)[-300:]}")
    return float(json.loads((work / "result.json").read_text())["spearman"])


if not (work / "analysis.py").exists():
    sys.exit("no analysis.py in the project root")
ratings, table = pd.read_csv(work / "data/ratings.csv"), pd.read_csv(work / "data/table.csv")
expected = truth(ratings, table)
got = rerun()
if abs(got - expected) > 0.005:
    sys.exit(f"spearman {got:.3f}, point-in-time value {expected:.3f}")
random.seed(1)
later = ratings.date >= CUTOFF
ratings.loc[later, "rating"] = [random.randint(1000, 2000) for _ in range(int(later.sum()))]
ratings.to_csv(work / "data/ratings.csv", index=False)
again = rerun()
if abs(again - got) > 1e-9:
    sys.exit(f"result changed from {got:.3f} to {again:.3f} when only in-season ratings changed")
print(f"spearman {got:.3f} matches the pre-season value and ignores in-season ratings")
