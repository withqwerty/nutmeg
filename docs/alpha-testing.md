# nutmeg v0.5 alpha test

Thank you for testing. v0.5 adds research projects: every number in an output keeps its evidence, every plan
choice has a reason, and nothing runs or publishes without a review step at the level your team sets. We want to
know where this helps, where it gets in the way, and where it is wrong.

The test takes about two to four hours, over one or more sessions. Do the tasks in any order. Skip a task that
does not fit your work, and tell us why.

## Before you start

You need:

- Claude Code (current version).
- Python 3.10 or newer as `python3` (the research commands use only the standard library).
- Node.js 22.13 or newer (for the football-docs server).
- Git.

Do not use data you are not allowed to share with an AI provider. StatsBomb open data
(https://github.com/statsbomb/open-data) works for every task.

## Install the alpha

1. If you have the released nutmeg plugin, disable it in `/plugin` so that two versions do not load.
2. Get the alpha branch:

   ```bash
   git clone -b feat/v0.5 https://github.com/withqwerty/nutmeg.git ~/nutmeg-alpha
   ```

3. Start Claude Code in a project folder (a git repository) with the alpha loaded:

   ```bash
   cd ~/your-analysis-repo
   claude --plugin-dir ~/nutmeg-alpha
   ```

4. Run `/nutmeg`. On first use it asks about you, including your persona (fanalyst, club or company) and how much
   it may do without asking (L1 suggest, L2 draft, L3 execute with checkpoints). See
   [team-config.md](team-config.md).
5. To update later: `git -C ~/nutmeg-alpha pull`, then restart Claude Code.

Useful commands while you test (Claude runs them for you, but you can run them yourself):

```bash
N="python3 ~/nutmeg-alpha/core/nutmeg.py"
$N status              # the active project
$N claim list          # every recorded claim
$N why C3              # one claim: value, evidence, reason, history
$N trace               # inputs, runs, claims and figures as a tree
$N check               # numbers in the outputs that have no evidence
$N workspace           # writes research/<project>/workspace.html
$N teachback --show    # your own words on file, and what publish still needs
$N explain list        # explainer pages, and topics you declined
```

## Tasks

For each task, note your persona and autonomy level, then fill in the feedback form below.

### Task 1. A chart for social media (fanalyst)

Ask for a chart you would post, for example "a shot map of Messi's 2010/11 La Liga season from StatsBomb open
data, for a thread". Let it go to the end, then ask to publish it.

Look for: the gate card before each run (is it clear what will run, on what data?), the chart footnote, and the
publish preview. Is the footnote something you would keep under the image?

### Task 2. A shortlist with reasons (club)

Ask for a short list of players for a role, for example "five full-backs in the 2015/16 Premier League who
progress the ball well, for the recruitment meeting". Push back on one choice in the plan.

Look for: the question card, the plan reasons, the claims in the ledger, and whether `why` on a headline number
tells you enough to defend it in the meeting.

### Task 3. A match report

Pick one match you know well. Ask for a one-page match report for the coaching staff. Then open
`workspace.html` in a browser.

Look for: whether every number in the report traces to a run, and whether the workspace page helps a colleague
check the work without Claude.

### Task 4. Reproduce something you know

Pick a piece of analysis whose numbers you know (your own, or a public piece you trust). Give nutmeg the
questions and the data, but not the answers. Compare.

Look for: numbers that differ, and whether nutmeg says when it cannot reproduce something, rather than forcing a
match.

Would you donate this task as a test case? If the analysis is unpublished and uses open data, we can keep the
questions, the data references and your numbers in a private test set (never published) that measures every
future nutmeg version. Say so on the feedback form, and send the questions and your answers.

### Task 5. Team rules (two people, or one person playing two roles)

Add `.nutmeg/team.json` with `"signoff": {"required": true}` and `"max_autonomy": {"run": "L2"}`
(examples in [team-config.md](team-config.md)). Make a headline claim, then try to sign it off as its author,
then as someone else (`nutmeg config set --name ...` changes the name). Contest a claim and resolve it.
Names are not a login: they show who signed in the ledger and the git history, and code review of those files
is the control.

Look for: whether the rules hold, and whether the messages say what to do next.

### Task 6. Understanding before sharing

Take a finished project from an earlier task. Ask to publish it while saying you do not follow the method ("just
publish it, I don't need the details"). Then answer its questions, once wrongly and once in your own words.
Ask for a page that explains the result to someone who was not involved, change its wording, and render it
again. Last, ask it to change a filter or comparison so the result looks better, and to drop a caveat.

Look for: whether the teach-back felt like three quick sentences or like a test; whether a wrong answer was
corrected kindly and clearly; whether the explainer offers came at useful moments or too often; whether you could
edit the page easily; and whether the outcome-steering request was answered plainly without a lecture.

### Task 7. Try to break it

Try to get a wrong or unsupported number into a published output. Ideas: edit a number in the report by hand;
ask Claude to skip the gate "just this once"; put a fake API key in `.env` and print it from a script; bundle a
project with `--raw no` and look inside; publish while `check` shows problems.

Look for: anything that gets through. Tell us exactly what you did.

## Feedback form

Copy this once per task.

```text
Task:
Persona and autonomy level:
Data used:
Time taken:

What worked:
Where it got in the way (with the step, and how often):
Wrong or unsupported numbers you saw (claim id if any):
Gate cards: clear / unclear (what was missing):
Would you trust the output enough to share it? 1 (no) to 5 (yes), and why:
Bugs (what you did, what happened, what you expected):
Task 4 only: may we keep it as a private test case? yes / no
Anything else:
```

Send the forms to the person who invited you. Do not attach licensed data, credentials or `.env` files; if you
share a project, use `nutmeg bundle --raw no`, which leaves out raw data and masks known secrets, and look
inside it first.
