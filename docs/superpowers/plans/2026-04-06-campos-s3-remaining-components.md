# Campos Plan 4 — S3 Remaining Components

**Predecessor:** Plan 3 (S2) — completed, tagged `s2-complete`
**Scope:** PercentileGroup + CategoryScoreCard + RankedList + PlayerHero 12-axis upgrade
**Repo:** `/Users/rahulkeerthi/Work/campos`

## Components

| # | Component | Current state | S3 target |
|---|-----------|---------------|-----------|
| 1 | PercentileGroup | Does not exist | Full 12-axis (composition on PercentileRibbon) |
| 2 | CategoryScoreCard | Does not exist | Full 12-axis (smallest component) |
| 3 | RankedList | Does not exist | Full 12-axis (leaderboard/similarity) |
| 4 | PlayerHero | Styled stub (S1) | Full 12-axis upgrade |

## Milestone A: PercentileGroup (Tasks 1-2)

Category header + aggregate score + nested PercentileRibbon rows.

```python
def percentile_group(
    label: str,
    rows: Sequence[PercentileRow],
    *,
    aggregate_score: float | None = None,
    title: str | None = None,
) -> Figure:
```

## Milestone B: CategoryScoreCard (Tasks 3-4)

Small tile: category label + subject score + optional comparison.

```python
def category_score_card(
    label: str,
    score: float,
    *,
    comparison_score: float | None = None,
    max_score: float = 100.0,
    title: str | None = None,
) -> Figure:
```

## Milestone C: RankedList (Tasks 5-6)

Rank + name + value bar. For leaderboards and similarity lists.

```python
def ranked_list(
    items: Sequence[dict],  # [{name, value, subtitle?, crest_url?}]
    *,
    title: str | None = None,
    max_items: int = 20,
    value_label: str = "Value",
) -> Figure:
```

## Milestone D: PlayerHero 12-axis (Tasks 7-8)

Upgrade existing styled component to pass all 12 axes.

## Milestone E: Close-out (Task 9)

Full test suite, s3-complete tag.

Total: 9 tasks
