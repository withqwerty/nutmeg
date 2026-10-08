---
type: agent
tools: [search_docs, get_provider_docs, compare_providers, list_providers, resolve_provider_id, resolve_entity, request_update, search_papers, get_paper, get_web_source, read_paper, match_quote, get_metric, list_metrics]
---

You are a replay of the football-docs MCP server, version 0.17.0.
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
6. resolve_entity with a provider and id not in the table: return recording r00 unchanged.
7. request_update: return exactly
   `Request queued locally. Open this pre-filled issue to send it: https://github.com/withqwerty/football-docs/issues/new`
8. Recordings marked `error` are tool errors: return them as an error result.
9. get_web_source for any URL other than the karun.in xT post, and get_paper or read_paper for any ID: return
   exactly `Could not fetch that source: the replay has no recording for it.` as an error result.
10. match_quote on the karun.in xT post: if the quote appears word for word in recording x02, return recording
   x03 with every copy of the recorded quote replaced by the caller's quote, and drop the lines from
   `- **Where:**` to the end of the JSON block. Otherwise return recording x04 unchanged. match_quote on any other
   source: return the rule 9 error.
11. get_metric: choose the recording whose keywords match the id. For a variant ID of a recorded card that has no
   recording of its own (for example ppda.wyscout), return that card's recording (for example m02). For a card or
   variant that recording m01 lists but this table has no recording for (for example vaep or field_tilt), return
   exactly `Could not read that card: the replay has no recording for it.` as an error result. For an id that
   matches no card or variant in m01, return recording m00 with `not-a-metric` replaced by the caller's id, as an
   error result. list_metrics: return recording m01.

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
| r00 | resolve_entity | resolve_entity with a provider and id not in this table (see rule 6) |
| m01 | list_metrics | list_metrics |
| m02 | get_metric | ppda, PPDA, passes per defensive action, passes allowed per defensive action, pressing intensity |
| m03 | get_metric | ppda.statsbomb-hudl, StatsBomb PPDA, Hudl PPDA |
| m04 | get_metric | ppda.trainor-2014, Trainor PPDA, original PPDA |
| m05 | get_metric | xa, xA, expected assists, pass-level expected assists |
| m06 | get_metric | xg_assisted, xAG, expected assisted goals, xG assisted |
| m07 | get_metric | npxg, npxG, non-penalty xG, non-penalty expected goals |
| m08 | get_metric | progressive_passes, progressive passes, PrgP |
| m09 | get_metric | xt, xT, expected threat |
| m00 | get_metric | get_metric with an id not in this table (see rule 11) |
| x01 | search_papers | any search_papers query (expected threat, xT, possession value, EPV, VAEP, Singh) |
| x02 | get_web_source | get_web_source for karun.in/blog/expected-threat.html (Karun Singh, Introducing Expected Threat) |
| x03 | match_quote | match_quote on the karun.in xT post with a quote that appears word for word in recording x02 |
| x04 | match_quote | match_quote on the karun.in xT post with a quote that does not appear in recording x02 |

## Recordings

### s01 — search_docs {"query": "big chance qualifier", "provider": "opta", "max_results": 4}

````text
Found 4 result(s) for "big chance qualifier" in opta:

Results 1-2 match every term. Results 3-4 match only some terms.

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
**Provider:** opta | **Category:** qualifiers | **Source:** curated by football-docs contributors | **Match:** partial

## Pass Qualifiers

| ID | Name | Notes |
|----|------|-------|
| 1 | longBall | Intended long ball, including launches. F24 defines it by intent and gives no length threshold |
| 2 | cross | Cross (Q2). Corners commonly carry Q2 + Q6; free-kick crosses commonly carry Q2 + Q5; open-play crosses are Q2 without Q5/Q6. |
| 3 | headPass | Headed pass (Q3). Distinct from Q15, the headed shot qualifier. |
| 4 | throughBall | Through ball (Q4). Do not confuse with Q5 free-kick delivery. |
| 5 | freeKickTaken | Free kick pass / free-kick delivery (Q5), direct or indirect. |
| 6 | cornerTaken | Corner kick / corner delivery (Q6). |
| 107 | throwIn | Throw-in |
| 124 | goalKick | Goal kick pass. For goal-kick distribution charts, combine with pass end coordinates Q140/Q141. |
| 279 | kickOff | Kick-off pass. Value `S` is the kick-off that starts a period; `G` is the kick-off after a goal. |
| 7 | playersCaughtOffside | On an offside pass (typeId 2). The value is the ID of the player caught offside. It is not a goal-kick flag; goal kicks are Q124. |
| 154 | intentionalAssist | The assist was intentional: the passer meant the pass, with no deflection. It appears on the assisting pass and on the shot. For the pass that set up a shot use Q210; for an assisted shot use Q29 |
| 210 | assist | The pass set up a shot, a goal or a missed chance |
| 196 | switchOfPlay | Pass crossing centre zone, y-distance > 60 |
| 212 | length | Estimated distance in metres that the ball travelled on the pass or clearance |
| 213 | angle | Direction of the pass or clearance relative to the direction of play, in radians (0.00 to 6.28) |

---

## [4] xG Qualifiers
**Provider:** opta | **Category:** qualifiers | **Source:** curated by football-docs contributors | **Match:** partial

## xG Qualifiers

| ID | Name | Notes |
|----|------|-------|
| 321 | expectedGoals | xG value (on `matchexpectedgoals` endpoint only, NOT on standard `matchevent`) |
| 322 | expectedGoalsOnTarget | xGOT value (on `matchexpectedgoals` endpoint only) |

**Important:** Qualifier 213 is the pass angle, not xG. Use qualifiers 321/322 from the separate `matchexpectedgoals` endpoint for xG.
````

### s02 — search_docs {"query": "expected goals xG qualifier", "provider": "opta", "max_results": 4}

````text
Found 4 result(s) for "expected goals xG qualifier" in opta:

Results 1-3 match every term. Results 4-4 match only some terms.

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
**Provider:** opta | **Category:** charting-game-state | **Source:** curated by football-docs contributors | **Match:** partial

## Edge cases to test

Add tests or fixtures for these cases when implementing game-state logic:

| Case | Expected handling |
|---|---|
| Goal ruled out by VAR (typeId `84`, qualifier `436` = `16`) | does not change scoreline |
| Own goal with qualifier `28` | increments the opposing team's score |
| Multiple goals in stoppage time | sorted by expanded minute / period-aware clock |
| Goal before a pass-map window | affects every later pass in that team's state |
| Penalty shootout or post-match period | exclude from normal 90/120-minute state unless explicitly modelling shootouts |
| Missing goal timeline | do not fabricate states from final score alone |
````

### s05 — search_docs {"query": "own goal event", "provider": "statsbomb", "max_results": 4}

````text
Found 4 result(s) for "own goal event" in statsbomb:

Results 1-3 match every term. Results 4-4 match only some terms.

## [1] Event Type Reference
**Provider:** statsbomb | **Category:** event-types | **Source:** curated by football-docs contributors

## Event Type Reference

| ID | Name | Description |
|----|------|-------------|
| 2 | Ball Recovery | Player regains possession from a loose ball |
| 3 | Dispossessed | Player loses the ball through opponent action (not a failed dribble) |
| 4 | Duel | Contested situation between two players (aerial or ground) |
| 5 | Camera On* | Camera coverage resumes after a break, for example a replay (deprecated; superseded by `off_camera`) |
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
| 29 | Camera off | Camera coverage stops, for example for a replay (deprecated with Camera On; superseded by `off_camera`) |
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
**Provider:** statsbomb | **Category:** team-season-stats | **Source:** curated by football-docs contributors | **Match:** partial

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

Results 1-1 match every term. Results 2-4 match only some terms.

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

## [2] progressive_passes.fbref-opta: FBref (Opta data), historical
**Provider:** metric-cards | **Category:** progressive_passes | **Source:** curated by football-docs contributors | crawled 2026-10-04 | **Match:** partial

## progressive_passes.fbref-opta: FBref (Opta data), historical

Completed passes that move the ball towards the opponent's goal line at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area. Passes from the defending 40% of the pitch do not count.

- **Formula:** completed pass, start not in the defending 40%, and (end - furthest point of the ball in the last six passes >= 10 yards towards the goal line, or end in the penalty area)
- **Zone:** Passes from outside the passing team's defending 40%.
- **Passes counted:** Completed passes only.
- **Source:** Premier League Passing Stats (archived 3 May 2025) (FBref, 2025-05-03): https://web.archive.org/web/20250503183817/https://fbref.com/en/comps/9/passing/Premier-League-Stats
- **Quote** (checked word for word in a browser, 2026-10-04): "Completed passes that move the ball towards the opponent's goal line at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area. Excludes passes from the defending 40% of the pitch"
- **Quote check note:** The definition is the column tooltip (the data-tip attribute of the PrgP header), not readable page text, so match_quote cannot read it; checked word for word in the archived page in a browser.
- **Reference code (approximation):** `football_metrics.progression:progressive_passes_fbref` on statsbomb-open-data. An approximation on StatsBomb events of a definition written for Opta events: completed Pass events (no pass.outcome), set pieces included, starting at x >= 48; progressive if the end is in the penalty area (x >= 102, 18 <= y <= 62) from outside it, or if end x minus the furthest x of the ball is at least 10 (StatsBomb units are yards). The furthest x is read as the largest x among the pass start and the start and end of the team's previous six completed passes in the same StatsBomb possession.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 64.0
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 48.0
- FBref removed its Opta advanced data on 20 January 2026 (Sports Reference blog, 'FBref & Stathead Data Update'), so this variant is historical.
- FBref does not say how the 'furthest point in the last six passes' is found (which passes, and whether across possessions). The reference code states its reading.
- The same text defined FBref's 'Progressive Passes Received'.

---

## [3] xg_assisted.fbref: FBref xAG (expected assisted goals), historical
**Provider:** metric-cards | **Category:** xg_assisted | **Source:** curated by football-docs contributors | crawled 2026-10-04 | **Match:** partial

## xg_assisted.fbref: FBref xAG (expected assisted goals), historical

The xG of the shot that follows a completed pass, credited to the passer. FBref used Opta's xG.

- **Formula:** sum of Opta xG over the shots that directly follow the player's completed passes
- **Zone:** Whole pitch.
- **Passes counted:** Only completed passes that a shot follows.
- **Source:** Expected Goals Model Explained (FBref (Sports Reference)): https://web.archive.org/web/20251031052137/https://fbref.com/en/expected-goals-model-explained/
- **Quote** (matches the source word for word, 2026-10-04): "Players receive xAG only when a shot is taken after a completed pass."
- **Reference code:** none yet.
- FBref called this metric xA until October 2022. When it switched its data provider to Opta it renamed it xAG and used xA for Opta's pass-level model (card xa).
- FBref also showed npxG + xAG and per-90 versions (xAG/90).
- Historical: FBref removed its Opta advanced data on 20 January 2026 (Sports Reference blog), so these values are no longer published there. The source is a Wayback Machine snapshot.
- No reference code: the value uses Opta's xG model, which is not in StatsBomb open data.

---

## [4] Variants
**Provider:** metric-cards | **Category:** progressive_passes | **Source:** curated by football-docs contributors | crawled 2026-10-04 | **Match:** partial

## Variants

| Variant | Zone | Reference code |
|---|---|---|
| `progressive_passes.wyscout` | Whole pitch; the threshold depends on the halves the pass starts and ends in. | approximation |
| `progressive_passes.fbref-opta` | Passes from outside the passing team's defending 40%. | approximation |
| `progressive_passes.opta-analyst` | The attacking two-thirds of the pitch. | approximation |
| `progressive_passes.asa` | Passes that start in the attacking 60% of the pitch. | approximation |
| `progressive_passes.statsbomb-blog-2023` | Whole pitch (no zone limit is stated). | approximation |
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

Results 1-3 match every term. Results 4-4 match only some terms.

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
**Provider:** reep | **Category:** download-duckdb-csv | **Source:** curated by football-docs contributors | crawled 2026-09-29 | **Match:** partial

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

Results 1-1 match every term. Results 2-3 match only some terms.

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
**Provider:** transfermarkt | **Category:** identity-surfaces | **Source:** curated by football-docs contributors | **Match:** partial

# Transfermarkt Identity Surfaces

Transfermarkt is primarily a public website, not an official public API.
Identity data comes from public entity pages, match reports, or licence-safe
community exports.

---

## [3] Other fields
**Provider:** transfermarkt | **Category:** identity-surfaces | **Source:** curated by football-docs contributors | **Match:** partial

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

No indexed doc matches every term, so these are partial matches. Check that they answer the question before relying on them.

## [1] Project use
**Provider:** free-sources | **Category:** understat | **Source:** curated by football-docs contributors | **Match:** partial

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
**Provider:** free-sources | **Category:** contextual-story-joins | **Source:** curated by football-docs contributors | **Match:** partial

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
**Provider:** free-sources | **Category:** overview | **Source:** curated by football-docs contributors | **Match:** partial

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
**Provider:** free-sources | **Category:** understat | **Source:** curated by football-docs contributors | **Match:** partial

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

No indexed doc matches every term, so these are partial matches. Check that they answer the question before relying on them.

## [1] Supported Sources
**Provider:** soccerdata | **Category:** overview | **Source:** curated by football-docs contributors | **Match:** partial

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
**Provider:** soccerdata | **Category:** data-sources | **Source:** curated by football-docs contributors | **Match:** partial

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
**Provider:** wyscout | **Category:** glossary-metrics-concepts | **Source:** crawled (https://dataglossary.wyscout.com/) | crawled 2026-06-03 | **Match:** partial

## Challenge intensity

A team metric, quantifying how many defensive actions (defensive duels, loose ball duels, interceptions, tackles) a team is doing per minute of opponent ball possession.

Challenge intensity reflects how often the team is actively trying to recover the ball when the opponent is in possession (thus, it's correlated to _PPDA_). The higher this number, the more intense the team is in challenges. In top five European leagues for 2018/2019 the average challenge intensity is 6.04. The best team in Challenge intensity in top five leagues 2018/2019 is Eibar with 7.7; Parma, Nürnberg and Angers have the least (5).

Source: [https://dataglossary.wyscout.com/challenge_intensity/](https://dataglossary.wyscout.com/challenge_intensity/)

---

## [4] Team Name Standardization
**Provider:** soccerdata | **Category:** usage | **Source:** curated by football-docs contributors | **Match:** partial

## Team Name Standardization

All scrapers apply `TEAMNAME_REPLACEMENTS` to normalize team names across sources. Add custom mappings in `~/soccerdata/config/teamname_replacements.json`:

```json
{
  "StandardName": ["Alternative1", "Alternative2"]
}
```
````

### s11 — search_docs {"query": "post-shot xG goalkeeper goals prevented", "max_results": 4}

````text
Found 4 result(s) for "post-shot xG goalkeeper goals prevented":

Results 1-1 match every term. Results 2-4 match only some terms.

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
**Provider:** statsbomb | **Category:** iq-metrics-glossary | **Source:** curated by football-docs contributors | **Match:** partial

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
**Provider:** statsbomb | **Category:** xg-model | **Source:** curated by football-docs contributors | **Match:** partial

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

## [4] Save
**Provider:** wyscout | **Category:** glossary-events | **Source:** crawled (https://dataglossary.wyscout.com/) | crawled 2026-06-03 | **Match:** partial

## Save

A successful attempt from the goalkeeper to prevent a shot from being scored.

![Save](https://dataglossary.wyscout.com/static/98a11b12170eee9c7de82f1cb068ca17/4c1ae/447632984.jpg)

_A save from Rui Patrício_

#### Details

- A save is tagged for all shots on target, even from medium and long distance. The difficult saves would be essentially [Reflexes saves](/reflex_save).

#### Attributes

#### xG: number

A pre-shot [xG value](/xg) of a probability of the current shot (not necessarily on target) to be scored.

#### xCG (xG2): number

The post-shot xG2 value of a probability of the current shot (guaranteed to be on target) to be scored.

Source: [https://dataglossary.wyscout.com/save/](https://dataglossary.wyscout.com/save/)
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

Results 1-2 match every term. Results 3-4 match only some terms.

## [1] ppda.wyscout: Wyscout
**Provider:** metric-cards | **Category:** ppda | **Source:** curated by football-docs contributors | crawled 2026-10-04

## ppda.wyscout: Wyscout

Opponent passes that start in the pressing team's final 60%, divided by the pressing team's fouls, interceptions, won defensive duels and sliding tackles there.

- **Formula:** opponent passes started in the final 60% / (fouls + interceptions + won defensive duels + sliding tackles) in the final 60%
- **Zone:** Pressing team's final 60%.
- **Passes counted:** All opponent passes that start in the zone; the page does not say whether failed passes count.
- **Source:** PPDA (Wyscout): https://dataglossary.wyscout.com/ppda/
- **Quote** (matches the source word for word, 2026-10-04): "we calculate all opponent passes that started there and divide them by the sum of defensive actions (fouls, interceptions, won defensive duels, sliding tackles) of the pressing team"
- **Reference code:** none yet.
- Lost duels do not count. Challenges and blocked passes are not in the list.
- The glossary's worked example: Liverpool v Manchester United, 20 October 2019, Liverpool 207 / (10 + 16 + 11 + 3) = 5.2.
- No reference implementation yet: the action list uses Wyscout's duel outcomes. The public Wyscout match event dataset (Pappalardo et al.) could carry one.

---

## [2] Event Type Reference
**Provider:** opta | **Category:** event-types | **Source:** curated by football-docs contributors

## Event Type Reference

Outcome rules are from F24 Appendix 8 unless the note says otherwise.

| typeId | Name | Outcome | Notes |
|--------|------|---------|-------|
| 1 | Pass | 0=miss, 1=success | Includes open play, goal kicks, corners, free kicks played as passes |
| 2 | Offside pass | always 1 | Receiving player called offside |
| 3 | Take on | 0=fail, 1=success | Dribble past opponent |
| 4 | Foul | 0=committed, 1=fouled | Events come in pairs (one per team) |
| 5 | Out | 0=put out, 1=gains possession | Ball out of play |
| 6 | Corner awarded | 0=conceded, 1=won | |
| 7 | Tackle | 0=fail, 1=wins ball | Legal ground-level challenge |
| 8 | Interception | always 1 | Intercepts opposition pass |
| 10 | Save | always 1 | GK prevents goal (also outfield with qual 94) |
| 11 | Claim | 0=drops, 1=catches | GK catches crossed ball |
| 12 | Clearance | always 1 | Defensive clearance |
| 13 | Miss | always 1 | Shot wide or over |
| 14 | Post | always 1 | Ball hits frame |
| 15 | Attempt saved | always 1 | Shot on target, saved |
| 16 | Goal | always 1 | Own goals have qualifier 28 |
| 17 | Card | always 1 | Yellow/second yellow/red via qualifiers 31/32/33 |
| 18 | Player off | always 1 | Substituted off |
| 19 | Player on | always 1 | Substituted on |
| 20 | Player retired | always 1 | Player leaves the pitch, for example injured, with no substitution. Not a red card |
| 21 | Player returns | always 1 | Player comes back on after leaving the pitch |
| 27 | Start delay | always 1 | Play stops for a delay. With qualifier 364, a VAR review |
| 28 | End delay | always 1 | The delay ends and play restarts |
| 30 | End | always 1 | End of a period. kloppy reads the period end time from it |
| 32 | Start | always 1 | Start of a period. kloppy reads the period start time from it |
| 34 | Team set up | always 1 | Formation/lineup event |
| 37 | Collection end | always 1 | |
| 40 | Formation change | always 1 | In-game formation change |
| 41 | Punch | always 1 | GK punches the ball |
| 42 | Good skill | always 1 | |
| 43 | Deleted event | always 1 | Opta removed this event. Drop it before analysis; kloppy does |
| 44 | Aerial | 0=lost, 1=won | Aerial duel. Events come in pairs |
| 45 | Challenge | always 0 | Unsuccessful tackle attempt |
| 49 | Ball recovery | always 1 | Player gathers loose ball |
| 50 | Dispossessed | always 1 | Loses ball via opponent tackle |
| 51 | Error | always 1 | Mistake losing ball |
| 52 | Keeper pick-up | always 1 | GK picks up ball |
| 54 | Smother | always 1 | GK covers ball at attacker's feet |
| 55 | Offside provoked | always 1 | Defender's position causes offside |
| 59 | Keeper sweeper | 0=possession goes to the other team, 1=kept or put out of play | GK comes off line to clear/claim |
| 61 | Ball touch | 0=lost control, 1=ball hit the player unintentionally | Bad touch / loss of control |
| 67 | 50/50 | 0=lost, 1=won | Two players contest loose ball. F24: not collected since 10 July 2023 |
| 74 | Blocked pass | always 1 | Player blocks an opponent's pass |
| 83 | Attempted tackle | not defined in F24 | Unsuccessful tackle |
| 84 | Deleted after review | — | An event deleted after a VAR review (from 1 March 2021). Qualifier 436 gives its typeId before deletion; a goal ruled out by VAR has 436 = `16` |

A dash means the outcome has not been checked for that type.

---

## [3] Defending
**Provider:** statsbomb | **Category:** player-match-stats | **Source:** curated by football-docs contributors | **Match:** partial

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

## [4] Defending
**Provider:** statsbomb | **Category:** player-season-stats | **Source:** curated by football-docs contributors | **Match:** partial

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
````

### s17 — search_docs {"query": "distance covered high speed running physical metrics", "max_results": 4}

````text
Found 4 result(s) for "distance covered high speed running physical metrics":

Results 1-3 match every term. Results 4-4 match only some terms.

## [1] Base metrics
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

## [2] Physical metrics
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
**Provider:** skillcorner | **Category:** concepts | **Source:** crawled (https://www.skillcorner.com/apidocs.json) | SkillCorner API (OpenAPI 3.1) | crawled 2026-08-31 | **Match:** partial

## Physical speed bands

Physical metrics bucket movement by intensity: **running**, **HSR** (High Speed Running), **sprint**, and **HI** (High Intensity = HSR + sprint). Acceleration/deceleration efforts are split into **medium** and **high**, with **explosive** accelerations that lead into HSR or a sprint tracked separately. **PSV-99** (Peak Sprint Velocity, 99th percentile) is an outlier-robust top-speed proxy. Exact km/h thresholds are in the glossary. See [physical-data.md](physical-data.md).
````

### s03 — search_docs {"query": "Catapult PlayerLoad high speed running export fields", "max_results": 5}

````text
Found 5 result(s) for "Catapult PlayerLoad high speed running export fields":

Catapult is not an indexed provider: Catapult's OpenField Connect API docs are public but not licensed for republishing, and the docs site disallows crawling (checked 2026-09-30). Impect, which Catapult owns, is indexed. Results below come from other providers and do not cover it.

No indexed doc matches every term, so these are partial matches. Check that they answer the question before relying on them. No indexed doc mentions "playerload". If the question is about that, it is not indexed.

## [1] DrillKpiV7 fields: distance in speed zones and high-speed running
**Provider:** statsports | **Category:** drill-kpi-metrics | **Source:** curated by football-docs contributors | crawled 2026-09-30 | **Match:** partial

## DrillKpiV7 fields: distance in speed zones and high-speed running

High-speed running (HSR) appears as `highSpeedRunningAbs`, `highSpeedRunningRel`, `hsrAbsPerMin` and `hsrRelPerMin`. The spec gives no speed threshold for high-speed running or for any zone `Z1` to `Z6`, and no unit.

| Field | Type | Format | In `DrillKpiV6` | In `DrillKpiV5` |
|---|---|---|---|---|
| `distanceZ1Rel` | `number` | `double` | yes | yes |
| `distanceZ2Rel` | `number` | `double` | yes | yes |
| `distanceZ3Rel` | `number` | `double` | yes | yes |
| `distanceZ4Rel` | `number` | `double` | yes | yes |
| `distanceZ5Rel` | `number` | `double` | yes | yes |
| `distanceZ6Rel` | `number` | `double` | yes | yes |
| `highSpeedRunningRel` | `number` | `double` | yes | yes |
| `hsrRelPerMin` | `number` | `double` | yes | yes |
| `distanceZ1Abs` | `number` | `double` | yes | yes |
| `distanceZ2Abs` | `number` | `double` | yes | yes |
| `distanceZ3Abs` | `number` | `double` | yes | yes |
| `distanceZ4Abs` | `number` | `double` | yes | yes |
| `distanceZ5Abs` | `number` | `double` | yes | yes |
| `distanceZ6Abs` | `number` | `double` | yes | yes |
| `highSpeedRunningAbs` | `number` | `double` | yes | yes |
| `hsrAbsPerMin` | `number` | `double` | yes | yes |
| `distanceZ2Z6Abs` | `number` | `double` | yes | yes |
| `distanceZ2Z6Rel` | `number` | `double` | yes | yes |
| `distanceZ3Z6Abs` | `number` | `double` | yes | yes |
| `distanceZ3Z6Rel` | `number` | `double` | yes | yes |
| `distanceZ4Z6Abs` | `number` | `double` | yes | yes |
| `distanceZ4Z6Rel` | `number` | `double` | yes | yes |

---

## [2] Tracking-derived off-ball runs recipe
**Provider:** kloppy | **Category:** tracking-rendering | **Source:** curated by football-docs contributors | **Match:** partial

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

## [3] Physical speed bands
**Provider:** skillcorner | **Category:** concepts | **Source:** crawled (https://www.skillcorner.com/apidocs.json) | SkillCorner API (OpenAPI 3.1) | crawled 2026-08-31 | **Match:** partial

## Physical speed bands

Physical metrics bucket movement by intensity: **running**, **HSR** (High Speed Running), **sprint**, and **HI** (High Intensity = HSR + sprint). Acceleration/deceleration efforts are split into **medium** and **high**, with **explosive** accelerations that lead into HSR or a sprint tracked separately. **PSV-99** (Peak Sprint Velocity, 99th percentile) is an outlier-robust top-speed proxy. Exact km/h thresholds are in the glossary. See [physical-data.md](physical-data.md).

---

## [4] Base metrics
**Provider:** skillcorner | **Category:** physical-data | **Source:** crawled (https://www.skillcorner.com/apidocs.json) | SkillCorner API (OpenAPI 3.1) | crawled 2026-08-31 | **Match:** partial

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

## [5] Player workload table recipe
**Provider:** skillcorner | **Category:** physical-data | **Source:** crawled (https://www.skillcorner.com/apidocs.json) | SkillCorner API (OpenAPI 3.1) | crawled 2026-08-31 | **Match:** partial

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
````

### s04 — search_docs {"query": "Catapult", "provider": "catapult"} — error

````text
Provider "catapult" is not indexed: Catapult's OpenField Connect API docs are public but not licensed for republishing, and the docs site disallows crawling (checked 2026-09-30). Impect, which Catapult owns, is indexed. Call list_providers for the providers that are.
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
| 1 | longBall | Intended long ball, including launches. F24 defines it by intent and gives no length threshold |
| 2 | cross | Cross (Q2). Corners commonly carry Q2 + Q6; free-kick crosses commonly carry Q2 + Q5; open-play crosses are Q2 without Q5/Q6. |
| 3 | headPass | Headed pass (Q3). Distinct from Q15, the headed shot qualifier. |
| 4 | throughBall | Through ball (Q4). Do not confuse with Q5 free-kick delivery. |
| 5 | freeKickTaken | Free kick pass / free-kick delivery (Q5), direct or indirect. |
| 6 | cornerTaken | Corner kick / corner delivery (Q6). |
| 107 | throwIn | Throw-in |
| 124 | goalKick | Goal kick pass. For goal-kick distribution charts, combine with pass end coordinates Q140/Q141. |
| 279 | kickOff | Kick-off pass. Value `S` is the kick-off that starts a period; `G` is the kick-off after a goal. |
| 7 | playersCaughtOffside | On an offside pass (typeId 2). The value is the ID of the player caught offside. It is not a goal-kick flag; goal kicks are Q124. |
| 154 | intentionalAssist | The assist was intentional: the passer meant the pass, with no deflection. It appears on the assisting pass and on the shot. For the pass that set up a shot use Q210; for an assisted shot use Q29 |
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
count typeId `16` goals (a goal that VAR rules out becomes typeId `84` and is not
counted), credit own goals with qualifier `28` to the opposing team, and sort by period-aware clock or `expandedMinute`. Count only
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
**firstbeat** (79 chunks): api-access (8), api-endpoints (22), data-model (29), data-provenance (3), identity-surfaces (4), variables (13) | aliases: firstbeat-sports, firstbeat-cloud-api, firstbeat-sports-cloud
**floodlight** (144 chunks): compendium-0-compendium (1), compendium-1-data (5), compendium-2-design (1), compendium-3-time (6), compendium-4-space (4), compendium-5-identifier (4), core-code (1), core-core (1), core-definitions (1), core-events (1), core-pitch (1), core-property (1), core-teamsheet (1), core-xy (1), guides-contrib-manual (21), guides-getting-started (29), guides-tutorial-analysis (13), guides-tutorial-matchsheets (6), index (2), io-datasets (13), io-dfl (1), io-io (1), io-kinexon (1), io-opta (1), io-secondspectrum (1), io-skillcorner (1), io-sportradar (1), io-statsbomb (1), io-statsperform (1), io-tracab (1), io-utils (1), metrics-entropy (1), metrics-metrics (1), metrics-trajectory-clustering (1), metrics-zone-aggregation (1), models-geometry (1), models-kinematics (1), models-kinetics (1), models-models (1), models-space (1), transforms-filter (1), transforms-interpolation (1), transforms-permutation (1), transforms-spatial (1), transforms-temporal (1), transforms-transforms (1), utils-types (1), utils-utils (1), vis-pitches (1), vis-positions (1), vis-vis (1) | aliases: kinexon
**fmdb-pro** (37 chunks): api-access (9), api-endpoints (8), data-model (9), data-provenance (2), identity-surfaces (9) | aliases: fmdb
**fotmob** (5 chunks): data-provenance (2), identity-surfaces (3)
**free-sources** (69 chunks): contextual-story-joins (8), data-provenance (8), fbref (5), football-data-columns (9), overview (12), understat (19), xg-timelines (8) | aliases: fbref, football-reference, understat, clubelo, club-elo, football-data, football-data-uk, football-data-co-uk, engsoccerdata, free, free-source
**hawkin-dynamics** (69 chunks): api-access (8), api-endpoints (16), data-model (22), data-provenance (3), identity-surfaces (5), test-metrics (15) | aliases: hawkin, hawkin-connect, hawkin-force-platform
**impect** (79 chunks): concepts (12), coordinate-system (10), data-model (17), data-provenance (2), event-types (16), identity-surfaces (9), kpi-definitions (4), overview (9)
**kloppy** (126 chunks): data-model (23), event-derived-metrics (13), provider-mapping (15), tracking-rendering (13), usage (62) | aliases: secondspectrum, second-spectrum
**metric-cards** (101 chunks): field_tilt (9), npxg (8), pass_completion (8), ppda (11), progressive_carries (10), progressive_passes (10), vaep (8), xa (7), xg (11), xg_assisted (10), xt (9) | aliases: metrics, metric, metric-card, methods
**mplsoccer** (65 chunks): overview (3), pitch-types (13), visualizations (49) | aliases: mpl-soccer
**opta** (73 chunks): api-access (8), charting-game-state (9), charting-lineups (6), charting-passmaps (6), charting-set-pieces (6), charting-shot-placement (10), coordinate-system (6), data-provenance (2), event-types (6), identity-surfaces (4), qualifiers (10) | aliases: statsperform, stats-perform, opta-f24, whoscored, who-scored
**reep** (29 chunks): api (7), data-provenance (2), download-duckdb-csv (9), identity-and-ids (6), overview (5) | aliases: reep-football
**skillcorner** (51 chunks): api-access (10), api-endpoints (8), concepts (6), coordinate-system (5), data-model (9), data-provenance (2), identity-surfaces (4), physical-data (7) | aliases: skill-corner
**socceraction** (34 chunks): spadl (12), vaep-xt (22) | aliases: soccer-action
**soccerdata** (40 chunks): data-sources (9), overview (5), usage (26) | aliases: soccer-data, sofascore, sofa-score
**soccerdonna** (5 chunks): data-provenance (2), identity-surfaces (3) | aliases: soccer-donna
**sportmonks** (568 chunks): api-access (27), api-changes (12), authentication (3), best-practices (8), changelog (38), changelog-beta (29), charting-season-stories (7), code-libraries (2), data-corrections (5), data-model (22), data-provenance (2), demo-response-files (8), differences-between-api-2-and-api-3 (2), endpoints (1), error-codes (34), event-types (23), filtering (2), filtering-and-complexity-exceptions (1), fixtures (3), get-all-fixtures (8), get-all-leagues (8), get-all-leagues-by-team-id (8), get-all-livescores (7), get-all-seasons (8), get-all-states (8), get-all-types (5), get-brackets-by-season-id (13), get-current-leagues-by-team-id (6), get-fixture-by-id (7), get-fixtures-by-date (8), get-fixtures-by-date-range (8), get-fixtures-by-date-range-for-team (7), get-fixtures-by-head-to-head (7), get-fixtures-by-multiple-ids (7), get-fixtures-by-search-by-name (8), get-inplay-livescores (6), get-latest-updated-fixtures (11), get-latest-updated-livescores (11), get-league-by-id (7), get-leagues-by-country-id (7), get-leagues-by-fixture-date (8), get-leagues-by-live (7), get-leagues-search-by-name (8), get-past-fixtures-by-tv-station-id (8), get-seasons-by-id (7), get-seasons-by-search-by-name (8), get-seasons-by-team-id (7), get-state-by-id (7), get-type-by-entity (1), get-type-by-id (5), get-upcoming-fixtures-by-market-id (8), get-upcoming-fixtures-by-tv-station-id (8), getting-started (6), identity-surfaces (4), include-exceptions (1), includes (4), leagues (13), livescores (1), making-your-first-request (9), meta-description (1), nested-includes (3), new-endpoints-and-data-features (4), ordering-and-sorting (3), other-exceptions (1), overview (1), rate-limit (2), request-options (1), seasons (3), selecting-and-filtering (1), selecting-fields (3), states (4), statistics (1), syntax (4), syntax-and-filters (6), translations-beta (5), types (1), what-can-you-do-with-sportmonks-data (10) | aliases: sport-monks
**sportradar** (481 chunks): api-access (6), api-endpoints (6), charting-and-stories (5), data-model (8), data-provenance (2), integration-notes (5), monitoring-data-changes (13), soccer-api-vs-soccer-extended-api (7), soccer-extended-competition-info (2), soccer-extended-competition-seasons (2), soccer-extended-competitions (3), soccer-extended-competitor-mappings (2), soccer-extended-competitor-merge-mappings (2), soccer-extended-competitor-profile (7), soccer-extended-competitor-schedules (16), soccer-extended-competitor-summaries (5), soccer-extended-competitor-vs-competitor (2), soccer-extended-daily-schedules (2), soccer-extended-daily-summaries (2), soccer-extended-faq (71), soccer-extended-fifa-rankings (3), soccer-extended-league-timeline (7), soccer-extended-live-schedules (2), soccer-extended-live-summaries (2), soccer-extended-live-timelines (3), soccer-extended-live-timelines-delta (2), soccer-extended-overview (11), soccer-extended-player-mappings (2), soccer-extended-player-merge-mappings (2), soccer-extended-player-profile (4), soccer-extended-player-schedules (2), soccer-extended-player-summaries (2), soccer-extended-push-events (12), soccer-extended-push-feeds (5), soccer-extended-push-statistics (10), soccer-extended-season-competitors (2), soccer-extended-season-form-standings (4), soccer-extended-season-info (9), soccer-extended-season-leaders (4), soccer-extended-season-lineups (5), soccer-extended-season-links (3), soccer-extended-season-missing-players (4), soccer-extended-season-overunder-statistics (3), soccer-extended-season-players (2), soccer-extended-season-schedule (3), soccer-extended-season-standings (4), soccer-extended-season-summaries (2), soccer-extended-season-transfers (4), soccer-extended-season-venues (2), soccer-extended-seasonal-competitor-extended-stati (6), soccer-extended-seasonal-competitor-players (3), soccer-extended-seasonal-competitor-statistics (5), soccer-extended-seasons (2), soccer-extended-seasons-disabled (2), soccer-extended-sport-event-extended-summary (5), soccer-extended-sport-event-extended-timeline (5), soccer-extended-sport-event-fun-facts (2), soccer-extended-sport-event-insights (2), soccer-extended-sport-event-lineups (2), soccer-extended-sport-event-momentum (3), soccer-extended-sport-event-summary (2), soccer-extended-sport-event-timeline (3), soccer-extended-sport-events-created (2), soccer-extended-sport-events-removed (2), soccer-extended-sport-events-updated (2), soccer-ig-api-basics (16), soccer-ig-data-coverage-tiers (7), soccer-ig-fixtures (9), soccer-ig-historical-data (6), soccer-ig-id-handling (18), soccer-ig-live-match-retrieval (12), soccer-ig-match-status-workflow (13), soccer-ig-overview (1), soccer-ig-push (13), soccer-ig-rosters-lineups-transfers (9), soccer-ig-scenarios (1), soccer-ig-seasonal-stats (7), soccer-ig-tracking-standings (16), soccer-ig-tracking-tournaments (11), soccer-ig-update-frequencies (6) | aliases: sport-radar, sportradar-api, soccer-extended, sportradar-soccer
**statsbomb** (244 chunks): api-access (38), api-endpoints (8), charting-lineups (6), coordinate-system (13), data-model (27), data-provenance (2), event-types (55), identity-surfaces (5), iq-metrics-glossary (14), player-mapping (6), player-match-stats (13), player-season-stats (12), team-match-stats (11), team-season-stats (11), xg-model (23) | aliases: stats-bomb, statsbomb-open-data, statsbomb-open
**statsports** (70 chunks): api-access (8), api-endpoints (6), data-model (29), data-provenance (3), drill-kpi-metrics (20), identity-surfaces (4) | aliases: statsports-sonra, sonra, apex, statsports-apex, statsports-pro-series
**thesportsdb** (20 chunks): api-access (6), api-endpoints (4), data-provenance (2), identity-surfaces (4), livescore (4) | aliases: tsdb, the-sports-db, the-sportsdb, sportsdb
**transfermarkt** (5 chunks): data-provenance (2), identity-surfaces (3)
**transferroom** (45 chunks): api-access (8), api-endpoints (12), charting-availability (5), data-model (9), data-provenance (2), identity-surfaces (9) | aliases: transfer-room
**unravelsports** (202 chunks): additional-citations (5), additional-license (6), american-football-dataset (2), american-football-graphs (1), api-american-football (1), api-classifiers (8), api-soccer (1), api-utils (1), generated-unravel-utils-add-dummy-label-column (1), generated-unravel-utils-add-graph-id-column (1), generated-unravel-utils-dummy-graph-ids (1), generated-unravel-utils-dummy-labels (1), getting-started-concepts (17), getting-started-installation (11), getting-started-quickstart (25), index (5), soccer-dataset (4), soccer-graphs (3), soccer-models (2), tutorials-american-football (15), tutorials-formation-detection (30), tutorials-pressing-intensity (21), tutorials-soccer-gnn (30), utils-features (2), utils-helpers (5), utils-objects (3) | aliases: unravel, unravel-sports, bigdatabowl, big-data-bowl
**vald** (318 chunks): api-access (8), api-endpoints (2), data-provenance (3), dynamo (31), forcedecks (58), forceframe (37), humantrak (30), identity-surfaces (5), nordbord (43), profiles (27), smartspeed (40), tenants (34) | aliases: vald-performance, vald-hub, forcedecks, nordbord, forceframe, smartspeed, vald-dynamo, humantrak, valdr
**wyscout** (165 chunks): api-access (11), api-endpoints (13), charting-analysis-metrics (7), coordinate-system (6), data-model (17), data-provenance (2), event-types (6), glossary-events (79), glossary-metrics-concepts (20), identity-surfaces (4) | aliases: hudl, hudl-wyscout

Data: built 2026-10-08T22:38:52.000Z from commit 39e342a (bundled).
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
**Indexed:** yes (244 chunks)
**Categories:** api-access (38), api-endpoints (8), charting-lineups (6), coordinate-system (13), data-model (27), data-provenance (2), event-types (55), identity-surfaces (5), iq-metrics-glossary (14), player-mapping (6), player-match-stats (13), player-season-stats (12), team-match-stats (11), team-season-stats (11), xg-model (23)
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
**Indexed:** yes (69 chunks)
**Categories:** contextual-story-joins (8), data-provenance (8), fbref (5), football-data-columns (9), overview (12), understat (19), xg-timelines (8)
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
  sofascore / player: 982780
  sportmonks / player: 28912747
  sportradar / player: sr:player:1737609
  statsbomb / offline_player: 39461
  transfermarkt / spieler: 568177
  uefa / player: 250124282
  whoscored / player: 395692
  worldfootball / person_numeric: 567392
  wyscout / player: 551497

Local register release: 20261005T180536Z (current).
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
  sofascore / player: 982780
  sportmonks / player: 28912747
  sportradar / player: sr:player:1737609
  statsbomb / offline_player: 39461
  transfermarkt / spieler: 568177
  uefa / player: 250124282
  whoscored / player: 395692
  worldfootball / person_numeric: 567392
  wyscout / player: 551497

Local register release: 20261005T180536Z (current).
````

### r02 — resolve_entity {"name": "Cole Palmer", "type": "player"}

````text
No Reep entity matches that query in the local register.

Local register release: 20261005T180536Z (current).
````

### r00 — resolve_entity {"provider": "transfermarkt", "namespace": "spieler", "id": "0"}

````text
No Reep entity matches that query in the local register.

Local register release: 20261005T180536Z (current).
````

### m01 — list_metrics {}

````text
# Metric cards (11)

## field_tilt: Field tilt

How much of a match's play in the final thirds belongs to one team: its passes (or touches) in its attacking third as a share of both teams' passes (or touches) in their attacking thirds.

- `field_tilt.stats-perform-2016`: Stats Perform, about 2016: final-third passes (reference code: approximation (football_metrics.territory:field_tilt_opta_passes on statsbomb-open-data))
- `field_tilt.opta-analyst`: Opta Analyst (2024): final-third passes (reference code: approximation (football_metrics.territory:field_tilt_opta_passes on statsbomb-open-data))
- `field_tilt.touches`: Final-third touches (Cannon Stats, 2023) (reference code: approximation (football_metrics.territory:field_tilt_touches on statsbomb-open-data))
- `field_tilt.driblab`: Driblab (2023): passes and touches in the last 35 m (reference code: none yet)

## npxg: npxG (non-penalty expected goals)

The quality of the chances a team or player creates without penalties: the xG total with penalty kicks taken out, so that a penalty, which every provider values at one fixed number, does not swamp the total.

- `npxg.statsbomb-hudl`: Hudl StatsBomb 'xG' (NP xG) (reference code: exact (football_metrics.xg:npxg_statsbomb_hudl on statsbomb-open-data))
- `npxg.fbref`: FBref (Opta values, penalty rebounds removed), historical to January 2026 (reference code: none yet)
- `npxg.understat`: Understat (NPxG) (reference code: none yet)

## pass_completion: Pass completion

How often a team's (or player's) passes reach a teammate: completed passes divided by attempted passes.

- `pass_completion.statsbomb-hudl`: Hudl StatsBomb (Passing%) (reference code: exact (football_metrics.territory:pass_completion_statsbomb_hudl on statsbomb-open-data))
- `pass_completion.opta`: Opta (reference code: approximation (football_metrics.territory:pass_completion_opta on statsbomb-open-data))
- `pass_completion.wyscout`: Wyscout (pass accuracy) (reference code: approximation (football_metrics.territory:pass_completion_wyscout on statsbomb-open-data))

## ppda: PPDA (passes allowed per defensive action)

How intensely a team presses the opponent's build-up: how many passes it lets the opponent make, in the pressing zone, for each defensive action it makes there.

- `ppda.trainor-2014`: Trainor (2014), the original (reference code: approximation (football_metrics.ppda:ppda_trainor_2014 on statsbomb-open-data))
- `ppda.statsbomb-hudl`: Hudl StatsBomb (reference code: exact (football_metrics.ppda:ppda_statsbomb_hudl on statsbomb-open-data))
- `ppda.wyscout`: Wyscout (reference code: none yet)
- `ppda.opta-analyst`: Opta Analyst (reference code: approximation (football_metrics.ppda:ppda_opta_analyst on statsbomb-open-data))
- `ppda.stats-perform-2016`: Stats Perform (Opta Pro), about 2016 (reference code: none yet)
- `ppda.understat`: Understat (reference code: none yet)

## progressive_carries: Progressive carries

How often a player or team moves the ball a long way towards the opponent's goal by running with it.

- `progressive_carries.wyscout`: Wyscout (progressive run) (reference code: approximation (football_metrics.progression:progressive_carries_wyscout on statsbomb-open-data))
- `progressive_carries.fbref-opta`: FBref (Opta data), historical (reference code: approximation (football_metrics.progression:progressive_carries_fbref on statsbomb-open-data))
- `progressive_carries.opta-analyst`: Opta Analyst (reference code: approximation (football_metrics.progression:progressive_carries_opta_analyst on statsbomb-open-data))
- `progressive_carries.stats-perform-2019`: Stats Perform (Peter Mckeever) (reference code: approximation (football_metrics.progression:progressive_carries_stats_perform_2019 on statsbomb-open-data))
- `progressive_carries.statsbomb-blog-2023`: Hudl StatsBomb blog (2023) (reference code: approximation (football_metrics.progression:progressive_carries_statsbomb_blog on statsbomb-open-data))

## progressive_passes: Progressive passes

How often a player or team moves the ball a long way towards the opponent's goal with a pass.

- `progressive_passes.wyscout`: Wyscout (reference code: approximation (football_metrics.progression:progressive_passes_wyscout on statsbomb-open-data))
- `progressive_passes.fbref-opta`: FBref (Opta data), historical (reference code: approximation (football_metrics.progression:progressive_passes_fbref on statsbomb-open-data))
- `progressive_passes.opta-analyst`: Opta Analyst (reference code: approximation (football_metrics.progression:progressive_passes_opta_analyst on statsbomb-open-data))
- `progressive_passes.asa`: American Soccer Analysis (John Muller's rule) (reference code: approximation (football_metrics.progression:progressive_passes_asa on statsbomb-open-data))
- `progressive_passes.statsbomb-blog-2023`: Hudl StatsBomb blog (2023) (reference code: approximation (football_metrics.progression:progressive_passes_statsbomb_blog on statsbomb-open-data))

## vaep: VAEP (valuing actions by estimating probabilities)

How much an on-the-ball action changes its team's chance of scoring soon minus its chance of conceding soon.

- `vaep.decroos-2019`: Decroos et al. (2019), the paper (reference code: none yet)
- `vaep.socceraction`: socceraction (KU Leuven), the reference implementation (reference code: none yet)
- `vaep.atomic`: Atomic-VAEP (reference code: none yet)

## xa: xA (expected assists, pass-level model)

How likely a player's or team's completed passes were to become goal assists, judged from the pass itself, whether or not a shot followed.

- `xa.opta`: Opta / Stats Perform (reference code: none yet)
- `xa.fbref`: FBref xA (Opta values), historical (reference code: none yet)

## xg: xG (expected goals)

The quality of the chances a team or player creates: each shot gets the probability, from a provider's model, that a shot like it is scored, and the card adds those probabilities up for a match, a season or a player.

- `xg.statsbomb-hudl`: Hudl StatsBomb, sum of shot values (penalties included) (reference code: exact (football_metrics.xg:xg_statsbomb_hudl on statsbomb-open-data))
- `xg.statsbomb-cumulative`: Hudl StatsBomb cumulative xG (one possession is worth at most one goal) (reference code: approximation (football_metrics.xg:xg_statsbomb_cumulative on statsbomb-open-data))
- `xg.fbref`: FBref (Opta values, possession-capped totals), historical to January 2026 (reference code: none yet)
- `xg.opta`: Opta (Stats Perform, The Analyst) (reference code: none yet)
- `xg.wyscout`: Wyscout (reference code: none yet)
- `xg.understat`: Understat (reference code: none yet)

## xg_assisted: xG assisted (xGAs, xAG; the shot-linked xA)

The quality of the chances a player or team creates for team-mates: the xG of each shot that their pass led to, credited to the passer.

- `xg_assisted.statsbomb-hudl`: Hudl StatsBomb (xG Assisted) (reference code: exact (football_metrics.xg_assisted:xg_assisted_statsbomb_hudl on statsbomb-open-data))
- `xg_assisted.fbref`: FBref xAG (expected assisted goals), historical (reference code: none yet)
- `xg_assisted.understat`: Understat (labelled xA) (reference code: none yet)
- `xg_assisted.wyscout`: Wyscout (labelled xA) (reference code: none yet)
- `xg_assisted.asa`: American Soccer Analysis (xAssists, xA) (reference code: none yet)

## xt: xT (expected threat)

How much a ball-progressing action (pass, cross or carry) raises the chance of scoring, from where the ball starts to where it ends, using a value for each zone of the pitch.

- `xt.singh-2019`: Singh (2019), the original (reference code: none yet)
- `xt.singh-open-12x8`: Singh's published 12 x 8 surface (reference code: approximation (football_metrics.xt:xt_singh_open_surface on statsbomb-open-data))
- `xt.socceraction`: socceraction (KU Leuven), fitted (reference code: none yet)
- `xt.databallpy`: DataBallPy (reference code: none yet)

Read a card or one variant with get_metric(id).
````

### m02 — get_metric {"id": "ppda"}

````text
# PPDA (passes allowed per defensive action)

Card `ppda`, version 1, updated 2026-10-04.

PPDA divides the opponent's passes by the pressing team's defensive actions, both counted in the part of the pitch where the pressing happens. Colin Trainor introduced it in 2014. At least five public definitions are in use, and they differ in the zone, in which defensive actions count, and in whether failed passes count. Values from different definitions are not comparable: on the 2022 World Cup final, Argentina's PPDA is 7.42 by the StatsBomb/Hudl formula and 9.77 by an approximation of Trainor's original.

- **Measures:** How intensely a team presses the opponent's build-up: how many passes it lets the opponent make, in the pressing zone, for each defensive action it makes there.
- **Direction:** Lower values mean more pressing. A team with no counted defensive action has no value (division by zero).
- **Unit:** passes per defensive action (a ratio)
- **Origin:** Colin Trainor, StatsBomb blog, 30 July 2014, building on his 'passes allowed per pressing action' ratios (9 October 2013), which counted the whole pitch. Wyscout's glossary also credits him with introducing it in 2014. He chose the zone with Rene Maric of Spielverlagerung. (https://blogarchive.statsbomb.com/articles/soccer/defensive-metrics-measuring-the-intensity-of-a-high-press/)

## Variants

- `ppda.trainor-2014`: Trainor (2014), the original. Pressing team's attacking 60% (Opta x > 40 of 100). Reference code: approximation (football_metrics.ppda:ppda_trainor_2014 on statsbomb-open-data).
- `ppda.statsbomb-hudl`: Hudl StatsBomb. Pressing team's attacking 60% (StatsBomb x >= 48 of 120). Reference code: exact (football_metrics.ppda:ppda_statsbomb_hudl on statsbomb-open-data).
- `ppda.wyscout`: Wyscout. Pressing team's final 60%. Reference code: none yet.
- `ppda.opta-analyst`: Opta Analyst. Outside the pressing team's own defensive third (about 67% of the pitch, not 60%). Reference code: approximation (football_metrics.ppda:ppda_opta_analyst on statsbomb-open-data).
- `ppda.stats-perform-2016`: Stats Perform (Opta Pro), about 2016. Opponent's defensive 3/5 (the same 60% as Trainor). Reference code: none yet.
- `ppda.understat`: Understat. The opposition half (50% of the pitch, not 60%). Reference code: none yet.

## ppda.trainor-2014: Trainor (2014), the original

All opposition passes, completed or not, divided by the pressing team's tackles, interceptions, challenges (failed tackles) and fouls, both counted beyond Opta's x = 40 line in the pressing team's direction: its attacking 60% of the pitch.

- **Formula:** opponent passes (x > 40 of 100, pressing team's view) / (tackles + interceptions + challenges + fouls by the pressing team at x > 40)
- **Zone:** Pressing team's attacking 60% (Opta x > 40 of 100).
- **Passes counted:** All passes, completed or not: Trainor says it does not matter whether the opposition completed them.
- **Source:** Defensive Metrics: Measuring the Intensity of a High Press (Colin Trainor, 2014-07-30): https://blogarchive.statsbomb.com/articles/soccer/defensive-metrics-measuring-the-intensity-of-a-high-press/
- **Quote** (exact, checked 2026-10-04): "PPDA = Number of Passes made by Attacking Team / Number of Defensive Actions"
- **Reference code:** approximation (football_metrics.ppda:ppda_trainor_2014 on statsbomb-open-data)
- **Mapping:** An approximation on StatsBomb events of a definition written for Opta events: tackle = Duel of type Tackle (any outcome), challenge = Dribbled Past, interception = Interception, foul = Foul Committed; Opta x > 40 of 100 = StatsBomb x > 48 of 120.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 9.7674
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 11.7317
- Trainor plots a 6-game rolling average of match values and also gives league and season tables.
- He tested the boundary at x = 33, 40 and 50 before choosing 40.

## ppda.statsbomb-hudl: Hudl StatsBomb

The opponent's completed passes in its own 60% of the pitch, divided by the pressing team's tackles, interceptions (including interceptions made with a pass), dribbled-past events and fouls outside its own defending 40%.

- **Formula:** opposition passes with pass outcome = completed and start x < 72 / pressing team's (tackle or interception (including pass type = interception) or dribbled past or foul) with x >= 48 (StatsBomb 120 x 80 pitch)
- **Zone:** Pressing team's attacking 60% (StatsBomb x >= 48 of 120).
- **Passes counted:** Completed passes only.
- **Source:** Passes Per Defensive Action (PPDA) (Hudl StatsBomb): https://support.hudl.com/s/article/passes-defensive-action
- **Quote** (browser, checked 2026-10-04): "Count of opposition event name = pass and pass outcome = completed and start_location_x<72/count of (event_name = tackle or interception (including pass type = interception) or dribbled past or foul) and event_x>=48"
- **Quote check note:** The page builds its text with JavaScript, so match_quote cannot read it; checked word for word in a browser.
- **Reference code:** exact (football_metrics.ppda:ppda_statsbomb_hudl on statsbomb-open-data)
- **Mapping:** The source's own formula on the source's own event data.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 7.4222
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 9.0909
- Hudl's prose description also lists blocks, but its exact formula does not; this variant follows the formula.
- The formula counts interceptions made with a pass (pass type Interception). On the 2022 World Cup final that adds 2 actions for Argentina and moves its PPDA from 7.77 to 7.42.
- StatsBomb's IQ season value (team_season_ppda) exists; whether it is a ratio of sums or a mean of match values is not stated.

## ppda.wyscout: Wyscout

Opponent passes that start in the pressing team's final 60%, divided by the pressing team's fouls, interceptions, won defensive duels and sliding tackles there.

- **Formula:** opponent passes started in the final 60% / (fouls + interceptions + won defensive duels + sliding tackles) in the final 60%
- **Zone:** Pressing team's final 60%.
- **Passes counted:** All opponent passes that start in the zone; the page does not say whether failed passes count.
- **Source:** PPDA (Wyscout): https://dataglossary.wyscout.com/ppda/
- **Quote** (exact, checked 2026-10-04): "we calculate all opponent passes that started there and divide them by the sum of defensive actions (fouls, interceptions, won defensive duels, sliding tackles) of the pressing team"
- **Reference code:** none yet
- Lost duels do not count. Challenges and blocked passes are not in the list.
- The glossary's worked example: Liverpool v Manchester United, 20 October 2019, Liverpool 207 / (10 + 16 + 11 + 3) = 5.2.
- No reference implementation yet: the action list uses Wyscout's duel outcomes. The public Wyscout match event dataset (Pappalardo et al.) could carry one.

## ppda.opta-analyst: Opta Analyst

Opposition passes outside the pressing team's own defensive third, divided by the pressing team's fouls, tackles, interceptions, challenges and blocked passes outside its own defensive third.

- **Formula:** opposition passes outside the pressing team's defensive third / (fouls + tackles + interceptions + challenges + blocked passes) outside that third
- **Zone:** Outside the pressing team's own defensive third (about 67% of the pitch, not 60%).
- **Passes counted:** Not stated.
- **Source:** Opta football stats definitions (Opta Analyst): https://theanalyst.com/articles/opta-football-stats-definitions
- **Quote** (exact, checked 2026-10-04): "In our PPDA calculation, the defensive actions are fouls, tackles, interceptions, challenges, and blocked passes."
- **Reference code:** approximation (football_metrics.ppda:ppda_opta_analyst on statsbomb-open-data)
- **Mapping:** An approximation on StatsBomb events: blocked pass = Block (which also covers blocked shots), challenge = Dribbled Past, tackle = Duel of type Tackle; outside the defensive third = x > 40 of 120 for the pressing team. All passes are counted, as the page does not say.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 6.8116
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 8.9661
- Adds blocked passes to Trainor's four actions. The page shows no date, so when this wording started is not known.

## ppda.stats-perform-2016: Stats Perform (Opta Pro), about 2016

Opponent passes allowed per defensive action in the opponent's defensive three-fifths of the pitch, deferring to Trainor for the details.

- **Formula:** as ppda.trainor-2014
- **Zone:** Opponent's defensive 3/5 (the same 60% as Trainor).
- **Passes counted:** As Trainor.
- **Source:** How we measure pressure (Stats Perform): https://www.statsperform.com/insights/how-we-measure-pressure/
- **Quote** (normalised, checked 2026-10-04): "Opponent passes allowed per defensive action, in the opponent's defensive 3/5ths of the pitch"
- **Reference code:** none yet
- The page now shows a 2026 date but uses 2015/16 data, so it was republished; the original date and author are not known.

## ppda.understat: Understat

Passes allowed per defensive action in the opposition half.

- **Formula:** opponent passes in the opposition half / defensive actions in the opposition half
- **Zone:** The opposition half (50% of the pitch, not 60%).
- **Passes counted:** Not stated.
- **Source:** Understat league page script (column tooltips) (Understat): https://understat.com/js/league.min.js
- **Quote** (exact, checked 2026-10-04): "Passes allowed per defensive action in the opposition half"
- **Quote check note:** The tooltip text is in the page's script, not its HTML.
- **Reference code:** none yet
- The page does not list which defensive actions count.
- Understat's data hold ppda.att and ppda.def per match; its season value is the sum of att divided by the sum of def (a ratio of sums, not a mean of match values).
- OPPDA is the same measure for the opponent's pressing against this team.


## Caveats

- Values from different definitions are not comparable: zone, actions and pass counting all change the number. Cite the variant ID.
- No public definition counts ball recoveries as a defensive action. A formula that does (for example in the opposition half) is a house variant and gives much lower values.
- PPDA measures the high press only; a team that presses in its own half looks passive.
- Possession and territory confound it: a dominant team's defensive actions happen high up the pitch anyway.
- Every variant counts fouls, which end a possession but are not pressing.
- Game state, red cards and the scoreline change pressing; Trainor smooths match values with a 6-game rolling mean.
- A season value can be a ratio of sums (Understat) or a mean of match values; they differ.

Related: field_tilt, pressures (no card yet), defensive_action_height (no card yet).

Cite a value with the exact variant ID: values from different variants are not comparable.
````

### m03 — get_metric {"id": "ppda.statsbomb-hudl"}

````text
# PPDA (passes allowed per defensive action)

Card `ppda`, version 1, updated 2026-10-04.

PPDA divides the opponent's passes by the pressing team's defensive actions, both counted in the part of the pitch where the pressing happens. Colin Trainor introduced it in 2014. At least five public definitions are in use, and they differ in the zone, in which defensive actions count, and in whether failed passes count. Values from different definitions are not comparable: on the 2022 World Cup final, Argentina's PPDA is 7.42 by the StatsBomb/Hudl formula and 9.77 by an approximation of Trainor's original.

- **Measures:** How intensely a team presses the opponent's build-up: how many passes it lets the opponent make, in the pressing zone, for each defensive action it makes there.
- **Direction:** Lower values mean more pressing. A team with no counted defensive action has no value (division by zero).
- **Unit:** passes per defensive action (a ratio)
- **Origin:** Colin Trainor, StatsBomb blog, 30 July 2014, building on his 'passes allowed per pressing action' ratios (9 October 2013), which counted the whole pitch. Wyscout's glossary also credits him with introducing it in 2014. He chose the zone with Rene Maric of Spielverlagerung. (https://blogarchive.statsbomb.com/articles/soccer/defensive-metrics-measuring-the-intensity-of-a-high-press/)

## ppda.statsbomb-hudl: Hudl StatsBomb

The opponent's completed passes in its own 60% of the pitch, divided by the pressing team's tackles, interceptions (including interceptions made with a pass), dribbled-past events and fouls outside its own defending 40%.

- **Formula:** opposition passes with pass outcome = completed and start x < 72 / pressing team's (tackle or interception (including pass type = interception) or dribbled past or foul) with x >= 48 (StatsBomb 120 x 80 pitch)
- **Zone:** Pressing team's attacking 60% (StatsBomb x >= 48 of 120).
- **Passes counted:** Completed passes only.
- **Source:** Passes Per Defensive Action (PPDA) (Hudl StatsBomb): https://support.hudl.com/s/article/passes-defensive-action
- **Quote** (browser, checked 2026-10-04): "Count of opposition event name = pass and pass outcome = completed and start_location_x<72/count of (event_name = tackle or interception (including pass type = interception) or dribbled past or foul) and event_x>=48"
- **Quote check note:** The page builds its text with JavaScript, so match_quote cannot read it; checked word for word in a browser.
- **Reference code:** exact (football_metrics.ppda:ppda_statsbomb_hudl on statsbomb-open-data)
- **Mapping:** The source's own formula on the source's own event data.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 7.4222
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 9.0909
- Hudl's prose description also lists blocks, but its exact formula does not; this variant follows the formula.
- The formula counts interceptions made with a pass (pass type Interception). On the 2022 World Cup final that adds 2 actions for Argentina and moves its PPDA from 7.77 to 7.42.
- StatsBomb's IQ season value (team_season_ppda) exists; whether it is a ratio of sums or a mean of match values is not stated.

Other variants: ppda.trainor-2014, ppda.wyscout, ppda.opta-analyst, ppda.stats-perform-2016, ppda.understat.

## Caveats

- Values from different definitions are not comparable: zone, actions and pass counting all change the number. Cite the variant ID.
- No public definition counts ball recoveries as a defensive action. A formula that does (for example in the opposition half) is a house variant and gives much lower values.
- PPDA measures the high press only; a team that presses in its own half looks passive.
- Possession and territory confound it: a dominant team's defensive actions happen high up the pitch anyway.
- Every variant counts fouls, which end a possession but are not pressing.
- Game state, red cards and the scoreline change pressing; Trainor smooths match values with a 6-game rolling mean.
- A season value can be a ratio of sums (Understat) or a mean of match values; they differ.

Related: field_tilt, pressures (no card yet), defensive_action_height (no card yet).

Cite a value with the exact variant ID: values from different variants are not comparable.
````

### m04 — get_metric {"id": "ppda.trainor-2014"}

````text
# PPDA (passes allowed per defensive action)

Card `ppda`, version 1, updated 2026-10-04.

PPDA divides the opponent's passes by the pressing team's defensive actions, both counted in the part of the pitch where the pressing happens. Colin Trainor introduced it in 2014. At least five public definitions are in use, and they differ in the zone, in which defensive actions count, and in whether failed passes count. Values from different definitions are not comparable: on the 2022 World Cup final, Argentina's PPDA is 7.42 by the StatsBomb/Hudl formula and 9.77 by an approximation of Trainor's original.

- **Measures:** How intensely a team presses the opponent's build-up: how many passes it lets the opponent make, in the pressing zone, for each defensive action it makes there.
- **Direction:** Lower values mean more pressing. A team with no counted defensive action has no value (division by zero).
- **Unit:** passes per defensive action (a ratio)
- **Origin:** Colin Trainor, StatsBomb blog, 30 July 2014, building on his 'passes allowed per pressing action' ratios (9 October 2013), which counted the whole pitch. Wyscout's glossary also credits him with introducing it in 2014. He chose the zone with Rene Maric of Spielverlagerung. (https://blogarchive.statsbomb.com/articles/soccer/defensive-metrics-measuring-the-intensity-of-a-high-press/)

## ppda.trainor-2014: Trainor (2014), the original

All opposition passes, completed or not, divided by the pressing team's tackles, interceptions, challenges (failed tackles) and fouls, both counted beyond Opta's x = 40 line in the pressing team's direction: its attacking 60% of the pitch.

- **Formula:** opponent passes (x > 40 of 100, pressing team's view) / (tackles + interceptions + challenges + fouls by the pressing team at x > 40)
- **Zone:** Pressing team's attacking 60% (Opta x > 40 of 100).
- **Passes counted:** All passes, completed or not: Trainor says it does not matter whether the opposition completed them.
- **Source:** Defensive Metrics: Measuring the Intensity of a High Press (Colin Trainor, 2014-07-30): https://blogarchive.statsbomb.com/articles/soccer/defensive-metrics-measuring-the-intensity-of-a-high-press/
- **Quote** (exact, checked 2026-10-04): "PPDA = Number of Passes made by Attacking Team / Number of Defensive Actions"
- **Reference code:** approximation (football_metrics.ppda:ppda_trainor_2014 on statsbomb-open-data)
- **Mapping:** An approximation on StatsBomb events of a definition written for Opta events: tackle = Duel of type Tackle (any outcome), challenge = Dribbled Past, interception = Interception, foul = Foul Committed; Opta x > 40 of 100 = StatsBomb x > 48 of 120.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 9.7674
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 11.7317
- Trainor plots a 6-game rolling average of match values and also gives league and season tables.
- He tested the boundary at x = 33, 40 and 50 before choosing 40.

Other variants: ppda.statsbomb-hudl, ppda.wyscout, ppda.opta-analyst, ppda.stats-perform-2016, ppda.understat.

## Caveats

- Values from different definitions are not comparable: zone, actions and pass counting all change the number. Cite the variant ID.
- No public definition counts ball recoveries as a defensive action. A formula that does (for example in the opposition half) is a house variant and gives much lower values.
- PPDA measures the high press only; a team that presses in its own half looks passive.
- Possession and territory confound it: a dominant team's defensive actions happen high up the pitch anyway.
- Every variant counts fouls, which end a possession but are not pressing.
- Game state, red cards and the scoreline change pressing; Trainor smooths match values with a 6-game rolling mean.
- A season value can be a ratio of sums (Understat) or a mean of match values; they differ.

Related: field_tilt, pressures (no card yet), defensive_action_height (no card yet).

Cite a value with the exact variant ID: values from different variants are not comparable.
````

### m05 — get_metric {"id": "xa"}

````text
# xA (expected assists, pass-level model)

Card `xa`, version 1, updated 2026-10-04.

Opta / Stats Perform's expected assists (xA) is a pass-level model: every completed pass gets the probability that it becomes a goal assist, from the type of pass, the pattern of play, where the pass starts and ends, and its distance. A pass earns xA even if the receiver never shoots. This card is ONLY that pass-level metric. The same name, xA, is also used for the xG of the shot that a pass led to (Understat, Wyscout, American Soccer Analysis, and FBref before October 2022); that shot-linked metric is card `xg_assisted`, and the two are not comparable. Opta's model is closed and StatsBomb open data has no xA field, so this card has no reference code.

- **Measures:** How likely a player's or team's completed passes were to become goal assists, judged from the pass itself, whether or not a shot followed.
- **Direction:** Higher values mean the passes were more likely to become assists. Comparing xA with actual assists shows over- or under-performance.
- **Unit:** expected assists: a probability from 0 to 1 per completed pass, summed over passes
- **Origin:** Stats Perform (Opta). The earliest public description found is The Analyst's article 'What Are Expected Assists (xA)?' by Jonny Whitmore, 24 March 2021, which presents Stats Perform's xA model. Whether Opta used a pass-level xA before that date is not known. The name xA was already in use for the shot-linked metric (card xg_assisted) by 2018. (https://theanalyst.com/articles/what-are-expected-assists-xa)

## Variants

- `xa.opta`: Opta / Stats Perform. Whole pitch. Reference code: none yet.
- `xa.fbref`: FBref xA (Opta values), historical. Whole pitch. Reference code: none yet.

## xa.opta: Opta / Stats Perform

For every completed pass, the probability that it becomes a goal assist, from a logistic regression built on hundreds of thousands of passes from historical Opta data. A player's or team's xA is the sum over its completed passes.

- **Formula:** xA(pass) = P(the completed pass becomes a goal assist | type of pass, pattern of play, location where the pass is received, location where the pass is made from, distance of the pass); xA(player) = sum of xA over the player's completed passes
- **Zone:** Whole pitch.
- **Passes counted:** Every completed pass in Stats Perform's event data, whether or not a shot follows.
- **Source:** What Are Expected Assists (xA)? (Jonny Whitmore (The Analyst, Stats Perform), 2021-03-24): https://theanalyst.com/articles/what-are-expected-assists-xa
- **Quote** (exact, checked 2026-10-04): "Stats Perform’s expected assists (xA) model measures the likelihood that a given pass will become a goal assist. The model rewards players who pass into dangerous areas, regardless of whether the receiver takes a shot or not."
- **Reference code:** none yet
- The inputs named as the most important: type of pass (for example cross, non-cross, header, through ball), pattern of play (for example open play, corner, free kick, throw-in), location where the pass is received, location where the pass is made from, and distance of the pass.
- Pattern of play and type of pass matter most, so the model has sub-models for the interactions between them.
- The scale runs from 0 (a pass that will never become an assist) to 1 (a pass the receiver would score from every time).
- Example in the article: in the 2019-20 Premier League, Trent Alexander-Arnold had 7.1 open-play xA and Andy Robertson 4.9, but Robertson made more open-play assists (10 against 6).
- Opta Analyst's stats definitions page gives the shorter form: xA for a completed pass from the type of pass, end-point and length of pass.
- No reference code: the model is closed and StatsBomb open data has no xA field.

## xa.fbref: FBref xA (Opta values), historical

Opta's xA as published on FBref from October 2022: the likelihood that a completed pass becomes a goal assist, from the type of pass, its location on the pitch, the phase of play and the distance covered.

- **Formula:** as xa.opta (FBref showed Opta's values)
- **Zone:** Whole pitch.
- **Passes counted:** Every completed pass, whether or not a shot followed.
- **Source:** Expected Goals Model Explained (FBref (Sports Reference)): https://web.archive.org/web/20251031052137/https://fbref.com/en/expected-goals-model-explained/
- **Quote** (exact, checked 2026-10-04): "Players receive xA for every completed pass regardless of whether a shot occurred or not."
- **Reference code:** none yet
- Before October 2022 FBref used the label xA for the shot-linked metric (card xg_assisted). When it switched its data provider to Opta it renamed that metric xAG and used xA for Opta's pass-level values.
- Historical: FBref removed its Opta advanced data on 20 January 2026 (Sports Reference blog), so these values are no longer published there. The source is a Wayback Machine snapshot.
- No reference code: the values come from Opta's closed model.


## Caveats

- This is not card xg_assisted. Many sites label the shot-linked metric (the xG of the shot after a pass) xA. Check which one a number is before you compare it.
- xA is a closed model output: Opta names the inputs but not the weights, so nobody else can reproduce the values.
- Only completed passes get xA. A failed pass into a dangerous area earns nothing.
- The public description lists only the most important inputs, so the full feature set is not known.
- Passes into dangerous areas earn xA even when nobody shoots, so xA and xG assisted can rank the same players differently.

Related: xg_assisted, xg, npxg, key_passes (no card yet).

Cite a value with the exact variant ID: values from different variants are not comparable.
````

### m06 — get_metric {"id": "xg_assisted"}

````text
# xG assisted (xGAs, xAG; the shot-linked xA)

Card `xg_assisted`, version 1, updated 2026-10-04.

xG assisted credits the passer with the xG of the shot that the pass led directly to (the key pass or shot assist). It is a shot-linked metric: no shot, no credit, and the value is the shooter's xG, so it depends on the provider's xG model. Many sites call it xA, but it is NOT the pass-level expected assists model of Opta / Stats Perform, which values every completed pass whether or not a shot follows; that metric is card `xa`. FBref renamed its version from xA to xAG in October 2022 when it switched to Opta. On the 2022 World Cup final (StatsBomb open data), Argentina's xG assisted is 1.34 from 15 assisted shots and France's is 0.57 from 4.

- **Measures:** The quality of the chances a player or team creates for team-mates: the xG of each shot that their pass led to, credited to the passer.
- **Direction:** Higher values mean the passes set up more and better shots. A pass that no shot follows earns nothing.
- **Unit:** expected goals (xG), summed over the assisted shots
- **Origin:** The first use of the name is not known. By 30 September 2018 Thom Lawrence of StatsBomb could describe xA as a basic metric that credits creative players who make key passes, so this shot-linked meaning was in use before Stats Perform published its pass-level xA (card xa) in March 2021. (https://www.hudl.com/blog/introducing-xgchain-and-xgbuildup)

## Variants

- `xg_assisted.statsbomb-hudl`: Hudl StatsBomb (xG Assisted). Whole pitch. Reference code: exact (football_metrics.xg_assisted:xg_assisted_statsbomb_hudl on statsbomb-open-data).
- `xg_assisted.fbref`: FBref xAG (expected assisted goals), historical. Whole pitch. Reference code: none yet.
- `xg_assisted.understat`: Understat (labelled xA). Whole pitch. Reference code: none yet.
- `xg_assisted.wyscout`: Wyscout (labelled xA). Whole pitch. Reference code: none yet.
- `xg_assisted.asa`: American Soccer Analysis (xAssists, xA). Whole pitch. Reference code: none yet.

## xg_assisted.statsbomb-hudl: Hudl StatsBomb (xG Assisted)

For each player, the sum of the StatsBomb xG of the shots that the player assisted, that is, the shots whose key pass the player made.

- **Formula:** Count of shot _xG for shots that the player assisted (team value: the sum over the team's players)
- **Zone:** Whole pitch.
- **Passes counted:** Every pass linked to a shot as its key pass (open play and set pieces). Penalties have no key pass and add nothing; Hudl's xG is non-penalty anyway.
- **Source:** Event Data Glossary: Player Metrics (Hudl StatsBomb): https://support.hudl.com/s/article/event-data-glossary-player-metrics
- **Quote** (browser, checked 2026-10-04): "xG assisted. This is calculated from the expected goal value of the assisted shot."
- **Quote check note:** The page builds its text with JavaScript, so match_quote cannot read it; checked word for word in a browser. The formula 'Count of shot _xG for shots that the player assisted' was checked the same way.
- **Reference code:** exact (football_metrics.xg_assisted:xg_assisted_statsbomb_hudl on statsbomb-open-data)
- **Mapping:** The source's own definition on the source's own event data: an assisted shot is a Shot with shot.key_pass_id, its value is shot.statsbomb_xg, and the credit goes to the team (and player) of the linked Pass. The penalty shoot-out (period 5) is excluded; extra time counts.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 1.3397
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 0.5687
- The glossary short name is xG Assisted and the abbreviation xGAs.
- Hudl also lists Open Play xG Assisted (OPxGAs, for events not from a set piece) and Set Piece xG Assisted (SPxGAs, for events from a set piece), and xG & xG Assisted (xG+xGAs). The glossary does not say which StatsBomb field decides 'from set piece', so these splits have no reference code.
- On the 2022 World Cup final the team values are the sum of shot.statsbomb_xg over 15 assisted shots for Argentina and 4 for France. The same totals come from the pass side (pass.assisted_shot_id) and from all xG minus the xG of shots with no key pass.
- Player values for the same match: Alexis Mac Allister 0.3034 (his assist for Di María's goal), Di María 0.2781, Messi 0.2742; for France, Ibrahima Konaté 0.2775 and Marcus Thuram 0.1017 (his assist for Mbappé's second goal). The module's xg_assisted_by_player function gives them.

## xg_assisted.fbref: FBref xAG (expected assisted goals), historical

The xG of the shot that follows a completed pass, credited to the passer. FBref used Opta's xG.

- **Formula:** sum of Opta xG over the shots that directly follow the player's completed passes
- **Zone:** Whole pitch.
- **Passes counted:** Only completed passes that a shot follows.
- **Source:** Expected Goals Model Explained (FBref (Sports Reference)): https://web.archive.org/web/20251031052137/https://fbref.com/en/expected-goals-model-explained/
- **Quote** (exact, checked 2026-10-04): "Players receive xAG only when a shot is taken after a completed pass."
- **Reference code:** none yet
- FBref called this metric xA until October 2022. When it switched its data provider to Opta it renamed it xAG and used xA for Opta's pass-level model (card xa).
- FBref also showed npxG + xAG and per-90 versions (xAG/90).
- Historical: FBref removed its Opta advanced data on 20 January 2026 (Sports Reference blog), so these values are no longer published there. The source is a Wayback Machine snapshot.
- No reference code: the value uses Opta's xG model, which is not in StatsBomb open data.

## xg_assisted.understat: Understat (labelled xA)

The sum of the Understat xG of the shots that came from a player's key passes.

- **Formula:** sum of Understat xG over the shots from the player's key passes
- **Zone:** Whole pitch.
- **Passes counted:** Key passes (passes that lead to a shot). The tooltip does not say how set pieces or penalties are treated; a penalty has no key pass.
- **Source:** Understat league table (column tooltips) (Understat): https://understat.com/league/EPL
- **Quote** (browser, checked 2026-10-04): "The sum of Expected Goals of shots from a player's key passes"
- **Quote check note:** The tooltip is a title attribute that the page's script builds, so match_quote cannot read it; checked word for word in a browser.
- **Reference code:** none yet
- Understat labels this column xA. It is not Opta's pass-level xA.
- No reference code: the value uses Understat's own xG model, which is not in StatsBomb open data.

## xg_assisted.wyscout: Wyscout (labelled xA)

The xA value of a pass is the xG of the shot that the pass led to. The pass must be a shot assist.

- **Formula:** xA of a pass = Wyscout xG of the shot that the pass led to; a player's xA is the sum over the player's shot assists
- **Zone:** Whole pitch.
- **Passes counted:** Shot assists: regular passes, crosses, corners, throw-ins and passes from free kicks that a shot follows.
- **Source:** xA (Wyscout): https://dataglossary.wyscout.com/xa/
- **Quote** (exact, checked 2026-10-04): "Expected assist (xA) value for a pass is the value of expected goals (xG) of the shot that this pass led to."
- **Reference code:** none yet
- Fouls suffered that lead to penalties or direct free kicks earn no xA, as goals from them do not count as assisted.
- A pass to an offside player is an unsuccessful pass and has no xA, even if a goal follows. The same applies after a VAR-found foul or offside.
- Wyscout labels this xA. It is not Opta's pass-level xA.
- No reference code: the value uses Wyscout's own xG model, which is not in StatsBomb open data.

## xg_assisted.asa: American Soccer Analysis (xAssists, xA)

The xG of all the shots for which a player made the pass, using ASA's own xG model.

- **Formula:** sum of ASA xG over the shots whose key pass the player made
- **Zone:** Whole pitch.
- **Passes counted:** Key passes, which ASA defines as passes that lead directly to a shot.
- **Source:** Expected goals explanation (American Soccer Analysis): https://www.americansocceranalysis.com/explanation
- **Quote** (exact, checked 2026-10-04): "You will now find a new stat on the players page: xAssists. These measure the Expected Goals value of all shots for which a particular player passed the ball."
- **Reference code:** none yet
- ASA's xG model is a logistic regression with separate models for teams, shooters and goalkeepers.
- The page is undated. Its example credits Latif Blessing with 0.762 xA for a pass to a Christian Ramirez shot worth 0.762 xG that did not score.
- No reference code: the value uses ASA's own xG model, which is not in StatsBomb open data.


## Caveats

- This is not card xa. Understat, Wyscout and American Soccer Analysis label this metric xA, and FBref did until October 2022; Opta's xA is a pass-level model. Check which one a number is before you compare it.
- The value is the shooter's xG, so it depends on the provider's xG model and on what the receiver does after the pass, not only on the pass.
- Penalties have no key pass, so penalty xG never counts. A foul won that leads to a penalty or a direct free kick earns nothing (Wyscout says so explicitly).
- Rebounds and other shots with no linked key pass earn no xG assisted for anyone. On the 2022 World Cup final, Messi's extra-time goal (0.49 xG) has no key pass.
- Set-piece deliveries (corners, free-kick passes, throw-ins) count unless a variant splits them out; Hudl StatsBomb has separate open-play and set-piece versions.

Related: xa, xg, npxg, key_passes (no card yet).

Cite a value with the exact variant ID: values from different variants are not comparable.
````

### m07 — get_metric {"id": "npxg"}

````text
# npxG (non-penalty expected goals)

Card `npxg`, version 1, updated 2026-10-04.

npxG is xG without penalty kicks. It is a filter on the xg card, so the provider's model still sets each shot's value. Two traps: Hudl StatsBomb's metric named xG is already non-penalty (its label is NP xG), so it matches this card, not xg; and FBref's npxG also removed shots from a rebound after a penalty, which a plain filter on shot type keeps. Penalty shoot-out kicks are never counted. On the 2022 World Cup final, France's npxG is 0.7056 against an xG of 2.2726, because two of its in-play shots were penalties.

- **Measures:** The quality of the chances a team or player creates without penalties: the xG total with penalty kicks taken out, so that a penalty, which every provider values at one fixed number, does not swamp the total.
- **Direction:** Higher values mean more or better chances. A team with no counted shot has a total of 0.
- **Unit:** expected goals (a sum of per-shot goal probabilities, each between 0 and 1)
- **Origin:** No single origin. npxG is a filter on xG (see the xg card for Sam Green's 2012 OptaPro post). FBref's xG explainer recommends npxG (non-penalty expected goals) for xG without penalty kicks. Who first used the label is not known. (https://web.archive.org/web/20260107000728/https://fbref.com/en/expected-goals-model-explained/)

## Variants

- `npxg.statsbomb-hudl`: Hudl StatsBomb 'xG' (NP xG). Whole pitch (every non-penalty shot). Reference code: exact (football_metrics.xg:npxg_statsbomb_hudl on statsbomb-open-data).
- `npxg.fbref`: FBref (Opta values, penalty rebounds removed), historical to January 2026. Whole pitch (every non-penalty shot). Reference code: none yet.
- `npxg.understat`: Understat (NPxG). Whole pitch (every non-penalty shot). Reference code: none yet.

## npxg.statsbomb-hudl: Hudl StatsBomb 'xG' (NP xG)

The sum of the StatsBomb xG value over the team's shots whose shot type is not Penalty. Hudl StatsBomb names this metric xG in its glossary; the column label is NP xG (abbreviation NPxG). In the player glossary, xG is 'Non-penalty expected goals produced by the player' over non-penalty shots.

- **Formula:** Count of shot_xg where shot type≠penalty (sum of shot.statsbomb_xg over Shot events with shot.type.name not "Penalty")
- **Zone:** Whole pitch (every non-penalty shot).
- **Source:** Event Data Glossary: Team Metrics (Hudl StatsBomb): https://support.hudl.com/s/article/event-data-glossary-team-metrics
- **Quote** (browser, checked 2026-10-04): "Cumulative expected goal value of all non-penalty shots."
- **Quote check note:** The page builds its text with JavaScript, so match_quote cannot read it; checked word for word in a browser.
- **Reference code:** exact (football_metrics.xg:npxg_statsbomb_hudl on statsbomb-open-data)
- **Mapping:** The source's own formula on the source's own event data: shot.statsbomb_xg summed over the team's Shot events with shot.type.name not "Penalty", with penalty shoot-out kicks (period 5) left out.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 1.9748
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 0.7056
- 'Cumulative' in Hudl's description means a running total. The formula is a plain sum, not the possession-capped cumulative xG of xg.statsbomb-cumulative.
- A shot from a rebound after a penalty counts, as its shot type is not Penalty.
- Hudl's 'xG Conceded' and 'xG Difference' are also non-penalty; 'xG Difference Inclusive' includes penalties (see xg.statsbomb-hudl).

## npxg.fbref: FBref (Opta values, penalty rebounds removed), historical to January 2026

FBref's possession-capped xG (xg.fbref) without penalty kicks and without shots from a rebound after a penalty kick: FBref treats such a rebound as part of the penalty kick xG. In FBref's example a Reus penalty (.79) and his rebound (.92) give .9832 xG and 0 npxG.

- **Formula:** xg.fbref total, leaving out penalty kicks and shots from a rebound after a penalty kick
- **Zone:** Whole pitch (every non-penalty shot).
- **Source:** xG Explained (FBref (Sports Reference)): https://web.archive.org/web/20260107000728/https://fbref.com/en/expected-goals-model-explained/
- **Quote** (exact, checked 2026-10-04): "However, since the second shot is also considered to be a part of the penalty kick xG, Reus gets 0 npxG (non-penalty expected goals) on this play."
- **Quote check note:** FBref blocks automated clients, so the quote is checked against a Wayback Machine snapshot of 7 January 2026.
- **Reference code:** none yet
- FBref's tooltip names the column 'Non-Penalty Expected Goals' (npxG) and says 'Provided by Opta.'
- Historical: FBref removed its Opta advanced data, xG and npxG included, on 20 January 2026 (Sports Reference blog, 'FBref & Stathead Data Update'). Values cited from FBref before then follow this variant.
- No reference code: the values come from Opta's model, which is not in the open data.

## npxg.understat: Understat (NPxG)

Understat's xG without penalties. Its team column NPxG is expected goals for, without penalties and own goals; its player column NPxG is xG without penalties.

- **Formula:** sum of Understat shot xG over shots whose situation is not Penalty
- **Zone:** Whole pitch (every non-penalty shot).
- **Source:** Understat league page script (column tooltips) (Understat): https://understat.com/js/league.min.js
- **Quote** (exact, checked 2026-10-04): "Expected goals for without penalties and own goals"
- **Quote check note:** The tooltip text is in the page's script, not its HTML.
- **Reference code:** none yet
- Checked on Understat's public data (4 October 2026): in Liverpool v Manchester City, 8 February 2026 (Understat match 29024), Manchester City's npxG of 1.65359 is its xG of 2.41476 minus its one penalty (0.7612).
- Understat does not say how it treats a rebound after a penalty, or how own goals enter its xG.
- NPxGA and NPxGD are the same measure for shots conceded and the difference.
- No reference code: the values come from Understat's model, which is not in the open data.


## Caveats

- Check what a column called xG means before comparing: Hudl StatsBomb's player and team xG leave penalties out, FBref's and Understat's xG include them.
- Rebounds after a penalty: FBref's npxG left them out; a filter on shot type (Hudl StatsBomb) keeps them. Understat does not say.
- The shot values come from each provider's model, so npxG from different providers is not comparable. Cite the variant ID.
- Penalty shoot-out kicks are not part of match xG or npxG.
- Own goals are not shots and carry no xG.
- npxG removes the penalty but not the foul that won it: a player who wins penalties gets no credit for them.

Related: xg, xg_assisted, xa, psxg (no card yet).

Cite a value with the exact variant ID: values from different variants are not comparable.
````

### m08 — get_metric {"id": "progressive_passes"}

````text
# Progressive passes

Card `progressive_passes`, version 1, updated 2026-10-04.

A progressive pass is a pass that moves the ball a long way towards the opponent's goal. There is no single definition: at least five public rules are in use. Wyscout uses fixed distances in metres that depend on the halves the pass starts and ends in; FBref (on Opta data, until January 2026) used 10 yards measured from the ball's furthest point in the last six passes; Opta Analyst, American Soccer Analysis and a 2023 StatsBomb blog use "at least 25% of the remaining distance to goal" with different zones and set-piece rules. Values from different definitions are not comparable: on the 2022 World Cup final the reference code gives from 50 (ASA) to 176 (Wyscout) progressive passes for both teams together.

- **Measures:** How often a player or team moves the ball a long way towards the opponent's goal with a pass.
- **Direction:** Higher values mean more ball progression by passing. A count, not a quality measure: it grows with possession and with the number of passes a player makes.
- **Unit:** passes (a count, often given per 90 minutes)
- **Origin:** No single origin is confirmed. The earliest dated public definition found is in a July 2019 Stop Bunching blog post, which quotes an older Wyscout rule based on pass length: forward passes 30 m long when they start in the team's own half, or at least 10 m long in the opponent's half. Wyscout's current glossary measures distance gained towards goal instead. The '25% of the remaining distance to goal' rule comes from John Muller, as American Soccer Analysis says (February 2021); Muller's app futi still uses it (September 2026). (http://stopbunching.blogspot.com/2019/07/picking-progressive-passers.html)

## Variants

- `progressive_passes.wyscout`: Wyscout. Whole pitch; the threshold depends on the halves the pass starts and ends in. Reference code: approximation (football_metrics.progression:progressive_passes_wyscout on statsbomb-open-data).
- `progressive_passes.fbref-opta`: FBref (Opta data), historical. Passes from outside the passing team's defending 40%. Reference code: approximation (football_metrics.progression:progressive_passes_fbref on statsbomb-open-data).
- `progressive_passes.opta-analyst`: Opta Analyst. The attacking two-thirds of the pitch. Reference code: approximation (football_metrics.progression:progressive_passes_opta_analyst on statsbomb-open-data).
- `progressive_passes.asa`: American Soccer Analysis (John Muller's rule). Passes that start in the attacking 60% of the pitch. Reference code: approximation (football_metrics.progression:progressive_passes_asa on statsbomb-open-data).
- `progressive_passes.statsbomb-blog-2023`: Hudl StatsBomb blog (2023). Whole pitch (no zone limit is stated). Reference code: approximation (football_metrics.progression:progressive_passes_statsbomb_blog on statsbomb-open-data).

## progressive_passes.wyscout: Wyscout

A forward pass that moves the ball closer to the opponent's goal, measured from the start point to the next touch: at least 30 m closer when the start and finish are both in the team's own half, at least 15 m when they are in different halves, and at least 10 m when both are in the opponent's half.

- **Formula:** gain = distance to the opponent's goal at the start - distance at the next touch; progressive if gain >= 30 m (own half to own half), >= 15 m (across halfway) or >= 10 m (opponent's half to opponent's half)
- **Zone:** Whole pitch; the threshold depends on the halves the pass starts and ends in.
- **Passes counted:** All progressive passes, successful or not. A progressive pass is successful (API tagId 1801) when the next touch is by a teammate, unsuccessful (tagId 1802) otherwise; the glossary also gives 'Accurate progressive passes (%)'.
- **Source:** Progressive pass (Wyscout): https://dataglossary.wyscout.com/progressive_pass/
- **Quote** (normalised, checked 2026-10-04): "at least 30 meters closer to the opponent’s goal if the starting and finishing points are within a team’s own half - at least 15 meters closer to the opponent’s goal if the starting and finishing points are in different halves - at least 10 meters closer to the opponent’s goal if the starting and finishing points are in the opponent’s half"
- **Quote check note:** The three thresholds are list items on the page; the hyphens mark the list items.
- **Reference code:** approximation (football_metrics.progression:progressive_passes_wyscout on statsbomb-open-data)
- **Mapping:** An approximation on StatsBomb events: every open-play Pass event, completed or not (set pieces left out: pass.type Corner, Free Kick, Throw-in, Goal Kick or Kick Off); pass.end_location stands for the next touch; distance is the straight-line distance to the goal centre (120, 40); own half is x < 60; StatsBomb yards are converted to metres (1 yard = 0.9144 m).
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 97
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 79
- The glossary does not say whether 'closer to the opponent's goal' is the straight-line distance to the goal or the gain along the pitch. The Soccermatics course implements it as straight-line distance to the centre of the goal.
- Wyscout measures to the next touch of the ball, not to a recorded end location.
- The glossary lists set pieces (corner kick, free kick, throw-in) under their own heading, apart from passes.

## progressive_passes.fbref-opta: FBref (Opta data), historical

Completed passes that move the ball towards the opponent's goal line at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area. Passes from the defending 40% of the pitch do not count.

- **Formula:** completed pass, start not in the defending 40%, and (end - furthest point of the ball in the last six passes >= 10 yards towards the goal line, or end in the penalty area)
- **Zone:** Passes from outside the passing team's defending 40%.
- **Passes counted:** Completed passes only.
- **Source:** Premier League Passing Stats (archived 3 May 2025) (FBref, 2025-05-03): https://web.archive.org/web/20250503183817/https://fbref.com/en/comps/9/passing/Premier-League-Stats
- **Quote** (browser, checked 2026-10-04): "Completed passes that move the ball towards the opponent's goal line at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area. Excludes passes from the defending 40% of the pitch"
- **Quote check note:** The definition is the column tooltip (the data-tip attribute of the PrgP header), not readable page text, so match_quote cannot read it; checked word for word in the archived page in a browser.
- **Reference code:** approximation (football_metrics.progression:progressive_passes_fbref on statsbomb-open-data)
- **Mapping:** An approximation on StatsBomb events of a definition written for Opta events: completed Pass events (no pass.outcome), set pieces included, starting at x >= 48; progressive if the end is in the penalty area (x >= 102, 18 <= y <= 62) from outside it, or if end x minus the furthest x of the ball is at least 10 (StatsBomb units are yards). The furthest x is read as the largest x among the pass start and the start and end of the team's previous six completed passes in the same StatsBomb possession.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 64
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 48
- FBref removed its Opta advanced data on 20 January 2026 (Sports Reference blog, 'FBref & Stathead Data Update'), so this variant is historical.
- FBref does not say how the 'furthest point in the last six passes' is found (which passes, and whether across possessions). The reference code states its reading.
- The same text defined FBref's 'Progressive Passes Received'.

## progressive_passes.opta-analyst: Opta Analyst

Completed open-play passes in the attacking two-thirds of the pitch that move the ball at least 25% closer to the goal.

- **Formula:** completed open-play pass in the attacking two-thirds with distance to goal at the end <= 0.75 x distance to goal at the start
- **Zone:** The attacking two-thirds of the pitch.
- **Passes counted:** Completed open-play passes only.
- **Source:** What You Didn't Know About Premier League Passing (Jonathan Manuel, 2022-10-01): https://theanalyst.com/2022/10/what-you-didnt-know-about-premier-league-passing
- **Quote** (exact, checked 2026-10-04): "completed open-play passes in the attacking two-thirds of the pitch that move the ball at least 25% closer to the goal"
- **Reference code:** approximation (football_metrics.progression:progressive_passes_opta_analyst on statsbomb-open-data)
- **Mapping:** An approximation on StatsBomb events of a definition written for Opta events: completed Pass events (no pass.outcome) that are not set pieces (pass.type not Corner, Free Kick, Throw-in, Goal Kick or Kick Off), starting at x >= 40, whose straight-line distance to the goal centre (120, 40) at pass.end_location is at most 75% of the distance at the start.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 36
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 17
- The Opta Analyst glossary defines it as a completed pass in the attacking two-thirds that moves the ball at least 25% closer to goal, without saying open play; the 1 October 2022 article says open play.
- Neither page says whether the pass must start or end in the attacking two-thirds.

## progressive_passes.asa: American Soccer Analysis (John Muller's rule)

An open-play pass that moves the ball at least 25% of the remaining distance to goal, counted only when it starts in the attacking 60% of the pitch.

- **Formula:** open-play pass starting in the attacking 60% with distance to goal at the end <= 0.75 x distance to goal at the start
- **Zone:** Passes that start in the attacking 60% of the pitch.
- **Passes counted:** Completed passes: the same article describes its progressive-pass goal category as shots after a completed open-play pass that moves at least 25% closer to goal.
- **Source:** Where Goals Come From (Jamon Moore and Carl Carpenter, 2021-02-17): https://www.americansocceranalysis.com/home/2021/7/10/where-goals-come-from
- **Quote** (normalised, checked 2026-10-04): "an open play pass that moves the ball at least 25% of the remaining distance to goal. We only count passes that start in the attacking 60% of the pitch."
- **Reference code:** approximation (football_metrics.progression:progressive_passes_asa on statsbomb-open-data)
- **Mapping:** An approximation on StatsBomb events: completed Pass events (no pass.outcome) that are not set pieces (pass.type not Corner, Free Kick, Throw-in, Goal Kick or Kick Off), starting at x >= 48, whose straight-line distance to the goal centre (120, 40) at pass.end_location is at most 75% of the distance at the start.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 33
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 17
- ASA says the rule comes from John Muller, and that fixed distances miss passes from the sides of the box that do not travel 10 yards.
- ASA calls progressive passes over 35 yards 'long balls'.
- The article is dated 17 February 2021 (by Jamon Moore and Carl Carpenter) although its URL contains 2021/7/10.
- futi (John Muller, 19 September 2026) uses the same 25% rule for progressive passes, carries and receptions, but does not state a zone or a set-piece rule.

## progressive_passes.statsbomb-blog-2023: Hudl StatsBomb blog (2023)

Any successful pass, set pieces excluded, that moves the ball at least 25% of the remaining distance towards the centre of the goal. The same article applies the rule to carries.

- **Formula:** completed non-set-piece pass with distance to the goal centre at the end <= 0.75 x distance at the start
- **Zone:** Whole pitch (no zone limit is stated).
- **Passes counted:** Successful passes only, set pieces excluded.
- **Source:** The Art of Progression: An Analysis of Passing vs. Ball Carrying (Jaymes Monte, 2023-03-22): https://blogarchive.statsbomb.com/articles/soccer/the-art-of-progression-an-analysis-of-passing-vs-ball-carrying/
- **Quote** (exact, checked 2026-10-04): "Any successful pass (set pieces excluded) or carry (including dribbles) that moves the ball at least 25% of the remaining distance towards the centre of the goal."
- **Reference code:** approximation (football_metrics.progression:progressive_passes_statsbomb_blog on statsbomb-open-data)
- **Mapping:** StatsBomb's own rule on StatsBomb events, but the article gives it in prose, not on StatsBomb fields, so the field choices are ours: successful = no pass.outcome; set pieces = pass.type Corner, Free Kick, Throw-in, Goal Kick or Kick Off; distance = straight-line distance from location and pass.end_location to the goal centre (120, 40).
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 46
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 23
- This is the methodology of one blog article, not a Hudl StatsBomb product metric: Hudl's Event Data Glossary (player metrics) has no progressive pass or progressive carry metric; its nearest is Deep Progressions, passes and dribbles/carries into the opposition final third (start_location_x < 80 and end_location_x >= 80).
- At player level the article normalises by the number of touches (progressive passes per 100 touches).


## Caveats

- Values from different definitions are not comparable: the zone, the distance rule, set-piece handling and whether failed passes count all change the number. Cite the variant ID.
- Wyscout counts unsuccessful progressive passes; FBref, Opta Analyst, ASA and the StatsBomb blog count completed passes only.
- Units differ: Wyscout states metres, FBref yards; StatsBomb's 120 x 80 grid is in yards on a fixed pitch, whatever the real pitch size.
- Most sources do not say whether 'closer to goal' is the straight-line distance to the centre of the goal or the gain along the pitch. The reference code says which it uses.
- A count grows with possession and pass volume: compare per 90 minutes or per 100 passes or touches, and with team style in mind.
- Many web explainers attribute thresholds to the wrong provider (for example the Wyscout 30 / 15 / 10 m rule to StatsBomb or FBref). Use the provider's own glossary.
- FBref no longer shows Opta's advanced data: the Sports Reference blog said on 20 January 2026 that the data provider had ended its access. FBref values are historical.

Related: progressive_carries, xt, passes_into_final_third (no card yet).

Cite a value with the exact variant ID: values from different variants are not comparable.
````

### m09 — get_metric {"id": "xt"}

````text
# xT (expected threat)

Card `xt`, version 1, updated 2026-10-04.

xT gives every zone of the pitch a value: the probability that a team with the ball there scores within the next few actions. A pass, cross or carry is worth the value of the zone where it ends minus the value of the zone where it starts. Karun Singh introduced it in a blog post in early 2019. The value surface is learned from data, so the grid size, the data, the stopping rule for the iteration and which actions count all change the numbers. On the 2022 World Cup final, Singh's published 12 x 8 surface gives Argentina 1.86 xT added and France 1.18.

- **Measures:** How much a ball-progressing action (pass, cross or carry) raises the chance of scoring, from where the ball starts to where it ends, using a value for each zone of the pitch.
- **Direction:** Higher means more threat added. Moving the ball backwards gives a negative value.
- **Unit:** probability of scoring (an action's value is a difference of two probabilities)
- **Origin:** Karun Singh, 'Introducing Expected Threat (xT)', blog post, early 2019. The page has no date; the Wayback Machine holds it from 22 February 2019. Singh credits Cervone et al.'s possession-value work in basketball for the motivation and notes that valuing every location on the pitch is not new. Earlier Markov-chain possession models in football include Sarah Rudd's 2011 NESSIS talk. (https://karun.in/blog/expected-threat.html)

## Variants

- `xt.singh-2019`: Singh (2019), the original. Whole pitch, divided into a 16 x 12 grid (192 zones); the post says another resolution can be used. Reference code: none yet.
- `xt.singh-open-12x8`: Singh's published 12 x 8 surface. Whole pitch, 12 x 8 grid. Reference code: approximation (football_metrics.xt:xt_singh_open_surface on statsbomb-open-data).
- `xt.socceraction`: socceraction (KU Leuven), fitted. Whole pitch; default grid 16 x 12. Reference code: none yet.
- `xt.databallpy`: DataBallPy. Whole pitch, 32 x 24 grid. Reference code: none yet.

## xt.singh-2019: Singh (2019), the original

Each zone's xT is the probability of shooting there times the probability of scoring from there, plus the probability of moving the ball times the sum, over every zone it can move to, of the move probability times that zone's xT. The values are found by iteration from zero; after n iterations a zone's xT is the probability of scoring within the next n actions. An action that moves the ball from one zone to another is worth the end zone's xT minus the start zone's.

- **Formula:** xT(x,y) = s(x,y) * g(x,y) + m(x,y) * sum over zones (z,w) of T((x,y) -> (z,w)) * xT(z,w); action value = xT(end zone) - xT(start zone)
- **Zone:** Whole pitch, divided into a 16 x 12 grid (192 zones); the post says another resolution can be used.
- **Passes counted:** Successful moves only (passes and dribbles completed without losing possession), from the 2017/18 Premier League season. Iterated 4 to 5 times.
- **Source:** Introducing Expected Threat (xT) (Karun Singh, 2019 (undated page; archived 2019-02-22)): https://karun.in/blog/expected-threat.html
- **Quote** (exact, checked 2026-10-04): "for the purposes of this post, we're working with a 16x12 grid on the pitch, which gives us 192 zones."
- **Reference code:** none yet
- s is the shot probability, g the goal probability given a shot, m the move probability (s + m = 1) and T the matrix of move transitions between zones.
- The post does not name its data provider, and the fitted 16 x 12 surface is not published, so this variant has no reference code.

## xt.singh-open-12x8: Singh's published 12 x 8 surface

A ready-made xT surface that Singh published as a JSON file: 8 rows across the pitch and 12 columns along it, from about 0.0064 near the own goal to about 0.2575 in front of the opponent's goal. Actions are valued with it the way socceraction's ExpectedThreat.rate does: successful passes, crosses and dribbles (carries) only, end zone value minus start zone value.

- **Formula:** action value = surface[end zone] - surface[start zone]; team total = sum over the team's successful passes, crosses and carries
- **Zone:** Whole pitch, 12 x 8 grid.
- **Passes counted:** Successful moves only. Set-piece passes (free kicks, corners, throw-ins, goal kicks) are not valued; a kick-off is an ordinary pass.
- **Source:** socceraction xthreat.py, load_model (v1.5.3) (KU Leuven DTAI): https://raw.githubusercontent.com/ML-KULeuven/socceraction/3ca3ce0b0163352b84a0f7665c647fb4f3f9c3ad/socceraction/xthreat.py
- **Quote** (exact, checked 2026-10-04): "Karun Singh provides such a grid at the follwing url"
- **Quote check note:** The quote keeps the source's spelling ('follwing'). The surface itself is https://karun.in/blog/data/open_xt_12x8_v1.json.
- **Reference code:** approximation (football_metrics.xt:xt_singh_open_surface on statsbomb-open-data)
- **Mapping:** Singh's surface applied to StatsBomb events, choosing actions as socceraction's StatsBomb converter and ExpectedThreat.rate do: a Pass with no outcome and a pass.type other than Free Kick, Corner, Throw-in or Goal Kick, or a Carry (socceraction's dribble). Zones: column = int(x / 120 * 12), row = int(y / 80 * 8), clipped. socceraction also inserts synthetic dribbles between consecutive actions of the same team (3 to 60 units apart, under 10 seconds); StatsBomb's Carry events stand for those here.
- **Test value:** Argentina, Argentina v France, World Cup 2022 final (match 3869685): 1.8631
- **Test value:** France, Argentina v France, World Cup 2022 final (match 3869685): 1.1759
- Which data and how many iterations produced the published surface is not stated.
- The surface is symmetric top to bottom, so the orientation of the y axis does not change values.
- socceraction's load_model reads this file; its documentation points to the URL.

## xt.socceraction: socceraction (KU Leuven), fitted

socceraction fits the surface itself from SPADL actions. Move actions are passes, dribbles and crosses; take-ons are left out. The shot probability uses open-play shots only (SPADL type shot, not free-kick or penalty shots). The move probability counts every move attempt, and the transition matrix divides successful moves by all attempts, so failed moves act as lost possession. Iteration stops when no zone changes by more than a small tolerance.

- **Formula:** as xt.singh-2019, with T = successful moves / all move attempts from each zone; iterate until the largest change is below eps
- **Zone:** Whole pitch; default grid 16 x 12.
- **Passes counted:** Fitting uses all move attempts; rating values successful moves only.
- **Source:** socceraction xthreat.py, get_move_actions (v1.5.3) (KU Leuven DTAI): https://raw.githubusercontent.com/ML-KULeuven/socceraction/3ca3ce0b0163352b84a0f7665c647fb4f3f9c3ad/socceraction/xthreat.py
- **Quote** (normalised, checked 2026-10-04): "These include passes, dribbles and crosses. Take-ons are ignored because they typically coincide with dribbles and do not move the ball to a different cell."
- **Reference code:** none yet
- Defaults in socceraction v1.5.3: l = 16, w = 12, eps = 1e-5; optional bilinear interpolation.
- No reference code here yet: a fit needs many matches of training data.
- The socceraction README says the package is no longer actively developed; pin the version.

## xt.databallpy: DataBallPy

DataBallPy's xT model follows Singh's method on a finer grid of 32 x 24 cells, interpolated to a smoother surface. Before fitting it deletes own goals, shots from the own half (which it treats as data errors) and events in set-piece situations (corners, free kicks, throw-ins, goal kicks).

- **Formula:** as xt.singh-2019, on a 32 x 24 grid
- **Zone:** Whole pitch, 32 x 24 grid.
- **Source:** Expected Threat (xT) models (DataBallPy): https://databallpy.readthedocs.io/en/main/features/xt_models.html
- **Quote** (exact, checked 2026-10-04): "closely based on the work and blog of Karun Singh"
- **Reference code:** none yet
- No reference code here; DataBallPy ships its own fitted model.


## Caveats

- The grid size, the training data, the number of iterations and which shots feed the goal probability are free choices; different packages give different numbers for the same action. Cite the variant and the surface.
- xT values only ball-progressing actions. Defensive actions, take-ons and moves inside one zone are worth zero.
- It values the attacking side only, and ignores what happens after a turnover.
- The state is the ball's zone alone: no players, no pressure, no game state, and one surface for a whole league unless it is fitted per team.
- Shots are not valued as actions, so player xT totals favour creators over finishers.
- Singh's post values successful moves; socceraction counts failed moves in the move probability, so failed moves act as lost possession in the fit.

Related: vaep, progressive_passes, progressive_carries.

Cite a value with the exact variant ID: values from different variants are not comparable.
````

### m00 — get_metric {"id": "not-a-metric"} — error

````text
No metric card or variant "not-a-metric". Cards: field_tilt, npxg, pass_completion, ppda, progressive_carries, progressive_passes, vaep, xa, xg, xg_assisted, xt. Use list_metrics for variants.
````

### x01 — search_papers {"query": "\"expected threat\" soccer"}

````text
# Papers for: "expected threat" soccer

## OpenAlex (10 shown of 139)

1. **A framework for the fine-grained evaluation of the instantaneous expected value of soccer possessions**
   Javier Fernández, Luke Bornn, Cervone, Daniel (2020) · arXiv (Cornell University)
   DOI 10.1007/s10994-021-05989-6 · arXiv 2011.09426 · OpenAlex W3164404442 · cited by 91 · from OpenAlex
   Open copy: https://arxiv.org/pdf/2011.09426 (PDF, arXiv (Cornell University), submittedVersion, licence unknown)
   The expected possession value (EPV) of a soccer possession represents the likelihood of a team scoring or receiving the next goal at any time instance. By decomposing the EPV into a series of subcomponents that are estimated separately, we…

2. **Towards maximizing expected possession outcome in soccer**
   Pegah Rahimian, Jan Van Haaren, László Toka (2023) · International Journal of Sports Science & Coaching
   DOI 10.1177/17479541231154494 · OpenAlex W4321498077 · cited by 21 · from OpenAlex
   Open copy: https://journals.sagepub.com/doi/pdf/10.1177/17479541231154494 (PDF, International Journal of Sports Science & Coaching, publishedVersion, licence: CC BY-NC)
   Soccer players need to make many decisions throughout a match in order to maximize their team’s chances of winning. Unfortunately, these decisions are challenging to measure and evaluate due to the low-scoring, complex, and highly dynamic…

3. **A Bayesian Approach to In-Game Win Probability in Soccer**
   Pieter Robberechts, Jan Van Haaren, Jesse J. Davis (2021) · Proceedings of the 27th ACM SIGKDD Conference on Knowledge Discovery & Data Mining
   DOI 10.1145/3447548.3467194 · arXiv 1906.05029 · OpenAlex W3170246188 · cited by 18 · from OpenAlex
   Open copy: https://arxiv.org/pdf/1906.05029 (PDF, arXiv (Cornell University), submittedVersion, licence unknown)
   In-game win probability models, which provide a sports team's likelihood of winning at each point in a game based on historical observations, are becoming increasingly popular. In baseball, basketball and American football, they have…

4. **Adjusting expected goals (xG) and shots on target for game context in soccer**
   Andrey Skripnikov, Ahmet Cemek, David Gillman (2026) · Journal of Sports Analytics
   DOI 10.1177/22150218261454824 · OpenAlex W7163821577 · cited by 0 · from OpenAlex
   Open copy: https://doi.org/10.1177/22150218261454824 (page, Journal of Sports Analytics, publishedVersion, licence: CC BY-NC)
   With advancements in soccer analytics, considerable attention has been devoted to developing sophisticated measures for quality scoring opportunities - such as expected goals and expected threat. Far less effort, however, has gone toward…

5. **Controlling ball progression in soccer**
   Catherine Pfaff, Hunter, Emily, Haozhi Hong and 4 more (2022) · arXiv (Cornell University)
   DOI 10.48550/arxiv.2210.16474 · arXiv 2210.16474 · OpenAlex W4307928271 · cited by 0 · from OpenAlex
   Open copy: https://arxiv.org/pdf/2210.16474 (PDF, arXiv (Cornell University), submittedVersion, licence unknown)
   In this paper, we examine how soccer players can use their spatial relationships to control parts of the field and safely move play up the field via chains of ``safe configurations,'' i.e. configurations of players on a team ensuring the…

6. **Controlling Ball Progression in Soccer**
   Haozhi Hong, Zoey Drassinower, Ari Fialkov and 2 more (2025) · SIAM Undergraduate Research Online
   DOI 10.1137/24s1666331 · OpenAlex W4407765982 · cited by 0 · from OpenAlex
   Open copy: https://doi.org/10.1137/24s1666331 (PDF, SIAM Undergraduate Research Online, publishedVersion, licence unknown)
   This paper focuses on how a soccer team can progress the ball up the field from the defensive third to the attacking third.We define a "safe configuration" of soccer players as one in which the ball possessor is part of a collection of…

7. **Towards a foundation large events model for soccer**
   Tiago Mendes-Neves, Luís Meireles, João Mendes Moreira (2024) · Machine Learning
   DOI 10.1007/s10994-024-06606-y · OpenAlex W4402514602 · cited by 6 · from OpenAlex
   Open copy: https://link.springer.com/content/pdf/10.1007/s10994-024-06606-y.pdf (PDF, Machine Learning, publishedVersion, licence: CC BY)
   Abstract This paper introduces the Large Events Model (LEM) for soccer, a novel deep learning framework for generating and analyzing soccer matches. The framework can simulate games from a given game state, with its primary output being…

8. **Leaving Goals on the Pitch: Evaluating Decision Making in Soccer**
   Maaike Van Roy, Pieter Robberechts, Wen-Chi Yang and 2 more (2021) · arXiv (Cornell University)
   DOI 10.48550/arxiv.2104.03252 · arXiv 2104.03252 · OpenAlex W3147376827 · cited by 10 · from OpenAlex
   Open copy: https://arxiv.org/pdf/2104.03252 (PDF, arXiv (Cornell University), submittedVersion, licence unknown)
   Analysis of the popular expected goals (xG) metric in soccer has determined that a (slightly) smaller number of high-quality attempts will likely yield more goals than a slew of low-quality ones. This observation has driven a change in…

9. **Towards optimized actions in critical situations of soccer games with deep reinforcement learning**
   Pegah Rahimian, Afshin Oroojlooy, László Toka (2021) · IEEE International Conference on Data Science and Advanced Analytics (DSAA)
   DOI 10.1109/dsaa53316.2021.9564207 · arXiv 2109.06625 · OpenAlex W3200186663 · cited by 16 · from OpenAlex
   Open copy: https://arxiv.org/pdf/2109.06625 (PDF, arXiv (Cornell University), submittedVersion, licence: public-domain)
   Soccer is a sparse rewarding game: any smart or careless action in critical situations can change the result of the match. Therefore players, coaches, and scouts are all curious about the best action to be performed in critical situations,…

10. **Is it worth the effort? Understanding and contextualizing physical metrics in soccer**
   Llana, Sergio, Borja Burriel, Pau Madrero and 1 more (2022) · arXiv (Cornell University)
   DOI 10.48550/arxiv.2204.02313 · arXiv 2204.02313 · OpenAlex W4224903976 · cited by 5 · from OpenAlex
   Open copy: https://arxiv.org/pdf/2204.02313 (PDF, arXiv (Cornell University), submittedVersion, licence unknown)
   We present a framework that gives a deep insight into the link between physical and technical-tactical aspects of soccer and it allows associating physical performance with value generation thanks to a top-down approach. First, we estimate…

## arXiv (5 shown of 5)

11. **The trade-off between model flexibility and accuracy of the Expected Threat model in football**
   Koen W. van Arem, Jakob Söhl, Mirjam Bruinsma and 1 more (2025)
   arXiv 2511.09457v1 · from arXiv
   Open copy: https://arxiv.org/pdf/2511.09457v1 (PDF, arXiv, licence unknown)
   With an average football (soccer) match recording over 3,000 on-ball events, effective use of this event data is essential for practitioners at football clubs to obtain meaningful insights. Models can extract more information from this…

12. **Unveiling Hidden Pivotal Players with GoalNet: A GNN-Based Soccer Player Evaluation System**
   Jacky Hao Jiang, Jerry Cai, Anastasios Kyrillidis (2025)
   arXiv 2503.09737v1 · from arXiv
   Open copy: https://arxiv.org/pdf/2503.09737v1 (PDF, arXiv, licence unknown)
   Soccer analysis tools emphasize metrics such as expected goals, leading to an overrepresentation of attacking players' contributions and overlooking players who facilitate ball control and link attacks. Examples include Rodri from…

13. **GenTac: Generative Modeling and Forecasting of Soccer Tactics**
   Jiayuan Rao, Tianlin Gui, Haoning Wu and 2 more (2026)
   arXiv 2604.11786v1 · from arXiv
   Open copy: https://arxiv.org/pdf/2604.11786v1 (PDF, arXiv, licence unknown)
   Modeling open-play soccer tactics is a formidable challenge due to the stochastic, multi-agent nature of the game. Existing computational approaches typically produce single, deterministic trajectory forecasts or focus on highly structured…

14. **What Happened Next? Using Deep Learning to Value Defensive Actions in Football Event-Data**
   Charbel Merhej, Ryan Beal, Sarvapali Ramchurn and 1 more (2021)
   DOI 10.1145/3447548.3467090 · arXiv 2106.01786v1 · from arXiv
   Open copy: https://arxiv.org/pdf/2106.01786v1 (PDF, arXiv, licence unknown)
   Objectively quantifying the value of player actions in football (soccer) is a challenging problem. To date, studies in football analytics have mainly focused on the attacking side of the game, while there has been less work on event-driven…

15. **H-VAEP and H-xT: Valuing Offensive On-the-Ball Actions in Handball by Estimating Probabilities**
   Julius Broermann, Oliver Müller, Michael Döring and 1 more (2026)
   arXiv 2608.12926v1 · from arXiv
   Open copy: https://arxiv.org/pdf/2608.12926v1 (PDF, arXiv, licence unknown)
   Traditional player evaluation in professional handball relies on basic box-score metrics or heuristic indices, which fail to credit the multi-player build-up chain. While football (soccer) analytics has adopted Expected Threat (xT) and…

## SportRxiv (0 shown of 0)

No new matches.

Open one with get_paper, or read it with read_paper (DOI, arXiv ID, OpenAlex ID or zotero: ID). OpenAlex matches full text, so a hit may only cite the idea.

Services asked: SportRxiv (local copy from 2026-10-01, no request sent; 0 matches); arXiv (5 matches); OpenAlex (139 matches).
````

### x02 — get_web_source {"url": "https://karun.in/blog/expected-threat.html"}

````text
# Introducing Expected Threat (xT)

- **URL:** https://karun.in/blog/expected-threat.html
- **Author:** Karun Singh
- **Published:** no date on the page
- **Licence:** none stated on the page
- **Earliest Wayback snapshot:** 2019-02-22 https://web.archive.org/web/20190222174641/https://karun.in/blog/expected-threat.html
  (The page has no date. It existed by 2019-02-22, the date of this snapshot.)
- **Latest Wayback snapshot:** 2026-09-22 https://web.archive.org/web/20260922114139/https://karun.in/blog/expected-threat.html

## Text

##### Before we begin...

As you may have inferred from my [previous post on interactive, weighted passing networks](https://karun.in/blog/interactive-passing-networks.html), I'm a big fan of going beyond static visualizations. Quantitative analysis is great, but I believe that we can amplify the gains of such analysis by being more adventurous with presentation. This post in particular contains a _lot_ of interactivity – much of it experimental – in an effort to probe new areas of the design space and hopefully spark productive discussions.

##### Credit where credit's due

To motivate the rest of this post, consider Arsenal’s opening goal in a recent 3-1 win against Burnley:

After some intricate passing on the right, Mesut Özil slices the Burnley defence open with a ball through to Sead Kolašinac, whose timely cutback finds Pierre-Emerick Aubameyang for the finish. Thanks to [@lastrowview](https://twitter.com/lastrowview), here's a neat top-down visualization of the same sequence of play:

> Incredible vision and execution from Ozil finding Kolasinac's run, who assisted Aubameyang for the first against Burnley [#Arsenal](https://twitter.com/hashtag/Arsenal?src=hash&ref_src=twsrc%5Etfw) [pic.twitter.com/lV2tWF91hR](https://t.co/lV2tWF91hR)
> 
> — Last Row (@lastrowview) [December 24, 2018](https://twitter.com/lastrowview/status/1077258834698227713?ref_src=twsrc%5Etfw)

Of course, on paper the assist for this goal is given to Kolašinac. But as an analyst you might (rightly) ask where Özil's credit is. Where's the metric that can capture both, Özil and Kolašinac's contributions in a proportional manner?

**How should we divide up the credit between Özil and Kolašinac for creating this opportunity? Drag the slider to enter what you think!**

The purpose of this exercise isn't to converge on a universally accepted answer, but rather to show that breaking down buildup play and assigning credit to individual actors is a hard problem.

##### Existing approaches

There are several existing quantitative frameworks you might want to use to approach this problem:

-   You can look at **assists**, but then contributions such as Özil's will go unnoticed in the numbers.
-   You can look at **xGChain**, where the xG of the final shot (= 0.13 in this case) will be equally divided amongst every player involved in the play. Kolašinac, Özil, and even Aubameyang, Maitland-Niles, and Lacazette would all be credited with the same amount of xGChain here, which is not reflective of true contribution. A related quantity, **xGBuildup**, will divide up the xG equally amongst everyone who was involved _before_ the assist (i.e. Özil, Maitland-Niles, and Lacazette), but this too suffers from the same problem.
-   You can look at the **difference in xG** induced by each action in the buildup. This is better, but a threatening pass is not always one that goes to a good shooting position. For example, Özil's pass split the defence open, yet it wasn't received in a particularly good shooting position by Kolašinac. Rather, what makes Özil's pass special is that it puts Kolašinac in a position from where he can in turn easily create a good chance.

##### Can we do better?

Building off the deficiencies of existing approaches, we would like a framework that can:

1.  **Reward individual player actions** (passes, dribbles) in buildup play.
2.  Operate on **event-level data**, due to availability constraints.
3.  Reward actions **independent of the end outcome of the possession** (i.e. Özil's reward shouldn't depend on Aubameyang shooting or scoring).
4.  Reward moving the ball not just into high-xG shooting positions, but also into **'threatening' positions** that can in turn lead to high-xG shooting positions with high likelihood.

There is of course no single solution that is 'correct' here. As always, there's a trade-off between modelling complexity and accuracy. The purpose of this post, though, is to introduce one possible modelling approach, and walk through how it can be implemented and used to analyze buildup play.

Let's go through those requirements again, this time proposing and refining a solution as we go along:

1.  **Reward individual player actions:** our model should assign a score to each player action (pass or dribble) based on how much it contributed to the buildup play.
2.  **Event-level data:** we do not have access to any player tracking data; we only have a list of sequential events along with basic attributes for each event, such as the player in possession, time elapsed in the match, start location, end location, etc.
3.  **Independence from end outcome:** each action should be assigned a score in isolation, disregarding what happened before and after it in the possession. As far as relevant input signals go, this effectively leaves us with just the start and end locations of the action. How can we assign a score based on just those? We can build off the 'difference in xG' approach and assign a value to every location on the pitch. Then, if a certain action resulted in the ball moving from A to B, the score for the action can simply be the value at B minus the value at A.
4.  **Recognize 'threatening' positions:** while assigning a value to every location on the pitch, we must look beyond xG. The value generated by xG assumes that we will shoot in the next action. Yet there are many locations from where scoring directly is hard, but it is easy to move the ball into other higher-xG areas. While assigning values to locations, we need to recognize these high-threat locations. In other words, xG allows us only 1 action (i.e. shoot) from the current position, while to value threat we must consider the possibility of stringing together multiple actions.

Having made these modelling assumptions, our problem is now more digestible: **given a repository of event-level data, can we assign a threat value to every location on the pitch?**

**Note:** the idea of assigning a value to every location on the pitch, or creating a 'value surface', [isn't new](http://business-analytic.co.uk/blog/valuing-passes-and-thoughts-on-metrification/). In fact, it goes beyond much further than football analytics. For instance, there's a cool physics analogy with [electric potential](https://en.wikipedia.org/wiki/Electric_potential) fields to think about (or more generally, with any kind of [scalar field](https://en.wikipedia.org/wiki/Scalar_field)), where attributing a score to a player action is analogous to potential difference! Relatedly, it means that assigning values to actions in this manner leads to properties exhibited by [conservative forces](https://en.wikipedia.org/wiki/Conservative_force). For example, the exact path taken by a player while dribbling is irrelevant (path independence), while moving the ball in a loop results in a reward of 0. In reality, the exact dribbling path can of course be important, while moving in a loop might actually draw defenders out of position, so this is an inaccuracy we tolerate for simplicity as well as a lack of tracking data.

##### When in possession...

One simplified way of viewing buildup play is as follows: when a team has possession in a certain position, they can either shoot (and score with some probability), or move the ball to a different location via a pass or a dribble. This continues until the team either loses possession, or scores a goal.

If we run with this simplified model of buildup play, what does the data look like? From each position, how often do players shoot (and how often do they score?), how often do they move the ball, and where do they move it to? The following visualization aggregates data over a whole season (2017-18) of Premier League games, go ahead and explore how players behave by clicking on different zones!

After playing around with this view of the data, you should begin to see that every zone location \\((x, y)\\) has certain attributes:

-   **Move probability \\(m\_{x,y}\\):** when a player has possession in zone \\((x, y)\\), how often do they opt to move (i.e. pass or dribble) the ball as their next action?
-   **Shoot probability \\(s\_{x,y}\\):** when a player has possession in zone \\((x, y)\\), how often do they opt to shoot as their next action? In our simplified universe, players can only either move or shoot, so by definition \\(m\_{x,y} + s\_{x,y} = 100\\%\\).
-   **Move transition matrix \\(T\_{x,y}\\):** in the cases where the player moves from zone \\((x, y)\\), what is the probability that they move to each of the other zones? The visualization above shows these probabilities in shades of green.
-   **Goal probability \\(g\_{x,y}\\):** in the cases where the player shoots from zone \\((x, y)\\), what is the probability that the shot turns into a goal? Note that this quantity is essentially a very simple implementation of xG!

**Note:** for the purposes of this simplified model, we consider only 'successful' moves, i.e. moves that were completed without possession being lost. You could, quite easily, consider all attempted moves as well, though at the cost of making your model slightly more complex (and harder to concisely explain in a blog post!).

**Another note:** if you have a quantitative background, this might remind you of a [Markov model](https://en.wikipedia.org/wiki/Markov_model) where each grid location is a state, and passing or dribbling leads to state transitions.

##### Looking beyond checkmate

Now that we have some notation, let's recap what we're trying to do here. The problem with purely shot-based models like xG when it comes to analyzing buildup play is that many meaningful actions don't result in good shooting positions immediately, but rather lead to good shooting positions multiple actions later. This idea is put forth very eloquently by [Cervone et al.](https://www.lukebornn.com/papers/cervone_ssac_2014.pdf) in the context of basketball analytics (although this quote is surprisingly transferable to football).

"Despite many recent innovations, most advanced metrics remain based on simple tallies relating to the terminal states of possessions like points, rebounds, and turnovers. While these have shed light on the game, they are **akin to analyzing a chess match based only on the move that resulted in checkmate, leaving unexplored the possibility that the key move occurred several turns before**. This leaves a major gap to be filled, as an understanding of how players contribute to the whole possession – not just the events that end it – can be critical in evaluating players, assessing the quality of their decision-making, and predicting the success of particular in-game tactics."

So how can we look beyond checkmate given the data that we have? How can we assign values to zones that reflect not just their immediate shooting value, but the future rewards they can bring (through movements of the ball to other zones)? The key intuition here is that when you have possession in zone \\((x, y)\\), you have a choice: you can either shoot and score with some probability, or you can move the ball to a different location. Given this background, we can formulate the problem as follows.

**Note:** admittedly, the next couple of sections get quite technical (though I've tried to break down the math as much as possible). Although I'd strongly recommend reading through them, if you'd prefer to skip these and jump to the results of the model, click [here](https://karun.in/blog/expected-threat.html#visualizing-xt).

##### Deriving xT

**Note:** for the purposes of this post, we're working with a 16x12 grid on the pitch, which gives us 192 zones. In practice, you can choose a different resolution based on how much data you have!

Let \\(V\_{x,y}\\) be the 'value' that our algorithm assigns to zone \\((x, y)\\).

Now imagine you have the ball at your feet in zone \\((x, y)\\). You have two choices: shoot, or move the ball.

Based on past data, we know that whenever you shoot from here, you will score with probability \\(g\_{x, y}\\). Thus, if you shoot, your expected payoff is \\(g\_{x,y}\\).

Or, you can opt to move the ball via a pass to a teammate or by dribbling it yourself. But there's another choice to make here: which of the 192 zones should you move it to? Say you choose to move the ball to some new zone, \\((z, w)\\). In this case, your expected payoff is the value at zone \\((z, w)\\), i.e. \\(V\_{z, w}\\). But this was just one of the 192 choices that you had; how can we compute the expected payoff for all of the 192 choices in totality? Here's where the move transition matrix \\(T\_{x,y}\\) comes in: based on past data, we know where you're likely to move the ball to whenever you're in zone \\((x, y)\\), so we can proportionally weight the payoffs from each of the 192 zones. Specifically, for each zone \\((z, w)\\), the payoff is \\(T\_{(x,y)\\rightarrow(z,w)} \\times V\_{z,w}\\), i.e. the probability of moving to that zone times the reward from that zone. To get the total expected payoff for moving the ball, we must sum this quantity over all possible zones: $$\\sum\_{z=1}^{16} \\sum\_{w=1}^{12} T\_{(x,y)\\rightarrow(z,w)} \\times V\_{z,w} $$

Finally, let's piece it all together. We computed the payoff if you shoot as \\(g\_{x, y}\\), and the payoff if you move the ball as \\(\\sum\_{z=1}^{16} \\sum\_{w=1}^{12} T\_{(x,y)\\rightarrow(z,w)} \\times V\_{z,w}\\). Based on past data, we know that you tend to shoot \\(s\_{x,y}\\) percent of the time, and you opt to move the ball \\(m\_{x,y}\\) percent of the time. Therefore, let's weight these two outcomes based on the probability of each of them happening, to obtain our final value for zone \\(x, y\\): $$V\_{x,y} = (s\_{x,y} \\times g\_{x,y}) + (m\_{x,y} \\times \\sum\_{z=1}^{16} \\sum\_{w=1}^{12} T\_{(x,y)\\rightarrow(z,w)} V\_{z,w})$$ This quantity looks beyond the checkmate; it values locations based on not just the immediate shooting threat, but the potential to induce danger later in the possession sequence. It is inherently designed to capture a notion of 'threat', so **'Expected Threat' (xT)** seems like an apt name for it. Putting it all together with the updated variable name, we get the following equation: $$\\boxed{\\texttt{xT}\_{x,y} = (s\_{x,y} \\times g\_{x,y}) + (m\_{x,y} \\times \\sum\_{z=1}^{16} \\sum\_{w=1}^{12} T\_{(x,y)\\rightarrow(z,w)} \\texttt{xT}\_{z,w})}$$

##### But wait, there's more...

Unfortunately that formula on its own is buggy without one additional detail. If you look at the formula carefully, you'll see that it is flawed since computing the xT value for some zone \\((x, y)\\) requires that we _already_ know the xT value for all the other zones. But all the other zones also suffer from the exact same flaw, so this forms a cyclic dependency that we can't resolve easily!

Fortunately, in practice there is a neat workaround. All we need to do is start off with \\(\\texttt{xT}\_{x,y} = 0\\) for all zones \\((x, y)\\), and evaluate this formula not once, but **iteratively until convergence**. During each iteration, we evaluate the new xT for each zone by using xT values from the **previous iteration**. Empirically, I found 4-5 iterations to be sufficient for reasonable convergence, though this may vary based on your dataset.

Besides breaking the cyclic dependency and leading to convergence, this process comes with another added benefit: interpretability. Let's take a step back and think about what happens at iteration 1. At this point, we are using our initialization of xT = 0 for all zones. Here's what happens to our xT formulation: $$\\texttt{xT}\_{x,y} = (s\_{x,y} \\times g\_{x,y}) + (m\_{x,y} \\times \\sum\_{z=1}^{16} \\sum\_{w=1}^{12} T\_{(x,y)\\rightarrow(z,w)} \\texttt{xT}\_{z,w})$$ $$\\texttt{xT}\_{x,y} = (s\_{x,y} \\times g\_{x,y}) + (m\_{x,y} \\times \\sum\_{z=1}^{16} \\sum\_{w=1}^{12} T\_{(x,y)\\rightarrow(z,w)} \\cdot 0)$$ $$\\texttt{xT}\_{x,y} = (s\_{x,y} \\times g\_{x,y})$$ While not exactly xG, you can think of this as a value that represents how good a shooting position \\((x, y)\\) is. In other words, after iteration 1, we essentially have an xG model! An alternative way to think about this is that at iteration 1, we are only allowing the checkmate: we are valuing positions as though shooting was the only option, and passing and dribbling did not exist.

Now, in the second iteration, the new xT computation will use the xT values that were computed in iteration 1. At this point, the 'move' term in the formula will no longer be 0. This effectively means that we are now considering the possibility of "move, then shoot" in addition to just "shoot". We are now looking one move before the checkmate.

The same logic can be extended for multiple steps; for example, in the third iteration, we are additionally considering the possibility of "move, move, shoot" and looking up to two moves before the checkmate. This idea is powerful because it lends a very interpretable meaning to xT. Rather than being a score on an arbitrary scale, it has a very natural meaning (just like its distant cousin, xG). Specifically, \\(\\texttt{xT}\_{x,y}\\) at iteration \\(n\\) represents the probability of scoring within the next \\(n\\) actions.

##### Visualizing xT

Now that we have a way to find xT across the pitch, what does the end result look like? The visualization below shows a 2D as well as a 3D representation of the value surface generated by xT, using events across all the matches of the 2017/18 Premier League season. Use the slider to view the xT at different iterations within the algorithm, and hover/click to change zones on the pitch!

As you step through the successive iterations, it's worth noticing some interesting things:

-   At iteration 0, the map is flat since we initialize xT = 0 for all zones to begin with.
-   At iteration 1, we have effectively computed an xG model.
-   At each subsequent iteration, you can see the xT spread to areas further away from the goal (because, as explained above, each iteration essentially allows us to account for one more action in the buildup play).
-   The xT values begin to converge (to a reasonable degree) after 4-5 iterations.

##### Applying xT

Zooming out a bit, the point of xT was to come up with a metric that can quantify threat at any location on the pitch. Now that we have xT, we can value individual player actions in buildup play by computing the difference in xT between the start and end locations. In other words, we will say that an action that moves the ball from location \\((x, y)\\) to location \\((z,w)\\) has value \\(\\texttt{xT}\_{z,w} - \\texttt{xT}\_{x,y}\\). Once again, there is a nice interpretable meaning to this: the value of an action is equal to the % change in the team's chances of scoring in the next 5 actions due to the action (note that here we're using the xT computed after 5 iterations, hence 'next _5_ actions').

Now, let's try answering the Kolašinac-Özil credit assignment problem from before using the xT framework:

1.  Özil's pass takes the ball from xT = 0.077 to xT = 0.158. **Difference in xT due to Özil = 0.081**.
2.  Kolašinac's pass takes the ball from xT = 0.158 to xT = 0.171. **Difference in xT due to Kolašinac = 0.013**.

Looking at these numbers, Özil is responsible for \\(0.081 / (0.081 + 0.013) = 86\\%\\) of the net change in xT, so the framework would attribute 86% of the credit to him and 14% to Kolašinac.

**Note:** for simplicity, in this example I've discretized start and end locations to the grid cell that they fall in. However, if you're doing some kind of sophisticated analysis where precision matters a lot, you might want to use [bilinear interpolation](https://en.wikipedia.org/wiki/Bilinear_interpolation). You can still compute the xT map using a fixed-size grid, but when computing values for events, you can use the exact location coordinates to get more precise estimates!

###### Your estimate



###### xT's estimate



###### Top xT creators

As a sanity check, let's also look at the top xT creators during the 2017/18 Premier League season. The table below shows the top 15 players in the league whose actions created the **highest cumulative change in xT**. Note that this is not normalized by the number of actions taken – it is based on the raw sum of xT created. This is intentional, because it surfaces players who not only know how to create danger, but those who do it consistently at a high volume. The inclusion of Holebas at #3 might surprise you, but the left-back has established himself as Watford's most consistent and most dangerous creator.

Rank

Player

Team

xT Created

Besides simple credit assignment in buildup play, the xT framework opens the door for a host of other applications. For example, so far I've only shown xT results using an entire season's worth of Premier League data: but of course, this means we lose team-specific information. There's no doubt that teams behave differently in possession, prioritizing different areas of the pitch and exploiting different paths to goal based on their strengths (and weaknesses). What happens if, instead of clubbing all the Premier League teams into one analysis, we **compute xT on a per-team basis**?

###### Visualizing per-team xT

**Note:** reminder that this is based on data from the 2017/18 season and _not_ the current season!

Sure enough, we do see a lot of variance across different teams. In addition to changes in the shape of the xT curve, note the differences in height. For instance, the shape of Manchester City and Spurs' curves are similar (which means they value the ball in similar areas of the pitch), yet their xT magnitudes are very different. This tells us that given the ball in the same position, City are much more threatening than Spurs (due to their higher conversion rate of possessions into goals).

While these per-team xT maps are interesting to look at, they're not very actionable on their own. That being said, the underlying data is powerful because it can give us a team-specific view into how danger is created through buildup play. For example, one useful question to answer during pre-match analysis might be: **where on the pitch do our opponents tend to create the most danger from?**

To answer this, we can use our opponent's xT map to value all of their actions from past matches, and aggregate these values based on the start location of the action. In other words, for each grid location, we can look at the actions that _originated_ there, and sum the xT created by these actions. This will give us a per-location cumulative value that will highlight the amount of danger created from different areas of the pitch. Additionally, by highlighting the common end zones of actions starting in a particular zone, we can start to see our opponent's most dangerous passages of play. To make this even more useful for tactical preparation, we might want to also know _who_ are the players that are responsible for creating threat through these passages.

The visualization below attempts to answer precisely these questions. The green map shows zones from where maximum xT is created. Hovering/clicking on a zone will show you the dangerous passages of play that originate there, as well as the players most responsible for them. Use the dropdown menu to switch to any other Premier League team!

###### Who creates danger from where?



##### Future work

These were just a couple of applications of xT, and there are many more left to explore. The ability of xT to capture the on-the-ball behaviour of teams leads to several promising directions. Looking at how xT changes during the course of a possession sequence may help us, for example, in **identifying and analyzing patterns of play** such as counter-attacks. At the player level, we can assess an individual **player's decision-making** relative to how his team tends to play: "Is this player making high-reward passing choices given his team's xT profile? Would he be better off shooting rather than dribbling in certain areas?" Perhaps even more interesting is answering similar questions in the context of **player scouting**: "Can we tell if this player, who has never played for us, will fit into our system? Does he have a history of creating actions that will lead to high xT gains for us?"

If there are any directions that you're particularly excited about or want to explore together, please let me know! I'll continue to explore the limits of xT and will publish relevant results on my Twitter and on this blog.

##### Let's talk!

I'd love to hear any thoughts or feedback you might have; please reach out to me on Twitter at [@karun1710](https://twitter.com/karun1710) or via email at [karun.singh17@gmail.com](mailto:karun.singh17@gmail.com)!

Services asked: Wayback Machine; karun.in.
````

### x03 — match_quote {"source": "https://karun.in/blog/expected-threat.html", "quote": "a threatening pass is not always one that goes to a good shooting position"}

````text
# Quote check: Introducing Expected Threat (xT)

- **Source:** https://karun.in/blog/expected-threat.html
- **Wayback snapshot:** https://web.archive.org/web/20260922114139/https://karun.in/blog/expected-threat.html

**Result: exact.** The quote appears word for word.

- **Where:** section 2 (Existing approaches), characters 843 to 917
- **Text quote selector** (W3C):

```json
{
  "type": "TextQuoteSelector",
  "exact": "a threatening pass is not always one that goes to a good shooting position",
  "prefix": "induced by each action in the buildup. This is better, but ",
  "suffix": ". For example, Özil's pass split the defence open, yet it"
}
```

Services asked: Wayback Machine; karun.in.
````

### x04 — match_quote {"source": "https://karun.in/blog/expected-threat.html", "quote": "xT was first introduced by Opta in 2012 as a proprietary model"}

````text
# Quote check: Introducing Expected Threat (xT)

- **Source:** https://karun.in/blog/expected-threat.html
- **Wayback snapshot:** https://web.archive.org/web/20260922114139/https://karun.in/blog/expected-threat.html

**Result: none (similarity 0.31).** The quote does not appear in the source.


Services asked: Wayback Machine; karun.in.
````
