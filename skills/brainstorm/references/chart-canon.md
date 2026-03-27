# Football Data Visualisation

Canonical chart types, design conventions, colour strategies, and anti-patterns specific to football analytics visualisation.

---

## The Football Analytics Chart Canon

### StatsBomb Radar (Pizza Chart)

Each spoke represents a metric normalised to a percentile rank within a positional peer group. Top/bottom 5% define boundaries.

**What makes the good ones good:**
- Per-90 normalisation for fair cross-player comparison
- Defensive metrics adjusted for team possession share
- Positional templates (attacking, defensive, midfield) -- not one-size-fits-all
- Percentile boundaries anchored to a defined population
- Actual numeric values shown alongside the visual

**Known weaknesses:** The eye focuses on area, not spoke length. Area is a function of variable ordering (arbitrary). Limit to 6-8 metrics maximum. Consider bar charts for precise comparison or distribution plots for statistical rigour.

### xG Shot Maps

Shot locations on a half-pitch, circle area encoding xG value. Solid circles for goals, translucent for misses.

**Conventions:**
- Circle **area** (not radius) maps to xG
- Home on left, away on right
- Edge/stroke colour can encode shot type (open play, set piece, penalty)
- Half-pitch preferred over full pitch for shot data

### Cumulative xG Timelines

Step-function chart showing expected goals accumulating over match time with goal event annotations. This has become the standard "match story" chart.

**Design essentials:**
- **Step function** (not smooth line) -- xG jumps at each shot, it does not flow continuously
- X-axis from 0 to 90+ (not just first-to-last shot; a football match has a defined duration)
- Goal annotations: scorer name and minute at the step point where the line steps up most significantly
- Two colours for home/away with clear legend
- Exclude penalties and own goals from xG totals (or annotate separately) for analytical purity
- Always extend the x-axis to the full match duration, including added time

### Passing Networks

Nodes at players' average passing/receiving positions. Edge thickness encodes pass frequency. Minimum threshold (e.g., 13+ passes) prevents visual clutter.

**Conventions:**
- Left-to-right horizontal orientation (matches how football is watched on TV)
- Node size can encode total involvement (passes + receptions)
- Weighted views (attack-weighted, defence-weighted) add analytical depth
- Interactive versions benefit from metric tabs and weighting sliders that reveal different tactical stories from the same underlying data
- Consider separating the network into offensive and defensive phases for clearer analysis

### Heat Maps

Kernel density estimation over touch/action locations. Key design detail: normalise colour boundaries so low-touch players do not get artificially hot colours. Without normalisation, a midfielder with 70 touches will always appear "hotter" than a centre-back with 30, even if the centre-back's touches are more spatially concentrated. The fix is adjusting heat boundaries per player or per position group.

### Pitch Control Models

Continuous surface showing which team controls each area. Blue vs red colouring. Requires tracking data (not just event data).

### Expected Threat (xT)

16x12 pitch grid with threat values per zone based on probability of possession leading to a goal. Visualised as 2D heatmap (green gradient) or 3D value surface.

---

## The Pitch as Canvas

### View Selection

| Use case | View | Rationale |
|---|---|---|
| Shot maps | Half pitch (attacking end) | Only attacking half matters |
| Passing networks | Full pitch, horizontal | Shows team shape across entire surface |
| Defensive actions | Full pitch or defensive half | Shows pressing height and compactness |
| Heat maps | Full pitch | Full spatial profile |
| Progressive carries/passes | Full pitch with arrows | Needs full surface for progression |
| xT value surface | Full pitch grid | Model applies everywhere |

### When to Abstract Away the Pitch

Use the pitch when spatial position is meaningful. Abstract it away when the insight is about magnitude, ranking, or trend over time:
- Radar/pizza charts: abstract entirely from geography
- xG timelines: time is x-axis
- Bump charts / league tables: ranking over time
- Rolling averages: temporal, not spatial

### Pitch Rendering Details

- **Orientation:** Left-to-right (horizontal) strongly preferred -- matches how viewers watch football on TV and in stadiums
- **Colour:** Muted pitch (light green or neutral grey) so data marks stand out. Many professional visualisations use grey/white pitch to avoid green competing with data colours
- **Dimensions:** Standard 105m x 68m (standardised coordinate systems in libraries). Real pitches vary but most viz libraries use a standard system
- **Markings:** Centre circle, penalty areas, goal areas for orientation. Halfway line and penalty spots essential. Corner arcs optional detail
- **Key libraries:** d3-soccer (D3 plugin with heatmap generation, action markers, tooltip support, two pitch layers #below and #above), mplsoccer (Python standard), Soccermatics (Python with built-in shot maps and passing networks)

### Notable Practitioners to Learn From

- **John Burn-Murdoch (FT):** Heavy annotation advocate. Research shows readers prefer charts with many well-placed annotations. Charts should feel like a complete story with beginning and end.
- **Tom Worville (formerly Athletic, now RB Leipzig):** "Lionel Messi's Ten Stages of Greatness" is a landmark in football data storytelling -- helped bring xG to mainstream audiences.
- **Mark Thompson (Twenty3):** Key insight on heatmap normalisation -- adjusting colour boundaries so players with fewer touches do not receive artificially hot colours.
- **Karun Singh (formerly Arsenal FC):** Created Expected Threat (xT). His interactive work includes iteration sliders, zone hover-for-detail, and weighted view sliders for passing networks.
- **StatsBomb:** Pioneered making advanced metrics accessible through consistent, well-designed visualisations. Open data initiative catalysed the entire football viz ecosystem.

---

## Season-Level and Multi-Season Storytelling

### Bump Charts for League Position

Y-axis inverted (1st at top). Key design choice: **highlight-and-dim** -- one or two teams in colour, everything else in grey. Do not try to colour all 20 teams.

### Rolling Averages

10-game rolling average is standard window for football form data. Shorter windows too noisy; longer windows lag. For xG rolling averages, window matters even more because individual match xG has very high variance.

### Handling Promoted/Relegated Teams

1. **Break the line** -- honest about the data gap
2. **Grey out the gap** -- faded/dashed section maintaining visual identity
3. **Small multiples per team** -- each team gets own panel
4. **Heatmap with empty cells** -- missing seasons as blank cells

### Form Guide Pattern

Recent results (W/D/L) as coloured blocks or circles in sequence. Convention: **green for win, amber for draw, red for loss**. Define as design tokens (`--color-win`, `--color-draw`, `--color-loss`). Add shape/pattern as secondary encoding for colour-blind accessibility. Red-green is the most common colour-blindness axis, so relying on colour alone is insufficient.

### FBRef Scouting Report Pattern

FBRef's scouting reports compare a player's statistics as percentile rankings against positional peers. The design -- horizontal bar chart with colour-coded percentile bands -- is clean, information-dense, and immediately interpretable. Key design decisions:
- Percentile rank against a clearly defined comparison group (league, position, minutes threshold)
- Raw numeric values shown alongside the visual bar
- Grouping related metrics (shooting, passing, defence) into sections
- The horizontal orientation allows natural left-to-right reading of magnitude

---

## Match-Level Visualisation

### Momentum Charts

Minute-by-minute pressure using vertical bars. Sharp spikes follow goals, cards, or tactical changes. Can use expected threat (xT) as the underlying signal.

### Win Probability Charts

Probability of each outcome (home win, draw, away win) evolving over match time. Football is low-scoring, so probabilities change in large jumps at goals and subtle drifts during open play. Context matters: 0-0 at 80 minutes is very different from 0-0 at 20 minutes.

### The 90-Minute Challenge

A 90-minute match typically has only 20-30 shots total:
- **Sparse-event charts** (shot maps, xG timelines) must handle long stretches of nothing
- **Continuous-flow charts** (momentum, possession) must balance signal vs noise
- **Hybrid approaches** overlay sparse events on continuous backgrounds

---

## Colour in Football Visualisation

### When Club Colours Work

- **Single-team focus:** Use primary colour boldly
- **Head-to-head:** Two teams with contrasting colours (Liverpool red vs Chelsea blue)
- **Small multiples:** Each panel is one team; colour is identification, not differentiation

### When Club Colours Clash

The Premier League has significant colour collisions:
- Multiple reds: Liverpool, Man Utd, Arsenal, Nottingham Forest, Southampton
- Multiple blues: Chelsea, Man City, Everton, Leicester, Brighton
- Never rely on colour alone to distinguish more than ~8 categories. For 20 teams, colour alone simply does not work.

### Solutions for Multi-Team Charts

1. **Highlight-and-dim:** Team(s) of interest in colour; everything else in grey. Most effective single technique for 20-team charts.
2. **Direct labelling:** Label each line/point directly. Eliminates need for 20 distinguishable colours.
3. **Small multiples:** Each team gets own panel.
4. **Club badge as marker:** Badge as data point marker (common in social media graphics).
5. **Sequential palette:** When ranking by one metric, use single-hue light-to-dark rather than 20 categorical colours.
6. **Redundant encoding:** Combine colour with pattern, shape, or label.

---

## Interactive Football Charts

### Interactions That Add Value

| Interaction | Value |
|---|---|
| **Filter by team** | Essential for multi-team views (dropdown or club picker) |
| **Hover for detail** | Precise values without cluttering the view |
| **Toggle metrics** | Switch perspectives (e.g., between teams) |
| **Weighting slider** | Continuous control over emphasis |
| **Time scrubbing** | Navigate through match or season |
| **Brushing and linking** | Select in one view, highlight in another |
| **Small multiples with shared hover** | Synchronised highlighting across panels |

### Interactions That Are Gimmicky

- 3D pitch rotations that add drama but make data harder to read
- Auto-playing animations users cannot control
- Excessive transitions that slow exploration
- Pan and zoom on small datasets where all data fits on screen

### Notable Interactive Patterns

- **Iteration sliders** for models like xT: show how values converge over computation iterations, building intuition for the model.
- **Weighted view sliders** for passing networks: unweighted to fully attack-weighted, revealing different tactical structures from the same data.
- **Zone hover-for-detail** on pitch grids: hover any zone to see its specific value without cluttering the overall view.
- **Team dropdown selectors** that swap data without changing the chart structure, enabling quick cross-team comparison.

---

## Football Visualisation Anti-Patterns

### Overloaded Radars
More than 10-12 spokes becomes unreadable. Variable ordering changes shape dramatically. Fix: 6-8 metrics maximum per template. Group related metrics together.

### Misleading xG Presentations
Single-match xG has enormous variance. Fix: always provide rolling averages for trend analysis. For single matches, show shot map alongside xG total. Never present xG without context about normal ranges.

### Too Many Metrics
A chart should answer one question. Use progressive disclosure -- headline metric first, drill down to supporting metrics.

### Small Sample Sizes
State sample size clearly. Use confidence intervals or faded encodings for small samples. Consider minimum appearance thresholds (e.g., 900+ minutes).

### Cherry-Picking Metrics
Use balanced templates showing multiple dimensions. Present metrics that could contradict the narrative alongside supporting ones.

### Context-Free Percentiles
Always show percentile rank against a clearly defined comparison group (league, position, minutes threshold).

### Deceptive Pitch Maps
Heat maps showing raw touch counts make high-possession teams look like they control every area. Fix: normalise by opportunity (defensive actions per opposition pass, not raw counts).

### Ignoring the Temporal Dimension
A whole season aggregated into one map loses the story of early vs late performance. Fix: provide time-series views alongside aggregate views.

---

## Design Principles Synthesis

1. **"Compared to what?"** Every metric needs context -- league average, positional peers, same player last season.
2. **One chart, one question.** Resist cramming multiple insights into one view.
3. **Annotate generously.** Research shows readers prefer heavily annotated charts over minimalist ones.
4. **Highlight and dim.** For multi-team views, colour only team(s) of interest; grey everything else.
5. **Show uncertainty.** Confidence intervals, faded regions, explicit sample sizes build trust.
6. **Pitch when spatial, abstract when temporal.** Use pitch as canvas when geography matters; standard chart types when it does not.
7. **Per-90 is the baseline.** Normalise everything by playing time.
8. **Direct label over legend.** Especially important for interactive charts where legends may scroll out of view.
