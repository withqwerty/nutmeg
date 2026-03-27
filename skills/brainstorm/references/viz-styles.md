# Visualisation Styles

When proposing approaches, frame them within one of these styles based on what the user is building. Ask early — "is this for a dashboard, a report, social media, or a narrative piece?" — and adapt accordingly.

---

## Analytical / Dashboard

**Goal:** Enable exploration and comparison. Clarity over beauty.

- Clean, minimal, high data-ink ratio
- Small multiples preferred over overlaid series
- Consistent axes, grids, and labels across panels
- Tooltips for precise values, filters for slicing
- Neutral colour palette (greys + one accent), club colours only for identification
- Common tools: Streamlit, Plotly, Observable, Tableau, Shiny

**When to recommend:** The user is building a tool for themselves or a team. They want to answer questions, not tell a story. Speed of iteration matters more than polish.

## Social Media / Shareable

**Goal:** Grab attention, communicate one finding fast. Optimised for Twitter/X, Instagram, Reddit.

- Bold colours, large type, strong visual hierarchy
- Club badges as data markers (community convention)
- Single chart per image, self-contained with title and source
- 4:5 or 1:1 aspect ratio for mobile
- Minimal interaction (static image or short GIF)
- Brand watermark / credit line
- Common tools: mplsoccer + matplotlib (Python), ggplot2 + ggsoccer (R)

**When to recommend:** The user wants to share a finding. The chart needs to work as a standalone image without any surrounding text.

## Editorial / Narrative

**Goal:** Advance an argument. The chart exists inside a story.

- Every chart has a point of view — it makes a claim, not just a display
- Physical metaphors when the subject allows (e.g., a "brick wall" for defensive blocks)
- Annotations are generous — label the anomaly, integrate colour into titles
- Static when the point is clear, interactive only for exploration
- Typographic hierarchy: display font for titles, condensed for labels, body for prose
- Consider narrative shape: how does information density rise and fall?
- Common tools: D3.js, Observable, Svelte, scrollytelling frameworks

**When to recommend:** The user is writing a blog post, article, or data essay. They want the chart to persuade, not just inform. Point them to `references/chart-canon.md` for the football-specific conventions.

**Inspiration:** The Pudding, The Athletic, FiveThirtyEight, John Burn-Murdoch (FT), Tom Worville.

## Minimal / Academic

**Goal:** Precise, reproducible, publication-ready. Follows journal conventions.

- Black/white or greyscale with one accent colour
- Axis labels with units, figure captions below
- Confidence intervals and error bars shown explicitly
- Sample sizes stated, statistical tests noted
- Reproducible from code (R Markdown, Jupyter, Quarto)
- Common tools: ggplot2, matplotlib, seaborn, Quarto

**When to recommend:** The user is writing a paper, thesis, or technical report. The chart needs to survive peer review. Aesthetics matter less than correctness and reproducibility.

---

## Adapting to experience level

**Beginners:** Default to Analytical or Social Media. These are the fastest path to a working chart. Avoid suggesting D3 or scrollytelling — the learning curve is steep.

**Intermediate:** Offer all four styles. Let them choose based on their goal. Provide starter code in their preferred language.

**Advanced:** They likely already have a style preference. Focus on the specific technique they're asking about (e.g., "how do I build a pitch control surface?") rather than style recommendations. Point to `references/chart-canon.md` for conventions and anti-patterns they might not know about.
