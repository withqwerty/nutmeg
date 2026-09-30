---
type: llm
---

The code (1) keeps only shot events, (2) excludes penalties using the shot type (shot_type == 'Penalty' or an equivalent check on the shot type), and (3) sums the StatsBomb xG column (shot_statsbomb_xg) per team.
