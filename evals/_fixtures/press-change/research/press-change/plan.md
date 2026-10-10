# Plan: Press change

Each choice says why it was made and what it rests on. Add choices with
`nutmeg plan choose`; check them with `nutmeg plan check`.

## Choices

### metric: PPDA: opponent passes allowed per defensive action, per match
- why: It is the pressing measure the board already sees in match reports.
- rests_on: user 'use the PPDA we report every week'

### method: difference in mean PPDA, last 15 matches before v first 15 after, all games, with a 95% interval
- why: Fifteen a side balances recency against noise and uses every competitive match.
- rests_on: user 'compare the same number of games either side'
