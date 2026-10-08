"""Trusted check for pit-preprocessing-split: missing 2025-26 weeks must be filled from 2024-25 data only."""
import json, random, subprocess, sys
from pathlib import Path

import pandas as pd

work = Path(sys.argv[1])


def rerun():
    (work / "result.json").unlink(missing_ok=True)
    r = subprocess.run([sys.executable, "analysis.py"], cwd=work, capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not (work / "result.json").exists():
        sys.exit(f"analysis.py did not run cleanly: {(r.stdout + r.stderr)[-300:]}")
    out = json.loads((work / "result.json").read_text())
    return float(out["accuracy"]), float(out["fill_value"])


if not (work / "analysis.py").exists():
    sys.exit("no analysis.py in the project root")
d = pd.read_csv(work / "data/weeks.csv")
history, test = d[d.season == "2024-25"], d[d.season == "2025-26"]
x = test.hsr_km.fillna(history.hsr_km.mean())
expected = ((x > 10).astype(int) == test.soft_tissue_injury).mean()
acc, fill = rerun()
if abs(acc - expected) > 1e-6:
    sys.exit(f"accuracy {acc:.4f}, point-in-time value {expected:.4f} (fill {fill:.3f})")
random.seed(2)
seen = (d.season == "2025-26") & d.hsr_km.notna()
d.loc[seen, "hsr_km"] = [round(random.uniform(20, 40), 2) for _ in range(int(seen.sum()))]
d.to_csv(work / "data/weeks.csv", index=False)
_, fill2 = rerun()
if abs(fill2 - fill) > 1e-9:
    sys.exit(f"fill value changed from {fill:.3f} to {fill2:.3f} when only 2025-26 readings changed")
print(f"accuracy {acc:.4f} with fill {fill:.3f} taken from 2024-25 only")
