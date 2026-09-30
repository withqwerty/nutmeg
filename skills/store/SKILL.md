---
name: nutmeg-store
description: "Choose how and where to store football data. Use when the user asks about database choices, file formats, cloud storage, data pipelines, or how to organise their football data project. Also covers publishing and sharing outputs (Streamlit, Observable, GitHub Pages)."
argument-hint: "[storage question or 'publish']"
allowed-tools: ["Read", "Write", "Bash", "AskUserQuestion", "mcp__plugin_nutmeg_football-docs__search_docs", "mcp__football-docs__search_docs"]
---

# Store

Help the user choose storage formats, locations, and publishing methods for their football data.

## Accuracy

Read and follow `${CLAUDE_PLUGIN_ROOT}/docs/accuracy-guardrail.md` before answering any question about provider-specific facts (IDs, endpoints, schemas, coordinates, rate limits). Always use `search_docs` — never guess from training data.
## First: check profile

Read `.nutmeg.user.md`. If it doesn't exist, continue with sensible defaults (Python and pandas, intermediate level) and suggest running `/nutmeg` setup at the end.

## Storage format decision tree

### Small projects (< 100MB, single user)

| Format | Best for | Tools |
|--------|---------|-------|
| JSON | Raw event data, API responses | Any language |
| CSV | Tabular stats, easy to share | Spreadsheets, pandas, R |
| Parquet | Columnar analytics, fast queries | polars, pandas, DuckDB, Arrow |
| SQLite | Relational queries, multiple tables | Any language, DB browser tools |

**Recommendation:** Start with JSON for raw data, Parquet for processed data.

### Medium projects (100MB - 10GB)

| Format | Best for | Notes |
|--------|---------|-------|
| Parquet files | Analytics workloads | 5-10x smaller than JSON, fast columnar reads |
| DuckDB | SQL analytics on local files | Queries Parquet/CSV directly, no server needed |
| SQLite | Relational data with joins | Single file, portable, ACID compliant |

**Recommendation:** Parquet for storage, DuckDB for querying.

### Large projects (> 10GB, multiple users)

| Solution | Best for | Cost |
|----------|---------|------|
| PostgreSQL | Production apps, complex queries | Free self-hosted; managed hosting is paid |
| BigQuery | Massive analytical queries | Free tier, then pay per query |
| Cloudflare R2 | Object storage (raw files) | Free tier, then pay per GB |
| S3 / GCS | Object storage at scale | Pay per GB |

Prices and free tiers change. Check the provider's current pricing page before you quote a number.

## Directory structure

Recommend this structure for football data projects:

```
project/
  data/
    raw/                  # Untouched API/scrape responses
      statsbomb/
        events/
        matches.json
      fbref/
        2024/
    processed/            # Cleaned, transformed data
      events.parquet
      shots.parquet
      passes.parquet
    derived/              # Computed metrics
      xg_model.parquet
      passing_networks/
  notebooks/              # Analysis notebooks
  scripts/                # Data pipeline scripts
  outputs/                # Charts, reports, exports
  .env                    # API keys (gitignored)
  .nutmeg.user.md         # Nutmeg profile
```

## Publishing and sharing

### Interactive dashboards

| Platform | Language | Cost | Notes |
|----------|---------|------|-------|
| Streamlit | Python | Free (community cloud) | Most popular for football analytics. Deploy from GitHub |
| Observable | JavaScript | Free tier | Great for D3.js visualisations. Notebooks + Framework |
| Shiny | R | Free tier (shinyapps.io) | R ecosystem integration |
| Gradio | Python | Free (HuggingFace Spaces) | Quick ML model demos |

### Static sites

| Platform | Notes |
|----------|-------|
| GitHub Pages | Free. Good for static charts (D3, matplotlib exports) |
| Cloudflare Pages | Free. Faster, more features than GH Pages |
| Vercel | Free tier. Good for Next.js/Astro sites |

### Sharing data

| Method | Best for |
|--------|---------|
| GitHub repo | Small datasets (< 100MB), code + data together |
| GitHub Releases | Larger files (check GitHub's current size limits) |
| Kaggle Datasets | Community sharing, discoverable, free |
| HuggingFace Datasets | ML-focused, versioned, free |

### Social media / content

| Output | Tool | Notes |
|--------|------|-------|
| Static charts | matplotlib, ggplot2, D3.js | Export as PNG/SVG |
| Animated charts | matplotlib.animation, D3 transitions | Export as GIF/MP4 |
| Twitter/X threads | Chart images + alt text | Accessibility matters |
| Blog posts | Markdown + embedded charts | GitHub Pages, Medium, Substack |

## Cost awareness

Based on the user's `.nutmeg.user.md` goals, flag costs:

- **Exploration/learning:** Everything can be free. StatsBomb open data + Jupyter/Colab + GitHub Pages.
- **Content creation:** Streamlit Community Cloud is free. Cloudflare Pages is free.
- **Professional:** Budget for commercial data access. Provider pricing is negotiated, so do not quote a figure.
- **Product:** Database hosting ($7-50/mo), consider data licensing costs separately.
