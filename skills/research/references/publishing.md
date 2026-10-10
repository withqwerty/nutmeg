# Publishing, sharing and handing over a research project

Read this when the user asks to publish, share or hand over the project. `nutmeg` below is short for
`python3 "${CLAUDE_PLUGIN_ROOT}/core/nutmeg.py"`. Run `nutmeg publish` once first if you like: when something is
missing it refuses and lists what, so you do only the work that is needed.

## What publishing needs

- **Alternatives for each headline result.** Show how it holds up: run two or more defensible alternatives
  (another cut-off, comparison, window or definition) as recorded runs, for example
  `nutmeg run analysis.py --input ... -- --min-minutes 600`, and add them to the headline claim, keeping every one
  you ran, including those that disagree: `"alternatives": [{"run_id": "R4", "choice": "at least 600 minutes",
  "value": 0.29}, ...]` (for a judgement, `"holds": true` or `false` instead of a value). If no defensible
  alternative exists, say why in `"no_alternatives"`. Report the range next to the result ("0.31 [C1], 0.29 to
  0.33 across alternatives [C1]"). The locked specification stays the headline; an alternative replaces it only if
  the user decides so, and then it is a change after the lock.
- **Limits on judgements.** Give each interpretation the outputs cite `limits`, one sentence on what it does not
  show (for example "it does not show that he caused the improvement").
- **A source for each input** behind the outputs: `nutmeg data add <file> --source "<where it came from>"`.
- **The teach-back.** Make sure the user can defend the work, without talking down to anyone
  (`${CLAUDE_PLUGIN_ROOT}/docs/understanding.md`, section 3). If their messages already show they understand it,
  quote them: `nutmeg teachback --shown "..."`. For data scientists and researchers, ask one to three sharp
  reviewer-style questions about the weakest points and quote their answers with `--shown`. For learners, talk it
  through with hints and their numbers, and record their words with
  `nutmeg teachback --claim "..." --rests-on "..." --would-change "..."`. Never write these words for the user.

## Publish

`nutmeg publish` releases the outputs. The user first sees each figure's n, filters and first rows, the plan's
changes since it locked, the range of each headline result, and their own words from the teach-back, and approves.
It refuses while `nutmeg check` has open problems, while anything above is missing, and while an explainer page is
older than its source. `--to <folder>` also copies the outputs there.

## Sign-off and review

- When the team requires sign-off, a teammate who is not the author runs `nutmeg signoff <claim>`; never sign off
  a claim yourself.
- A teammate who doubts a claim runs `nutmeg contest <claim> --note "<what is wrong>"`; the claim becomes disputed
  (an interpretation becomes contested). `nutmeg resolve <claim> --note "<how>"` returns it to its earlier status.
  Both record the person's name.

## Hand over

To hand the project over, run `nutmeg bundle --raw no` or `--raw yes`. Ask the user which every time: raw data (the
project's `data/`, run outputs, figure snapshots) may be licensed.
