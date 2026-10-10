import argparse
import csv
import statistics

parser = argparse.ArgumentParser()
parser.add_argument("--min-minutes", type=int, default=900)
parser.add_argument("--compare", choices=("median", "mean"), default="median")
args = parser.parse_args()

with open("data/players.csv") as handle:
    rows = [r for r in csv.DictReader(handle) if int(r["minutes"]) >= args.min_minutes]
for r in rows:
    r["xt_p90"] = (float(r["xt_passes"]) + float(r["xt_carries"])) * 90 / int(r["minutes"])
squad = [r["xt_p90"] for r in rows if r["signed_summer_2026"] == "no"]
baseline = statistics.median(squad) if args.compare == "median" else statistics.mean(squad)
print(f"existing squad {args.compare} xT per 90: {baseline:.2f} (n={len(squad)}, min {args.min_minutes} minutes)")
for r in sorted(rows, key=lambda r: -r["xt_p90"]):
    if r["signed_summer_2026"] == "yes":
        print(f"{r['player']}: {r['xt_p90']:.2f} xT per 90 from {r['minutes']} minutes")
