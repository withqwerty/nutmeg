"""Pressing before and after the manager change: difference in mean PPDA (new minus previous), Welch interval."""
import argparse
import csv
import json
import math
import statistics

parser = argparse.ArgumentParser()
parser.add_argument("--window", type=int, default=15, help="matches each side of the change")
parser.add_argument("--league-only", action="store_true")
parser.add_argument("--adjust", action="store_true", help="adjust PPDA for opponent possession and cup games")
args = parser.parse_args()

rows = list(csv.DictReader(open("data/matches.csv")))
for r in rows:
    r["ppda"], r["opponent_possession"] = float(r["ppda"]), float(r["opponent_possession"])
use = [r for r in rows if not args.league_only or r["competition"] == "league"]
before = [r for r in use if r["manager"] == "previous"][-args.window:]
after = [r for r in use if r["manager"] == "new"][:args.window]


def value(r):
    if not args.adjust:
        return r["ppda"]
    return r["ppda"] - 0.12 * (r["opponent_possession"] - 50) - (1.2 if r["competition"] == "cup" else 0)


a, b = [value(r) for r in before], [value(r) for r in after]
diff = statistics.mean(b) - statistics.mean(a)
se = math.sqrt(statistics.variance(a) / len(a) + statistics.variance(b) / len(b))
p = math.erfc(abs(diff / se) / math.sqrt(2))
print(json.dumps({"window": args.window, "league_only": args.league_only, "adjusted": args.adjust,
                  "n_before": len(a), "n_after": len(b), "ppda_before": round(statistics.mean(a), 2),
                  "ppda_after": round(statistics.mean(b), 2), "difference": round(diff, 2),
                  "ci_low": round(diff - 1.96 * se, 2), "ci_high": round(diff + 1.96 * se, 2), "p": round(p, 3)}))
