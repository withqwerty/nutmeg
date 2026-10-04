# Figure provenance contract (`nutmeg-figure-provenance/v1`)

Every chart in a nutmeg research project has a provenance file next to it:
`research/<slug>/figures/<name>.prov.json`. `nutmeg figure register` writes it.
The workspace page, `nutmeg publish`, `nutmeg trace` and chart components (for example
campos) read it. This page defines the file so other tools can read and write it too.

## Fields

| Field | Type | Meaning |
|---|---|---|
| `contract` | string | Always `nutmeg-figure-provenance/v1`. |
| `figure` | string | The figure name (letters, digits, `.`, `-`, `_`). Also the file name stem. |
| `image` | string or null | Path of the chart file, relative to the repository root. |
| `sources` | list | One object per data source: `{"name": "StatsBomb open data", "panel": "left"}`. `panel` is optional; use it for multi-panel figures. |
| `competition_season` | string or null | For example `Premier League 2025/26`. |
| `filters` | string or null | The filters on the plotted rows, for example `min 900 minutes`. |
| `n` | integer | The sample size the chart shows. Defaults to the snapshot's row count. |
| `metric` | string or null | The metric plotted. |
| `uncertainty` | string or null | The uncertainty shown, for example `bootstrap 95% CI`. Null means none is shown. |
| `run_id` | string or null | The recorded run that produced the data (`runs/<id>/run.json`). |
| `claims` | list of strings | Ledger claim IDs the chart shows. Each one exists in `claims.jsonl`. |
| `data_snapshot` | string | Repository-relative path of the CSV or JSON of the plotted rows, kept as `figures/<name>.data.csv` or `.data.json`. |
| `data_sha256` | string | SHA-256 of the snapshot. |
| `rows` | integer | Rows in the snapshot (CSV: lines after the header; JSON: list length, or the length of its `rows` or `data` list). |
| `date` | string | `YYYY-MM-DD` (UTC) when the figure was registered. |
| `footnote` | string | The short footnote to print under the chart. |
| `footnote_long` | string | The long form, one line per field. |

## The footnote

The short form joins these parts with ` · `, leaving out empty ones:

```
Source: <sources joined with " + "> · <competition and season> · <filters> · n = <n> · <metric> · <uncertainty or "no uncertainty shown"> · <date> · <claim IDs>
```

Example:

```
Source: StatsBomb open data · Premier League 2015/16 · min 900 minutes · n = 214 · progressive actions per 90 · no uncertainty shown · 2026-10-02 · C1, C2
```

Put it under the chart in small text. In matplotlib, use `fig.text(0.01, 0.01, footnote, fontsize=7, ha="left")`;
in ggplot2, `labs(caption = footnote)`; in Vega-Lite or Observable Plot, a caption or a `text` mark below the
plot. Charts carry no links; the claim IDs lead back to the ledger.

## Rules for writers

- Write the snapshot first. The snapshot holds the rows the chart plots, not the raw input.
- Every claim ID must exist in the ledger before the figure is registered.
- When the project keeps data out of git, the snapshot (`figures/*.data.csv|json`) is gitignored and the
  provenance file keeps only its hash.
- Readers must ignore fields they do not know, so later versions can add fields.
