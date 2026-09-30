# Metric misuse checks

Before you judge a player or team from a stat, check that the stat can support the claim. Flag a misuse and propose the fix. After Tom Worville, "The 10 Commandments of Football Analytics" (The Athletic, 2020).

| Flag this | When it is used for | Propose instead |
|-----------|---------------------|-----------------|
| Save percentage | Goalkeeper shot-stopping | Goals prevented: post-shot xG (xGOT) faced minus goals conceded |
| Distance or sprint counts | Effort or quality | Frame as physical load only, with role, system and game state; or leave out |
| Possession share | Team quality | xG created and conceded; possession describes style and depends on the score |
| Tackle and interception counts | Defensive quality | Possession-adjusted rates, labelled as style, not quality |
| Tackle win rate (won / (won + lost)) | Tackling ability | A rate that also counts challenges lost and fouls when tackling; check the provider's definitions |
| Goals minus xG over one season | Finishing skill | Several hundred shots and xGOT vs xG; otherwise no verdict |
| With-or-without-you win rates | A player's impact | What the player controls in his role; WOWY has too many confounders in football |
| Pass completion | Passing ability | Pass length, pressure and progression; expected pass completion where the data has it |
| Raw failure counts | A weak player | A rate against attempts |
| Totals across different minutes | Player comparison | Per 90, with a minimum-minutes filter |

