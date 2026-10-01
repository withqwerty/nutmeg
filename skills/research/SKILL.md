---
name: nutmeg-research
description: "Run a football analysis as a research project that shows its work: a question card, a plan where every choice has a reason, and a claim ledger that ties every number, provider fact, ID and citation to its evidence. Use when the user wants analysis to publish or to decide on (a recruitment shortlist, a match or opposition report, a club memo, a chart or thread for social media), asks for sourced or checkable numbers, or says 'research project'. Quick questions stay outside projects."
argument-hint: "[the question to research]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "AskUserQuestion", "mcp__plugin_nutmeg_football-docs__search_docs", "mcp__football-docs__search_docs", "mcp__plugin_nutmeg_football-docs__resolve_entity", "mcp__football-docs__resolve_entity", "mcp__plugin_nutmeg_football-docs__get_provider_docs", "mcp__football-docs__get_provider_docs"]
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
  - `registry`: a Reep Register record;
  - `rule`: a practitioner rule, such as `${CLAUDE_PLUGIN_ROOT}/docs/metric-misuse.md`;
  - `paper`: a paper or post;
  - `claim`: an earlier claim in this ledger;
  - `user`: the user's instruction, quoted.
- Never invent a source. If nothing supports a choice, say so in the reason and use `user` only
  when the user asked for it.

Run `nutmeg plan check`, fix what it reports, then show the user the plan and ask them to approve
or change it before you fetch or compute anything.

## 4. Run the analysis through the gate

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

## 5. Record claims

Every number, provider fact, ID, citation, definition and interpretation that appears in the
project's outputs goes into the ledger:

```bash
nutmeg claim add --json '{"kind": "computed", "statement": "npxG/90 rose to 0.41", "value": 0.41,
  "evidence": {"run_id": "R3", "metric": "npxG per 90", "n": 31, "filters": {"min_minutes": 900}},
  "why": "Per 90 with a 900-minute floor keeps small samples out."}'
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

- An interpretation is never "verified". It is `supported` or `contested`.
- Put the claim ID next to the number in reports and captions, for example `0.41 [C3]`.
- Never write a number in an output that is not in the ledger.
- `nutmeg claim list` shows the ledger and any bad lines.

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

## 7. Explain and review claims

- `nutmeg why <claim>` prints a claim's value, definition, evidence (the run and code lines, the
  docs source, the Reep ID and release, or the paper and quote), filters, n, up to five sample
  rows, the reason and its history. Use it to answer "where does this number come from?". Add
  `code_lines` (for example `analysis.py:12-20`) and `snapshot` (a CSV or JSON of the rows behind
  the number) to a computed claim's evidence so `why` can show them.
- `nutmeg trace` prints inputs, runs, claims and figures as a tree.
- A teammate who doubts a claim runs `nutmeg contest <claim> --note "<what is wrong>"`; the claim
  becomes disputed (an interpretation becomes contested). `nutmeg resolve <claim> --note "<how>"`
  returns it to its earlier status. Both record the person's name.

## 8. Close

When the user is done with the project, run `nutmeg close`. The files stay; only the active marker
goes. `nutmeg open <slug>` makes it active again.

## Language

The ledger and plan are plain files. Analysis code can be Python, R or SQL; follow the user's
profile in `.nutmeg.user.md`.
