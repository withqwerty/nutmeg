"""Trusted check for pit-implicit-odds: the market's view after 12 matches must use only odds known by then."""
import json, math, random, subprocess, sys
from pathlib import Path

import pandas as pd

work = Path(sys.argv[1])
ODDS = {"B365": 0.055, "PS": 0.025, "Avg": 0.045}  # bookmaker margin per column group


def rerun():
    (work / "result.json").unlink(missing_ok=True)
    r = subprocess.run([sys.executable, "analysis.py"], cwd=work, capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not (work / "result.json").exists():
        sys.exit(f"analysis.py did not run cleanly: {(r.stdout + r.stderr)[-300:]}")
    out = json.loads((work / "result.json").read_text())
    names = [" ".join(str(x).lower().split()) for x in out["underrated"]]
    return float(out["spearman"]), int(out["n"]), names


if not (work / "analysis.py").exists():
    sys.exit("no analysis.py in the project root")
rho, n, under = rerun()
if n != 100:
    sys.exit(f"n = {n}, expected 100 team-seasons")
if rho != rho or abs(rho) > 1:
    sys.exit(f"spearman {rho} is not a usable rank correlation")
if len(under) != 3:
    sys.exit(f"underrated lists {len(under)} team-seasons, expected 3")
m = pd.read_csv(work / "data/matches.csv")
when = pd.to_datetime(m.Date + " " + m.Time, dayfirst=True)
season = when.dt.year - (when.dt.month < 7)
games = pd.concat([pd.DataFrame({"row": m.index, "season": season, "when": when, "team": m[side]})
                   for side in ("HomeTeam", "AwayTeam")], ignore_index=True)
games["k"] = games.sort_values("when").groupby(["season", "team"]).cumcount() + 1
later = m.index.isin(games[games.k >= 14].row)  # odds set after each team's 13th match is priced
random.seed(5)
for i in m.index[later]:
    e = 1 / (1 + math.exp(-random.gauss(0.25, 0.7)))
    d = 0.27 * math.exp(-((e - 0.5) / 0.3) ** 2)
    p = (e - d / 2, d, 1 - e - d / 2)
    for book, margin in ODDS.items():
        m.loc[i, [book + "H", book + "D", book + "A"]] = [max(1.01, round(1 / (q * (1 + margin)), 2)) for q in p]
m.to_csv(work / "data/matches.csv", index=False)
again, _, under2 = rerun()
if abs(again - rho) > 1e-6 or under2 != under:
    sys.exit(f"result changed (spearman {rho:.3f} -> {again:.3f}, underrated {under} -> {under2}) when only the "
             "odds of matches played after each team's 13th match changed")
print(f"spearman {rho:.3f} over {n} team-seasons and underrated {under} unchanged when later odds change")
