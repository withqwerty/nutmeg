import csv
from collections import defaultdict

xt = defaultdict(float)
with open("data/events.csv") as handle:
    for r in csv.DictReader(handle):
        xt[r["player"]] += float(r["xt_added"])
with open("data/players.csv") as handle:
    rows = [r for r in csv.DictReader(handle) if int(r["minutes"]) >= 900]
for r in rows:
    r["xt_p90"] = xt[r["player"]] * 90 / int(r["minutes"])
squad = sorted(r["xt_p90"] for r in rows if r["signed_summer_2026"] == "no")
median = (squad[len(squad) // 2] if len(squad) % 2 else (squad[len(squad) // 2 - 1] + squad[len(squad) // 2]) / 2)
print(f"existing squad median xT per 90: {median:.2f} (n={len(squad)})")
for r in sorted(rows, key=lambda r: -r["xt_p90"]):
    if r["signed_summer_2026"] == "yes":
        print(f"{r['player']}: {r['xt_p90']:.2f} xT per 90 from {r['minutes']} minutes")
