# Plan: Signings xt

Each choice says why it was made and what it rests on. Add choices with
`nutmeg plan choose`; check them with `nutmeg plan check`.

## Choices

### metric: expected threat (xT) added by passes and carries, per 90
- why: xT credits moves that take the ball to more dangerous areas, which is what 'threat with the ball' means here.
- rests_on: paper Karun Singh, Introducing Expected Threat (2018)

### filter: at least 900 league minutes
- why: Per-90 rates from fewer minutes swing too much to rank players on.
- rests_on: rule nutmeg metric-misuse checks: per 90 needs a minimum-minutes filter

### method: compare each signing with the median of the existing squad
- why: A plain ranking hides whether any signing is better than the players already here.
- rests_on: user 'are they actually better than what we had?'
