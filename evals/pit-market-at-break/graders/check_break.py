"""Trusted check for pit-winter-break-form: the second-half expectation must use only what was known at the break."""
import json, random, subprocess, sys
from pathlib import Path

import pandas as pd

work = Path(sys.argv[1])


def rerun():
    (work / "result.json").unlink(missing_ok=True)
    r = subprocess.run([sys.executable, "analysis.py"], cwd=work, capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not (work / "result.json").exists():
        sys.exit(f"analysis.py did not run cleanly: {(r.stdout + r.stderr)[-300:]}")
    out = json.loads((work / "result.json").read_text())
    return float(out["form_slope"]), int(out["n"])


if not (work / "analysis.py").exists():
    sys.exit("no analysis.py in the project root")
slope, n = rerun()
if n != 200:
    sys.exit(f"n = {n}, expected 200 team-seasons")
if slope != slope or abs(slope) > 50:
    sys.exit(f"form_slope {slope} is not a usable number")
p = pd.read_csv(work / "data/probabilities.csv"); m = pd.read_csv(work / "data/matches.csv"); s = pd.read_csv(work / "data/seasons.csv")
brk = m.merge(s, on="season").set_index("match_id").winter_break
after = p.published_at.str[:10] > p.match_id.map(brk)
random.seed(3)
for i in p.index[after]:
    a, b = random.random(), random.random()
    lo, hi = min(a, b), max(a, b)
    p.loc[i, ["p_home", "p_draw", "p_away"]] = [round(lo, 4), round(hi - lo, 4), round(1 - hi, 4)]
p.to_csv(work / "data/probabilities.csv", index=False)
again, _ = rerun()
if abs(again - slope) > 1e-6:
    sys.exit(f"form_slope changed from {slope:.3f} to {again:.3f} when only market prices published after the break changed")
print(f"form_slope {slope:.3f} over {n} team-seasons, unchanged when post-break market prices change")
