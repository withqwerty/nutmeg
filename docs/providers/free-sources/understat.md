# Understat

understat.com. Free xG data for the top 5 European leagues and Russian Premier League.

## What's available

| Data | Granularity |
|------|------------|
| Team xG per match | Per match |
| Player xG per match | Per match |
| Shot-level data | Per shot (location, xG, result, situation, body part) |
| Team season stats | Per season |
| Player season stats | Per season |

## Access methods

**Python (soccerdata):**

```python
import soccerdata as sd
understat = sd.Understat('ENG-Premier League', '2024')
shots = understat.read_shot_events()  # Per-shot with xG
team_stats = understat.read_team_season_stats()
```

**Direct HTTP:**

Understat serves data as JSONP embedded in HTML pages. Parse with regex or use the soccerdata wrapper.

```python
import requests, re, json
url = 'https://understat.com/match/12345'
html = requests.get(url).text
# Data is in a script tag as JSON encoded with hex escapes
match = re.search(r"var shotsData\s*=\s*JSON\.parse\('(.+?)'\)", html)
data = json.loads(codecs.decode(match.group(1), 'unicode_escape'))
```

## xG model

Understat uses a neural network trained on ~100,000 shots. Features include:
- Shot distance and angle
- Body part (foot, head)
- Situation (open play, set piece, counter, penalty)
- Last action (pass, cross, through ball, dribble, etc.)

Their xG model is independent from StatsBomb and Opta. Values will differ.

## Coverage

| League | Available since |
|--------|----------------|
| Premier League | 2014/15 |
| La Liga | 2014/15 |
| Bundesliga | 2014/15 |
| Serie A | 2014/15 |
| Ligue 1 | 2014/15 |
| Russian Premier League | 2014/15 |

## Caveats

- No official API. Data is scraped from the website.
- No rate limit documentation. Be respectful (1-2 req/sec).
- xG model methodology is not fully published. It's a black box.
- No event data beyond shots. No passes, tackles, etc.
- Data updates can lag 1-2 days after matches.
