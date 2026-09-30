"""Adopt agent-mock recordings that match the real football-docs server.

Usage (from the nutmeg repo root, after an eval run):

    python3 evals/_scaffold/adopt_replays.py \
        --server /path/to/football-docs/dist/index.js \
        --reep /path/to/reep-register-v1.duckdb \
        evals/results/<run>/mock-recordings

For each recording, it calls the same tool with the same input on the real
server and writes the recording to evals/mocks/.replay/football-docs/ with the
real server's response in place of the agent mock's. Later eval runs then
replay real answers for those exact calls, with no model call. The report
says how many mock answers already matched the real server.
"""
import argparse
import glob
import json
import os
import subprocess


def start(server, reep):
    env = dict(os.environ, FOOTBALL_DOCS_DATA="bundled", REEP_DUCKDB_PATH=reep)
    proc = subprocess.Popen(["node", server], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, env=env)
    counter = [0]

    def request(method, params):
        counter[0] += 1
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": counter[0], "method": method, "params": params}) + "\n")
        proc.stdin.flush()
        while True:
            reply = json.loads(proc.stdout.readline())
            if reply.get("id") == counter[0]:
                return reply

    request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                           "clientInfo": {"name": "nutmeg-replay-check", "version": "1"}})
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    proc.stdin.flush()
    return proc, request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", required=True)
    parser.add_argument("--reep", required=True)
    parser.add_argument("--dest", default="evals/mocks/.replay/football-docs")
    parser.add_argument("recordings", nargs="+", help="mock-recordings directories")
    args = parser.parse_args()

    proc, request = start(args.server, args.reep)
    os.makedirs(args.dest, exist_ok=True)
    adopted, matched, rejected = 0, 0, []
    for rec_dir in args.recordings:
        for path in sorted(glob.glob(os.path.join(rec_dir, "football-docs", "*.json"))):
            rec = json.load(open(path))
            tool = os.path.basename(path).rsplit("-", 1)[0]
            result = request("tools/call", {"name": tool, "arguments": rec["input"]}).get("result", {})
            real = "\n".join(c.get("text", "") for c in result.get("content", []))
            real_error = bool(result.get("isError"))
            mock_error = rec.get("verdict") == "tool_error"
            if rec.get("output", "").strip() == real.strip() and real_error == mock_error:
                matched += 1
            else:
                rejected.append(f"{tool} {json.dumps(rec['input'])[:100]}")
            rec["output"] = real
            rec["verdict"] = "tool_error" if real_error else "ok"
            with open(os.path.join(args.dest, os.path.basename(path)), "w") as f:
                json.dump(rec, f, indent=2)
            adopted += 1
    proc.kill()
    print(f"wrote {adopted} replays with real responses; {matched} mock answers already matched the real server")
    for line in rejected:
        print("  mock differed from real:", line)


if __name__ == "__main__":
    main()
