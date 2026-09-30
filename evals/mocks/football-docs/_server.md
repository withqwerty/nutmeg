---
type: agent
tools: [search_docs, get_provider_docs, compare_providers, list_providers, resolve_provider_id, resolve_entity, request_update]
---

You are a replay of the football-docs MCP server, version 0.14.0.
You never write new documentation content. Every answer is one recorded response below, copied exactly.

How to answer a call:

1. Look at the tool name and the words in its arguments.
2. Choose the recording for that tool whose keywords share the most words with the arguments (ignore case and
   punctuation). For search_docs, get_provider_docs and compare_providers, any search recording may be used.
3. Return that recording's text exactly, character for character. Do not add, drop or reword anything.
4. search_docs, get_provider_docs or compare_providers with no keyword overlap at all: return recording
   s03. The real server almost always returns loosely related results.
5. resolve_provider_id for a provider not in the table: return exactly
   `Provider "<query>" is not registered. Use request_update to suggest adding it, or open a GitHub issue with the new-provider template.`
   as an error result.
6. resolve_entity with a provider and id not in the table: return exactly
   `No Reep entity matches that query in the local register.` then a blank line, then
   `Local register release: 20260926T145536Z (current).`
7. request_update: return exactly
   `Request queued locally. Open this pre-filled issue to send it: https://github.com/withqwerty/football-docs/issues/new`
8. Recordings marked `error` are tool errors: return them as an error result.

## Routing table

| Recording | Tool | Keywords |
| --- | --- | --- |
| s01 | search_docs | big chance, bigChance, 214, shot qualifiers, headed, head, own goal qualifier (Opta) |
| s02 | search_docs | xG, expected goals, xGOT, 321, 322, matchexpectedgoals, matchevent, endpoint, feed (Opta) |
| s05 | search_docs | own goal, Own Goal For, Own Goal Against, goal attribution (StatsBomb) |
| s06 | search_docs | penalty, shot type, set piece shot (StatsBomb) |
| s14 | search_docs | shot fields, statsbomb_xg, shot_statsbomb_xg, statsbombpy events, non-penalty xG, npxG (StatsBomb) |
| s07 | search_docs | FBref, advanced stats, xG on FBref, progressive passes, 2026 removal |
| s15 | search_docs | soccerdata FBref, read_player_season_stats, read_team_season_stats |
| s08 | search_docs | Reep, register, download, DuckDB, CSV, release, latest.json, REEP_DUCKDB_PATH, bulk IDs, crosswalk |
| s09 | search_docs | Transfermarkt IDs, spieler, identity surfaces (Transfermarkt) |
| s13 | search_docs | FBref IDs, person ID, identity surfaces (FBref) |
| s10 | search_docs | Sofascore, 403, challenge, anti-bot, blocked, Cloudflare, scraper broken |
| s11 | search_docs | goalkeeper, shot-stopping, save percentage, post-shot xG, PSxG, goals prevented |
| s12 | search_docs | tackles, interceptions, defensive actions, possession-adjusted, PAdj, defender |
| s16 | search_docs | tackle win rate, tackles won, tackles lost, challenges lost, dribbled past, duels |
| s17 | search_docs | distance covered, km, sprints, physical metrics, running |
| s03 | search_docs | Catapult, STATSports, Kinexon, GPS, wearables, PlayerLoad, physical export fields |
| s04 | search_docs | any call with provider set to catapult, statsports, kinexon or another GPS vendor |
| g01 | get_provider_docs | get_provider_docs for Opta (any topic about qualifiers or big chance) |
| l01 | list_providers | list_providers |
| p01 | resolve_provider_id | Catapult, STATSports, Kinexon, GPS vendors |
| p02 | resolve_provider_id | Reep, Reep Register, reep.football |
| p03 | resolve_provider_id | Opta, Stats Perform |
| p04 | resolve_provider_id | StatsBomb, Hudl StatsBomb |
| p05 | resolve_provider_id | FBref |
| p06 | resolve_provider_id | Transfermarkt |
| p07 | resolve_provider_id | Sofascore, soccerdata |
| r01 | resolve_entity | resolve_entity with provider transfermarkt and id 568177 (with or without namespace) |
| r03 | resolve_entity | resolve_entity with provider fbref and id dc7f8a28 (with or without namespace) |
| r02 | resolve_entity | resolve_entity by name (any name) |

## Recordings

### s01 — search_docs {"query": "big chance qualifier", "provider": "opta", "max_results": 4}

````text
Found 4 result(s) for "big chance qualifier" in opta:

## [1] Zone and low-xG proxies
**Provider:** opta | **Category:** charting-shot-placement | **Source:** curated by football-docs contributors

## Zone and low-xG proxies

If a continuous xG source is unavailable, zone qualifiers can be used as a rough
proxy, but label the result as a proxy rather than xG:

| Zone qualifier family | Typical use |
|---|---|
| `16`, `60`, `61` | small-box zones; usually exclude from low-xG placement-skill cuts |
| `17` | box centre |
| `62`, `63`, `64`, `65` | box wide/deep-box zones |
| `18` | out-of-box centre |
| `66`, `67`, `68`, `69` | out-of-box wide/deep zones |
| `19`, `70`, `71` | thirty-five-plus / long-range zones |
| `214` | big chance; usually exclude from low-xG placement-skill cuts |
| `9` | penalty; exclude or analyse separately |

For a robust first pass, join continuous xG from `matchexpectedgoals` where possible.
If you only have `matchevent`, a low-xG proxy can exclude small-box, big-chance, and
penalty qualifiers, then report zone-adjusted residuals so wide-angle geometry does
not masquerade as finishing skill.

---

## [2] Shot Qualifiers
**Provider:** opta | **Category:** qualifiers | **Source:** curated by football-docs contributors

## Shot Qualifiers

| ID | Name | Notes |
|----|------|-------|
| 15 | head | Headed shot/goal |
| 20 | rightFoot | Right-footed shot |
| 72 | leftFoot | Left-footed shot |
| 21 | otherBodyPart | Knee, chest, etc. |
| 22 | regularPlay | The event happened in open play, not from a set play |
| 24 | setPiece | The event followed a free kick that was not struck directly. A shot struck directly from a free kick is Q26 |
| 25 | fromCorner | Shot followed a corner |
| 26 | freeKick | Shot struck directly from a free kick |
| 29 | assisted | A team-mate's pass set up the shot or chance |
| 160 | throwInSetPiece | The shot or pass came from a throw-in set piece |
| 214 | bigChance | Big chance: a clear-cut chance the player should score, such as a one-on-one |
| 9 | penalty | Penalty taken, or penalty awarded (on a foul, typeId 4) |
| 108 | volley | Volley: the ball did not bounce before the shot |
| 328 | firstTouch | Shot struck first time, without a controlling touch |
| 263 | directCorner | Shot or goal directly from a corner (Olimpico) |
| 136 | keeperTouched | Goal where the goalkeeper got a touch on the ball |
| 82 | blocked | The shot was blocked |
| 146 | blockedX | X coordinate where the shot was blocked, or where an opponent touched an off-target shot |
| 147 | blockedY | Y coordinate for the same point as Q146 |

Qualifiers 16-19 and 60-71 are pitch zones for the shot location (for example 16
small box centre, 17 box centre, 18 out of box centre, 19 35+ centre). See
charting-shot-placement for the full zone list.

---

## [3] Pass Qualifiers
**Provider:** opta | **Category:** qualifiers | **Source:** curated by football-docs contributors

## Pass Qualifiers

| ID | Name | Notes |
|----|------|-------|
| 1 | longBall | Pass longer than 32 metres |
| 2 | cross | Cross (Q2). Corners commonly carry Q2 + Q6; free-kick crosses commonly carry Q2 + Q5; open-play crosses are Q2 without Q5/Q6. |
| 3 | headPass | Headed pass (Q3). Distinct from Q15, the headed shot qualifier. |
| 4 | throughBall | Through ball (Q4). Do not confuse with Q5 free-kick delivery. |
| 5 | freeKickTaken | Free kick pass / free-kick delivery (Q5), direct or indirect. |
| 6 | cornerTaken | Corner kick / corner delivery (Q6). |
| 107 | throwIn | Throw-in |
| 124 | goalKick | Goal kick pass. For goal-kick distribution charts, combine with pass end coordinates Q140/Q141. |
| 279 | kickOff | Kick-off pass. Value `S` is the kick-off that starts a period; `G` is the kick-off after a goal. |
| 7 | playersCaughtOffside | On an offside pass (typeId 2). The value is the ID of the player caught offside. It is not a goal-kick flag; goal kicks are Q124. |
| 154 | intentionalAssist | Pass that creates a scoring chance, for example a cross into the box or a through ball |
| 210 | assist | The pass set up a shot, a goal or a missed chance |
| 196 | switchOfPlay | Pass crossing centre zone, y-distance > 60 |
| 212 | length | Estimated distance in metres that the ball travelled on the pass or clearance |
| 213 | angle | Direction of the pass or clearance relative to the direction of play, in radians (0.00 to 6.28) |

---

## [4] Shot context and consequence filters
**Provider:** opta | **Category:** charting-shot-placement | **Source:** curated by football-docs contributors

## Shot context and consequence filters

Shot-placement stories often ask whether a miss, save, post hit, or weak finish
changed the match state. Join each shot row to a running scoreline timeline before
building late-game, close-game, or "mattered" filters.

| Derived field | How to derive it | Use |
|---|---|---|
| `team_score_at_shot` / `opp_score_at_shot` | Count valid goals strictly before the shot clock, from the shooting team's perspective | Tooltip, score-state splits, consequence labels |
| `goal_diff_at_shot` | `team_score_at_shot - opp_score_at_shot` | Classify whether the shooter was leading, level, or trailing |
| `state_at_shot` | `winning`, `drawing`, or `losing` from `goal_diff_at_shot` | Filter shot maps by game state or pressure context |
| `is_late` | minute threshold such as `minute >= 80`, using expanded minutes when available | Late-shot and stoppage-time story filters |
| `is_close_final` | final margin within one goal, after converting to the shooting team's perspective | Avoid overstating misses in already-decided matches |
| `mattered` | shot taken while the goal difference was within one and the final margin was within one | Narrative filter for chances that could plausibly change the result |

Use the goal-timeline reconstruction in [charting-game-state.md](charting-game-state.md):
drop disallowed goals with qualifier `8`, credit own goals with qualifier `28` to
the opposing team, and sort by period-aware clock or `expandedMinute`. Count only
goals before the shot; a goal event at the same clock should not retroactively
change the shot's pre-shot state unless the provider explicitly links them.

Keep these consequence fields separate from provider facts. `mattered`,
`late`, `close final`, and `pressure shot` are analysis labels layered on top of
Opta events, not Opta event types.
````

### s02 — search_docs {"query": "expected goals xG qualifier", "provider": "opta", "max_results": 4}

````text
Found 4 result(s) for "expected goals xG qualifier" in opta:

## [1] Shot placement data surfaces
**Provider:** opta | **Category:** charting-shot-placement | **Source:** curated by football-docs contributors

## Shot placement data surfaces

Opta/WhoScored-style shot placement charts need the F24 event stream plus, when
available, the separate expected-goals endpoint:

| Need | Best Opta surface | Notes |
|---|---|---|
| Shot origin, body part, outcome, and goal-mouth endpoint | `matchevent/{token}?fx={matchId}` | Shot events are typeIds `13`, `14`, `15`, and `16`; goal-mouth coordinates are qualifiers `102` and `103`. |
| Continuous provider xG and xGOT | `matchexpectedgoals/{token}?fx={matchId}` | Use qualifiers `321` (`expectedGoals`) and `322` (`expectedGoalsOnTarget`) from this endpoint when present. |
| Lineups and player labels | `matchstats/{token}?fx={matchId}` | Join by `playerId`; use `matchName`, position, and lineup fields for display. |

Do not read qualifier `213` as xG: it is the pass or clearance angle. The public
Opta Analyst-style feed supplies xG as qualifier `321` on `matchexpectedgoals`.

---

## [2] Build a goalmouth shot chart
**Provider:** opta | **Category:** charting-shot-placement | **Source:** curated by football-docs contributors

## Build a goalmouth shot chart

A goalmouth shot chart needs the shot event, the goal-mouth endpoint qualifiers,
and the expected-goals surface in one joined row. Use this recipe when an agent
asks for a goalmouth chart, shot-placement chart, PSxG chart, xGOT marker-size
plot, post-distance view, or crossbar/goal-frame analysis.

| Chart field | Opta source | Implementation note |
|---|---|---|
| Shot outcome | `matchevent/{token}?fx={matchId}` typeIds `13`, `14`, `15`, `16` | Encode miss, post/woodwork, saved, blocked, and goal as separate outcomes before styling markers. |
| Goal-mouth endpoint | qualifiers `102` (`GoalMouthY`) and `103` (`GoalMouthZ`) | These are goal-mouth coordinates, not pitch coordinates. Missing values mean the shot is not plottable in the goal frame. |
| xG / PSxG / xGOT | `matchexpectedgoals/{token}?fx={matchId}` qualifiers `321` and `322` | Use xGOT/PSxG for marker radius only when present; missing xGOT should become an unavailable/default size, not zero danger. |
| Marker style | derived from outcome plus xGOT | Goals, saved shots, posts, misses, and blocks should have distinct colour/shape/fill treatment; keep opacity low enough for clustered shots. |
| Frame metrics | `GoalMouthY`, `GoalMouthZ`, goal-post/crossbar constants | Calculate post distance or frame distance only after declaring the coordinate scale and conversion. |

Prefer a direct event-id join between `matchevent` shots and
`matchexpectedgoals` rows. If that ID is not present in your feed, fall back to a
strict match on match, team, player, period, clock, and shot order, then flag the
join as inferred.

---

## [3] Match drama score recipe
**Provider:** opta | **Category:** charting-game-state | **Source:** curated by football-docs contributors

## Match drama score recipe

Use this recipe when an agent asks for a post-match entertainment score, drama
ranking, blockbuster index, weekend replay chart, or match receipt from
Opta/WhoScored-style event timelines.

| Component | Source | Rule |
|---|---|---|
| total goals | final score or valid goal timeline | Cap at a stated football-realistic maximum rather than min-maxing a single match. |
| lead changes | running scoreline milestones | Count only changes from one non-level leader to the other; drawing level is not a lead change unless your product says so. |
| comeback | running scoreline plus final result | Label whether it means draw-from-behind, win-from-behind, or both. |
| late drama | goal milestones | Count goals after a declared minute threshold, such as 80, only when they change match state. |
| xG swing | shot xG events split by half or interval | Compare expected-goal differential between periods; return unavailable if xG is not licensed. |
| possession volatility | possession intervals, where available | Count flips in the possession-leading team across stable intervals; do not infer this from final possession alone. |
| spectacle/flair | event types and qualifiers | Examples include volleys, direct free kicks, long-range goals, good-skill events, and successful take-ons. |

Implementation notes:

- Build the score from named components, then expose both the final score and the
  component values. A one-number drama score without components is hard to audit.
- Keep provider facts separate from product judgements. `lead_changes`,
  `late_drama_goals`, and `xg_swing` can be derived facts; `entertainment_score`
  is a product metric with chosen weights and caps.
- Use absolute caps for per-match components, then document them. Cross-match
  min-max normalisation can make early-season rankings unstable.
- Treat missing optional sources honestly: if xG, xGOT, or possession intervals
  are unavailable, either omit those components or use a labelled neutral value.
- Use the same valid-goal reconstruction rules as the rest of this document:
  disallowed goals do not count, and own goals are credited to the opponent.
- Do not compare scores across providers unless component definitions, event
  inclusion rules, and optional-source fallbacks are aligned.

---

## [4] Edge cases to test
**Provider:** opta | **Category:** charting-game-state | **Source:** curated by football-docs contributors

## Edge cases to test

Add tests or fixtures for these cases when implementing game-state logic:

| Case | Expected handling |
|---|---|
| Disallowed goal with qualifier `8` | does not change scoreline |
| Own goal with qualifier `28` | increments the opposing team's score |
| Multiple goals in stoppage time | sorted by expanded minute / period-aware clock |
| Goal before a pass-map window | affects every later pass in that team's state |
| Penalty shootout or post-match period | exclude from normal 90/120-minute state unless explicitly modelling shootouts |
| Missing goal timeline | do not fabricate states from final score alone |
````

### s05 — search_docs {"query": "own goal event", "provider": "statsbomb", "max_results": 4}

````text
Found 4 result(s) for "own goal event" in statsbomb:

## [1] Event Type Reference
**Provider:** statsbomb | **Category:** event-types | **Source:** curated by football-docs contributors

## Event Type Reference

| ID | Name | Description |
|----|------|-------------|
| 2 | Ball Recovery | Player regains possession from a loose ball |
| 3 | Dispossessed | Player loses the ball through opponent action (not a failed dribble) |
| 4 | Duel | Contested situation between two players (aerial or ground) |
| 5 | Camera On* | Signals the stop of the camera capturing gameplay for a replay/video cut (deprecated; superseded by `off_camera`) |
| 6 | Block | Player blocks a shot, pass, or cross |
| 8 | Offside | Player caught in an offside position |
| 9 | Clearance | Defensive action to remove the ball from a dangerous area |
| 10 | Interception | Player intercepts an opponent's pass |
| 14 | Dribble | Attempt to beat an opponent with the ball (success or failure) |
| 16 | Shot | Attempt on goal |
| 17 | Pressure | Player applies pressure on an opponent in possession |
| 18 | Half Start | Marks the start of each half/period |
| 19 | Substitution | Player substitution |
| 20 | Own Goal Against | An own goal scored against the team |
| 21 | Foul Won | Player wins a foul from an opponent |
| 22 | Foul Committed | Player commits a foul |
| 23 | Goal Keeper | Goalkeeper-specific actions (saves, punches, claims, etc.) |
| 24 | Bad Behaviour | Disciplinary action not linked to a foul (e.g. dissent) |
| 25 | Own Goal For | An own goal scored for the team |
| 26 | Player On | Player enters the pitch (substitution on) |
| 27 | Player Off | Player leaves the pitch (substitution off) |
| 28 | Shield | Player shields the ball from an opponent |
| 30 | Pass | Any pass between players, including crosses, through balls, etc. |
| 33 | 50/50 | Contested loose ball between two players |
| 34 | Half End | Marks the end of each half/period |
| 35 | Starting XI | Starting lineup announcement (one per team per match) |
| 36 | Tactical Shift | Formation or positional change during play |
| 37 | Error | Player makes an on-the-ball mistake that leads to a shot on goal |
| 38 | Miscontrol | Player fails to control the ball cleanly |
| 39 | Dribbled Past | Player is beaten by an opponent's dribble |
| 40 | Injury Stoppage | Play stopped due to injury |
| 41 | Referee Ball-Drop | Referee drops the ball to resume play after an injury stoppage |
| 42 | Ball Receipt* | Player receives a pass (the asterisk is part of the name) |
| 43 | Carry | Player moves with the ball at their feet between events |

> The event-type vocabulary and field set below describe the **Events API
> v8.0.0** feed (`GET /api/v8/events/{match_id}`). Each match also carries a
> `metadata.data_version` string (see `data-model.md`) — the exact set of
> fields present on a given match depends on the data version it was collected
> under.

---

---

## [2] Attack Direction
**Provider:** statsbomb | **Category:** coordinate-system | **Source:** curated by football-docs contributors

## Attack Direction

The team in possession **always attacks left to right** (toward x=120). StatsBomb normalises all coordinates so that the acting team's goal is at x=0 and the opponent's goal is at x=120. This means:

- A shot from the edge of the box will have x around 96-102
- A goalkeeper's location will be around x=0-2 (own goal) or x=118-120 (opponent GK in freeze frames, shown from that team's perspective)
- Centre circle is at approximately (60, 40)

When viewing freeze frame data, opponent positions are shown from the perspective of the team performing the event. The opponent keeper will appear near x=120.

---

## [3] Post-Shot xG (PSxG) and goalkeeping value
**Provider:** statsbomb | **Category:** iq-metrics-glossary | **Source:** curated by football-docs contributors

## Post-Shot xG (PSxG) and goalkeeping value

PSxG models goal probability **after** the shot is struck, using placement and
velocity — only defined for on-target, unblocked shots. Used to value
goalkeeping.

- `np_psxg` — non-penalty PSxG earned from a player's on-target shots.
- `npot_psxg_faced` / `np_psxg_faced_90` — non-penalty on-target PSxG faced by a
  goalkeeper.
- `gsaa` (Goals Saved Above Average) — goals the keeper saved/conceded versus
  expectation (PSxG faced minus goals conceded). `gsaa_ratio` expresses it as a
  share of shots faced. `xs_ratio` (season) — expected save % given PSxG faced.
- `save_ratio` — % of on-target shots saved.
- `gk_positioning_error` / `np_optimal_gk_dlength` — average distance of the
  keeper from the modelled optimal position for facing a shot.
- `da_aggressive_distance` — average distance from goal at which the keeper
  performs defensive actions (sweeping tendency).
- `ccaa` / `clcaa` — Claimable Collection Attempts over Average: how often the
  keeper attempts to claim a claimable pass vs the average keeper.
- `claim_success` — % of claim attempts that succeed.
- `goals_conceded` (player-match) — goals conceded by the keeper, excluding
  penalties and own goals.

The Events v8 shot object decomposes shot xG into: `statsbomb_xg` (chance
quality — pre-strike situation including GK/defender positions),
`shot_execution_xg` (incorporates placement & velocity),
`shot_execution_xg_uplift` (`shot_execution_xg − statsbomb_xg`; can be
negative), `gk_save_difficulty_xg` (renamed from `statsbomb_xg2`; difficulty for
the keeper given placement/velocity/position), `gk_positioning_xg_suppression`
and `gk_shot_stopping_xg_suppression` (threat suppressed by keeper positioning /
shot-stopping). See `xg-model.md`.

---

## [4] Goals & expected goals
**Provider:** statsbomb | **Category:** team-season-stats | **Source:** curated by football-docs contributors

## Goals & expected goals

| Column | Type | Description |
|---|---|---|
| `team_season_goals_pg` | double | Goals scored (incl. penalties) + opponent own goals, per game |
| `team_season_goals_conceded_pg` | double | Goals conceded (incl. penalties) + own goals, per game |
| `team_season_gd` / `team_season_gd_pg` | double | Goal difference (total / per game, incl. penalties) |
| `team_season_np_gd_pg` | double | Non-penalty goal difference per game |
| `team_season_own_goals_pg` | double | Own goals per game |
| `team_season_opposition_own_goals_pg` | double | Opposition own goals per game |
| `team_season_penalty_goals_pg` | double | Penalties scored per game |
| `team_season_penalty_goals_conceded_pg` | double | Penalty goals conceded per game |
| `team_season_np_xg_pg` | double | npxG per game |
| `team_season_op_xg_pg` | double | Open-play xG per game |
| `team_season_sp_xg_pg` | double | Set-piece xG per game |
| `team_season_np_xg_conceded_pg` | double | npxG conceded per game |
| `team_season_op_xg_conceded_pg` | double | Open-play xG conceded per game |
| `team_season_sp_xg_conceded_pg` | double | Set-piece xG conceded per game |
| `team_season_xgd` / `team_season_xgd_pg` | double | xG minus xG conceded (total / per game, incl. penalties) |
| `team_season_np_xgd_pg` | double | Non-penalty xGD per game |
| `team_season_np_xg_per_shot` | double | npxG per shot |
| `team_season_np_xg_per_shot_conceded` | double | npxG per shot conceded |
````

### s06 — search_docs {"query": "shot type penalty", "provider": "statsbomb", "max_results": 4}

````text
Found 4 result(s) for "shot type penalty" in statsbomb:

## [1] Non-Penalty xG (npxG)
**Provider:** statsbomb | **Category:** xg-model | **Source:** curated by football-docs contributors

### Non-Penalty xG (npxG)
Filter out penalties to isolate open-play shot quality:

```python
npxg = sum(
    s["shot"]["statsbomb_xg"]
    for s in shots
    if s["shot"]["type"]["name"] != "Penalty"
)
```

---

---

## [2] Goalkeeper Types
**Provider:** statsbomb | **Category:** event-types | **Source:** curated by football-docs contributors

### Goalkeeper Types

| ID | Name |
|----|------|
| 25 | Collected |
| 26 | Goal Conceded |
| 27 | Keeper Sweeper |
| 28 | Penalty Conceded |
| 29 | Penalty Saved |
| 30 | Punch |
| 31 | Save |
| 32 | Shot Faced |
| 33 | Shot Saved |
| 34 | Smother |
| 109 | Penalty Saved to Post |
| 110 | Saved to Post |
| 113 | Shot Saved Off Target |
| 114 | Shot Saved to Post |

---

## [3] Goalkeeping
**Provider:** statsbomb | **Category:** player-match-stats | **Source:** curated by football-docs contributors

## Goalkeeping

| Column | Type | Description |
|---|---|---|
| `player_match_goals_conceded` | integer | Goals conceded (excludes penalties and own goals) |
| `player_match_gsaa` | double | Goals saved/conceded vs expectation (post-shot xG faced) |
| `player_match_gsaa_ratio` | percentage | Goals saved above average as a % of shots faced |
| `player_match_save_ratio` | percentage | % of on-target shots saved |
| `player_match_npot_psxg_faced` | double | Non-penalty on-target post-shot xG faced |
| `player_match_npot_shots_faced` | double | Non-penalty on-target shots faced |
| `player_match_penalties_faced` | integer | Penalties faced |
| `player_match_penalties_conceded` | integer | Penalties faced that resulted in goals |
| `player_match_ccaa` | percentage | Claimable Collection Attempts over Average — claim-attempt rate vs average keeper |
| `player_match_claim_success` | percentage | % of claim attempts that succeed |
| `player_match_da_aggressive_distance` | double | Average distance from goal at which the keeper performs defensive actions |
| `player_match_gk_positioning_error` | double | Average distance from the optimal position for facing a shot |

---

## [4] Attacking output (per 90 unless noted)
**Provider:** statsbomb | **Category:** player-season-stats | **Source:** curated by football-docs contributors

## Attacking output (per 90 unless noted)

| Column | Type | Description |
|---|---|---|
| `player_season_goals_90` | double | All goals (incl. penalties) |
| `player_season_npg_90` | double | Goals excluding penalties |
| `player_season_np_shots_90` | double | Non-penalty shots |
| `player_season_np_xg_90` | double | Non-penalty xG produced |
| `player_season_np_xg_per_shot` | double | Average npxG per shot (shot quality) |
| `player_season_np_psxg_90` | double | Post-shot xG earned from on-target shots |
| `player_season_npxgxa_90` | double | Non-penalty xG + xA combined |
| `player_season_npga_90` | double | Non-penalty goals + assists |
| `player_season_assists_90` | double | Assists |
| `player_season_op_assists_90` | double | Open-play assists |
| `player_season_xa_90` | double | xG assisted (from the assisted shot's xG) |
| `player_season_op_xa_90` | double | xA from open play |
| `player_season_sp_xa_90` | double | xA from set pieces |
| `player_season_key_passes_90` | double | Shot-creating passes |
| `player_season_op_key_passes_90` | double | Open-play key passes |
| `player_season_sp_key_passes_90` | double | Set-piece key passes |
| `player_season_sp_assists_90` | double | Set-piece assists |
| `player_season_shots_key_passes_90` | double | Non-penalty shots + key passes |
| `player_season_conversion_ratio` | percentage | % of non-penalty shots converted |
| `player_season_penalty_conversion_ratio` | percentage | % of penalty shots converted |
| `player_season_shot_on_target_ratio` | percentage | % of total shots on target (incl. goals, saved, cleared off line) |
| `player_season_shot_touch_ratio` | percentage | Shots as a proportion of touches |
| `player_season_over_under_performance_90` | double | Actual goal contribution minus xG+xA |
| `player_season_positive_outcome_90` | double | Possessions through the player ending in shot/attacking-half FK/corner |
| `player_season_positive_outcome_score` | percentage | Frequency of involvement in positive-outcome sequences |
````

### s14 — search_docs {"query": "shot statsbomb_xg shot type", "provider": "statsbomb", "max_results": 4}

````text
Found 4 result(s) for "shot statsbomb_xg shot type" in statsbomb:

## [1] Where xG Appears in the Data
**Provider:** statsbomb | **Category:** xg-model | **Source:** curated by football-docs contributors

## Where xG Appears in the Data

```json
{
  "type": { "id": 16, "name": "Shot" },
  "shot": {
    "statsbomb_xg": 0.024542088,
    "end_location": [117.3, 38.3, 0.8],
    "technique": { "id": 93, "name": "Normal" },
    "body_part": { "id": 40, "name": "Right Foot" },
    "type": { "id": 87, "name": "Open Play" },
    "outcome": { "id": 100, "name": "Saved" },
    "freeze_frame": [ ... ]
  }
}
```

The `statsbomb_xg` field is a float between 0.0 and 1.0 representing the probability that the shot results in a goal, given the circumstances of the shot.

---

---

## [2] Match xG
**Provider:** statsbomb | **Category:** xg-model | **Source:** curated by football-docs contributors

### Match xG
Sum all `statsbomb_xg` values for a team's shots in a match to get the team's total expected goals.

```python
import json

with open("events/3869685.json") as f:
    events = json.load(f)

for team in ["Argentina", "France"]:
    shots = [e for e in events if e["type"]["name"] == "Shot" and e["team"]["name"] == team]
    total_xg = sum(s["shot"]["statsbomb_xg"] for s in shots)
    goals = sum(1 for s in shots if s["shot"]["outcome"]["name"] == "Goal")
    print(f"{team}: {len(shots)} shots, {total_xg:.2f} xG, {goals} goals")
```

---

## [3] Non-Penalty xG (npxG)
**Provider:** statsbomb | **Category:** xg-model | **Source:** curated by football-docs contributors

### Non-Penalty xG (npxG)
Filter out penalties to isolate open-play shot quality:

```python
npxg = sum(
    s["shot"]["statsbomb_xg"]
    for s in shots
    if s["shot"]["type"]["name"] != "Penalty"
)
```

---

---

## [4] Fields
**Provider:** statsbomb | **Category:** event-types | **Source:** curated by football-docs contributors

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `statsbomb_xg` | float | xG "chance quality" -- likelihood of scoring from the shot situation (location, GK and blocker positions), **not** considering shot execution |
| `gk_save_difficulty_xg` | float | Likelihood of the keeper conceding, given shot placement/velocity and keeper position (on-target, unblocked shots only). Some feeds label this field `statsbomb_xg2` |
| `shot_execution_xg` | float | Likelihood of scoring after execution -- incorporates placement & velocity on top of the `statsbomb_xg` features |
| `shot_execution_xg_uplift` | float | `shot_execution_xg − statsbomb_xg`; how much execution improved (or, if negative, worsened) the chance |
| `gk_positioning_xg_suppression` | float | Goal-scoring threat suppressed by the keeper's positioning vs an average keeper |
| `gk_shot_stopping_xg_suppression` | float | Goals prevented above expectation by the keeper's shot-stopping |
| `end_location` | [x, y] or [x, y, z] | Where the shot ended up. Z is height in yards (present for shots that leave the ground) |
| `key_pass_id` | string | UUID of the pass that assisted this shot |
| `technique` | object | How the shot was struck |
| `body_part` | object | Which body part was used |
| `type` | object | How the shot originated |
| `outcome` | object | Result of the shot |
| `first_time` | boolean | Whether the shot was taken first-time |
| `freeze_frame` | array | Positions of all visible players at the moment of the shot |
| `one_on_one` | boolean | Whether the shooter was one-on-one with the keeper |
| `open_goal` | boolean | Whether the goal was unguarded |
| `follows_dribble` | boolean | Whether the shot followed a successful dribble |
| `redirect` | boolean | Whether the shot was a deflection/redirect |
| `saved_to_post` | boolean | Whether the keeper saved onto the post |
| `saved_off_target` | boolean | Whether the keeper saved to a position off target |
````

### s07 — search_docs {"query": "FBref xG progressive passes", "max_results": 4}

````text
Found 4 result(s) for "FBref xG progressive passes":

## [1] free-sources - fbref
**Provider:** free-sources | **Category:** fbref | **Source:** curated by football-docs contributors

# FBref

Football Reference (fbref.com). A comprehensive free source for historical results,
basic statistics and squad information across 100+ competitions.

> **Advanced statistics were removed on 20 January 2026.** Stats Perform (which owns
> Opta, FBref's provider since 2022) terminated FBref's access to its feeds, and
> Sports Reference removed the Opta-sourced data with immediate effect. Everything
> beyond basic goals, assists and appearances went with it — xG, xAG, progressive
> passes and carries, shot- and goal-creating actions, defensive actions, possession
> and the advanced goalkeeping tables. No replacement provider has been announced.
>
> Anything written before that date describing FBref as a free xG source is stale.
> For xG, use Understat or StatsBomb open data instead.

---

## [2] Player reports
**Provider:** wyscout | **Category:** glossary-metrics-concepts | **Source:** crawled (https://dataglossary.wyscout.com/) | crawled 2026-06-03

## Player reports

#### Rankings

For every position, there's a set of parameters that are selected for the player rankings section in the player report.

- _Goalkeepers_: Conceded goals, Shots faced, Saves, xG saved, Recoveries, Defensive duels, Aerial duels, Passes, Average pass length
- _Full-backs_: Recoveries, Counterpressing recoveries, Defensive duels, Offensive duels, Dribbles, Passes, Crosses, Average pass length, Progressive runs, Progressive passes, Deep completions, Deep completed crosses, Goals, xG, Assists, xA, Shots, xG per shot, Shot assists
- _Central defenders_: Recoveries, Counterpressing recoveries, Defensive duels, Aerial duels Offensive duels, Dribbles, Passes, Average pass length, Progressive runs, Progressive passes, Deep completions, Deep completed crosses
- _Midfielders_: Goals, xG, Assists, xA, Shots, xG per shot, Passes, Crosses, Shot assists, Offensive duels, Defensive duels, Aerial duels, Dribbles, Progressive runs, Progressive passes, Deep completions, Deep completed crosses, Recoveries, Counterpressing recoveries
- _Forwards_: Goals, xG, Assists, xA, Shots, xG per shot, Passes, Crosses, Shot assists, Second assists, Touches in penalty area, Received passes, Received long passes, Offensive duels, Dribbles, Progressive runs, Progressive passes, Recoveries in final third, Counterpressing recoveries

Source: [https://dataglossary.wyscout.com/player_reports/](https://dataglossary.wyscout.com/player_reports/)

---

## [3] Team stats (per season)
**Provider:** free-sources | **Category:** fbref | **Source:** curated by football-docs contributors

### Team stats (per season)

| Category | Examples |
|----------|---------|
| Standard | Goals, assists, appearances, minutes |
| Shooting | Goals, penalties (basic shooting only since January 2026) |
| Passing | Total/short/medium/long, key passes, final third passes, progressive passes |
| Pass types | Live ball, dead ball, free kicks, through balls, switches, crosses |
| Goal and shot creation | SCA, GCA, types (live, dead, take-on, shot, foul, defensive) |
| Defensive | Tackles, interceptions, blocks, clearances, errors |
| Possession | Touches by zone, take-ons, carries, progressive carries, receiving |
| Goalkeeper | Save %, PSxG, crosses stopped, sweeper actions |

---

## [4] FBref
**Provider:** free-sources | **Category:** overview | **Source:** curated by football-docs contributors

## FBref

**What it provides**: Historical results, basic player and team statistics, and squad
information across 100+ competitions.

**Advanced statistics ended on 20 January 2026**, when Stats Perform terminated
FBref's access to the Opta feeds that supplied them. No replacement has been
announced. Treat any guidance that presents FBref as a free source of xG or
possession-adjusted metrics as out of date.

**Stat categories still available**: goals, assists, appearances, minutes, cards and
match results. The advanced tables (passing detail, pass types, GCA/SCA, defensive
actions, possession, advanced goalkeeping) are no longer served.

**Coverage**: 100+ competitions. Basic stats and results run back to the 1990s for
many leagues. Advanced metrics covered 2017/18 to January 2026 only.

**Access**: Web scraping or `soccerdata` Python library. See `fbref.md` for details.

**Key URL patterns**:
- Team: `https://fbref.com/en/squads/{team_id}/{team_name}-Stats`
- Player: `https://fbref.com/en/players/{player_id}/{player_name}`
- Match: `https://fbref.com/en/matches/{match_id}/{match_name}`
- Season: `https://fbref.com/en/comps/{comp_id}/{season}/stats`
````

### s15 — search_docs {"query": "soccerdata FBref player season stats", "max_results": 4}

````text
Found 4 result(s) for "soccerdata FBref player season stats":

## [1] Access methods
**Provider:** free-sources | **Category:** fbref | **Source:** curated by football-docs contributors

### Access methods

**Python (soccerdata):**

```python
import soccerdata as sd
fbref = sd.FBref('ENG-Premier League', '2024')
team_stats = fbref.read_team_season_stats(stat_type='standard')
player_stats = fbref.read_player_season_stats(stat_type='shooting')
```

**R (worldfootballR):**

```r
library(worldfootballR)
team_stats <- fb_season_team_stats("ENG", "M", 2024, "standard")
player_stats <- fb_big5_advanced_season_stats(season_end_year=2024, stat_type="standard")
```

---

## [2] Fetch data -- returns pandas DataFrames
**Provider:** soccerdata | **Category:** usage | **Source:** curated by football-docs contributors

# Fetch data -- returns pandas DataFrames
schedule = fbref.read_schedule()
team_stats = fbref.read_team_season_stats(stat_type="passing")
player_stats = fbref.read_player_season_stats(stat_type="standard")
```

---

## [3] FBref (sd.FBref)
**Provider:** soccerdata | **Category:** data-sources | **Source:** curated by football-docs contributors

## FBref (sd.FBref)

Source: fbref.com. Note that FBref lost its Opta feed in January 2026 and no longer
serves advanced statistics, which is why several `stat_type` values below were removed
upstream. Selenium-based (requires Chrome/Chromium), 7-second rate limit enforced. Supports "Big 5 European Leagues Combined" as a virtual league for efficient bulk scraping.

**Methods**:

| Method | Returns | Index | Notes |
|---|---|---|---|
| `read_leagues()` | League metadata | -- | |
| `read_seasons()` | Available seasons with URLs | -- | Includes round-robin vs elimination format |
| `read_schedule()` | Match schedule | `[league, season, game]` | Columns: week, date, time, home/away team, home/away xG, score, game_id |
| `read_team_season_stats(stat_type)` | Aggregated team stats | `[league, season, team]` | |
| `read_team_match_stats(stat_type)` | Per-match team logs | `[league, season, team, game]` | Optional `team` filter |
| `read_player_season_stats(stat_type)` | Aggregated player stats | `[league, season, team, player]` | |
| `read_player_match_stats(stat_type)` | Per-match player stats | `[league, season, game, team, player]` | Optional `match_id` filter |
| `read_lineup(match_id=None)` | Lineups | `[league, season, game]` | jersey_number, position, minutes_played, is_starter |
| `read_events(match_id=None)` | In-match events | `[league, season, game]` | Goals, cards, substitutions with timing |

**Team season stat types** (as of soccerdata 1.9.1; `keeper_adv`, `passing`, `passing_types`, `goal_shot_creation`, `defense`, and `possession` were removed after fbref.com restricted access to those pages): `standard`, `keeper`, `shooting`, `playing_time`, `misc`.

**Team match stat types** (as of soccerdata 1.9.1; same removals as above): `schedule`, `shooting`, `keeper`, `misc`.

**Player match stat types** (as of soccerdata 1.9.1; same removals as above): `summary`, `keepers`.

---

## [4] FBref
**Provider:** free-sources | **Category:** overview | **Source:** curated by football-docs contributors

## FBref

**What it provides**: Historical results, basic player and team statistics, and squad
information across 100+ competitions.

**Advanced statistics ended on 20 January 2026**, when Stats Perform terminated
FBref's access to the Opta feeds that supplied them. No replacement has been
announced. Treat any guidance that presents FBref as a free source of xG or
possession-adjusted metrics as out of date.

**Stat categories still available**: goals, assists, appearances, minutes, cards and
match results. The advanced tables (passing detail, pass types, GCA/SCA, defensive
actions, possession, advanced goalkeeping) are no longer served.

**Coverage**: 100+ competitions. Basic stats and results run back to the 1990s for
many leagues. Advanced metrics covered 2017/18 to January 2026 only.

**Access**: Web scraping or `soccerdata` Python library. See `fbref.md` for details.

**Key URL patterns**:
- Team: `https://fbref.com/en/squads/{team_id}/{team_name}-Stats`
- Player: `https://fbref.com/en/players/{player_id}/{player_name}`
- Match: `https://fbref.com/en/matches/{match_id}/{match_name}`
- Season: `https://fbref.com/en/comps/{comp_id}/{season}/stats`
````

### s08 — search_docs {"query": "Reep register download DuckDB", "max_results": 4}

````text
Found 4 result(s) for "Reep register download DuckDB":

## [1] reep - download-duckdb-csv
**Provider:** reep | **Category:** download-duckdb-csv | **Source:** curated by football-docs contributors | crawled 2026-09-29

# Reep download: DuckDB and CSV

The whole register is a free download with no key and no sign-up. It comes as
one DuckDB file, or as one gzipped CSV per table. The CSV release is the source
contract; the DuckDB file is built from it. Written from reep.football on
2026-09-22.

---

## [2] Stable download links
**Provider:** reep | **Category:** download-duckdb-csv | **Source:** curated by football-docs contributors | crawled 2026-09-29

## Stable download links

These links always resolve to the current release:

- DuckDB: https://reep.football/downloads/duckdb (the file is `reep-register-v1.duckdb`)
- One CSV per table: `https://reep.football/downloads/csv/<table>`, for example
  https://reep.football/downloads/csv/bridges

Each release also publishes `checksums.txt` and `schema.json` next to the files;
the manifest at https://data.reep.football/releases/latest.json lists every file
for the current release.

Tables available as CSV: `bridges`, `entities`, `relationships`, `matches`,
`aliases`, `players`, `coaches`, `referees`, `teams`, `competitions`, `seasons`,
`stages`, `observed_clubs`, `redirects`, `coverage`, and the Wikidata overlay
tables `overlay_xids`, `overlay_aliases` and `overlay_links`.

Source: [downloads](https://reep.football/data/). The old page address,
https://reep.football/downloads, redirects there; the `/downloads/duckdb` and
`/downloads/csv/<table>` links above still work.

---

## [3] Using Reep through football-docs
**Provider:** reep | **Category:** overview | **Source:** curated by football-docs contributors | crawled 2026-09-29

## Using Reep through football-docs

The `resolve_entity` tool maps an entity to its IDs at every provider. It looks
up a provider ID with its namespace, a Reep ID, or a name, and uses the first
source that is set up in the MCP server's environment:

1. `REEP_DUCKDB_PATH`: the path to a downloaded copy of the register. No key is
   needed, and lookups run locally. Each answer ends with the file's release stamp
   checked against the latest release, and says how to download the new file
   when it is out of date.
2. `REEP_API_KEY`: a Reep API key, issued by hand on request (email
   getintouch+nutmeg@withqwerty.com). There is no self-service sign-up.

With neither set, the tool explains both options and returns the DuckDB query
that answers the question from the download. Example MCP configuration:

```json
{
  "mcpServers": {
    "football-docs": {
      "command": "npx",
      "args": ["-y", "football-docs"],
      "env": { "REEP_DUCKDB_PATH": "/path/to/reep-register-v1.duckdb" }
    }
  }
}
```

---

## [4] Keeping a local copy current
**Provider:** reep | **Category:** download-duckdb-csv | **Source:** curated by football-docs contributors | crawled 2026-09-29

## Keeping a local copy current

A new release is cut every week, and each file carries its stamp in the
`release_metadata` table:

```sql
SELECT value FROM release_metadata WHERE key = 'source_stamp';
```

Compare it with the `stamp` field of
https://data.reep.football/releases/latest.json, which needs no key. When they
differ, download the file again from https://reep.football/downloads/duckdb over
the old copy, then resolve stored Reep IDs through the `redirects` table. Check
before any bulk matching job.
````

### s09 — search_docs {"query": "identity surfaces player ID", "provider": "transfermarkt", "max_results": 4}

````text
Found 3 result(s) for "identity surfaces player ID" in transfermarkt:

## [1] Entity ID fields
**Provider:** transfermarkt | **Category:** identity-surfaces | **Source:** curated by football-docs contributors

## Entity ID fields

| Entity | Common surface |
|---|---|
| Competition | `wettbewerb` code |
| Season | competition code plus season year |
| Match | match or game ID |
| Team | `verein` ID |
| Player | `spieler` ID |
| Coach | staff or manager profile ID |

The numeric IDs embedded in public URLs are the identity keys. URL slugs are
handles and can change without changing the underlying ID. Common URL
families include `spieler` for players, `verein` for teams, `wettbewerb` for
competitions, and match or game IDs for fixtures.

---

## [2] transfermarkt - identity-surfaces
**Provider:** transfermarkt | **Category:** identity-surfaces | **Source:** curated by football-docs contributors

# Transfermarkt Identity Surfaces

Transfermarkt is primarily a public website, not an official public API.
Identity data comes from public entity pages, match reports, or licence-safe
community exports.

---

## [3] Other fields
**Provider:** transfermarkt | **Category:** identity-surfaces | **Source:** curated by football-docs contributors

## Other fields

- Player: name variants, date of birth, birth place, citizenship, height,
  position, foot, profile aliases, current club, historical clubs, and
  national-team profile surfaces where available.
- Team: official name, historical names, country, city, gender where
  inferable, competition participation, and successor or predecessor context.
- Match: date, home and away teams, score, attendance, competition, season,
  and round label.
- Season: competition code, season year, display label, and match membership.
````

### s13 — search_docs {"query": "identity surfaces player ID", "provider": "fbref", "max_results": 4}

````text
Found 4 result(s) for "identity surfaces player ID" in fbref (free-sources):

## [1] Project use
**Provider:** free-sources | **Category:** understat | **Source:** curated by football-docs contributors

## Project use

Understat is useful as an xG enrichment source for match-result, season-story,
and game-state surfaces when the primary fixture provider does not include
shot-level or match-level xG. Cache by competition, season, team names, and match
date rather than by Understat match ID alone, because Understat IDs are not
portable across providers.

When joining to Opta, SportMonks, football-data.co.uk, or another fixture source:

- match by date plus home/away team aliases;
- keep the provider's final score as the fixture authority;
- store Understat `xG` and `xGA` as an enrichment layer;
- expose the xG model name so it is not confused with StatsBomb, Opta, or
  provider-supplied expected-goals values.

---

## [2] Base fixture authority
**Provider:** free-sources | **Category:** contextual-story-joins | **Source:** curated by football-docs contributors

## Base fixture authority

Choose one provider as the authority for fixture identity, final scores, and match
status before joining context.

| Need | Good base source |
|---|---|
| in-season fixture ids and live status | SportMonks, Opta, TheSportsDB, Sportradar |
| historical result grids | football-data.co.uk, engsoccerdata |
| shot-level xG enrichment | Understat, StatsBomb Open Data where covered |
| broad season stats | FBref / soccerdata |

Do not let an enrichment source silently override the base fixture score or status.
If an enrichment feed lags behind the fixture authority, preserve the base fixture
and mark the enrichment fields unavailable.

---

## [3] StatsBomb Open Data
**Provider:** free-sources | **Category:** overview | **Source:** curated by football-docs contributors

## StatsBomb Open Data

**What it provides**: Full event-level data identical to their commercial product -- every pass, shot, duel, carry, pressure event with coordinates, xG, and freeze frames for shots.

**Coverage** (as of 2025):
- FIFA World Cups (2018, 2022)
- FIFA Women's World Cup (2019, 2023)
- UEFA Euro (2020, 2024)
- La Liga (2004/05-2020/21 -- Messi-era seasons)
- Premier League (select seasons)
- NWSL (multiple seasons)
- FA Women's Super League (multiple seasons)
- Champions League (select seasons)
- Various international tournaments

**Access**:
```bash
git clone https://github.com/hudl/open-data.git
```

Or via kloppy:
```python
from kloppy import statsbomb
dataset = statsbomb.load_open_data(match_id=3788741)
```

**Data format**: JSON files organised by competition and season. See `docs/providers/statsbomb/` for full event type documentation.

**License**: Free for non-commercial use with attribution. Must credit StatsBomb.

---

## [4] API Response Keys
**Provider:** free-sources | **Category:** understat | **Source:** curated by football-docs contributors

### API Response Keys

| API path | Response keys |
|---|---|
| `getLeagueData/{league}/{season}` | `teams` (dict keyed by team ID, each with `id`, `title` and `history`), `players` (list), `dates` (list) |
| `getTeamData/{team}/{season}` | `dates`, `players`, `statistics` (`situation`, `formation`, `gameState`, `timing`, `shotZone`, `attackSpeed`, `result`) |
| `getMatchData/{match_id}` | `shots` (`h` and `a`), `rosters` (`h` and `a`), `tmpl` |
| `getPlayerData/{player_id}` | `player`, `matches`, `groups`, `positionsList`, `minMaxPlayerStats`, `shots`, `lastMatch` |
````

### s10 — search_docs {"query": "Sofascore 403 challenge scraper", "max_results": 4}

````text
Found 4 result(s) for "Sofascore 403 challenge scraper":

## [1] Supported Sources
**Provider:** soccerdata | **Category:** overview | **Source:** curated by football-docs contributors

## Supported Sources

| Scraper Class | Source | Access Method | Rate Limit | Coverage |
|---|---|---|---|---|
| `sd.FBref` | fbref.com (Opta/StatsBomb data) | Selenium (Chrome) | 7s between requests | Top leagues + many more, 2017/18+ for detailed stats |
| `sd.Understat` | understat.com | HTTP (JSON API) | None explicit | Big 5 European leagues only |
| `sd.WhoScored` | whoscored.com (Opta data) | Selenium (Chrome) | 5s + 0-5s random | Top leagues, detailed event data |
| `sd.Sofascore` | sofascore.com | HTTP (JSON API) | None explicit | Wide coverage |
| `sd.ESPN` | ESPN public API | HTTP (JSON API) | None explicit | Top leagues |
| `sd.ClubElo` | clubelo.com | HTTP (CSV API) | None explicit | All European clubs, 1939-present |
| `sd.SoFIFA` | sofifa.com (FIFA game ratings) | Selenium (Chrome) | 1s between requests | All FIFA-rated leagues |
| `sd.MatchHistory` | football-data.co.uk | HTTP (CSV download) | None | 25+ leagues, results + betting odds |

---

## [2] Sofascore (sd.Sofascore)
**Provider:** soccerdata | **Category:** data-sources | **Source:** curated by football-docs contributors

## Sofascore (sd.Sofascore)

Source: sofascore.com API. HTTP-based JSON API.

**Methods**:

| Method | Returns | Index | Notes |
|---|---|---|---|
| `read_leagues()` | League metadata with league_id | -- | |
| `read_seasons()` | Season metadata with season_id | -- | |
| `read_league_table()` | Standings | `[league, season]` | MP, W, D, L, GF, GA, GD, Pts |
| `read_schedule()` | Match schedule | `[league, season, game]` | round, week, date, scores, game_id |

---

## [3] Challenge intensity
**Provider:** wyscout | **Category:** glossary-metrics-concepts | **Source:** crawled (https://dataglossary.wyscout.com/) | crawled 2026-06-03

## Challenge intensity

A team metric, quantifying how many defensive actions (defensive duels, loose ball duels, interceptions, tackles) a team is doing per minute of opponent ball possession.

Challenge intensity reflects how often the team is actively trying to recover the ball when the opponent is in possession (thus, it's correlated to _PPDA_). The higher this number, the more intense the team is in challenges. In top five European leagues for 2018/2019 the average challenge intensity is 6.04. The best team in Challenge intensity in top five leagues 2018/2019 is Eibar with 7.7; Parma, Nürnberg and Angers have the least (5).

Source: [https://dataglossary.wyscout.com/challenge_intensity/](https://dataglossary.wyscout.com/challenge_intensity/)

---

## [4] Result: 403 Forbidden
**Provider:** sportmonks | **Category:** error-codes | **Source:** llms_txt (https://docs.sportmonks.com/football/llms-full.txt) | v3 | crawled 2026-08-31T00:17:40.848Z

# Result: 403 Forbidden
```

**3. Accessing premium endpoints**

```bash
````

### s11 — search_docs {"query": "post-shot xG goalkeeper goals prevented", "max_results": 4}

````text
Found 4 result(s) for "post-shot xG goalkeeper goals prevented":

## [1] Goalkeeping
**Provider:** statsbomb | **Category:** player-season-stats | **Source:** curated by football-docs contributors

## Goalkeeping

| Column | Type | Description |
|---|---|---|
| `player_season_goals_faced_90` | double | Goals conceded by the keeper |
| `player_season_gsaa_90` | double | Goals saved/conceded vs expectation (season prevention) |
| `player_season_gsaa_ratio` | percentage | Goals saved above average as % of shots faced |
| `player_season_save_ratio` | percentage | % of on-target shots saved |
| `player_season_shots_faced_90` | double | All shots faced (incl. off-target) |
| `player_season_ot_shots_faced_90` | double | On-target shots faced |
| `player_season_ot_shots_faced_ratio` | percentage | % of shots faced that were on target |
| `player_season_np_psxg_faced_90` | double | Post-shot xG faced |
| `player_season_np_xg_faced_90` | double | Total npxG from all non-penalty shots faced (incl. off target) |
| `player_season_npot_psxg_faced_90` | double | Non-penalty on-target PSxG faced |
| `player_season_xs_ratio` | percentage | Expected save % given PSxG of shots faced |
| `player_season_clcaa` | percentage | Claimable Collection Attempts over Average |
| `player_season_da_aggressive_distance` | double | Avg distance from goal of keeper defensive actions |
| `player_season_np_optimal_gk_dlength` | double | Avg distance from the modelled optimal shot-facing position |
| `player_season_penalties_faced_90` | double | Penalties faced |
| `player_season_penalties_conceded_90` | double | Penalties faced that resulted in goals |

---

## [2] Post-Shot xG (PSxG) and goalkeeping value
**Provider:** statsbomb | **Category:** iq-metrics-glossary | **Source:** curated by football-docs contributors

## Post-Shot xG (PSxG) and goalkeeping value

PSxG models goal probability **after** the shot is struck, using placement and
velocity — only defined for on-target, unblocked shots. Used to value
goalkeeping.

- `np_psxg` — non-penalty PSxG earned from a player's on-target shots.
- `npot_psxg_faced` / `np_psxg_faced_90` — non-penalty on-target PSxG faced by a
  goalkeeper.
- `gsaa` (Goals Saved Above Average) — goals the keeper saved/conceded versus
  expectation (PSxG faced minus goals conceded). `gsaa_ratio` expresses it as a
  share of shots faced. `xs_ratio` (season) — expected save % given PSxG faced.
- `save_ratio` — % of on-target shots saved.
- `gk_positioning_error` / `np_optimal_gk_dlength` — average distance of the
  keeper from the modelled optimal position for facing a shot.
- `da_aggressive_distance` — average distance from goal at which the keeper
  performs defensive actions (sweeping tendency).
- `ccaa` / `clcaa` — Claimable Collection Attempts over Average: how often the
  keeper attempts to claim a claimable pass vs the average keeper.
- `claim_success` — % of claim attempts that succeed.
- `goals_conceded` (player-match) — goals conceded by the keeper, excluding
  penalties and own goals.

The Events v8 shot object decomposes shot xG into: `statsbomb_xg` (chance
quality — pre-strike situation including GK/defender positions),
`shot_execution_xg` (incorporates placement & velocity),
`shot_execution_xg_uplift` (`shot_execution_xg − statsbomb_xg`; can be
negative), `gk_save_difficulty_xg` (renamed from `statsbomb_xg2`; difficulty for
the keeper given placement/velocity/position), `gk_positioning_xg_suppression`
and `gk_shot_stopping_xg_suppression` (threat suppressed by keeper positioning /
shot-stopping). See `xg-model.md`.

---

## [3] Post-Shot xG (PSxG / xGOT)
**Provider:** statsbomb | **Category:** xg-model | **Source:** curated by football-docs contributors

## Post-Shot xG (PSxG / xGOT)

Post-shot xG models goal probability *after* the shot is struck, using
placement and velocity; it is only defined for on-target, unblocked shots and is
the basis for valuing goalkeeping. In the event feed this corresponds to the
`gk_save_difficulty_xg` / execution fields above; in the stats endpoints it
surfaces as `np_psxg` (earned), `np_psxg_faced` / `npot_psxg_faced` (faced by a
keeper), and is turned into Goals Saved Above Average (`gsaa`, `gsaa_ratio`,
`xs_ratio`). PSxG is a commercial-API concept — it is not a standard field in
the open-data event JSON, where only `statsbomb_xg` (and, on v8+ feeds, the
decomposition) appears.

---

## [4] xG
**Provider:** wyscout | **Category:** glossary-metrics-concepts | **Source:** crawled (https://dataglossary.wyscout.com/) | crawled 2026-06-03

## xG

Expected goals (xG) is a predictive ML model used to assess the likelihood of scoring for every shot made in the game.

For every shot, the xG model calculates the probability to score based on event parameters:

- Location of the shot
- Location of the assist
- Foot or head
- Assist type
- Was there a dribble of a field player or a goalkeeper immediately before the shot?
- Is it coming from a set piece?
- Was the shot a counterattack or did it happen in a transition?
- Tagger's assessment of the danger of the shot

These parameters (plus a few technical ones) are used to train the xG model on the historical Wyscout data and predict the probability of the shot being scored.

The probabilities range between 0 and 1. A shot of 0.1 xG means a shot like this should be scored 10% of the time. A shot of 0.8 xG means a shot like this should be scored 80% of the time. A penalty xG value is fixed to 0.76.

![Shot](https://dataglossary.wyscout.com/static/17fa59939729ae8b02a301e25135e3c8/b0254/635719742.png)

_M. de Roon with 0.006 xG shot_

![Shot](https://dataglossary.wyscout.com/static/a860641cdd71245877f42ce281a28d99/ba0a7/678490445.png)

_S. Mané with 0.85 xG shot_

At the moment there are no additional constraints for xG of shots in the same possession. So a sequence of shots in short succession (like a rebound after a save) could theoretically yield an xG value of > 1. Currently they are considered to be different shots and all xG values are calculated at the shot level.

#### Pre-shot and post-shot xG

The pre-shot xG model (or ‘xG' for short) is trained on all shots (including blocked shots and shots wide), only using the information at the moment the shot is token. However, Wyscout also calculates post-shot xG (’PSxG' for short or 'xCG' in goalkeeper context for 'Expected conceded goals'). Here only shots on target are used in training (all blocked shots and shots wide automatically have a post-shot xG value of 0), and parameters like the coordinates of the goal where the shot is estimated to go in are included. The post-shot xG for a given shot is usually higher than the pre-shot and can reflect finishing skills. Post-shot xG is especially valuable for evaluating goalkeeper impact on conceded goals.

Source: [https://dataglossary.wyscout.com/xg/](https://dataglossary.wyscout.com/xg/)
````

### s12 — search_docs {"query": "possession adjusted defensive actions", "max_results": 4}

````text
Found 4 result(s) for "possession adjusted defensive actions":

## [1] Possession-adjusted
**Provider:** wyscout | **Category:** glossary-metrics-concepts | **Source:** crawled (https://dataglossary.wyscout.com/) | crawled 2026-06-03

## Possession-adjusted

Possession-adjusted (styled as _PAdj_ or _Opp30_) is a method to calculate _defensive_ statistics to take possession values into account.

While the average duration of the match is slighly on rise every year and is at 95 minutes 30 seconds for 2019, the pure time of ball in play is in decrease and is generally between 50 and 60 minutes depending on the league. Wyscout took 60 minutes as a reasonable value to adjust possession-dependent stats to.

The logic for adjusting defensive statistics is the following: you can only make defensive contribution when you're not in the possession of the ball. Therefore, when you look for high defensive values, normally you would only encounter the defenders of the lower teams in the league: their defenders, being dominated by a possession-leading team, are forced to make more actions (defensive duels, interception, sliding tackles etc.). The defenders of possession-based teams are naturally making less actions. Adjusting these values to the possession (_as if_ the match was played with a 50%/50% possession) gives further insight to the frequency of defensive actions.

_Example:_

In the match of AFC Bournemouth - Manchester City (0:1, 2 March 2019) Man City had had 80% of possession (42:37 pure possession time), while Bournemouth only had 20% (10:35 pure possession time).

Aké, who played the whole match for Bournemouth, had 10 interceptions. His PAdj interceptions value would be: 10 / 42.5 * 30 = 7.06.

Walker, who played the whole match for Man City, had 5 interceptions. His PAdj interceptions value would be: 5 / 10.5 * 30 = 14.3.

Therefore, while Walker made only half of interceptions of Aké, the huge difference in possession make his possession-adjusted value twice higher.

Source: [https://dataglossary.wyscout.com/p_adj/](https://dataglossary.wyscout.com/p_adj/)

---

## [2] Defending
**Provider:** statsbomb | **Category:** player-season-stats | **Source:** curated by football-docs contributors

## Defending

| Column | Type | Description |
|---|---|---|
| `player_season_tackles_90` | double | Successful challenges |
| `player_season_challenge_ratio` | percentage | % of duels where a tackle is made vs being dribbled past |
| `player_season_interceptions_90` | double | Interceptions |
| `player_season_tackles_and_interceptions_90` | double | Tackles + interceptions |
| `player_season_ball_recoveries_90` | double | Ball recoveries |
| `player_season_fhalf_ball_recoveries_90` | double | Ball recoveries in opposition half |
| `player_season_clearance_90` | double | Clearances |
| `player_season_aerial_wins_90` | double | Aerial duels won |
| `player_season_aerial_ratio` | percentage | % of aerial duels won |
| `player_season_blocks_per_shot` | double | Blocks per shot faced |
| `player_season_aggressive_actions_90` | double | Tackles/pressures/fouls within 2 s of opposition ball receipt |
| `player_season_defensive_action_90` | float | Tackles, pressure events and fouls per 90 |
| `player_season_defensive_action_regains_90` | double | Team won ball back within 5 s of the player's defensive action |
| `player_season_errors_90` | double | On-ball mistakes leading to a shot |
| `player_season_fouls_90` | double | Fouls committed |
| `player_season_fouls_won_90` | double | Times fouled |
| `player_season_penalty_wins_90` | double | Penalties won |
| `player_season_padj_clearances_90` | double | Possession-adjusted clearances |
| `player_season_padj_interceptions_90` | double | Possession-adjusted interceptions |
| `player_season_padj_pressures_90` | double | Possession-adjusted pressures |
| `player_season_padj_tackles_90` | double | Possession-adjusted tackles |
| `player_season_padj_tackles_and_interceptions_90` | double | Possession-adjusted tackles + interceptions |
| `player_season_average_x_defensive_action` | double | Avg distance from goal line of successful defensive actions (x-axis 0–100) |
| `player_season_average_x_pass` | double | Avg distance from goal line of successful passes (0–100) |
| `player_season_average_x_pressure` | double | Avg distance from goal line of pressures (0–100) |

---

## [3] wyscout - glossary-metrics-concepts
**Provider:** wyscout | **Category:** glossary-metrics-concepts | **Source:** crawled (https://dataglossary.wyscout.com/) | crawled 2026-06-03

# Wyscout Glossary — Metrics & Concepts

Wyscout's analytical **concepts** (xG, xA, ball possession, pitch coordinates, possession-adjusted, minutes played, attack, player reports) and **metrics** (PPDA, ball progression, challenge intensity, physical metrics, player metrics, match-level metrics, Wyscout Index, defensive actions, long-pass share, loss index), from the official Data Glossary with figures permalinked. These apply across the Wyscout Platform, reports and the API (v3 and v4).

---

## [4] Story metric fields and tags
**Provider:** wyscout | **Category:** charting-analysis-metrics | **Source:** curated by football-docs contributors

## Story metric fields and tags

For entertainment-index, player-profile, or tactical story charts, these
Wyscout concepts commonly appear together:

| Story concept | Advanced/glossary metric | Event tag or field to check |
|---|---|---|
| High press intensity | `PPDA` | Opponent passes in the final/lower 60 percent of the pitch divided by defensive actions: fouls, interceptions, won defensive duels, and sliding tackles. Lower is more intense. |
| Possession-adjusted defending | `PAdj` / `Opp30` | Use for defensive metrics only; it normalises defensive actions as if possession were balanced. |
| Progressive passing | Progressive passes | `progressive_pass` secondary tag. |
| Progressive carrying | Progressive runs | `progressive_run` secondary tag, or carry `progression` where consuming event payloads. |
| Deep completions | Deep completions | API tag is `deep_completition` for the pass completion; preserve the misspelt contract spelling. |
| Deep completed crosses | Deep completed crosses | `deep_completed_cross` secondary tag. |
| Chance creation | xA / shot assists | `shot_assist` is the pass leading to a shot; Wyscout xA is the xG value of that shot. |
| Counterpressing | Counterpressing recoveries | `counterpressing_recovery` secondary tag. |

Do not mix glossary display labels with API tag names without a mapping layer.
The glossary says "Deep completions"; the event API tag is
`deep_completition`.
````

### s16 — search_docs {"query": "tackles won lost challenges", "max_results": 4}

````text
Found 4 result(s) for "tackles won lost challenges":

## [1] Event Type Reference
**Provider:** opta | **Category:** event-types | **Source:** curated by football-docs contributors

## Event Type Reference

| typeId | Name | Per match avg | Outcome | Notes |
|--------|------|---------------|---------|-------|
| 1 | Pass | ~925 | 0=miss, 1=success | Includes open play, goal kicks, corners, free kicks played as passes |
| 2 | Offside pass | ~3 | always 1 | Receiving player called offside |
| 3 | Take on | ~35 | 0=fail, 1=success | Dribble past opponent |
| 4 | Foul | ~44 | 0=committed, 1=fouled | Events come in pairs (one per team) |
| 5 | Out | ~106 | 0=put out, 1=gains possession | Ball out of play |
| 6 | Corner awarded | ~18 | 0=conceded, 1=won | |
| 7 | Tackle | ~32 | 0=fail, 1=wins ball | Legal ground-level challenge |
| 8 | Interception | ~13 | always 1 | Intercepts opposition pass |
| 10 | Save | ~11 | always 1 | GK prevents goal (also outfield with qual 94) |
| 11 | Claim | ~2 | 0=drops, 1=catches | GK catches crossed ball |
| 12 | Clearance | ~53 | always 1 | Defensive clearance |
| 13 | Miss | ~9 | always 1 | Shot wide or over |
| 14 | Post | <1 | always 1 | Ball hits frame |
| 15 | Attempt saved | ~11 | always 1 | Shot on target, saved |
| 16 | Goal | ~2.5 | always 1 | Own goals have qualifier 28 |
| 17 | Card | ~4 | always 1 | Yellow/second yellow/red via qualifiers |
| 18 | Player off | ~9 | always 1 | Substituted off |
| 19 | Player on | ~1 | always 1 | Substituted on |
| 20 | Player retired | — | — | Player leaves the pitch |
| 21 | Player returns | — | — | Player comes back on after leaving the pitch |
| 27 | Start delay | ~3 | always 1 | Play stops for a delay. With qualifier 364, a VAR review |
| 28 | End delay | ~3 | always 1 | The delay ends and play restarts |
| 30 | End | ~6 | always 1 | End of a period. kloppy reads the period end time from it |
| 32 | Start | — | — | Start of a period. kloppy reads the period start time from it |
| 34 | Team set up | ~2 | always 1 | Formation/lineup event |
| 37 | Collection end | — | — | |
| 40 | Formation change | — | — | In-game formation change |
| 41 | Punch | — | — | GK punches the ball |
| 42 | Good skill | — | — | |
| 43 | Deleted event | — | — | Opta removed this event. Drop it before analysis; kloppy does |
| 44 | Aerial | ~60 | 0=lost, 1=won | Aerial duel |
| 45 | Challenge | ~15 | always 0 | Unsuccessful tackle attempt |
| 49 | Ball recovery | ~80 | always 1 | Player gathers loose ball |
| 50 | Dispossessed | ~10 | always 1 | Loses ball via opponent tackle |
| 51 | Error | ~1 | always 1 | Mistake losing ball |
| 52 | Keeper pick-up | ~5 | always 1 | GK picks up ball |
| 54 | Smother | <1 | always 1 | GK covers ball at attacker's feet |
| 55 | Offside provoked | ~3 | always 1 | Defender's position causes offside |
| 59 | Keeper sweeper | ~5 | always 1 | GK comes off line to clear/claim |
| 61 | Ball touch | ~3 | always 1 | Bad touch / loss of control |
| 67 | 50/50 | ~2 | 0=lost, 1=won | Two players contest loose ball |
| 74 | Blocked pass | ~10 | always 1 | Player blocks an opponent's pass |
| 83 | Attempted tackle | ~15 | always 0 | Unsuccessful tackle |

A dash means the per-match average or outcome has not been checked for that type.

---

## [2] Defending
**Provider:** statsbomb | **Category:** player-match-stats | **Source:** curated by football-docs contributors

## Defending

| Column | Type | Description |
|---|---|---|
| `player_match_tackles` | double | Successful challenges made |
| `player_match_challenge_ratio` | percentage | % of duels where the player makes a tackle vs getting dribbled past |
| `player_match_interceptions` | double | Interceptions |
| `player_match_ball_recoveries` | integer | Ball recoveries |
| `player_match_fhalf_ball_recoveries` | integer | Ball recoveries in the opposition (final) half |
| `player_match_clearances` | double | Clearances |
| `player_match_aerials` | double | Aerial duels |
| `player_match_successful_aerials` | double | Successful aerials |
| `player_match_aerial_ratio` | percentage | % of aerial duels entered that are won |
| `player_match_blocks_per_shot` | double | Blocks made per shot faced |
| `player_match_aggressive_actions` | double | Tackles, pressures and fouls within 2 s of an opposition ball receipt |
| `player_match_defensive_actions` | integer | Tackles, pressure events and fouls recorded |
| `player_match_fouls` | double | Fouls committed |
| `player_match_fouls_won` | double | Times the player is fouled |
| `player_match_penalties_won` | double | Penalties won |

---

## [3] Defending
**Provider:** statsbomb | **Category:** player-season-stats | **Source:** curated by football-docs contributors

## Defending

| Column | Type | Description |
|---|---|---|
| `player_season_tackles_90` | double | Successful challenges |
| `player_season_challenge_ratio` | percentage | % of duels where a tackle is made vs being dribbled past |
| `player_season_interceptions_90` | double | Interceptions |
| `player_season_tackles_and_interceptions_90` | double | Tackles + interceptions |
| `player_season_ball_recoveries_90` | double | Ball recoveries |
| `player_season_fhalf_ball_recoveries_90` | double | Ball recoveries in opposition half |
| `player_season_clearance_90` | double | Clearances |
| `player_season_aerial_wins_90` | double | Aerial duels won |
| `player_season_aerial_ratio` | percentage | % of aerial duels won |
| `player_season_blocks_per_shot` | double | Blocks per shot faced |
| `player_season_aggressive_actions_90` | double | Tackles/pressures/fouls within 2 s of opposition ball receipt |
| `player_season_defensive_action_90` | float | Tackles, pressure events and fouls per 90 |
| `player_season_defensive_action_regains_90` | double | Team won ball back within 5 s of the player's defensive action |
| `player_season_errors_90` | double | On-ball mistakes leading to a shot |
| `player_season_fouls_90` | double | Fouls committed |
| `player_season_fouls_won_90` | double | Times fouled |
| `player_season_penalty_wins_90` | double | Penalties won |
| `player_season_padj_clearances_90` | double | Possession-adjusted clearances |
| `player_season_padj_interceptions_90` | double | Possession-adjusted interceptions |
| `player_season_padj_pressures_90` | double | Possession-adjusted pressures |
| `player_season_padj_tackles_90` | double | Possession-adjusted tackles |
| `player_season_padj_tackles_and_interceptions_90` | double | Possession-adjusted tackles + interceptions |
| `player_season_average_x_defensive_action` | double | Avg distance from goal line of successful defensive actions (x-axis 0–100) |
| `player_season_average_x_pass` | double | Avg distance from goal line of successful passes (0–100) |
| `player_season_average_x_pressure` | double | Avg distance from goal line of pressures (0–100) |

---

## [4] Wyscout Index
**Provider:** wyscout | **Category:** glossary-metrics-concepts | **Source:** crawled (https://dataglossary.wyscout.com/) | crawled 2026-06-03

## Wyscout Index

An index (available in the Rankings app) that sorts players in a competition for each position based on their stats.

![Wyscout Index Bundesliga](https://dataglossary.wyscout.com/static/5fddd112a03c2162f1435e12649e8d3d/a3357/wyscout-index.png)

_Top 11 team according to wyscout index in Bundesliga 2019/2020_

For every position, there's a set of parameters that are taken in consideration in the final ranking. Here's a sample (not exhaustive) list of top relevant stats per position.

- _Goalkeeper_: Conceded goals, Goal mistakes, Saves, Shots faced, Penalty saves, Exits from the line, Pass accuracy.
- _Full-back_: Accelerations, Crosses, Defensive duels won, Sliding tackles, Key passes, Clearances, Pressing attempts, Interceptions, Loose ball duels won, Dribbles won
- _Centre-back_: Team conceded goals, Defensive duels won, Loose ball duels won, Interceptions, Clearances, Aerial duels won, Sliding tackles, Lost balls, Blocked shots, Yellow/red cards, Pass accuracy.
- _Defensive midfielder_: Goals, Chances created, Dribbles won, Shots on target, Loose ball duels won, Assists, Passes, Through passes, Sliding tackles, Interceptions
- _Central midfielder_: Goals, Chances created, Through passes, Loose ball duels won, Shots on target, Pressing attempts, Assists, Aerial duels won, Interceptions, Defensive duels won
- _Attacking midfielder_: Goals, Chances created, Dribbles won, Through passes, Shots on target, Assists, Crosses, Accelerations, Loose ball duels won, Pressing attempts
- _Winger:_ Goals, Shots on target, Assists, Through passes, Crosses, Chances created, Acceleration, Driibles won, Loose ball duels won, Aerial duels won
- _Forward_: Goals, Chances created, Through passes, Assists, Shots, Dribbles won, Shots on target, Duels won, Crosses, Link-up plays

Every stat is assigned a weight, either positive on negative. Based on this, the algorithm calculates the distribution inside a season and assigns values linearly according to minimum and maximum values in the league. For example, the goalkeeper with most goals conceded would receive -4.6 points, and the one with least goals conceded would have a zero: the value for goalkeepers in the middle would be distributed linearly.

The index is calculated a sum of statistical params multiplied by weights as described above.

The index is updated after every match played.

Source: [https://dataglossary.wyscout.com/wyscout_index/](https://dataglossary.wyscout.com/wyscout_index/)
````

### s17 — search_docs {"query": "distance covered high speed running physical metrics", "max_results": 4}

````text
Found 4 result(s) for "distance covered high speed running physical metrics":

## [1] Physical metrics
**Provider:** wyscout | **Category:** glossary-metrics-concepts | **Source:** crawled (https://dataglossary.wyscout.com/) | crawled 2026-06-03

## Physical metrics

These metrics are only available for specific competitions and players with at least 60 minutes of active play across all matches.

| Metric | Definition | Products |
|---|---|---|
| Count HI per 90 | The number of High Intensity actions: sum of Count HSR (High Speed Runs) and Count Sprint, normalized per 90 minutes. | Advanced Search |
| Count High Acceleration per 90 | The number of Accelerations detected with a peak value greater than 3 m/s², normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| Count High Deceleration per 90 | The number of Decelerations detected with a peak value less than -3 m/s², normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| Count HSR per 90 | The number of High Speed Runs detected between 20 km/h and 25 km/h, normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| Count Medium Acceleration per 90 | The number of Accelerations detected with a peak value between 1.5 m/s² and 3 m/s², normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| Count Medium Deceleration per 90 | The number of Decelerations detected with a peak value between -1.5 m/s² and -3 m/s², normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| Count Sprint per 90 | The number of Sprints exceeding 25 km/h, normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| HI Distance per 90 | High Intensity. Distance covered above 20 km/h, normalized per 90 minutes. | Advanced Search |
| HSR Distance per 90 | High Speed Runs. Distance covered between 20 km/h and 25 km/h, normalized per 90 minutes. | Advanced Search |
| Meter/min | Total distance covered across all actions, divided per number of minutes. | Advanced Search |
| Max Speed (km/h) | The maximum speed recorded. | Advanced Search |
| Running Distance per 90 | Distance covered between 15 km/h and 20 km/h, normalized per 90 minutes. | Advanced Search |
| Sprinting Distance per 90 | Distance covered above 25 km/h, normalized per 90 minutes. | Advanced Search |
| Total Distance per 90 | Total distance covered, normalized per 90 minutes. | Advanced Search |

Source: [https://dataglossary.wyscout.com/physical_metrics/](https://dataglossary.wyscout.com/physical_metrics/)

---

## [2] Base metrics
**Provider:** skillcorner | **Category:** physical-data | **Source:** crawled (https://www.skillcorner.com/apidocs.json) | SkillCorner API (OpenAPI 3.1) | crawled 2026-08-31

## Base metrics

| Metric stem | Meaning |
|---|---|
| `total_distance` | Total distance covered (m) |
| `total_metersperminute` | Distance per minute (m/min) |
| `running_distance` | Distance in the running speed band |
| `hsr_distance` / `hsr_count` | High Speed Running distance / number of efforts |
| `sprint_distance` / `sprint_count` | Sprinting distance / number of sprints |
| `hi_distance` / `hi_count` | High Intensity distance / efforts (HSR + sprint band) |
| `medaccel_count` / `highaccel_count` | Medium / high acceleration counts |
| `meddecel_count` / `highdecel_count` | Medium / high deceleration counts |
| `explacceltohsr_count` | Explosive accelerations leading into HSR |
| `explacceltosprint_count` | Explosive accelerations leading into a sprint |
| `timetohsr` / `timetohsr_top3` | Time to reach HSR (and top-3 average) |
| `timetosprint` / `timetosprint_top3` | Time to reach sprint speed (and top-3 average) |
| `psv99` / `psv99_top5` | Peak Sprint Velocity (99th percentile) and top-5 average — a max-speed proxy robust to outliers |

(Speed-band thresholds — what counts as running / HSR / sprint — are defined in the SkillCorner glossary: <https://skillcorner.crunch.help/en>.)

---

## [3] Tracking-derived physical output recipe
**Provider:** kloppy | **Category:** tracking-rendering | **Source:** curated by football-docs contributors

## Tracking-derived physical output recipe

Use this recipe when an agent asks for a physical report, raw-tracking workload
table, speed-band totals, top-speed list, sprint count, or high-speed-running
summary from kloppy `TrackingDataset` frames rather than from a provider's
official physical endpoint.

| Output field | Source fields | Rule |
|---|---|---|
| `player_id` / `team_id` | tracking player object, lineup join | Emit stable provider ids only after the tracking roster has been joined to match players. |
| `minutes_observed` | player coordinates, frame rate | Count frames where the player has a usable position; report the denominator before ranking rates. |
| `total_distance_m` | provider cumulative distance or player coordinates | Prefer documented provider cumulative distance; otherwise derive frame-to-frame distance in metres with a consistent missing-position rule. |
| speed-band distances | provider speed or derived speed, live flag | Bucket live-frame distance into declared walking, jogging, HSR, and sprint bands. Keep thresholds in the response metadata. |
| `sprint_count` | speed series, frame rate, live flag | Count sustained contiguous live-frame runs above the sprint threshold, with an explicit minimum duration and optional short-gap merge rule. |
| `top_speed_mps` | provider speed or derived speed | Use the maximum non-glitch speed from live frames; return `null` when no usable speed sample exists. |
| quality flags | missing speed, missing distance, live/dead state, coordinate unit | State whether values are provider supplied, derived, partially unavailable, or computed without a live-ball flag. |

Core fallback: derive speed from adjacent coordinates when no trusted provider
speed is available.

Safety rule: this is not the same contract as official provider physical metrics.

Implementation notes:

- Use provider speed when present and documented. If it is missing, derive speed
  from adjacent coordinates as `distance_m / dt_seconds`, then smooth or
  aggregate before displaying labels so one-frame jitter does not dominate.
- Convert coordinates to metres before computing distance or speed. Tracking
  feeds may expose metres, centimetres, or normalised pitch coordinates.
- Apply a declared glitch guard before top speed, speed-band totals, and sprint
  detection. Impossible spikes should become missing samples, not records.
- Treat period boundaries separately for speed derivation, smoothing, and sprint
  detection. Do not connect a run across half-time or extra-time breaks.
- Filter speed-band totals and sprint detection to live frames when the feed
  exposes a live/dead flag. Distance covered and observed minutes may still count
  every tracked frame, but label that choice.
- Keep a provider/derived source flag per metric family. It is acceptable for
  distance to be provider supplied while speed is derived, but the API response
  should make that visible.
- Do not compare custom thresholds against SkillCorner, Wyscout, or other
  provider physical outputs without labelling the threshold set. A derived
  tracking workload report is not the same contract as official provider
  physical metrics.

---

## [4] Physical speed bands
**Provider:** skillcorner | **Category:** concepts | **Source:** crawled (https://www.skillcorner.com/apidocs.json) | SkillCorner API (OpenAPI 3.1) | crawled 2026-08-31

## Physical speed bands

Physical metrics bucket movement by intensity: **running**, **HSR** (High Speed Running), **sprint**, and **HI** (High Intensity = HSR + sprint). Acceleration/deceleration efforts are split into **medium** and **high**, with **explosive** accelerations that lead into HSR or a sprint tracked separately. **PSV-99** (Peak Sprint Velocity, 99th percentile) is an outlier-robust top-speed proxy. Exact km/h thresholds are in the glossary. See [physical-data.md](physical-data.md).
````

### s03 — search_docs {"query": "Catapult PlayerLoad high speed running export fields", "max_results": 5}

````text
Found 5 result(s) for "Catapult PlayerLoad high speed running export fields":

## [1] Tracking-derived off-ball runs recipe
**Provider:** kloppy | **Category:** tracking-rendering | **Source:** curated by football-docs contributors

## Tracking-derived off-ball runs recipe

Use this recipe when an agent asks for off-ball runs, high-speed runs away from
the ball, forward runs, channel runs, run maps, or run-detection timelines from
optical tracking feeds.

| Output field | Source fields | Rule |
|---|---|---|
| `player_id` / `team_id` | tracking entity, lineup join | Emit provider ids and display labels only after the identity join is proven. |
| `period` / `start_ms` / `end_ms` | frame period and timestamp | Use the tracking period clock, not wall-clock time. |
| `duration_s` | consecutive above-threshold frames | Count the span of the run, not just the number of sampled frames. |
| `distance_m` | player coordinates or provider cumulative distance | Prefer provider distance when documented; otherwise derive consistently from live-frame coordinates. |
| `peak_speed_mps` | provider speed or coordinate delta / frame interval | Convert units before thresholding; keep the source of speed visible. |
| `towards_goal` | attacking direction plus player displacement | Resolve attacking direction per team and period before labelling a run forward. |
| quality flags | live/dead state, missing positions, ball proximity, direction confidence | Report rejected or skipped windows rather than filling with zero. |

Implementation notes:

- Filter to live frames when the feed exposes a live/dead flag. If an older
  export lacks that flag, state the fallback rather than silently changing the
  definition.
- Detect candidate runs as contiguous spans above a declared speed threshold,
  with an optional short-gap merge rule. Label both the threshold and the
  minimum duration.
- Exclude on-ball carrying or receiving actions by checking player-ball
  proximity across the run. A common rule is to reject runs where the player is
  close to the ball during the body of the run, while allowing a short trailing
  receive window at the end.
- Resolve attacking direction from provider metadata where available, such as
  `home_team_side` plus period. If metadata is absent and you infer direction
  from goalkeeper depth or team shape, label that inference and expose a
  confidence flag.
- Do not classify "towards goal" from raw `+x` movement until the coordinate
  frame, team side, and period have been normalised.
- Keep this separate from provider official physical metrics. A derived run
  detector is a product rule over frames; provider high-speed running or sprint
  counts may use different thresholds, smoothing, and live-ball handling.

---

## [2] Physical speed bands
**Provider:** skillcorner | **Category:** concepts | **Source:** crawled (https://www.skillcorner.com/apidocs.json) | SkillCorner API (OpenAPI 3.1) | crawled 2026-08-31

## Physical speed bands

Physical metrics bucket movement by intensity: **running**, **HSR** (High Speed Running), **sprint**, and **HI** (High Intensity = HSR + sprint). Acceleration/deceleration efforts are split into **medium** and **high**, with **explosive** accelerations that lead into HSR or a sprint tracked separately. **PSV-99** (Peak Sprint Velocity, 99th percentile) is an outlier-robust top-speed proxy. Exact km/h thresholds are in the glossary. See [physical-data.md](physical-data.md).

---

## [3] Base metrics
**Provider:** skillcorner | **Category:** physical-data | **Source:** crawled (https://www.skillcorner.com/apidocs.json) | SkillCorner API (OpenAPI 3.1) | crawled 2026-08-31

## Base metrics

| Metric stem | Meaning |
|---|---|
| `total_distance` | Total distance covered (m) |
| `total_metersperminute` | Distance per minute (m/min) |
| `running_distance` | Distance in the running speed band |
| `hsr_distance` / `hsr_count` | High Speed Running distance / number of efforts |
| `sprint_distance` / `sprint_count` | Sprinting distance / number of sprints |
| `hi_distance` / `hi_count` | High Intensity distance / efforts (HSR + sprint band) |
| `medaccel_count` / `highaccel_count` | Medium / high acceleration counts |
| `meddecel_count` / `highdecel_count` | Medium / high deceleration counts |
| `explacceltohsr_count` | Explosive accelerations leading into HSR |
| `explacceltosprint_count` | Explosive accelerations leading into a sprint |
| `timetohsr` / `timetohsr_top3` | Time to reach HSR (and top-3 average) |
| `timetosprint` / `timetosprint_top3` | Time to reach sprint speed (and top-3 average) |
| `psv99` / `psv99_top5` | Peak Sprint Velocity (99th percentile) and top-5 average — a max-speed proxy robust to outliers |

(Speed-band thresholds — what counts as running / HSR / sprint — are defined in the SkillCorner glossary: <https://skillcorner.crunch.help/en>.)

---

## [4] Player workload table recipe
**Provider:** skillcorner | **Category:** physical-data | **Source:** crawled (https://www.skillcorner.com/apidocs.json) | SkillCorner API (OpenAPI 3.1) | crawled 2026-08-31

## Player workload table recipe

Use this recipe when an agent asks for a physical table, player workload view,
high-speed running leaderboard, sprint chart, or top-speed comparison from
SkillCorner-style physical data.

| Display field | SkillCorner source | Notes |
|---|---|---|
| minutes observed | `minutes_full_all` or the relevant split | Show the denominator next to rate metrics; do not compare tiny samples to full-match workloads without a minutes filter. |
| distance | `total_distance_full_all` | Values are metres. Convert to kilometres for display, but keep raw metres in data exports. |
| metres per minute | `total_metersperminute_full_all` or derived from distance/minutes | Useful when comparing players with different minutes; state whether it is all time or ball-in-play. |
| HSR distance/count | `hsr_distance_*`, `hsr_count_*` | HSR thresholds come from the SkillCorner glossary and may differ from Wyscout or a custom tracking pipeline. |
| sprint distance/count | `sprint_distance_*`, `sprint_count_*` | Counts are efforts, not metres; keep count and distance separate. |
| high-intensity output | `hi_distance_*`, `hi_count_*` | HI combines HSR and sprint bands. Avoid double-counting it with HSR/sprint components in totals. |
| top-speed proxy | `psv99` or `psv99_top5` | Peak/time metrics are bare fields, not split fields. Do not construct `psv99_full_all`. |
| acceleration load | `medaccel_count_*`, `highaccel_count_*`, `meddecel_count_*`, `highdecel_count_*` | Treat acceleration/deceleration counts as a separate load family from distance. |
| quality status | `physical_check_passed`, `count_match`, `count_match_failed` | Filter or flag rows that fail QC before ranking players. |

Choose one comparison basis before plotting:

- absolute match output: `*_full_all` values, best for "what did this player do
  today?";
- per-90: `*_p90`, best for season/competition leaderboards with minutes
  thresholds;
- ball-in-play: `*_p60bip`, best when comparing intensity independent of dead
  time;
- possession phase: `*_p30tip` / `*_p30otip`, best for in-possession versus
  out-of-possession physical profiles.

Do not mix providers' speed bands silently. SkillCorner HSR/sprint thresholds are
defined in its glossary; Wyscout exposes similar labels with km/h thresholds, and
custom tracking pipelines often use local m/s cut-offs. When joining physical
data to event or video views, keep `match_id`, `player_id`, `team_id`, period,
minutes basis, units, and QC flags in the exported data.

---

## [5] Physical metrics
**Provider:** wyscout | **Category:** glossary-metrics-concepts | **Source:** crawled (https://dataglossary.wyscout.com/) | crawled 2026-06-03

## Physical metrics

These metrics are only available for specific competitions and players with at least 60 minutes of active play across all matches.

| Metric | Definition | Products |
|---|---|---|
| Count HI per 90 | The number of High Intensity actions: sum of Count HSR (High Speed Runs) and Count Sprint, normalized per 90 minutes. | Advanced Search |
| Count High Acceleration per 90 | The number of Accelerations detected with a peak value greater than 3 m/s², normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| Count High Deceleration per 90 | The number of Decelerations detected with a peak value less than -3 m/s², normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| Count HSR per 90 | The number of High Speed Runs detected between 20 km/h and 25 km/h, normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| Count Medium Acceleration per 90 | The number of Accelerations detected with a peak value between 1.5 m/s² and 3 m/s², normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| Count Medium Deceleration per 90 | The number of Decelerations detected with a peak value between -1.5 m/s² and -3 m/s², normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| Count Sprint per 90 | The number of Sprints exceeding 25 km/h, normalized per 90 minutes. The action needs to last for at least 1 second. | Advanced Search |
| HI Distance per 90 | High Intensity. Distance covered above 20 km/h, normalized per 90 minutes. | Advanced Search |
| HSR Distance per 90 | High Speed Runs. Distance covered between 20 km/h and 25 km/h, normalized per 90 minutes. | Advanced Search |
| Meter/min | Total distance covered across all actions, divided per number of minutes. | Advanced Search |
| Max Speed (km/h) | The maximum speed recorded. | Advanced Search |
| Running Distance per 90 | Distance covered between 15 km/h and 20 km/h, normalized per 90 minutes. | Advanced Search |
| Sprinting Distance per 90 | Distance covered above 25 km/h, normalized per 90 minutes. | Advanced Search |
| Total Distance per 90 | Total distance covered, normalized per 90 minutes. | Advanced Search |

Source: [https://dataglossary.wyscout.com/physical_metrics/](https://dataglossary.wyscout.com/physical_metrics/)
````

### s04 — search_docs {"query": "Catapult", "provider": "catapult"} — error

````text
Provider "catapult" is not indexed. Call list_providers for available provider keys, or use request_update to suggest adding it.
````

### g01 — get_provider_docs {"provider": "opta", "topic": "big chance"}

````text
Provider docs for **opta** (Opta) matching "big chance":

## [1] Zone and low-xG proxies
**Provider:** opta | **Category:** charting-shot-placement | **Source:** curated by football-docs contributors

## Zone and low-xG proxies

If a continuous xG source is unavailable, zone qualifiers can be used as a rough
proxy, but label the result as a proxy rather than xG:

| Zone qualifier family | Typical use |
|---|---|
| `16`, `60`, `61` | small-box zones; usually exclude from low-xG placement-skill cuts |
| `17` | box centre |
| `62`, `63`, `64`, `65` | box wide/deep-box zones |
| `18` | out-of-box centre |
| `66`, `67`, `68`, `69` | out-of-box wide/deep zones |
| `19`, `70`, `71` | thirty-five-plus / long-range zones |
| `214` | big chance; usually exclude from low-xG placement-skill cuts |
| `9` | penalty; exclude or analyse separately |

For a robust first pass, join continuous xG from `matchexpectedgoals` where possible.
If you only have `matchevent`, a low-xG proxy can exclude small-box, big-chance, and
penalty qualifiers, then report zone-adjusted residuals so wide-angle geometry does
not masquerade as finishing skill.

---

## [2] Shot Qualifiers
**Provider:** opta | **Category:** qualifiers | **Source:** curated by football-docs contributors

## Shot Qualifiers

| ID | Name | Notes |
|----|------|-------|
| 15 | head | Headed shot/goal |
| 20 | rightFoot | Right-footed shot |
| 72 | leftFoot | Left-footed shot |
| 21 | otherBodyPart | Knee, chest, etc. |
| 22 | regularPlay | The event happened in open play, not from a set play |
| 24 | setPiece | The event followed a free kick that was not struck directly. A shot struck directly from a free kick is Q26 |
| 25 | fromCorner | Shot followed a corner |
| 26 | freeKick | Shot struck directly from a free kick |
| 29 | assisted | A team-mate's pass set up the shot or chance |
| 160 | throwInSetPiece | The shot or pass came from a throw-in set piece |
| 214 | bigChance | Big chance: a clear-cut chance the player should score, such as a one-on-one |
| 9 | penalty | Penalty taken, or penalty awarded (on a foul, typeId 4) |
| 108 | volley | Volley: the ball did not bounce before the shot |
| 328 | firstTouch | Shot struck first time, without a controlling touch |
| 263 | directCorner | Shot or goal directly from a corner (Olimpico) |
| 136 | keeperTouched | Goal where the goalkeeper got a touch on the ball |
| 82 | blocked | The shot was blocked |
| 146 | blockedX | X coordinate where the shot was blocked, or where an opponent touched an off-target shot |
| 147 | blockedY | Y coordinate for the same point as Q146 |

Qualifiers 16-19 and 60-71 are pitch zones for the shot location (for example 16
small box centre, 17 box centre, 18 out of box centre, 19 35+ centre). See
charting-shot-placement for the full zone list.

---

## [3] Pass Qualifiers
**Provider:** opta | **Category:** qualifiers | **Source:** curated by football-docs contributors

## Pass Qualifiers

| ID | Name | Notes |
|----|------|-------|
| 1 | longBall | Pass longer than 32 metres |
| 2 | cross | Cross (Q2). Corners commonly carry Q2 + Q6; free-kick crosses commonly carry Q2 + Q5; open-play crosses are Q2 without Q5/Q6. |
| 3 | headPass | Headed pass (Q3). Distinct from Q15, the headed shot qualifier. |
| 4 | throughBall | Through ball (Q4). Do not confuse with Q5 free-kick delivery. |
| 5 | freeKickTaken | Free kick pass / free-kick delivery (Q5), direct or indirect. |
| 6 | cornerTaken | Corner kick / corner delivery (Q6). |
| 107 | throwIn | Throw-in |
| 124 | goalKick | Goal kick pass. For goal-kick distribution charts, combine with pass end coordinates Q140/Q141. |
| 279 | kickOff | Kick-off pass. Value `S` is the kick-off that starts a period; `G` is the kick-off after a goal. |
| 7 | playersCaughtOffside | On an offside pass (typeId 2). The value is the ID of the player caught offside. It is not a goal-kick flag; goal kicks are Q124. |
| 154 | intentionalAssist | Pass that creates a scoring chance, for example a cross into the box or a through ball |
| 210 | assist | The pass set up a shot, a goal or a missed chance |
| 196 | switchOfPlay | Pass crossing centre zone, y-distance > 60 |
| 212 | length | Estimated distance in metres that the ball travelled on the pass or clearance |
| 213 | angle | Direction of the pass or clearance relative to the direction of play, in radians (0.00 to 6.28) |

---

## [4] Shot context and consequence filters
**Provider:** opta | **Category:** charting-shot-placement | **Source:** curated by football-docs contributors

## Shot context and consequence filters

Shot-placement stories often ask whether a miss, save, post hit, or weak finish
changed the match state. Join each shot row to a running scoreline timeline before
building late-game, close-game, or "mattered" filters.

| Derived field | How to derive it | Use |
|---|---|---|
| `team_score_at_shot` / `opp_score_at_shot` | Count valid goals strictly before the shot clock, from the shooting team's perspective | Tooltip, score-state splits, consequence labels |
| `goal_diff_at_shot` | `team_score_at_shot - opp_score_at_shot` | Classify whether the shooter was leading, level, or trailing |
| `state_at_shot` | `winning`, `drawing`, or `losing` from `goal_diff_at_shot` | Filter shot maps by game state or pressure context |
| `is_late` | minute threshold such as `minute >= 80`, using expanded minutes when available | Late-shot and stoppage-time story filters |
| `is_close_final` | final margin within one goal, after converting to the shooting team's perspective | Avoid overstating misses in already-decided matches |
| `mattered` | shot taken while the goal difference was within one and the final margin was within one | Narrative filter for chances that could plausibly change the result |

Use the goal-timeline reconstruction in [charting-game-state.md](charting-game-state.md):
drop disallowed goals with qualifier `8`, credit own goals with qualifier `28` to
the opposing team, and sort by period-aware clock or `expandedMinute`. Count only
goals before the shot; a goal event at the same clock should not retroactively
change the shot's pre-shot state unless the provider explicitly links them.

Keep these consequence fields separate from provider facts. `mattered`,
`late`, `close final`, and `pressure shot` are analysis labels layered on top of
Opta events, not Opta event types.
````

### l01 — list_providers {}

````text
Indexed providers:

**besoccer** (16 chunks): api-access (7), api-endpoints (7), data-provenance (2) | aliases: be-soccer, besoccerapps, resultados-de-futbol
**databallpy** (63 chunks): data-model (14), overview (8), usage (41) | aliases: data-ball-py, databall-py, metrica, metrica-sports, metricasports, sportec, dfl, sportec-dfl, open-dfl, tracab
**driblab** (32 chunks): api-access (9), api-endpoints (9), data-model (12), data-provenance (2) | aliases: driblab-pro, driblab-api
**espn** (21 chunks): api-access (5), identity-and-coverage (4), match-summary (5), scoreboard (4), teams-and-standings (3) | aliases: espn-soccer, espn-fc
**fast-forward** (250 chunks): api (27), benchmarks (5), concepts-coordinate-systems (12), concepts-dataset (13), concepts-distributed-compute (25), concepts-filelike (7), concepts-layouts (7), concepts-orientations (15), concepts-transformations (12), getting-started (16), index (21), providers (5), providers-cdf (6), providers-gradientsports (6), providers-hawkeye (8), providers-optavision (6), providers-respovision (7), providers-scisports (6), providers-secondspectrum (6), providers-signality (6), providers-skillcorner (8), providers-sportec (6), providers-statsperform (6), providers-tracab (8), reporting-issues (6) | aliases: fastforward, fast-forward-football, unravel-fast-forward, hawkeye, hawk-eye, scisports, signality, respovision, gradientsports, optavision
**floodlight** (144 chunks): compendium-0-compendium (1), compendium-1-data (5), compendium-2-design (1), compendium-3-time (6), compendium-4-space (4), compendium-5-identifier (4), core-code (1), core-core (1), core-definitions (1), core-events (1), core-pitch (1), core-property (1), core-teamsheet (1), core-xy (1), guides-contrib-manual (21), guides-getting-started (29), guides-tutorial-analysis (13), guides-tutorial-matchsheets (6), index (2), io-datasets (13), io-dfl (1), io-io (1), io-kinexon (1), io-opta (1), io-secondspectrum (1), io-skillcorner (1), io-sportradar (1), io-statsbomb (1), io-statsperform (1), io-tracab (1), io-utils (1), metrics-entropy (1), metrics-metrics (1), metrics-trajectory-clustering (1), metrics-zone-aggregation (1), models-geometry (1), models-kinematics (1), models-kinetics (1), models-models (1), models-space (1), transforms-filter (1), transforms-interpolation (1), transforms-permutation (1), transforms-spatial (1), transforms-temporal (1), transforms-transforms (1), utils-types (1), utils-utils (1), vis-pitches (1), vis-positions (1), vis-vis (1)
**fmdb-pro** (37 chunks): api-access (9), api-endpoints (8), data-model (9), data-provenance (2), identity-surfaces (9) | aliases: fmdb
**fotmob** (5 chunks): data-provenance (2), identity-surfaces (3)
**free-sources** (60 chunks): contextual-story-joins (8), data-provenance (8), fbref (5), overview (12), understat (19), xg-timelines (8) | aliases: fbref, football-reference, understat, clubelo, club-elo, football-data, football-data-uk, football-data-co-uk, engsoccerdata, free, free-source
**impect** (79 chunks): concepts (12), coordinate-system (10), data-model (17), data-provenance (2), event-types (16), identity-surfaces (9), kpi-definitions (4), overview (9)
**kloppy** (126 chunks): data-model (23), event-derived-metrics (13), provider-mapping (15), tracking-rendering (13), usage (62) | aliases: secondspectrum, second-spectrum
**mplsoccer** (65 chunks): overview (3), pitch-types (13), visualizations (49) | aliases: mpl-soccer
**opta** (73 chunks): api-access (8), charting-game-state (9), charting-lineups (6), charting-passmaps (6), charting-set-pieces (6), charting-shot-placement (10), coordinate-system (6), data-provenance (2), event-types (6), identity-surfaces (4), qualifiers (10) | aliases: statsperform, stats-perform, opta-f24, whoscored, who-scored
**reep** (29 chunks): api (7), data-provenance (2), download-duckdb-csv (9), identity-and-ids (6), overview (5) | aliases: reep-football
**skillcorner** (51 chunks): api-access (10), api-endpoints (8), concepts (6), coordinate-system (5), data-model (9), data-provenance (2), identity-surfaces (4), physical-data (7) | aliases: skill-corner
**socceraction** (34 chunks): spadl (12), vaep-xt (22) | aliases: soccer-action
**soccerdata** (40 chunks): data-sources (9), overview (5), usage (26) | aliases: soccer-data, sofascore, sofa-score
**soccerdonna** (5 chunks): data-provenance (2), identity-surfaces (3) | aliases: soccer-donna
**sportmonks** (567 chunks): api-access (27), api-changes (12), authentication (3), best-practices (8), changelog (38), changelog-beta (29), charting-season-stories (7), code-libraries (2), data-corrections (5), data-model (22), data-provenance (2), demo-response-files (8), differences-between-api-2-and-api-3 (2), endpoints (1), error-codes (34), event-types (22), filtering (2), filtering-and-complexity-exceptions (1), fixtures (3), get-all-fixtures (8), get-all-leagues (8), get-all-leagues-by-team-id (8), get-all-livescores (7), get-all-seasons (8), get-all-states (8), get-all-types (5), get-brackets-by-season-id (13), get-current-leagues-by-team-id (6), get-fixture-by-id (7), get-fixtures-by-date (8), get-fixtures-by-date-range (8), get-fixtures-by-date-range-for-team (7), get-fixtures-by-head-to-head (7), get-fixtures-by-multiple-ids (7), get-fixtures-by-search-by-name (8), get-inplay-livescores (6), get-latest-updated-fixtures (11), get-latest-updated-livescores (11), get-league-by-id (7), get-leagues-by-country-id (7), get-leagues-by-fixture-date (8), get-leagues-by-live (7), get-leagues-search-by-name (8), get-past-fixtures-by-tv-station-id (8), get-seasons-by-id (7), get-seasons-by-search-by-name (8), get-seasons-by-team-id (7), get-state-by-id (7), get-type-by-entity (1), get-type-by-id (5), get-upcoming-fixtures-by-market-id (8), get-upcoming-fixtures-by-tv-station-id (8), getting-started (6), identity-surfaces (4), include-exceptions (1), includes (4), leagues (13), livescores (1), making-your-first-request (9), meta-description (1), nested-includes (3), new-endpoints-and-data-features (4), ordering-and-sorting (3), other-exceptions (1), overview (1), rate-limit (2), request-options (1), seasons (3), selecting-and-filtering (1), selecting-fields (3), states (4), statistics (1), syntax (4), syntax-and-filters (6), translations-beta (5), types (1), what-can-you-do-with-sportmonks-data (10) | aliases: sport-monks
**sportradar** (481 chunks): api-access (6), api-endpoints (6), charting-and-stories (5), data-model (8), data-provenance (2), integration-notes (5), monitoring-data-changes (13), soccer-api-vs-soccer-extended-api (7), soccer-extended-competition-info (2), soccer-extended-competition-seasons (2), soccer-extended-competitions (3), soccer-extended-competitor-mappings (2), soccer-extended-competitor-merge-mappings (2), soccer-extended-competitor-profile (7), soccer-extended-competitor-schedules (16), soccer-extended-competitor-summaries (5), soccer-extended-competitor-vs-competitor (2), soccer-extended-daily-schedules (2), soccer-extended-daily-summaries (2), soccer-extended-faq (71), soccer-extended-fifa-rankings (3), soccer-extended-league-timeline (7), soccer-extended-live-schedules (2), soccer-extended-live-summaries (2), soccer-extended-live-timelines (3), soccer-extended-live-timelines-delta (2), soccer-extended-overview (11), soccer-extended-player-mappings (2), soccer-extended-player-merge-mappings (2), soccer-extended-player-profile (4), soccer-extended-player-schedules (2), soccer-extended-player-summaries (2), soccer-extended-push-events (12), soccer-extended-push-feeds (5), soccer-extended-push-statistics (10), soccer-extended-season-competitors (2), soccer-extended-season-form-standings (4), soccer-extended-season-info (9), soccer-extended-season-leaders (4), soccer-extended-season-lineups (5), soccer-extended-season-links (3), soccer-extended-season-missing-players (4), soccer-extended-season-overunder-statistics (3), soccer-extended-season-players (2), soccer-extended-season-schedule (3), soccer-extended-season-standings (4), soccer-extended-season-summaries (2), soccer-extended-season-transfers (4), soccer-extended-season-venues (2), soccer-extended-seasonal-competitor-extended-stati (6), soccer-extended-seasonal-competitor-players (3), soccer-extended-seasonal-competitor-statistics (5), soccer-extended-seasons (2), soccer-extended-seasons-disabled (2), soccer-extended-sport-event-extended-summary (5), soccer-extended-sport-event-extended-timeline (5), soccer-extended-sport-event-fun-facts (2), soccer-extended-sport-event-insights (2), soccer-extended-sport-event-lineups (2), soccer-extended-sport-event-momentum (3), soccer-extended-sport-event-summary (2), soccer-extended-sport-event-timeline (3), soccer-extended-sport-events-created (2), soccer-extended-sport-events-removed (2), soccer-extended-sport-events-updated (2), soccer-ig-api-basics (16), soccer-ig-data-coverage-tiers (7), soccer-ig-fixtures (9), soccer-ig-historical-data (6), soccer-ig-id-handling (18), soccer-ig-live-match-retrieval (12), soccer-ig-match-status-workflow (13), soccer-ig-overview (1), soccer-ig-push (13), soccer-ig-rosters-lineups-transfers (9), soccer-ig-scenarios (1), soccer-ig-seasonal-stats (7), soccer-ig-tracking-standings (16), soccer-ig-tracking-tournaments (11), soccer-ig-update-frequencies (6) | aliases: sport-radar, sportradar-api, soccer-extended, sportradar-soccer
**statsbomb** (237 chunks): api-access (38), api-endpoints (8), charting-lineups (6), coordinate-system (13), data-model (27), data-provenance (2), event-types (48), identity-surfaces (5), iq-metrics-glossary (14), player-mapping (6), player-match-stats (13), player-season-stats (12), team-match-stats (11), team-season-stats (11), xg-model (23) | aliases: stats-bomb, statsbomb-open-data, statsbomb-open
**thesportsdb** (20 chunks): api-access (6), api-endpoints (4), data-provenance (2), identity-surfaces (4), livescore (4) | aliases: tsdb, the-sports-db, the-sportsdb, sportsdb
**transfermarkt** (5 chunks): data-provenance (2), identity-surfaces (3)
**transferroom** (45 chunks): api-access (8), api-endpoints (12), charting-availability (5), data-model (9), data-provenance (2), identity-surfaces (9) | aliases: transfer-room
**unravelsports** (202 chunks): additional-citations (5), additional-license (6), american-football-dataset (2), american-football-graphs (1), api-american-football (1), api-classifiers (8), api-soccer (1), api-utils (1), generated-unravel-utils-add-dummy-label-column (1), generated-unravel-utils-add-graph-id-column (1), generated-unravel-utils-dummy-graph-ids (1), generated-unravel-utils-dummy-labels (1), getting-started-concepts (17), getting-started-installation (11), getting-started-quickstart (25), index (5), soccer-dataset (4), soccer-graphs (3), soccer-models (2), tutorials-american-football (15), tutorials-formation-detection (30), tutorials-pressing-intensity (21), tutorials-soccer-gnn (30), utils-features (2), utils-helpers (5), utils-objects (3) | aliases: unravel, unravel-sports, bigdatabowl, big-data-bowl
**wyscout** (165 chunks): api-access (11), api-endpoints (13), charting-analysis-metrics (7), coordinate-system (6), data-model (17), data-provenance (2), event-types (6), glossary-events (79), glossary-metrics-concepts (20), identity-surfaces (4) | aliases: hudl, hudl-wyscout

Data: built 2026-09-29T07:27:10.000Z from commit 2d483df (bundled).
````

### p01 — resolve_provider_id {"query": "Catapult"} — error

````text
Provider "Catapult" is not registered. Use request_update to suggest adding it, or open a GitHub issue with the new-provider template.
````

### p02 — resolve_provider_id {"query": "Reep"}

````text
Resolved "Reep" to provider ID: **reep**
**Display name:** Reep
**Indexed:** yes (29 chunks)
**Categories:** api (7), data-provenance (2), download-duckdb-csv (9), identity-and-ids (6), overview (5)
**Aliases:** reep-football, reep.football
**Access level:** open-data
**Licence/status:** Releases are CC0 1.0, provider-ID bridges included. The download needs no key. API keys are issued by hand on request (getintouch+nutmeg@withqwerty.com); there is no self-service sign-up.
**Public-safety notes:** Document the current register only (reep.football, /api/v1). Spec snapshot in specs/reep/ comes from the public, unauthenticated https://reep.football/openapi.yaml - see specs/README.md. Endpoint claims are validated against it in CI. Do not hard-code release counts; they change weekly.
**Version:** v1
**Last crawled:** 2026-09-22
**Registered sources:** curated: https://reep.football/openapi.yaml; curated: https://reep.football/get-started; curated: https://reep.football/id-policy
````

### p03 — resolve_provider_id {"query": "Opta"}

````text
Resolved "Opta" to provider ID: **opta**
**Display name:** Opta
**Indexed:** yes (73 chunks)
**Categories:** api-access (8), charting-game-state (9), charting-lineups (6), charting-passmaps (6), charting-set-pieces (6), charting-shot-placement (10), coordinate-system (6), data-provenance (2), event-types (6), identity-surfaces (4), qualifiers (10)
**Aliases:** statsperform, stats-perform, opta-f24, whoscored, who-scored
**Access level:** licensed
**Licence/status:** No complete public API contract; curated notes must avoid restricted payloads.
**Public-safety notes:** Keep examples general and public-safe; do not include customer feeds or private paths.
**Version:** unversioned
**Last crawled:** not crawled
**Registered sources:** curated
````

### p04 — resolve_provider_id {"query": "StatsBomb"}

````text
Resolved "StatsBomb" to provider ID: **statsbomb**
**Display name:** StatsBomb
**Indexed:** yes (237 chunks)
**Categories:** api-access (38), api-endpoints (8), charting-lineups (6), coordinate-system (13), data-model (27), data-provenance (2), event-types (48), identity-surfaces (5), iq-metrics-glossary (14), player-mapping (6), player-match-stats (13), player-season-stats (12), team-match-stats (11), team-season-stats (11), xg-model (23)
**Aliases:** stats-bomb, statsbomb-open-data, statsbomb-open
**Access level:** public
**Licence/status:** Public open-data repository and public documentation; verify upstream licence before redistributing raw data.
**Public-safety notes:** Index public docs and public-safe event/data-model notes only.
**Version:** unversioned
**Last crawled:** not crawled
**Registered sources:** github_docs: https://github.com/hudl/open-data; curated
````

### p05 — resolve_provider_id {"query": "FBref"}

````text
Resolved "FBref" to provider ID: **free-sources**
**Display name:** Free sources
**Indexed:** yes (60 chunks)
**Categories:** contextual-story-joins (8), data-provenance (8), fbref (5), overview (12), understat (19), xg-timelines (8)
**Aliases:** fbref, football-reference, understat, clubelo, club-elo, football-data, football-data-uk, football-data-co-uk, engsoccerdata, free, free-source
**Access level:** public-web
**Licence/status:** Public sources with differing terms; verify upstream terms before redistribution.
**Public-safety notes:** Document source shapes, joins, and public-safe usage caveats only.
**Version:** unversioned
**Last crawled:** not crawled
**Registered sources:** curated
````

### p06 — resolve_provider_id {"query": "Transfermarkt"}

````text
Resolved "Transfermarkt" to provider ID: **transfermarkt**
**Display name:** Transfermarkt
**Indexed:** yes (5 chunks)
**Categories:** data-provenance (2), identity-surfaces (3)
**Aliases:** none
**Access level:** public-web
**Licence/status:** Public website evidence; respect upstream terms and avoid scraped payload dumps.
**Public-safety notes:** Use identity-surface facts and public-safe observations only.
**Version:** unversioned
**Last crawled:** not crawled
**Registered sources:** curated
````

### p07 — resolve_provider_id {"query": "Sofascore"}

````text
Resolved "Sofascore" to provider ID: **soccerdata**
**Display name:** soccerdata
**Indexed:** yes (40 chunks)
**Categories:** data-sources (9), overview (5), usage (26)
**Aliases:** soccer-data, sofascore, sofa-score
**Access level:** open-source
**Licence/status:** Open-source library documentation; upstream site terms vary.
**Public-safety notes:** Describe supported public sources and avoid private scraper state.
**Version:** 1.9.1
**Last crawled:** not crawled
**Registered sources:** readthedocs: https://soccerdata.readthedocs.io/en/latest/; github_docs: https://github.com/probberechts/soccerdata
````

### r01 — resolve_entity {"provider": "transfermarkt", "namespace": "spieler", "id": "568177"}

````text
Found 1 result(s) in the local Reep register:

### Cole Jermaine Palmer (player)
Reep ID: rp53af22bbeaa667
Matched: transfermarkt / spieler: 568177
Provider IDs:
  api_football / player: 152982
  besoccer / player: 675016
  capology / player: cole-palmer-37382
  driblab / player: 1330225
  eafc / player: 257534
  fbref / person: dc7f8a28
  fifa / person: dl10343h8yopcgerzur5samwa
  fm / player: 28120042
  fotmob / person: 1096353
  national_football_teams / player: 92970
  opta / person: dl10343h8yopcgerzur5samwa
  opta / person_numeric: 244851
  second_spectrum / person: 14de05fe-fd33-4d52-a75f-e0e0f9ec3231
  skillcorner / player: 26154
  sportmonks / player: 28912747
  sportradar / player: sr:player:1737609
  statsbomb / offline_player: 39461
  transfermarkt / spieler: 568177
  uefa / player: 250124282
  worldfootball / person_numeric: 567392
  wyscout / player: 551497

Local register release: 20260926T145536Z (current).
````

### r03 — resolve_entity {"provider": "fbref", "namespace": "person", "id": "dc7f8a28"}

````text
Found 1 result(s) in the local Reep register:

### Cole Jermaine Palmer (player)
Reep ID: rp53af22bbeaa667
Matched: fbref / person: dc7f8a28
Provider IDs:
  api_football / player: 152982
  besoccer / player: 675016
  capology / player: cole-palmer-37382
  driblab / player: 1330225
  eafc / player: 257534
  fbref / person: dc7f8a28
  fifa / person: dl10343h8yopcgerzur5samwa
  fm / player: 28120042
  fotmob / person: 1096353
  national_football_teams / player: 92970
  opta / person: dl10343h8yopcgerzur5samwa
  opta / person_numeric: 244851
  second_spectrum / person: 14de05fe-fd33-4d52-a75f-e0e0f9ec3231
  skillcorner / player: 26154
  sportmonks / player: 28912747
  sportradar / player: sr:player:1737609
  statsbomb / offline_player: 39461
  transfermarkt / spieler: 568177
  uefa / player: 250124282
  worldfootball / person_numeric: 567392
  wyscout / player: 551497

Local register release: 20260926T145536Z (current).
````

### r02 — resolve_entity {"name": "Cole Palmer", "type": "player"}

````text
No Reep entity matches that query in the local register.

Local register release: 20260926T145536Z (current).
````
