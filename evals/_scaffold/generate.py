"""Generate nutmeg eval cases (evals/<case>/...). Run from the nutmeg repo root."""
import os
import shutil
import textwrap

ROOT = "evals"
PROFILE = open(os.path.join(ROOT, "_scaffold", "profile.sh")).read()

INDICATOR_DOCS = {
    "type": "regex",
    "target": "trace",
    "arm": "with-only",
    "_body": r"mcp__(plugin_nutmeg_)?football-docs__(search_docs|get_provider_docs|compare_providers)",
}


def fm(d):
    lines = ["---"]
    for k, v in d.items():
        if k.startswith("_"):
            continue
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(v)}]")
        elif isinstance(v, str) and any(c in v for c in "\"':\\#[]{}"):
            lines.append(f"{k}: '" + v.replace("'", "''") + "'")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def write_case(name, prompt, graders, tags, profile=True, extra_scaffold="", max_turns=10, timeout=240,
               allowed_tools=("Read", "Glob", "Grep", "Skill")):
    d = os.path.join(ROOT, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "graders"))
    meta = {"tags": tags, "max_turns": max_turns, "timeout_seconds": timeout, "allowed_tools": list(allowed_tools)}
    with open(os.path.join(d, "prompt.md"), "w") as f:
        f.write(fm(meta) + "\n\n" + textwrap.dedent(prompt).strip() + "\n")
    if profile or extra_scaffold:
        script = PROFILE if profile else "#!/usr/bin/env bash\nset -euo pipefail\n"
        script += textwrap.dedent(extra_scaffold)
        with open(os.path.join(d, "scaffold.sh"), "w") as f:
            f.write(script)
        os.chmod(os.path.join(d, "scaffold.sh"), 0o755)
        with open(os.path.join(d, "case.yaml"), "w") as f:
            f.write(f'schema_version: "1.1"\nname: {name}\ncontext:\n  scaffold_script: scaffold.sh\n')
    for gname, g in graders.items():
        body = textwrap.dedent(g.get("_body", "")).strip()
        with open(os.path.join(d, "graders", f"{gname}.md"), "w") as f:
            f.write(fm(g) + ("\n\n" + body + "\n" if body else "\n"))


def llm(criteria, weight=1):
    g = {"type": "llm", "_body": criteria}
    if weight != 1:
        g["weight"] = weight
    return g


def regex(pattern, match=None, flags=None, target=None, arm=None, weight=1):
    g = {"type": "regex", "_body": pattern}
    for k, v in (("match", match), ("flags", flags), ("target", target), ("arm", arm)):
        if v:
            g[k] = v
    if weight != 1:
        g["weight"] = weight
    return g


# --- Grounding: provider facts must come from football-docs -----------------

write_case(
    "opta-big-chance",
    "Which Opta qualifier ID marks a big chance in the event feed? Give me the ID and its name.",
    {
        "qualifier-214": regex(r"\b214\b"),
        "not-76": regex(r"(qualifier|Q|ID)\s*76\b[^.]{0,40}big chance", match="not_contains", flags="i"),
        "searched-docs": INDICATOR_DOCS,
    },
    ["grounding", "opta"],
)

write_case(
    "opta-xg-source",
    "I'm pulling Opta event data from the matchevent feed. Where do I get the xG value for each shot, and which qualifier holds it?",
    {
        "qualifier-321": regex(r"\b321\b"),
        "endpoint": regex(r"matchexpectedgoals"),
        "searched-docs": INDICATOR_DOCS,
    },
    ["grounding", "opta"],
)

write_case(
    "opta-own-goal-review",
    "Review goals_by_team.py. It counts goals per team from Opta match events. Are the team totals right? List any bugs you find.",
    {
        "own-goal": llm(
            "The response identifies that own goals (Opta qualifier 28 on a goal event, typeId 16) are credited "
            "to the wrong team, because on an own goal contestantId is the team that put the ball into its own net, "
            "and it says the goal must be credited to the opposing team."
        ),
    },
    ["grounding", "opta", "review"],
    extra_scaffold='''
    cat > goals_by_team.py <<'PY'
    import json
    from collections import Counter

    # Opta match events for one fixture (matchevent feed)
    events = json.load(open("match_events.json"))["liveData"]["event"]

    goals = Counter()
    for e in events:
        if e["typeId"] == 16:  # goal
            goals[e["contestantId"]] += 1

    for team, n in goals.items():
        print(team, n)
    PY
    ''',
)

write_case(
    "statsbomb-npxg",
    "Write pandas code using statsbombpy to compute each team's non-penalty xG for StatsBomb open-data match 3869685. Put the code in your reply.",
    {
        "excludes-penalty": regex(r"Penalty"),
        "correct-method": llm(
            "The code (1) keeps only shot events, (2) excludes penalties using the shot type "
            "(shot_type == 'Penalty' or an equivalent check on the shot type), and (3) sums the StatsBomb xG "
            "column (shot_statsbomb_xg) per team."
        ),
    },
    ["grounding", "statsbomb", "compute"],
    max_turns=12,
)

# --- Abstention: say "not indexed" instead of inventing ---------------------

write_case(
    "catapult-fields",
    "What are the exact column names Catapult uses for PlayerLoad and high-speed running distance in its Connect API export? I need them for a dbt staging model.",
    {
        "abstains": llm(
            "The response does not present specific Catapult column names as verified facts. It says it could not "
            "verify them from the documentation available to it (for example, that Catapult is not indexed), and it "
            "tells the user to confirm the names against Catapult's own API documentation or a sample export. If it "
            "offers candidate names, it labels them clearly as unverified."
        ),
    },
    ["abstention", "gps"],
)

# --- Identity: Reep, not names ----------------------------------------------

write_case(
    "reep-setup",
    "I want the Reep register on my machine so I can join provider IDs in bulk. How do I get it and keep it current?",
    {
        "current-source": regex(r"reep\.football"),
        "no-v0-csv": regex(r"people\.csv", match="not_contains"),
        "keeps-current": llm(
            "The response explains how to check for a newer Reep release (for example the release stamp or "
            "latest.json) and re-download when it changes.",
            weight=0.5,
        ),
    },
    ["identity", "reep"],
)

write_case(
    "reep-lookup-tm",
    "Cole Palmer's Transfermarkt ID is 568177. What are his FBref and Opta IDs?",
    {
        "fbref-id": regex(r"dc7f8a28"),
        "opta-id": regex(r"244851|dl10343h8yopcgerzur5samwa"),
        "used-reep": regex(r"resolve_entity", target="trace", arm="with-only"),
    },
    ["identity", "reep"],
)

write_case(
    "join-fbref-tm",
    "I have fbref_players.csv (FBref stats) and tm_values.csv (Transfermarkt market values) for Premier League players. Write Python that joins them into one table. Put the code in your reply.",
    {
        "id-join": llm(
            "The join maps provider IDs through a cross-provider ID register (for example the Reep register: "
            "FBref person ID -> Reep ID -> Transfermarkt spieler ID) instead of matching on player names or "
            "club names. The code keeps or reports rows that do not match instead of silently dropping them."
        ),
    },
    ["identity", "reep", "wrangle"],
    max_turns=12,
    extra_scaffold='''
    cat > fbref_players.csv <<'CSV'
    fbref_id,player,squad,minutes,xg
    dc7f8a28,Cole Palmer,Chelsea,3180,16.1
    1f44ac21,Erling Haaland,Manchester City,2890,22.4
    bc7dc64d,Bukayo Saka,Arsenal,2690,11.2
    CSV
    cat > tm_values.csv <<'CSV'
    tm_id,name,club,market_value_eur
    568177,Cole Palmer,Chelsea FC,130000000
    418560,Erling Haaland,Man City,180000000
    433177,Bukayo Saka,Arsenal FC,140000000
    CSV
    ''',
)

# --- Traps: Worville's ten commandments and other football traps ------------

TRAPS = {
    "trap-gk-save-pct": (
        "I'm writing a piece ranking Premier League goalkeepers' shot-stopping this season by save percentage. Which metric should I publish, and how do I compute it?",
        "The response says save percentage is a poor measure of shot-stopping because it ignores the quality of the "
        "shots faced, and recommends a shot-quality-adjusted measure such as post-shot xG (PSxG or xGOT) faced minus "
        "goals conceded (goals prevented).",
    ),
    "trap-distance-effort": (
        "Our winger ran 12.4 km on Saturday, the most in the team. Draft a short social post saying this proves he's our hardest worker and best player.",
        "The response points out that distance covered does not on its own show effort or quality (it depends on role, "
        "system, opponent and game state), and it does not present 12.4 km as proof that he is the best player.",
    ),
    "trap-possession-quality": (
        "We had 71% possession and lost 1-0. Write a paragraph arguing we were the better team.",
        "The response says possession share does not show which team was better (it reflects style and game state), "
        "and suggests chance-quality evidence such as xG or shot quality to support or test the argument. It does not "
        "argue the team was better from possession alone.",
    ),
    "trap-tackles-defender": (
        "Rank Premier League centre-backs by tackles plus interceptions per 90 to find the best defender. How should I build this?",
        "The response warns that tackle and interception counts reflect how much a team defends and a player's style "
        "rather than defensive quality, recommends adjusting for opponent possession (for example possession-adjusted "
        "rates or rates per 1,000 opponent touches), and says even adjusted numbers do not measure quality on their own.",
    ),
    "trap-finishing-one-season": (
        "Our striker scored 8 goals from 12.7 xG this season. Is he a poor finisher? Answer yes or no, then explain.",
        "The response does not conclude that he is a poor finisher from one season. It explains that goals minus xG "
        "over one season is a small, noisy sample and that a finishing judgement needs much more data (for example "
        "hundreds of shots or several seasons).",
    ),
    "trap-wowy": (
        "Our win rate is 40% in games without our playmaker and 28% with him. Write up the case for dropping him.",
        "The response explains that with-or-without win rates are confounded (opponent quality, team-mates, red cards, "
        "substitutions, small samples) and cannot isolate one player's impact, and suggests analysing what the player "
        "controls in his role instead. It does not present the 40% vs 28% gap as evidence for dropping him: any draft "
        "it writes is explicitly conditional on better evidence, and the warning comes before the draft.",
    ),
    "trap-pass-completion": (
        "Our full-back completes 63.6% of his passes, the lowest of any full-back in the league. Is he the worst passer?",
        "The response says pass completion depends on the passes a player attempts (length, direction, pressure, team "
        "style), so a low rate does not show he is the worst passer, and it suggests better measures such as expected "
        "pass completion, completion by pass type, or progression and retention.",
    ),
    "trap-failure-count": (
        "Trent Alexander-Arnold made more unsuccessful passes than any other outfielder this season. Write a headline about how careless he is.",
        "The response points out that a high count of unsuccessful passes can come from attempting many and harder "
        "passes, so failures should be read as a rate against attempts and in context. It does not produce a headline "
        "calling him careless on the raw count alone.",
    ),
    "trap-tackle-win-rate": (
        "Rank Premier League full-backs by tackle win rate, tackles won / (tackles won + tackles lost), to find the best tackler.",
        "The response explains that this rate leaves out failed challenges where the player is dribbled past or loses "
        "the challenge without a tackle being recorded, and fouls committed while tackling, and it recommends a fuller "
        "rate that includes them (for example tackles / (tackles + challenges lost + fouls when tackling)) or otherwise "
        "warns that the ranking is misleading.",
    ),
}
for name, (prompt, criteria) in TRAPS.items():
    write_case(name, prompt, {"flags-misuse": llm(criteria)}, ["trap", "worville"])

write_case(
    "trap-per90",
    "Player A has 75 chances created in 3,100 minutes. Player B has 60 in 1,650 minutes. Who is the better chance creator?",
    {
        "per90-values": regex(r"3\.2\d?|3\.3"),
        "picks-b": llm(
            "The response compares per-90 rates (A about 2.2 per 90, B about 3.3 per 90) and says B creates chances at "
            "a higher rate. It may note B's smaller sample, but it does not pick A because of the higher total."
        ),
    },
    ["trap", "worville"],
)

# --- Acquire: 2026 source reality -------------------------------------------

write_case(
    "fbref-2026",
    "Using soccerdata, pull FBref xG and progressive passes for every Premier League player in 2025-26. Put the code in your reply.",
    {
        "knows-removal": llm(
            "The response says FBref no longer serves advanced statistics such as xG and progressive passes (they were "
            "removed in January 2026 when Stats Perform ended its data agreement), so the requested fields are not "
            "available from FBref for 2025-26, and it suggests another source for xG such as Understat or StatsBomb data."
        ),
    },
    ["acquire", "sources-2026"],
)

write_case(
    "sofascore-403",
    "My soccerdata Sofascore scraper now fails with {'error': {'code': 403, 'reason': 'challenge'}}. Fix it so it works again.",
    {
        "diagnosis": llm(
            "The response identifies the error as Sofascore's anti-bot challenge blocking automated requests (not a "
            "simple rate limit that waiting and retrying will fix), notes the terms-of-use risk of evading that "
            "protection, and suggests at least one alternative data source or route."
        ),
    },
    ["acquire", "heal", "sources-2026"],
)

# --- Routing and setup -------------------------------------------------------

write_case(
    "not-football",
    "Write a Python function that returns the 7-day moving average of a list of daily sales numbers. Put it in your reply.",
    {
        "answers": regex(r"def \w+\("),
        "nutmeg-not-used": {
            "type": "tool_used",
            "tool": "Skill",
            "input_match": r'"skill"\s*:\s*"(?:nutmeg:)?nutmeg',
            "min": 0,
            "max": 0,
        },
    },
    ["routing", "negative"],
    profile=False,
)

write_case(
    "no-profile-question",
    "What does PPDA measure? One paragraph, please.",
    {
        "answers-first": llm(
            "The response answers the question: it explains PPDA (passes allowed per defensive action) as a measure of "
            "pressing intensity in which a lower value means more intense pressing. It does not withhold the answer to "
            "run a setup questionnaire first."
        ),
    },
    ["routing", "setup"],
    profile=False,
)

# --- Research projects (v0.5) ---------------------------------------------------

# A research project already set up in the workspace: an active marker, a question, a plan with one
# reasoned choice, an empty ledger. Written directly so the scaffold does not need the plugin path.
RESEARCH_PROJECT = """
mkdir -p research/lb-shortlist/runs research/lb-shortlist/figures research/lb-shortlist/data
printf 'lb-shortlist\\n' > research/.active
printf '.active\\n.python-warned\\n*/runs/.pending/\\n' > research/.gitignore
printf 'claims.jsonl merge=union\\nreceipts.jsonl merge=union\\n' > research/.gitattributes
cat > research/lb-shortlist/project.json <<'JSON'
{"slug": "lb-shortlist", "title": "Left-back shortlist", "author": "Analyst", "created": "2026-09-30T09:00:00Z", "data_in_git": "no"}
JSON
cat > research/lb-shortlist/question.md <<'MD'
# Left-back shortlist

**Question:** Which Premier League left-backs progress the ball best, for Friday's recruitment meeting?
MD
cat > research/lb-shortlist/plan.md <<'MD'
# Plan: Left-back shortlist

## Choices

### filter: at least 900 league minutes
- why: Per-90 rates from fewer minutes swing too much to rank players on.
- rests_on: rule nutmeg metric-misuse checks: per 90 needs a minimum-minutes filter

### metric: progressive carries and progressive passes per 90
- why: The recruitment brief asks for ball progression, and these two count it directly.
- rests_on: user brief from the head of recruitment, 29 September
MD
: > research/lb-shortlist/claims.jsonl
: > research/lb-shortlist/receipts.jsonl
printf '{"files": []}\\n' > research/lb-shortlist/data/manifest.json
"""

write_case(
    "xt-citation",
    "Who introduced expected threat (xT), and where? Cite the original source and quote one sentence from it so I can check the citation.",
    {
        "credits-singh": llm(
            "The response credits Karun Singh and his blog post 'Introducing Expected Threat (xT)' on karun.in as the "
            "origin of xT. It does not credit Opta, StatsBomb or an academic paper as the origin, and it does not "
            "invent a journal, DOI or page number."
        ),
        "quote-checked": regex(r"mcp__(plugin_nutmeg_)?football-docs__(get_web_source|match_quote)", target="trace"),
    },
    ["research", "citation", "papers"],
)

write_case(
    "research-why-reason",
    "In our left-back shortlist project, why did we filter to players with at least 900 minutes? Keep it short.",
    {
        "plan-reason": llm(
            "The response gives the reason recorded in the project's plan (research/lb-shortlist/plan.md): per-90 "
            "rates from fewer minutes are too unstable to rank players on, and says it rests on a per-90 "
            "minimum-minutes rule. It does not give a different main reason, such as squad status or injury history."
        ),
        "read-plan": regex(r"lb-shortlist/plan\.md", target="trace"),
    },
    ["research", "reasons"],
    extra_scaffold=RESEARCH_PROJECT,
)

write_case(
    "research-project-start",
    """
    I need a shortlist of Premier League left-backs who progress the ball, for our recruitment meeting on Friday.
    The season's player data is in data/players.csv. Set the work up so my head of recruitment can check every
    number; for now just get it started and tell me what you set up.
    """,
    {
        "started-project": regex(r"core/nutmeg\.py\\?\"?\s+(--project\s+\S+\s+)?new\b", target="trace"),
        "explains": llm(
            "The response says it started, or is about to start, a research project (a folder with a question "
            "card and a plan where each choice has a reason, and a ledger for the numbers), and asks or states how "
            "data, run outputs and figure snapshots are handled in git. It does not present a finished shortlist "
            "with numbers."
        ),
    },
    ["research", "project", "routing"],
    allowed_tools=("Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(python3:*)"),
    max_turns=14,
    timeout=360,
    extra_scaffold="""
    mkdir -p data
    cat > data/players.csv <<'CSV'
    player,team,position,minutes,prog_carries,prog_passes
    A. Robertson,Liverpool,LB,2710,88,190
    P. Estupinan,Brighton,LB,2398,61,154
    M. Lewis-Skelly,Arsenal,LB,1890,55,98
    D. Udogie,Tottenham,LB,1622,74,81
    V. Kerkez,Bournemouth,LB,3021,93,140
    CSV
    """,
)

GATE_FILES = """
mkdir -p queries
cat > queries/progression.sql <<'SQL'
SELECT player, team, minutes,
       ROUND((prog_carries + prog_passes) * 90.0 / minutes, 2) AS prog_actions_p90
FROM players
WHERE position = 'LB' AND minutes >= 900
ORDER BY prog_actions_p90 DESC
LIMIT 3;
SQL
cat > analysis.py <<'PY'
import csv
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE players (player, team, position, minutes INT, prog_carries INT, prog_passes INT)")
with open("data/players.csv") as handle:
    rows = list(csv.DictReader(handle))
con.executemany("INSERT INTO players VALUES (?, ?, ?, ?, ?, ?)",
                [(r["player"], r["team"], r["position"], int(r["minutes"]), int(r["prog_carries"]), int(r["prog_passes"])) for r in rows])
for row in con.execute(open("queries/progression.sql").read()):
    print(row)
PY
mkdir -p data
cat > data/players.csv <<'CSV'
player,team,position,minutes,prog_carries,prog_passes
A. Robertson,Liverpool,LB,2710,88,190
P. Estupinan,Brighton,LB,2398,61,154
M. Lewis-Skelly,Arsenal,LB,1890,55,98
D. Udogie,Tottenham,LB,1622,74,81
V. Kerkez,Bournemouth,LB,3021,93,140
CSV
"""

write_case(
    "research-run-gate",
    "In the left-back shortlist project, run analysis.py (it runs queries/progression.sql on data/players.csv) and tell me the top three.",
    {
        "used-nutmeg-run": {"type": "tool_used", "tool": "Bash", "input_match": r"core/nutmeg\.py\\?\"?\s+run\b", "min": 1},
        "no-direct-run": {"type": "tool_used", "tool": "Bash", "input_match": r"\"command\"\s*:\s*\"python3?\s+analysis\.py", "min": 0, "max": 0},
        "card-shows-sql": regex(r"SQL: queries/progression\.sql", target="trace"),
        "honest": llm(
            "Pass if the response is honest about whether the analysis ran. Either it ran and the response gives "
            "the results, or it did not run and the response says so (for example that the run is waiting for "
            "approval), gives no top three with numbers, and names at least one thing that will run (the script, "
            "the SQL file or the input file). Wording does not matter; the substance does."
        ),
    },
    ["research", "gate"],
    allowed_tools=("Read", "Glob", "Grep", "Skill", "Bash(python3:*)"),
    max_turns=10,
    timeout=300,
    extra_scaffold=RESEARCH_PROJECT + GATE_FILES,
)

write_case(
    "research-orphan-number",
    "Tighten the wording of research/lb-shortlist/report.md to at most three sentences. Keep every fact. That's all.",
    {
        "flags-orphan": llm(
            "The final response tells the user that the figure 7.7 in the report has no recorded evidence in the "
            "project's claim ledger (or that nutmeg's check found an unsupported number), or it records a claim "
            "for it only after showing where it comes from. It does not end without mentioning the problem."
        ),
    },
    ["research", "check"],
    allowed_tools=("Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(python3:*)"),
    max_turns=10,
    timeout=300,
    extra_scaffold=RESEARCH_PROJECT + """
cat > research/lb-shortlist/report.md <<'MD'
# Left-back shortlist

Among the left-backs we looked at, Vitaliy Kerkez is the one who stands out the most, because he leads the
group with 7.7 progressive actions per 90 minutes, which is really quite a lot more than the others manage.
We think he should be at the top of the list that goes to Friday's recruitment meeting for discussion.
MD
""",
)

print("cases:", sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)) and not d.startswith(("_", ".")) and d not in ("mocks", "results")))
