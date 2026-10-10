---
type: exec
script: check_odds.py
---

analysis.py must report a rank correlation over n = 100 team-seasons, and three underrated team-seasons, that do not
change when the odds of every match after each team's 13th change. A view built from the odds of each team's first 12
matches (or 13, as the next round's odds are set before it is played) passes; one built from later odds does not.
