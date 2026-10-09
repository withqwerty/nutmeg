# Fictional league data, 2021-22 to 2025-26

Twenty teams, a double round robin of 38 matches a team each season, August to May. `matches.csv` has the five
seasons one after another, one row per match, in the football-data.co.uk format:

- `Div`: league division
- `Date`: match date (dd/mm/yyyy)
- `Time`: kick-off time
- `HomeTeam`, `AwayTeam`: home and away team
- `FTHG`, `FTAG`: full-time home and away goals
- `FTR`: full-time result (H = home win, D = draw, A = away win)
- `B365H`, `B365D`, `B365A`: Bet365 home win, draw and away win odds
- `PSH`, `PSD`, `PSA`: Pinnacle home win, draw and away win odds
- `AvgH`, `AvgD`, `AvgA`: market average home win, draw and away win odds

All odds are decimal pre-match 1X2 odds.
