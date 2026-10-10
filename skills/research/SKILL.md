---
name: nutmeg-research
description: "Run football analysis as a research project that shows its work: a question, a plan with reasons, a claim ledger tying every number to evidence. Use for work to publish or decide on (shortlists, match or opposition reports, memos, charts, threads) or when sourced numbers are asked for."
argument-hint: "[the question to research]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "AskUserQuestion", "mcp__plugin_nutmeg_football-docs__search_docs", "mcp__football-docs__search_docs", "mcp__plugin_nutmeg_football-docs__resolve_entity", "mcp__football-docs__resolve_entity", "mcp__plugin_nutmeg_football-docs__get_provider_docs", "mcp__football-docs__get_provider_docs", "mcp__plugin_nutmeg_football-docs__get_metric", "mcp__football-docs__get_metric", "mcp__plugin_nutmeg_football-docs__list_metrics", "mcp__football-docs__list_metrics"]
---

# Research

Work like a research assistant, not an autopilot. The user must be able to check every input, every
query and every number, and see why each choice was made. A research project keeps that trail in
files the user and their teammates can open.

Read and follow `${CLAUDE_PLUGIN_ROOT}/docs/accuracy-guardrail.md`. Provider facts come from
football-docs and IDs from the Reep Register, never from memory.

## The nutmeg command

Run every project command through the plugin's core, in exactly this form:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/core/nutmeg.py" <command> ...
```

Below, `nutmeg <command>` is short for that line. Run `nutmeg --help` or `nutmeg <command> --help`
for the options. If `python3` is missing or older than 3.10, tell the user that research projects
need Python 3.10 or newer, and continue the task without a project.

## When to start a project

Start one when the user wants analysis to publish or to decide on: a shortlist, a match or
opposition report, a memo, a chart or thread for social media, or any answer they ask to be
sourced. Do not start one for a quick question ("what is PPDA?", "what is Opta's qualifier for a
cross?"), a code fix or a lookup.

## 1. Start the project

1. Pick a short slug, for example `shortlist-lb` or `arsenal-press-2025`.
2. Run `nutmeg new <slug> --question "<the question in one sentence>"`.
3. If the command says there is no team policy for data in git, ask the user with
   AskUserQuestion: keep data, run outputs and figure snapshots out of git (recommended for
   licensed club or provider data), or commit them with the project. Then run it again with
   `--data-in-git no` or `--data-in-git yes`.

The project lives in `research/<slug>/` and becomes the active project. `nutmeg status` shows it.

4. Run `nutmeg config show` and note the user's levels for plan, run and publish (section 10). They
   decide where you stop for approval.

## 2. Write the question card

Fill in `research/<slug>/question.md`: the question, the decision or output it informs, the data
and scope (competitions, seasons, providers) and what is out of scope. Use the user's words. If the
decision it informs is unclear, ask one question.

## 3. Write the plan with reasons

Every choice of metric, filter, join, threshold, source, method or chart is a plan choice. Add each
with:

```bash
nutmeg plan choose --kind metric --choice "npxG per 90" \
  --why "Penalties distort per-player comparisons." \
  --rests-type docs --rests-ref "football-docs: <provider> <doc title>"
```

- `--why` is one sentence a data scientist can check. Say why this option and not the obvious
  other one.
- `--rests-type` and `--rests-ref` say what the reason rests on:
  - `docs`: a football-docs result (name the provider and the doc you used);
  - `metric`: a football-docs metric card variant, by its ID from `get_metric` (for example
    `--rests-type metric --rests-ref ppda.statsbomb-hudl`); use it for any metric that has a card, so readers see
    exactly which definition a number uses;
  - `registry`: a Reep Register record;
  - `rule`: a practitioner rule, such as `${CLAUDE_PLUGIN_ROOT}/docs/metric-misuse.md`;
  - `paper`: a paper or post;
  - `claim`: an earlier claim in this ledger;
  - `user`: the user's instruction, quoted.
- Never invent a source. If nothing supports a choice, say so in the reason and use `user` only
  when the user asked for it.

Run `nutmeg plan check` and fix what it reports. Make the choices before you run anything: the plan locks
automatically at the first `nutmeg run`, and that locked plan is the primary specification. Choices added or changed
later are allowed, but the publish card and the workspace list them as made after the lock (`nutmeg plan diff`).
Then follow the user's plan level:
- L1 or L2: show the user the plan and ask them to approve or change it before you fetch or compute
  anything.
- L3: show the plan with its reasons and carry on; the user can stop you at any time, and every run
  still goes through the gate.

## 4. Run the analysis through the gate

For data from a scrape, a download or an unknown source, record it first with
`nutmeg data add <file> --source "<where it came from>"`: its profile reports duplicated rows, repeated IDs and
empty columns, which you then deal with (and say how) before analysis.

Put each analysis step in a `.py`, `.R` or `.sql` file in the repository, then run it with:

```bash
nutmeg run analysis.py --input data/events.csv --sql queries/shots.sql -- --season 2025
```

- `--input` once for each data file or folder the step reads. Nutmeg hashes each one.
- `--sql` once for each SQL file the script runs, so the user sees the exact query.
- `--sends host:columns` for any data the step sends to an outside service, for example
  `--sends api.example.com:player_id,minutes`.
- Arguments after `--` go to the script.
- Write output files to the folder in `$NUTMEG_OUTPUT_DIR`, so the run records them.

Run `nutmeg run` on its own: no `&&`, `;`, pipes or redirects. Before it runs, the user sees a gate
card with the services and data the step uses, the inputs and the exact code and SQL, and approves
it. A re-run shows only what changed since the last run of the same file. If the user declines,
ask what to change.

If the user wants to see the card without running anything (or run the code themselves), use
`nutmeg gate` with the same arguments.

Inside a project, a direct `python3 script.py`, `Rscript`, `duckdb` or `psql` call raises a "not
recorded" card. Numbers from an unrecorded run cannot go into the ledger, so use `nutmeg run`.

A run must not change the files it reads: write cleaned data to a new file. If an input changes after a run (new
data, a correction), `nutmeg check` marks the claims from that run as stale; run it again and update them.

## 5. Record claims

Every number, provider fact, ID, citation, definition and interpretation that appears in the
project's outputs goes into the ledger:

Add claims in batches, not one call each: write them to a JSON Lines file (one claim per line) and add them all
in one call. Each is checked on its own, and the command lists any it rejects so you can fix just those.

```bash
nutmeg claim add --file new-claims.jsonl
```

where each line looks like:

```json
{"kind": "computed", "statement": "npxG/90 rose to 0.41", "value": 0.41, "evidence": {"run_id": "R3", "metric": "npxG per 90", "n": 31, "filters": {"min_minutes": 900}}, "why": "Per 90 with a 900-minute floor keeps small samples out."}
```

Each kind needs its evidence:

| Kind | Use for | Evidence it needs |
|---|---|---|
| `computed` | a number the analysis produced | `run_id` of the recorded run (`nutmeg run` prints it), plus `value`; add `metric`, `n`, `filters` |
| `provider_fact` | a fact about a provider's data | `provider`, and `source`: the football-docs result you used |
| `identity` | a player, team or match ID | `reep_id` and `release` from the Reep Register |
| `literature` | a citation | `citation`; add `source_id` and the quote match from football-docs |
| `definition` | what a term or metric means here | `definition` |
| `interpretation` | a judgement that rests on other claims | `claims`: the IDs it rests on |
| `gap` | something the work set out to establish and could not | `reason` (no data, too small a sample); never a `value` |

- An interpretation is never "verified". It is `supported` or `contested`.
- When a question cannot be answered with the data, say so in the output rather than leaving it out or guessing.
- Put the claim ID next to the number in reports and captions, for example `0.41 [C3]`.
- Never write a number in an output that is not in the ledger.
- In text, record one number per claim: a statement such as "7 shots, 3 key passes and 2 goals" with one `value`
  leaves the other numbers without evidence. A table is one claim: its `value` is the list of the numbers the table
  shows, row by row, with the rows in `evidence.snapshot` (a CSV the run wrote), and the line above the table cites
  it, for example `Table 2: points by season [C9]`. `nutmeg check` then checks every number in the table against
  that list.
- When a claim is replaced, withdraw the old one with a reason:
  `nutmeg claim withdraw C4 --note "replaced by C23-C26"`. Outputs that still cite it then fail the check.
- `nutmeg claim list` shows the ledger and any bad lines.

Write the report as you go. Draft it as soon as the main result exists, and add claims as numbers go into it, in
batches. Do not claim numbers ahead of writing, or numbers the outputs will not show. If a long task is cut short,
the report should already hold the main answer. Publishing has its own requirements
(`${CLAUDE_SKILL_DIR}/references/publishing.md`); do not spend the analysis on them.

## 6. Write outputs and check them

Write the report as `research/<slug>/report.md` (more reports can go in `research/<slug>/reports/`)
and figure captions next to the figures. Put the claim ID next to each number.

Run `nutmeg check`. It lists every number with no ledger claim, every number that matches more
than one claim, every citation without a resolved source and quote match, and every provider fact
without a football-docs source. Fix each one: add the claim with its evidence, or correct the
output.

When a step ends with open problems, nutmeg stops you once with the list. Fix them. If the user
says a problem is not one, record their reason:
`nutmeg check --accept <id> --reason "<the user's reason>"`. Never accept a problem on your own.

## 7. Charts

- Save the rows each chart plots as a CSV or JSON snapshot, then register the chart:
  `nutmeg figure register <name> --data <snapshot> --source "<source>" --claims C3,C5 --season "<competition and season>" --filters "<filters>" --metric "<metric>" --run R2 --image <chart file>`.
  Put the footnote it prints under the chart. `/nutmeg:brainstorm` has the chart conventions.

**When the user asks to publish, share or hand over the project, read
`${CLAUDE_SKILL_DIR}/references/publishing.md` first.** It covers what publishing needs (alternatives for headline
results, limits on judgements, a source for each input, the teach-back), sign-off, `nutmeg publish` and
`nutmeg bundle`. Do not do that work during the analysis.

## 8. Explain claims

- `nutmeg why <claim>` prints a claim's value, definition, evidence (the run and code lines, the
  docs source, the Reep ID and release, or the paper and quote), filters, n, up to five sample
  rows, the reason and its history. Use it to answer "where does this number come from?". Add
  `code_lines` (for example `analysis.py:12-20`) and `snapshot` (a CSV or JSON of the rows behind
  the number) to a computed claim's evidence so `why` can show them.
- `nutmeg trace` prints inputs, runs, claims and figures as a tree.
- `nutmeg workspace` writes `research/<slug>/workspace.html`: the review queue, question, plan with reasons, ledger
  with each claim's evidence, report, figures, runs and the glossary entries it links. Regenerate it after changes
  and tell the user where it is. It is view-only; approvals happen here in Claude Code.
- Use terms from `${CLAUDE_PLUGIN_ROOT}/docs/glossary.md` for metrics where you can. For a metric that is not in it,
  add a `definition` claim so readers know what it means: name the metric's term in its statement, or set
  `evidence.term` to it, so `nutmeg check` links the two.

## 9. Understanding

Follow `${CLAUDE_PLUGIN_ROOT}/docs/understanding.md`:

- Explain terms, methods and results with this project's own numbers when the user is unsure.
- Offer an explainer page at the moments that file lists, once per topic, and never again after a no
  (`nutmeg explain decline "<topic>"`). Make it with `nutmeg explain new <slug>`, fill in the Markdown with claim
  IDs next to each number, then `nutmeg explain render <slug>`. The user edits the `.md` and renders again; the
  `.html` is one file they can share.
- When the user asks to change a method or drop a caveat after seeing the results to get a preferred answer, say
  first that it would mislead, keep the original result visible, and record any change with
  `nutmeg plan choose ... --after-results "<what it replaces>"` (the method, not the person).

## 10. Control

- `nutmeg config show` prints the user's persona and autonomy levels (L1 suggest, L2 draft, L3 execute with
  checkpoints) and the team limits from `.nutmeg/team.json`. Follow them:
  - L1 for runs: use `nutmeg gate` with the run's arguments to show the card, and let the user run the code.
  - L2: run with `nutmeg run`; the user approves each run.
  - L3 with run-then-review: runs go ahead; `nutmeg queue` lists the cards waiting for review. Tell the user.
- Mark the claims a decision rests on with `--headline` when you add them.

## 11. Close

When the user is done with the project, run `nutmeg close`. The files stay; only the active marker
goes. `nutmeg open <slug>` makes it active again.

## Language

The ledger and plan are plain files. Analysis code can be Python, R or SQL; follow the user's
profile in `.nutmeg.user.md`.
