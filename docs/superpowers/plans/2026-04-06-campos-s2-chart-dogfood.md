# Campos Plan 3 — S2 Chart Dogfood

**Spec:** `docs/superpowers/specs/2026-04-05-campos-design.md` (v2.1)
**Predecessor:** Plan 2 (S1) — completed, ShotMap 12-axis GREEN, tagged `s1-complete`
**Scope:** Build RadarChart + PercentileRibbon upgrade + PlayerTable to 12-axis green
**Repo:** `/Users/rahulkeerthi/Work/campos`

---

## Components in scope

| # | Component | Current state | S2 target |
|---|-----------|---------------|-----------|
| 1 | RadarChart | Does not exist | Full 12-axis green |
| 2 | PercentileRibbon | Stub (42 lines) | Upgrade to full 12-axis: comparison overlay, styling |
| 3 | PlayerTable | Does not exist | Full 12-axis green (pandas-Styler, 1000+ rows) |

---

## Milestone A: RadarChart (Tasks 1–6)

### Task 1 — RadarChart schema + scaffolding

Create `python/src/campos/components/radar_chart.py` with signature:

```python
def radar_chart(
    categories: Sequence[RadarCategory],
    *,
    title: str | None = None,
    comparison_label: str | None = None,
    subject_label: str | None = None,
) -> Figure:
```

RadarCategory schema already exists: `label`, `value`, `max`, `comparison_value` (optional), `reversed` (optional).

Implementation:
- Polar axes with category labels evenly spaced around perimeter
- Subject polygon filled with accent.primary at alpha=0.25, edge at alpha=0.8
- If any `comparison_value` set: comparison polygon in accent.secondary
- Reversed scale: for categories where `reversed=True`, invert the normalised value (1 - norm)
- Y-axis (radial) gridlines at 0.25, 0.5, 0.75, 1.0
- Theme-aware colours from rcParams
- Handle 3-12 categories; <3 raises ValueError

### Task 2 — RadarChart edge cases (Axes 1-5)

- Empty categories → ValueError (radar needs ≥3)
- 3 categories (sparse) → triangle renders cleanly
- 12 categories (dense end) → labels don't collide
- Missing: `comparison_value=None` on some categories → skip comparison polygon for those points (or use 0)
- Extreme: `value > max` → clamp to max; `value < 0` → clamp to 0; `max=0` → treat as max=1

### Task 3 — RadarChart quality axes (6-10)

- Axis 6: Unicode/CJK/RTL category labels + title
- Axis 7: responsive at 400-1600px
- Axis 8: dark + light themes, club accent
- Axis 9: composable, returns Figure
- Axis 10: no rcParams mutation

### Task 4 — RadarChart A11y + tests (Axes 11-12)

- Contrast ratios for polygon fills against both themes
- Accessible label: "Radar chart: N categories"
- Comparison polygon uses dashed line (not just colour)
- Full test suite in `python/tests/test_radar_chart.py`

### Task 5 — Export + commitment device

- Add to `campos/__init__.py`
- Create `docs/component_log/radar_chart.md`
- Create `docs/component_log/radar_chart_signoff.md`

### Task 6 — Commit RadarChart

---

## Milestone B: PercentileRibbon upgrade (Tasks 7–10)

### Task 7 — Comparison overlay

Add `comparison_percentile` rendering to the existing stub:
- If `row.comparison_percentile` is set, render a thin vertical marker line at that position
- Use accent.secondary colour for comparison marker
- Add optional `comparison_label: str | None = None` parameter

### Task 8 — PercentileRibbon styling upgrade

- Background track bar (dim colour) behind the main bar
- Value label formatting improvements
- Category grouping visual separator when consecutive rows have different `category` values

### Task 9 — PercentileRibbon 12-axis tests

Same axes as ShotMap: empty, sparse, dense (60 rows), missing (NaN percentile), extreme (>100, <0), text edges, responsive, themeable, composable, hygiene, A11y, tested.

### Task 10 — PercentileRibbon sign-off + commit

---

## Milestone C: PlayerTable (Tasks 11–15)

### Task 11 — PlayerTable schema + scaffolding

```python
def player_table(
    players: Sequence[Player],
    metrics: Sequence[str],
    values: dict[str, Sequence[float]],
    *,
    title: str | None = None,
    sort_by: str | None = None,
    ascending: bool = False,
) -> Figure:
```

Renders a table as a matplotlib figure (not pandas-Styler for now — matplotlib table for consistency with other components).

### Task 12 — PlayerTable rendering

- Header row with metric names
- Player name column (bold, left-aligned)
- Position pill in a dedicated column
- Metric cells with colour-scaled backgrounds (green = high percentile, red = low)
- Sortable by any metric column

### Task 13 — PlayerTable dense state (1000+ rows)

- Truncate to top N with "... and M more" footer
- Default N=25, configurable via `max_rows` parameter
- Performance test: 1000 players renders in <5s

### Task 14 — PlayerTable 12-axis tests

### Task 15 — PlayerTable sign-off + commit

---

## Milestone D: Close-out (Task 16)

### Task 16 — S2 tag + summary

- Run full test suite
- Tag `s2-complete`
- Summary of all components' axis status

---

## Summary

| Milestone | Tasks | Component |
|-----------|-------|-----------|
| A | 1–6 | RadarChart (new, 12-axis) |
| B | 7–10 | PercentileRibbon (upgrade, 12-axis) |
| C | 11–15 | PlayerTable (new, 12-axis) |
| D | 16 | Close-out + tag |

**Total tasks:** 16
