---
name: nutmeg-review
description: "Review football data code and visualisations for correctness. Use after building a chart, data pipeline, or analysis. Dispatches specialised reviewers for data correctness, chart conventions, visual inspection, and interactive edge cases."
argument-hint: "[what to review, e.g. 'my shot map code' or 'the passmap page']"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep", "Agent", "mcp__football-docs__search_docs"]
---

# Review

Dispatch specialised reviewers to check football data code and visualisations for correctness, convention compliance, and edge cases.

## Accuracy

Read and follow `docs/accuracy-guardrail.md` before answering any question about provider-specific facts.

## First: check profile

Read `.nutmeg.user.md`. If it doesn't exist, tell the user to run `/nutmeg` first.

## Determine scope

Look at what the user wants reviewed. Read the relevant files. Then decide which reviewers to dispatch:

| Signal | Dispatch |
|---|---|
| Code processes football data (fetching, filtering, transforming, computing metrics) | **data-reviewer** agent |
| Code renders a chart or visualisation | **chart-reviewer** agent (Mode 1: Code Review) |
| User provides a URL or says "check how it looks" | **chart-reviewer** agent (Mode 2: Visual Inspection) |
| Chart has filters, tooltips, state, or dynamic data | **chart-reviewer** agent (Mode 3: Interactive Edge Cases) |
| Code does both data processing AND chart rendering | **Both agents** in parallel |

**Always dispatch at least one.** If unclear, dispatch both — redundant findings are better than missed issues.

## Dispatch

Spawn agents in parallel when dispatching multiple. Each agent receives:

1. The file paths to review
2. The user's profile (language, provider, experience level)
3. Which mode(s) to run (for chart-reviewer)
4. Context: what the user said they built and what they're worried about

### Data reviewer prompt template

```
Review the football data code in [FILE_PATHS].

The user is working with [PROVIDER] data in [LANGUAGE].
They built: [DESCRIPTION]
Their concern: [WHAT_THEY_SAID]

Follow the full review checklist in your agent prompt. Use search_docs to verify
provider-specific facts (coordinate systems, qualifier IDs, event types).
```

### Chart reviewer prompt template

```
Review the chart code in [FILE_PATHS].

Mode(s): [Code Review / Visual Inspection / Interactive Edge Cases]
The user is building: [DESCRIPTION]
Their concern: [WHAT_THEY_SAID]
Stack: [LANGUAGE + LIBRARIES from profile]
[If visual inspection: URL or instructions to render]

Load skills/brainstorm/references/chart-canon.md for convention checking.
```

## Synthesise findings

After both agents report back:

1. **Deduplicate** — if both flag the same issue (e.g., wrong coordinate system), merge into one finding
2. **Sort by severity** — Critical first, then Warning, then Info
3. **Group logically** — Data issues, then Rendering issues, then Convention issues, then Edge cases
4. **Present concisely** — table format with severity, location, issue, fix

## When to suggest visual inspection

If the chart-reviewer's code review finds potential rendering issues but can't confirm without seeing the output, suggest:

> "The code review found [N] potential rendering issues. Want me to visually inspect the chart? I'll need a URL or you can run it locally."

Don't require visual inspection — many users can't easily serve their chart locally. Code review alone catches most issues.

## After review

If findings are found:
- Ask the user which ones to fix
- For Critical issues, offer to fix them directly
- For Warning/Info, explain the trade-off and let them decide

If no findings:
- Say so clearly. Don't invent issues to justify the review.
- Optionally mention what was checked so the user knows the review was thorough.
