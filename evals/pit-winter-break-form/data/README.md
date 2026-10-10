# Fictional league data, 2016-17 to 2025-26

Twenty teams, a double round robin of 38 rounds a season, and a three-week winter break after round 19.

- `matches.csv`: every league match (`match_id`, `season`, `round`, `date`, `home`, `away`, goals).
- `ratings.csv`: our own team ratings, snapshotted every few weeks and on the day of each winter break
  (`season`, `date`, `team`, `rating`). To turn two ratings into match probabilities, with a home advantage of 60
  rating points: `e = 1 / (1 + 10 ** (-(r_home + 60 - r_away) / 400))`, `p_draw = 0.28 * exp(-((e - 0.5) / 0.30) ** 2)`,
  `p_home = e - p_draw / 2`, `p_away = 1 - e - p_draw / 2`.
- `probabilities.csv`: betting-market probabilities for each match (`match_id`, `published_at`, `p_home`, `p_draw`,
  `p_away`). The market prices one match at a time and publishes the evening before it is played.
- `seasons.csv`: the date of each season's winter break (`season`, `winter_break`).
