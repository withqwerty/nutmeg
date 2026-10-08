"""Record real football-docs responses and build the eval mock.

Usage (from the nutmeg repo root):

    python3 evals/_scaffold/record_football_docs.py \
        --server /path/to/football-docs/dist/index.js \
        --reep /path/to/reep-register-v1.duckdb

It starts the football-docs MCP server over stdio with its bundled index,
calls each tool in RECORDINGS, and writes evals/mocks/football-docs/_server.md:
an agent mock that may only replay these recorded responses. Re-run it when
football-docs changes, then re-run the evals.
"""
import argparse
import json
import os
import subprocess

XT_URL = "https://karun.in/blog/expected-threat.html"
XT_QUOTE = "a threatening pass is not always one that goes to a good shooting position"

# key -> (tool, arguments, keywords that route a call to this recording)
RECORDINGS = {
    "s01": ("search_docs", {"query": "big chance qualifier", "provider": "opta", "max_results": 4},
            "big chance, bigChance, 214, shot qualifiers, headed, head, own goal qualifier (Opta)"),
    "s02": ("search_docs", {"query": "expected goals xG qualifier", "provider": "opta", "max_results": 4},
            "xG, expected goals, xGOT, 321, 322, matchexpectedgoals, matchevent, endpoint, feed (Opta)"),
    "s05": ("search_docs", {"query": "own goal event", "provider": "statsbomb", "max_results": 4},
            "own goal, Own Goal For, Own Goal Against, goal attribution (StatsBomb)"),
    "s06": ("search_docs", {"query": "shot type penalty", "provider": "statsbomb", "max_results": 4},
            "penalty, shot type, set piece shot (StatsBomb)"),
    "s14": ("search_docs", {"query": "shot statsbomb_xg shot type", "provider": "statsbomb", "max_results": 4},
            "shot fields, statsbomb_xg, shot_statsbomb_xg, statsbombpy events, non-penalty xG, npxG (StatsBomb)"),
    "s07": ("search_docs", {"query": "FBref xG progressive passes", "max_results": 4},
            "FBref, advanced stats, xG on FBref, progressive passes, 2026 removal"),
    "s15": ("search_docs", {"query": "soccerdata FBref player season stats", "max_results": 4},
            "soccerdata FBref, read_player_season_stats, read_team_season_stats"),
    "s08": ("search_docs", {"query": "Reep register download DuckDB", "max_results": 4},
            "Reep, register, download, DuckDB, CSV, release, latest.json, REEP_DUCKDB_PATH, bulk IDs, crosswalk"),
    "s09": ("search_docs", {"query": "identity surfaces player ID", "provider": "transfermarkt", "max_results": 4},
            "Transfermarkt IDs, spieler, identity surfaces (Transfermarkt)"),
    "s13": ("search_docs", {"query": "identity surfaces player ID", "provider": "fbref", "max_results": 4},
            "FBref IDs, person ID, identity surfaces (FBref)"),
    "s10": ("search_docs", {"query": "Sofascore 403 challenge scraper", "max_results": 4},
            "Sofascore, 403, challenge, anti-bot, blocked, Cloudflare, scraper broken"),
    "s11": ("search_docs", {"query": "post-shot xG goalkeeper goals prevented", "max_results": 4},
            "goalkeeper, shot-stopping, save percentage, post-shot xG, PSxG, goals prevented"),
    "s12": ("search_docs", {"query": "possession adjusted defensive actions", "max_results": 4},
            "tackles, interceptions, defensive actions, possession-adjusted, PAdj, defender"),
    "s16": ("search_docs", {"query": "tackles won lost challenges", "max_results": 4},
            "tackle win rate, tackles won, tackles lost, challenges lost, dribbled past, duels"),
    "s17": ("search_docs", {"query": "distance covered high speed running physical metrics", "max_results": 4},
            "distance covered, km, sprints, physical metrics, running"),
    "s03": ("search_docs", {"query": "Catapult PlayerLoad high speed running export fields", "max_results": 5},
            "Catapult, STATSports, Kinexon, GPS, wearables, PlayerLoad, physical export fields"),
    "s04": ("search_docs", {"query": "Catapult", "provider": "catapult"},
            "any call with provider set to catapult, statsports, kinexon or another GPS vendor"),
    "g01": ("get_provider_docs", {"provider": "opta", "topic": "big chance"},
            "get_provider_docs for Opta (any topic about qualifiers or big chance)"),
    "l01": ("list_providers", {}, "list_providers"),
    "p01": ("resolve_provider_id", {"query": "Catapult"}, "Catapult, STATSports, Kinexon, GPS vendors"),
    "p02": ("resolve_provider_id", {"query": "Reep"}, "Reep, Reep Register, reep.football"),
    "p03": ("resolve_provider_id", {"query": "Opta"}, "Opta, Stats Perform"),
    "p04": ("resolve_provider_id", {"query": "StatsBomb"}, "StatsBomb, Hudl StatsBomb"),
    "p05": ("resolve_provider_id", {"query": "FBref"}, "FBref"),
    "p06": ("resolve_provider_id", {"query": "Transfermarkt"}, "Transfermarkt"),
    "p07": ("resolve_provider_id", {"query": "Sofascore"}, "Sofascore, soccerdata"),
    "r01": ("resolve_entity", {"provider": "transfermarkt", "namespace": "spieler", "id": "568177"},
            "resolve_entity with provider transfermarkt and id 568177 (with or without namespace)"),
    "r03": ("resolve_entity", {"provider": "fbref", "namespace": "person", "id": "dc7f8a28"},
            "resolve_entity with provider fbref and id dc7f8a28 (with or without namespace)"),
    "r02": ("resolve_entity", {"name": "Cole Palmer", "type": "player"},
            "resolve_entity by name (any name)"),
    "r00": ("resolve_entity", {"provider": "transfermarkt", "namespace": "spieler", "id": "0"},
            "resolve_entity with a provider and id not in this table (see rule 6)"),
    "m01": ("list_metrics", {}, "list_metrics"),
    "m02": ("get_metric", {"id": "ppda"},
            "ppda, PPDA, passes per defensive action, passes allowed per defensive action, pressing intensity"),
    "m03": ("get_metric", {"id": "ppda.statsbomb-hudl"}, "ppda.statsbomb-hudl, StatsBomb PPDA, Hudl PPDA"),
    "m04": ("get_metric", {"id": "ppda.trainor-2014"}, "ppda.trainor-2014, Trainor PPDA, original PPDA"),
    "m05": ("get_metric", {"id": "xa"}, "xa, xA, expected assists, pass-level expected assists"),
    "m06": ("get_metric", {"id": "xg_assisted"}, "xg_assisted, xAG, expected assisted goals, xG assisted"),
    "m07": ("get_metric", {"id": "npxg"}, "npxg, npxG, non-penalty xG, non-penalty expected goals"),
    "m08": ("get_metric", {"id": "progressive_passes"}, "progressive_passes, progressive passes, PrgP"),
    "m09": ("get_metric", {"id": "xt"}, "xt, xT, expected threat"),
    "m00": ("get_metric", {"id": "not-a-metric"}, "get_metric with an id not in this table (see rule 11)"),
    "x01": ("search_papers", {"query": "\"expected threat\" soccer"},
            "any search_papers query (expected threat, xT, possession value, EPV, VAEP, Singh)"),
    "x02": ("get_web_source", {"url": XT_URL},
            "get_web_source for karun.in/blog/expected-threat.html (Karun Singh, Introducing Expected Threat)"),
    "x03": ("match_quote", {"source": XT_URL, "quote": XT_QUOTE},
            "match_quote on the karun.in xT post with a quote that appears word for word in recording x02"),
    "x04": ("match_quote", {"source": XT_URL, "quote": "xT was first introduced by Opta in 2012 as a proprietary model"},
            "match_quote on the karun.in xT post with a quote that does not appear in recording x02"),
}

FALLBACK_SEARCH = "s03"

RULES = f"""You are a replay of the football-docs MCP server, version {{version}}.
You never write new documentation content. Every answer is one recorded response below, copied exactly.

How to answer a call:

1. Look at the tool name and the words in its arguments.
2. Choose the recording for that tool whose keywords share the most words with the arguments (ignore case and
   punctuation). For search_docs, get_provider_docs and compare_providers, any search recording may be used.
3. Return that recording's text exactly, character for character. Do not add, drop or reword anything.
4. search_docs, get_provider_docs or compare_providers with no keyword overlap at all: return recording
   {FALLBACK_SEARCH}. The real server almost always returns loosely related results.
5. resolve_provider_id for a provider not in the table: return exactly
   `Provider "<query>" is not registered. Use request_update to suggest adding it, or open a GitHub issue with the new-provider template.`
   as an error result.
6. resolve_entity with a provider and id not in the table: return recording r00 unchanged.
7. request_update: return exactly
   `Request queued locally. Open this pre-filled issue to send it: https://github.com/withqwerty/football-docs/issues/new`
8. Recordings marked `error` are tool errors: return them as an error result.
9. get_web_source for any URL other than the karun.in xT post, and get_paper or read_paper for any ID: return
   exactly `Could not fetch that source: the replay has no recording for it.` as an error result.
10. match_quote on the karun.in xT post: if the quote appears word for word in recording x02, return recording
   x03 with every copy of the recorded quote replaced by the caller's quote, and drop the lines from
   `- **Where:**` to the end of the JSON block. Otherwise return recording x04 unchanged. match_quote on any other
   source: return the rule 9 error.
11. get_metric: choose the recording whose keywords match the id. For a variant ID of a recorded card that has no
   recording of its own (for example ppda.wyscout), return that card's recording (for example m02). For a card or
   variant that recording m01 lists but this table has no recording for (for example vaep or field_tilt), return
   exactly `Could not read that card: the replay has no recording for it.` as an error result. For an id that
   matches no card or variant in m01, return recording m00 with `not-a-metric` replaced by the caller's id, as an
   error result. list_metrics: return recording m01.
"""


def record(server, reep):
    env = dict(os.environ, FOOTBALL_DOCS_DATA="bundled", REEP_DUCKDB_PATH=reep)
    proc = subprocess.Popen(["node", server], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, env=env)
    counter = [0]

    def send(msg):
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()

    def request(method, params):
        counter[0] += 1
        send({"jsonrpc": "2.0", "id": counter[0], "method": method, "params": params})
        while True:
            reply = json.loads(proc.stdout.readline())
            if reply.get("id") == counter[0]:
                return reply

    init = request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                  "clientInfo": {"name": "nutmeg-eval-recorder", "version": "1"}})
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    version = init["result"]["serverInfo"]["version"]
    tools = request("tools/list", {})["result"]["tools"]
    out = {}
    for key, (tool, args, _) in RECORDINGS.items():
        result = request("tools/call", {"name": tool, "arguments": args}).get("result", {})
        text = "\n".join(c.get("text", "") for c in result.get("content", []))
        out[key] = (text.rstrip(), bool(result.get("isError")))
    proc.kill()
    return version, tools, out


def build(version, tools, recorded, mock_dir):
    lines = ["---", "type: agent",
             "tools: [search_docs, get_provider_docs, compare_providers, list_providers, "
             "resolve_provider_id, resolve_entity, request_update, search_papers, get_paper, "
             "get_web_source, read_paper, match_quote, get_metric, list_metrics]",
             "---", "", RULES.format(version=version),
             "## Routing table", "", "| Recording | Tool | Keywords |", "| --- | --- | --- |"]
    for key, (tool, _, keywords) in RECORDINGS.items():
        lines.append(f"| {key} | {tool} | {keywords} |")
    lines += ["", "## Recordings", ""]
    for key, (tool, args, _) in RECORDINGS.items():
        text, is_error = recorded[key]
        lines += [f"### {key} — {tool} {json.dumps(args)}{' — error' if is_error else ''}", "",
                  "````text", text, "````", ""]
    os.makedirs(mock_dir, exist_ok=True)
    with open(os.path.join(mock_dir, "_server.md"), "w") as f:
        f.write("\n".join(lines))
    with open(os.path.join(mock_dir, "_tools.json"), "w") as f:
        json.dump({"tools": tools}, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", required=True, help="path to football-docs dist/index.js")
    parser.add_argument("--reep", required=True, help="path to a Reep release DuckDB")
    parser.add_argument("--out", default="evals/mocks/football-docs")
    args = parser.parse_args()
    version, tools, recorded = record(args.server, args.reep)
    build(version, tools, recorded, args.out)
    print(f"football-docs {version}: {len(recorded)} recordings -> {args.out}/_server.md")
