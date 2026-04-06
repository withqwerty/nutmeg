# Campos Plan 2 — S1 Risk-First Dogfood

**Spec:** `docs/superpowers/specs/2026-04-05-campos-design.md` (v2.1)
**Predecessor:** Plan 1 (S0 Validation) — completed, all gates passed
**Scope:** Build ShotMap to full 12-axis green + PlayerHero to styled stub + theme light variant + composition API
**Repo:** `/Users/rahulkeerthi/Work/campos`

---

## Why S1 exists

S0 proved agents can discover and invoke stubs. S1 proves the hardest component (ShotMap) can reach production quality across the 12-axis bar within the 10-day commitment window. If ShotMap closes, the remaining components are lower-risk. If it doesn't, the axis-flex rules fire automatically.

### S0 signals driving this plan

1. **Composition API** — 8/20 eval tasks needed multi-component layout; every agent invented a different hack
2. **Theme inconsistency** — player_hero ignores theme; shot_map uses dark pitch colours regardless of theme state
3. **Light theme missing** — `use_theme("light")` raises ValueError; audience audit repos show light backgrounds are common
4. **ShotMap is the highest-frequency hand-rolled component** — appeared in 6/10 audited repos

---

## Files this plan creates or modifies

### New files
```
docs/estimates/shotmap.md                  # Task 1: baseline time estimates
docs/component_log/shotmap.md              # Task 2: commitment device
theme/tokens_light.json                    # Task 4: light theme tokens
python/src/campos/theme/_rcparams_light.py # Task 4: generated light rcParams
python/src/campos/compose.py               # Task 5: composition helper
python/tests/fixtures/                     # Task 7+: test fixture data files
python/tests/test_shot_map.py              # Tasks 7-16: 12-axis test suite
python/tests/test_compose.py               # Task 5: composition tests
python/tests/test_player_hero.py           # Task 18: PlayerHero typography tests
```

### Modified files
```
python/src/campos/components/shot_map.py   # Tasks 7-16: real implementation
python/src/campos/components/player_hero.py # Tasks 17-19: typography upgrade
python/src/campos/theme/api.py             # Task 4: light variant support
python/src/campos/theme/_rcparams.py       # Task 4: rename to _rcparams_dark.py or refactor
python/src/campos/theme/__init__.py        # Task 4: re-exports
python/src/campos/__init__.py              # Task 5: export compose
python/tests/test_stubs.py                 # Tasks 7+: migrate to test_shot_map.py
scripts/generate_python_theme.py           # Task 4: support light variant generation
theme/tokens.json                          # Task 4: add light variant section or keep separate file
```

---

## Task execution tiers

Same model as Plan 1. Tasks are grouped into milestones (A–F). Each milestone is a logical checkpoint.

- **Tier 1 (mechanical):** File creation, config, scaffolding — execute without review
- **Tier 2 (judgement):** Implementation decisions, visual output — verify tests pass
- **Tier 3 (creative):** Visual design, typography, composition — inspect rendered output

---

## Milestone A: Pre-build ceremony (Tasks 1–3)

### Task 1 — Baseline estimate ritual

**Tier:** 1 (mechanical)
**Spec ref:** N6 (axis-flex rule)

Create `docs/estimates/shotmap.md` with per-axis hour estimates for ShotMap.

```markdown
# ShotMap Baseline Estimate

**Author estimate, committed before S1 build begins.**
**Rule (N6):** If actual exceeds these thresholds, axis-flex fires automatically:
- >150% total → Axis 11 (A11y) defers to v1.x for all subsequent components
- >200% total → Axis 7 A4 clause also defers (responsive 400/800/1200/1600 stays)
- >250% total → full replan

| Axis | Name | Estimate (hours) | Actual (hours) | Notes |
|------|------|:-----------------:|:--------------:|-------|
| 1 | Empty | 0.5 | | Stub already handles; add snapshot test |
| 2 | Sparse | 0.5 | | 1-shot layout verification |
| 3 | Dense | 2.0 | | 500+ shots, hex binning or truncation |
| 4 | Missing | 1.0 | | NaN xG, None outcome, missing coords |
| 5 | Extreme | 1.0 | | Negative/overflow xG, duplicate coords |
| 6 | Text edges | 1.0 | | Unicode title, long team names |
| 7 | Responsive | 2.0 | | 400/800/1200/1600 px widths |
| 8 | Themeable | 2.0 | | Dark + light + club accent |
| 9 | Composable | 1.0 | | Returns Figure, subplot-friendly |
| 10 | Mpl hygiene | 0.5 | | No global rcParams mutation |
| 11 | A11y | 3.0 | | Contrast ratios, alt text, dual encoding |
| 12 | Tested | 2.0 | | Snapshot tests for all fixtures above |
| — | **Total** | **16.5** | | |

Per-axis average: 1.375 hours. Flex threshold (>2 days/axis = >16 hours/axis) is not expected to fire.
```

Commit: `docs(s1): add ShotMap baseline estimate (16.5h total)`

---

### Task 2 — Commitment device

**Tier:** 1 (mechanical)
**Spec ref:** N2 (10-day escape hatch)

Create `docs/component_log/shotmap.md`:

```markdown
# Component Log: ShotMap

- **Component:** ShotMap
- **Start date:** YYYY-MM-DD (fill when S1 build begins)
- **Cut date:** YYYY-MM-DD (10 working days after start)
- **In-scope axes:** 1–12 (all; subject to N6 flex rule if actuals exceed baseline)

If this component is not green on all in-scope axes by end of day on the cut date, it is cut from v1. This decision is not re-litigated.

## Daily log

| Day | Date | Work done | Axes advanced | Cumulative hours |
|-----|------|-----------|:-------------:|:----------------:|
| 1 | | | | |
| 2 | | | | |
| ... | | | | |
| 10 | | | | |

## Day-11 result

**Status:** (green / cut — fill on day 11)
**Public declaration:** (link to GitHub issue or post)
```

Commit: `docs(s1): add ShotMap commitment device`

---

### Task 3 — Nutmeg readiness gate (N5)

**Tier:** 2 (judgement)
**Spec ref:** N5

Verify that nutmeg's `acquire` skill can emit Campos-schema Shot objects from at least one provider the target audience uses (FBref, WhoScored, or similar via soccerdata/scraping).

**Steps:**
1. In the nutmeg repo, check if `acquire` can produce a DataFrame with columns mappable to Shot schema (x, y normalised 0-1, xg, outcome)
2. If yes: document the provider and mapping in `docs/estimates/shotmap.md` under a "Data pipeline" section
3. If no: document the gap. Per N5, this doesn't block S1 (ShotMap can be built with fixture data) but launch timing may be affected

**Expected outcome:** Gate passes with FBref shot data via soccerdata. If it doesn't, note the gap but proceed with S1 — the eval already proved agents can use fixture data.

Commit: `docs(s1): verify nutmeg acquire readiness for Shot data`

---

## Milestone B: Theme upgrade (Tasks 4–6)

### Task 4 — Light theme variant

**Tier:** 2 (judgement)

The dark theme exists. Add a light variant so ShotMap (Task 7+) and PlayerHero (Task 17+) can be tested against both themes for Axis 8.

**Steps:**

1. Create `theme/tokens_light.json` with inverted surface/text colours:
   ```json
   {
     "color": {
       "surface": { "base": "#ffffff", "hero": "#f5f5f7", "chip": "#e8e8ed" },
       "text": { "primary": "#1a1a1a", "secondary": "#6b7280" },
       "accent": { "primary": "#059669", "secondary": "#7c3aed" },
       "border": { "hairline": "#d1d5db" }
     }
   }
   ```
   Keep typography, spacing, radius identical to dark tokens.

2. Update `scripts/generate_python_theme.py` to accept a `--variant` flag and generate both `_rcparams_dark.py` and `_rcparams_light.py`

3. Run the generator for both variants

4. Refactor `python/src/campos/theme/api.py`:
   - `use_theme("dark")` applies dark rcParams (existing behaviour)
   - `use_theme("light")` applies light rcParams (currently raises ValueError — fix this)
   - `use_theme()` defaults to "dark" (unchanged)
   - `theme("light")` context manager works correctly

5. Add tests to `python/tests/test_theme.py`:
   - `test_use_theme_light_applies_light_rcparams`
   - `test_theme_context_manager_light`
   - `test_unknown_theme_still_raises`

Commit: `feat(theme): add light variant with inverted surface/text tokens`

---

### Task 5 — Composition helper

**Tier:** 2 (judgement)

Address the #1 S0 gap: agents inventing composition hacks. Create a `campos.compose()` function that lays out multiple Campos Figures into a single Figure.

**Steps:**

1. Create `python/src/campos/compose.py`:

   ```python
   def compose(
       figures: Sequence[Figure],
       *,
       layout: str = "vertical",  # "vertical" | "horizontal" | "grid"
       title: str | None = None,
       figsize: tuple[float, float] | None = None,
   ) -> Figure:
   ```

   **Implementation approach:**
   - Rasterize each input Figure to an RGBA array via `canvas.draw()` + `buffer_rgba()`
   - Create a master Figure with subplots matching the layout
   - `imshow()` each rasterized image into its subplot
   - Close the input Figures to prevent memory leaks
   - This is the same pattern the eval agents invented — we're just standardising it

2. Add to `python/src/campos/__init__.py`:
   ```python
   from campos.compose import compose
   ```

3. Create `python/tests/test_compose.py`:
   - `test_compose_vertical_two_figures`
   - `test_compose_horizontal_two_figures`
   - `test_compose_grid_four_figures`
   - `test_compose_single_figure_passthrough`
   - `test_compose_with_title`
   - `test_compose_empty_raises_valueerror`

Commit: `feat(api): add compose() helper for multi-component layout`

---

### Task 6 — Component theme auto-application

**Tier:** 2 (judgement)

S0 showed player_hero renders with white matplotlib defaults while shot_map gets dark pitch colours from mplsoccer. Fix: components should respect the active Campos theme.

**Steps:**

1. In each component (`shot_map.py`, `player_hero.py`, `percentile_ribbon.py`), read the current `matplotlib.rcParams` at render time to pick colours:
   - `fig_facecolor = mpl.rcParams['figure.facecolor']`
   - `text_color = mpl.rcParams['text.color']`
   - Don't call `use_theme()` inside components — that would mutate global state (Axis 10 violation). Instead, respect whatever rcParams the user has set.

2. For `shot_map.py`, the mplsoccer pitch colours should read from rcParams too:
   - `pitch_color` → `mpl.rcParams['axes.facecolor']`
   - `line_color` → `mpl.rcParams['axes.labelcolor']` or the secondary text token

3. For `player_hero.py`, set `fig.patch.set_facecolor(mpl.rcParams['figure.facecolor'])` and use `mpl.rcParams['text.color']` for text

4. Add tests:
   - `test_shot_map_respects_light_theme` — apply light theme, render, check pitch background is not dark
   - `test_player_hero_respects_dark_theme` — apply dark theme, render, check fig facecolor is dark

Commit: `fix(components): respect active theme rcParams instead of hardcoding colours`

---

## Milestone C: ShotMap core implementation (Tasks 7–10)

Replace the 30-line scatter stub with the real component.

### Task 7 — ShotMap core: xG-sized markers + outcome colours

**Tier:** 3 (creative)

Replace the stub scatter with proper shot rendering.

**Steps:**

1. Replace the body of `shot_map()` in `python/src/campos/components/shot_map.py`

2. **Marker sizing:** Scale by xG. Use `s = xg * 400 + 40` (minimum 40pt for visibility, max ~440pt for xG=1.0). This replaces the stub's `max(50, xg * 600)`.

3. **Outcome colours** (from tokens):
   - `goal` → accent.primary (`#7cd3a3` dark / `#059669` light)
   - Non-goal outcomes → accent.secondary (`#a78bfa` dark / `#7c3aed` light)
   - Read from rcParams or tokens at render time, not hardcoded

4. **Coordinate handling:** Keep the 0-1 → 0-100 pitch scaling. Shots with `x is None or y is None` silently skipped (existing behaviour).

5. **Empty state:** Keep the `(no shots with coordinates)` placeholder (existing behaviour, Axis 1).

6. Create `python/tests/fixtures/` directory with test fixture files:
   - `shots_basic.json` — 5 shots (2 goals, 3 non-goals) for basic rendering
   - `shots_empty.json` — empty list
   - `shots_sparse.json` — 1 shot
   - `shots_dense.json` — 500 shots (generated with random coords + xG)

7. Migrate shot_map tests from `test_stubs.py` to `python/tests/test_shot_map.py`. Keep `test_stubs.py` for player_hero and percentile_ribbon stubs.

Commit: `feat(shot_map): replace stub with xG-sized markers and outcome colours`

---

### Task 8 — Body-part shape encoding

**Tier:** 2 (judgement)
**Spec ref:** "shot-type shapes"

Add marker shape differentiation by body part.

**Steps:**

1. Map `Shot.body_part` to matplotlib marker shapes:
   - `"foot"` → `'o'` (circle, default)
   - `"head"` → `'D'` (diamond)
   - `"other"` → `'s'` (square)
   - `None` → `'o'` (circle, fallback)

2. Since mplsoccer's `pitch.scatter()` doesn't support per-point markers, render one scatter call per body-part group:
   ```python
   for body_part, marker in [("foot", "o"), ("head", "D"), ("other", "s"), (None, "o")]:
       group = [s for s in plottable if (s.body_part or "foot") == (body_part or "foot")]
       if group:
           pitch.scatter(xs, ys, s=sizes, c=colours, marker=marker, ...)
   ```

3. This satisfies Axis 11 partial (colour is not the only encoding — shape also differentiates).

4. Add fixture: `shots_body_parts.json` — shots with mixed body parts

5. Add tests:
   - `test_head_shots_use_diamond_marker`
   - `test_foot_shots_use_circle_marker`
   - `test_none_body_part_defaults_to_circle`

Commit: `feat(shot_map): add body-part shape encoding (foot/head/other)`

---

### Task 9 — Axes 1–2: empty + sparse edge cases

**Tier:** 1 (mechanical)

Formalise the empty and sparse handling with snapshot tests.

**Steps:**

1. **Axis 1 (Empty):** Already works from stub. Add explicit tests:
   - `test_empty_list_renders_placeholder` — verify "(no shots with coordinates)" text exists
   - `test_all_shots_missing_coords_renders_placeholder` — shots with `x=None` only

2. **Axis 2 (Sparse):** 1 shot must render with visible marker, no broken layout:
   - `test_single_shot_renders_visible_marker` — check PathCollection has 1 point
   - `test_single_goal_renders_in_goal_colour`
   - Verify axis limits are sensible (not zoomed to a single point)

3. Save reference PNGs to `python/tests/fixtures/reference/` for visual regression (manual inspection, not pixel-diff — matplotlib rendering varies across platforms).

Commit: `test(shot_map): add Axis 1 (empty) and Axis 2 (sparse) tests`

---

### Task 10 — Axes 3–5: dense, missing, extreme

**Tier:** 2 (judgement)

**Axis 3 (Dense):**
1. Render 500 shots. Verify:
   - No performance cliff (render completes in <5 seconds)
   - No overflow / overlapping that makes the plot unreadable at standard figsize
   - Consider alpha transparency for dense scatter: `alpha=0.7` to handle overlap
2. Add test: `test_500_shots_renders_under_5_seconds`

**Axis 4 (Missing):**
1. Shots with `xg=NaN` → skip or use fallback size (minimum marker)
2. Shots with `outcome=None` → use non-goal colour
3. Shots with `x=None` or `y=None` → already skipped
4. Add tests:
   - `test_nan_xg_shot_uses_minimum_marker_size`
   - `test_none_outcome_uses_non_goal_colour`

**Axis 5 (Extreme):**
1. `xg < 0` → clamp to 0 for sizing, don't crash
2. `xg > 1` → clamp to 1 for sizing, don't crash
3. `x` or `y` outside 0-1 → clamp to 0-1 range (don't render outside pitch)
4. Add tests:
   - `test_negative_xg_clamped_to_minimum_size`
   - `test_xg_above_one_clamped_to_maximum_size`
   - `test_coordinates_outside_unit_range_clamped`

Commit: `feat(shot_map): handle dense (500+), missing (NaN), and extreme (out-of-range) data`

---

## Milestone D: ShotMap quality axes (Tasks 11–14)

### Task 11 — Axis 6: text edges

**Tier:** 2 (judgement)

ShotMap doesn't display player names by default, but it may show a title. Test that title text with Unicode, long names, and special characters renders correctly.

**Steps:**

1. Add an optional `title: str | None = None` parameter to `shot_map()`:
   ```python
   def shot_map(shots: Sequence[Shot], *, title: str | None = None) -> Figure:
   ```
   If provided, render as `fig.suptitle(title, ...)` using theme-aware text colour.

2. Add tests with edge-case titles:
   - `test_unicode_title_renders` — `"Ødegaard — Arsenal"`
   - `test_cjk_title_renders` — `"张伟 — Beijing Guoan"`
   - `test_long_title_no_clipping` — 60-character title
   - `test_rtl_characters_render` — `"عمر مرموش"`

3. Verify no `UnicodeDecodeError` or clipped text in any case.

Commit: `feat(shot_map): add optional title parameter with text-edge tests`

---

### Task 12 — Axis 7: responsive rendering

**Tier:** 2 (judgement)

Verify ShotMap renders correctly at multiple output widths.

**Steps:**

1. Add tests that render at 400, 800, 1200, 1600 px widths:
   ```python
   @pytest.mark.parametrize("width_px", [400, 800, 1200, 1600])
   def test_responsive_width(width_px):
       dpi = 100
       figsize_w = width_px / dpi
       shots = load_fixture("shots_basic.json")
       fig = shot_map(shots)
       fig.set_size_inches(figsize_w, figsize_w)  # square
       fig.savefig(io.BytesIO(), format="png", dpi=dpi)
       # If it renders without error, pass
   ```

2. Visually inspect the 400px render (smallest) — markers should be visible, not sub-pixel. If markers are too small at 400px, add a `min_marker_size` floor.

3. A4 print test (deferrable per N6 if actuals exceed baseline):
   - Render at 210mm × 148mm (A4 half-page) at 300 DPI
   - Verify no clipping

Commit: `test(shot_map): add Axis 7 responsive rendering tests (400-1600px)`

---

### Task 13 — Axis 8: themeable + club accent

**Tier:** 2 (judgement)

**Steps:**

1. Verify shot_map renders correctly with both dark and light themes:
   - `test_dark_theme_dark_pitch` — pitch background matches dark surface.hero
   - `test_light_theme_light_pitch` — pitch background matches light surface.hero

2. Add club accent override. When the user sets a custom accent colour via rcParams before calling shot_map, goal markers should use that colour:
   ```python
   # User code:
   mpl.rcParams['campos.accent.primary'] = '#C8102E'  # Liverpool red
   fig = shot_map(shots)
   ```
   Implementation: check for a custom `campos.accent.primary` rcParam key; if not set, fall back to the theme default.

3. Add tests:
   - `test_club_accent_overrides_goal_colour`
   - `test_default_accent_when_no_override`

Commit: `feat(shot_map): support club accent override for goal markers`

---

### Task 14 — Axes 9–10: composable + matplotlib hygiene

**Tier:** 2 (judgement)

**Axis 9 (Composable):**
1. Verify `shot_map()` returns a `Figure` (already does)
2. Verify it never calls `plt.show()` (already doesn't)
3. Test composition via `campos.compose()`:
   ```python
   def test_shot_map_composable_with_ribbon():
       fig1 = shot_map(shots)
       fig2 = percentile_ribbon(rows)
       composed = compose([fig1, fig2], layout="horizontal")
       assert isinstance(composed, Figure)
   ```
4. Test in subplot context:
   ```python
   def test_shot_map_figure_embeddable_in_subplot():
       # Verify the returned figure can be rasterized and placed in another figure
       fig = shot_map(shots)
       buf = io.BytesIO()
       fig.savefig(buf, format="png")
       assert buf.tell() > 0
   ```

**Axis 10 (Matplotlib hygiene):**
1. Test that calling `shot_map()` doesn't mutate `mpl.rcParams`:
   ```python
   def test_shot_map_does_not_mutate_rcparams():
       before = dict(mpl.rcParams)
       shot_map(shots)
       after = dict(mpl.rcParams)
       assert before == after
   ```
2. Test that calling `shot_map()` doesn't affect subsequent non-Campos plots.

Commit: `test(shot_map): add Axis 9 (composable) and Axis 10 (mpl hygiene) tests`

---

## Milestone E: ShotMap advanced + A11y (Tasks 15–16)

### Task 15 — Companion bee-swarm distribution panel

**Tier:** 3 (creative)
**Spec ref:** "companion bee-swarm"

Add an optional companion panel showing the xG distribution as a bee-swarm / strip plot.

**Steps:**

1. Add parameter to `shot_map()`:
   ```python
   def shot_map(
       shots: Sequence[Shot],
       *,
       title: str | None = None,
       show_distribution: bool = False,
   ) -> Figure:
   ```

2. When `show_distribution=True`:
   - Create a 2-column figure layout (pitch left, distribution right) with width ratio ~3:1
   - Right panel: vertical strip/bee-swarm of xG values, same outcome colours
   - Y-axis shared with pitch (or at least visually aligned)
   - Label: "xG distribution"

3. When `show_distribution=False` (default): current single-panel behaviour unchanged. **Backwards compatible.**

4. Add tests:
   - `test_distribution_panel_renders`
   - `test_distribution_panel_off_by_default`
   - `test_distribution_panel_with_empty_shots`

5. Add fixture: `shots_distribution.json` — 20 shots with varied xG for a visible swarm

Commit: `feat(shot_map): add optional xG bee-swarm distribution panel`

---

### Task 16 — Axis 11 (A11y) + Axis 12 (tested)

**Tier:** 2 (judgement)
**Note:** Subject to N6 flex rule. If cumulative hours at this point exceed 150% of baseline (24.75h), defer A11y to v1.x and mark Axis 11 as deferred.

**Axis 11 (A11y):**

1. **Contrast ratios:** Verify goal colour (#7cd3a3) and non-goal colour (#a78bfa) both meet WCAG AA against dark pitch (#12141a) and light pitch (#f5f5f7). Calculate programmatically:
   ```python
   def contrast_ratio(hex1, hex2):
       # WCAG luminance formula
       ...
   ```
   If any pair fails AA (ratio < 4.5:1 for text, < 3:1 for large graphics), adjust the colour.

2. **Alt text:** Set `fig.get_axes()[0].set_label("Shot map: N shots, M goals")` as accessible label.

3. **Colour not only encoding:** Already addressed by Task 8 (body-part shape encoding). Additionally, goal shots get a white edge ring while non-goals don't — provides shape + colour dual encoding for outcome.

4. Add tests:
   - `test_contrast_ratio_dark_theme_meets_wcag_aa`
   - `test_contrast_ratio_light_theme_meets_wcag_aa`
   - `test_figure_has_accessible_label`

**Axis 12 (Tested):**

5. Verify all 11 axes have at least one test. Create a checklist in `python/tests/test_shot_map.py` header:
   ```python
   # 12-axis coverage:
   # [x] Axis 1 (Empty): test_empty_list_renders_placeholder
   # [x] Axis 2 (Sparse): test_single_shot_renders_visible_marker
   # ... etc
   ```

6. Run full test suite: `cd python && pytest -v`

Commit: `feat(shot_map): add A11y (contrast, alt text, dual encoding) + axis coverage checklist`

---

## Milestone F: PlayerHero typography upgrade (Tasks 17–19)

Per spec N7: build PlayerHero in parallel to force the theme to answer display-typography, unicode, gradient, and photo-framing questions during theme design rather than discovering gaps in S3.

**Scope:** Not full 12-axis green. Goal is a typographically styled card that stress-tests the theme, with realistic player profile layout.

### Task 17 — PlayerHero real typography

**Tier:** 3 (creative)

Replace the minimal stub with a properly typeset player card.

**Steps:**

1. Redesign `player_hero()` layout:
   - **Name** in display typography (tokens: size 48, weight 800, tracking -0.02)
   - **Position** as a pill/chip below the name (chip background from tokens)
   - **Nation + Age** as secondary text
   - **Club name** if provided, with club primary colour accent
   - **Season label** if provided, as a badge

2. Use theme-aware colours:
   - Read `mpl.rcParams['figure.facecolor']` for background
   - Read `mpl.rcParams['text.color']` for primary text
   - Apply display typography tracking via per-character letter-spacing (N3 constraint: matplotlib can't do this via rcParams)

3. Layout using `fig.text()` positioning (not axes — this is a chrome component, not a chart):
   - Name at y=0.7, large
   - Position pill at y=0.5
   - Meta line (nation · age) at y=0.35
   - Club + season at y=0.2

4. Handle optional fields gracefully:
   - `club=None` → no club line
   - `season_label=None` → no season badge
   - `photo_url` → not rendered in v1 matplotlib (no image loading), but reserved space
   - `position=None` → skip position pill

5. Preserve existing test compatibility: the stub tests in `test_stubs.py` must still pass.

Commit: `feat(player_hero): upgrade to full typography with theme-aware styling`

---

### Task 18 — PlayerHero text edge cases

**Tier:** 2 (judgement)

**Steps:**

1. Create `python/tests/test_player_hero.py` with text-edge tests:
   - `test_unicode_name_renders` — `Player(name="Ødegaard")`
   - `test_cjk_name_renders` — `Player(name="张伟")`
   - `test_long_name_no_clipping` — `Player(name="Trent Alexander-Arnold")`
   - `test_rtl_name_renders` — `Player(name="عمر مرموش")`
   - `test_all_caps_name` — `Player(name="HAALAND")`
   - `test_two_line_position` — `Player(position="Attacking Midfielder / Winger")`

2. Verify no clipping, no encoding errors, no layout breaks.

3. Test both dark and light themes:
   - `test_dark_theme_white_text_on_dark_bg`
   - `test_light_theme_dark_text_on_light_bg`

Commit: `test(player_hero): add text-edge and theme tests`

---

### Task 19 — PlayerHero composition integration

**Tier:** 2 (judgement)

Verify PlayerHero works with `campos.compose()` alongside other components.

**Steps:**

1. Add integration test:
   ```python
   def test_hero_plus_ribbon_compose():
       player = Player(id="salah", name="Mohamed Salah", position="Forward")
       rows = [PercentileRow(stat_id="xg", label="xG", value=0.54, percentile=97)]
       fig_hero = player_hero(player)
       fig_ribbon = percentile_ribbon(rows)
       composed = compose([fig_hero, fig_ribbon], layout="vertical", title="Scouting Card")
       assert isinstance(composed, Figure)
       composed.savefig(io.BytesIO(), format="png")  # renders without error
   ```

2. Add 3-component integration:
   ```python
   def test_full_scouting_report_compose():
       fig_hero = player_hero(player)
       fig_ribbon = percentile_ribbon(rows)
       fig_shots = shot_map(shots)
       composed = compose([fig_hero, fig_ribbon, fig_shots], layout="grid")
       assert isinstance(composed, Figure)
   ```

Commit: `test(compose): add multi-component integration tests`

---

## Milestone G: Close-out (Tasks 20–22)

### Task 20 — Full test suite run

**Tier:** 1 (mechanical)

**Steps:**

1. Run: `cd /Users/rahulkeerthi/Work/campos/python && pytest -v --tb=short`
2. All tests must pass
3. Count total tests — should be ≥40 (18 from S0 + ~25 new from S1)
4. Fix any failures

Commit: (only if fixes needed)

---

### Task 21 — ShotMap 12-axis sign-off

**Tier:** 2 (judgement)

Create `docs/component_log/shotmap_signoff.md` with the completed checklist:

```markdown
# ShotMap 12-Axis Sign-Off

| Axis | Name | Status | Test(s) | Notes |
|------|------|:------:|---------|-------|
| 1 | Empty | ✅ | test_empty_list_renders_placeholder | |
| 2 | Sparse | ✅ | test_single_shot_renders_visible_marker | |
| 3 | Dense | ✅ | test_500_shots_renders_under_5_seconds | |
| 4 | Missing | ✅ | test_nan_xg, test_none_outcome | |
| 5 | Extreme | ✅ | test_negative_xg, test_xg_above_one | |
| 6 | Text edges | ✅ | test_unicode_title, test_cjk_title | |
| 7 | Responsive | ✅ | test_responsive_width[400-1600] | |
| 8 | Themeable | ✅ | test_dark/light_theme, test_club_accent | |
| 9 | Composable | ✅ | test_composable_with_ribbon | |
| 10 | Mpl hygiene | ✅ | test_does_not_mutate_rcparams | |
| 11 | A11y | ✅/DEFERRED | test_contrast_ratio, test_alt_text | Per N6 if hours exceeded |
| 12 | Tested | ✅ | (this checklist) | |
```

Fill actual status based on test results.

Commit: `docs(s1): ShotMap 12-axis sign-off`

---

### Task 22 — Commitment device close-out

**Tier:** 1 (mechanical)

**Steps:**

1. Fill in the day-11 result in `docs/component_log/shotmap.md`
2. Update `docs/estimates/shotmap.md` with actual hours per axis
3. Check if any flex rules fired:
   - Total hours > 24.75 (150%) → Axis 11 deferred for subsequent components
   - Total hours > 33.0 (200%) → Axis 7 A4 clause deferred
   - Total hours > 41.25 (250%) → full replan required
4. Record the decision

Commit: `docs(s1): close commitment device — record actuals and flex-rule outcome`

---

## Summary

| Milestone | Tasks | Deliverable |
|-----------|-------|-------------|
| A: Pre-build ceremony | 1–3 | Estimates, commitment device, nutmeg gate |
| B: Theme upgrade | 4–6 | Light variant, compose(), theme-aware components |
| C: ShotMap core | 7–10 | Real implementation with xG markers, shapes, edge cases |
| D: ShotMap quality | 11–14 | Text edges, responsive, themeable, composable |
| E: ShotMap advanced | 15–16 | Bee-swarm panel, A11y, full test coverage |
| F: PlayerHero typography | 17–19 | Styled card, text edges, composition integration |
| G: Close-out | 20–22 | Test suite, sign-off, commitment device result |

**Total tasks:** 22
**Estimated scope:** 16.5h ShotMap + ~8h theme/compose/PlayerHero = ~24.5h total
**Gate:** ShotMap closes all in-scope axes by cut date, or axis-flex rules fire automatically
