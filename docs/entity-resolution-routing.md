# Entity Resolution Routing

Nutmeg routes football entity-resolution work. It does not own provider facts,
identity doctrine, or private register mutation rules.

Use this routing whenever the user asks about:

- matching the same player, coach, team, match, season, or competition across
  providers;
- resolving a provider ID into another provider's ID;
- deciding whether two provider records are the same real-world entity;
- understanding provider ID grains, duplicate pages, split teams, or season and
  stage quirks;
- building candidate-generation, evidence, review, or matching code.

## Route By Question

| User Need | Route |
|---|---|
| "What does this provider ID represent?" | Use `football-docs` identity-surface docs with `search_docs`. |
| "Which fields are safe evidence for this provider?" | Use `football-docs`; search for `identity surfaces`, `id schemes`, and provider quirks. |
| "Resolve this public player/team/coach ID." | Use the reep tools (`resolve`, `translate`, `current`), or `resolve_entity` when they are not available (see "Looking Up IDs" below). |
| "Fill Reep IDs into my database." | Use the `reep sync` command: a dry run first, `--apply` only when the user agrees (see "Filling a database" below). |
| "Join two providers' data." | Join through Reep IDs: `(provider, namespace, id)` → Reep ID → the other provider's ID. Report unmatched rows; never join on names alone. |
| "Write matching or candidate-recovery code." | Point to `reep-toolkit` for public guides, provider cards, schemas, templates and reference scripts. |
| "How should a partner/team run an entity-resolution process?" | Mention the matching logic pack only if the user has access to that private material. |
| "What is Reep's private minting doctrine?" | Do not answer from Nutmeg. Point to Reep Register documentation or ask the user to provide the private docs. |

## Provider Facts

Provider facts belong in `football-docs`, not in Nutmeg. Always check the docs
before answering provider-specific claims about:

- ID grains and URL handles;
- entity hierarchy and season or stage shape;
- lineups, squads, appearances, current-team fields, and career surfaces;
- profile attributes such as DOB, nationality, position, and role;
- source access constraints and public/private data boundaries.

Useful searches:

```text
search_docs(query="identity surfaces player ID team ID match ID", provider="<provider>")
search_docs(query="provider quirks duplicate players split teams season stages", provider="<provider>")
search_docs(query="lineup squad career membership current team", provider="<provider>")
```

## Looking Up IDs

The Reep Register is published as a CC0 release. Nutmeg has two ways to read it:
the optional reep tools, and football-docs' `resolve_entity`. Use the reep tools when
the user has added them; otherwise use `resolve_entity`.

### 1. The reep tools (optional)

The `reep` MCP server is not part of the plugin. A user who joins data from more
than one provider can add it once, for all projects. It needs `uvx` (part of
[uv](https://docs.astral.sh/uv/)):

```bash
claude mcp add --scope user reep -- uvx --from 'reep[mcp]>=0.1,<0.2' reep mcp
uvx --from 'reep>=0.1,<0.2' reep catalog sync    # the register: about 210 MB, free, no key
```

A user who already has the register file for `resolve_entity` (below) can reuse it
instead of the download; reep then reads that file as it is, so the user replaces
it each week as before:

```bash
claude mcp add --scope user reep -e REEP_DUCKDB_PATH=/absolute/path/reep-register-v1.duckdb -- uvx --from 'reep[mcp]>=0.1,<0.2' reep mcp
```

Then restart Claude Code. Offer this when a task needs many ID lookups, translations
between providers, or Reep IDs in the user's database. Do not add it without asking.

Its read-only tools are `resolve`, `translate`, `current`, `entity`, `search`,
`providers` and `status` (full names `mcp__reep__resolve` and so on). The server's
own instructions describe them, and `uvx --from 'reep>=0.1,<0.2' reep skill print`
prints the full guide; follow those.

- If `status()` shows `backend` as `null`, there is no register. Tell the user the
  download is about 210 MB (free, no key) and ask them to run the `catalog sync`
  line above, or to reuse their register file.
- If the server is listed as failed in `/mcp`, `uvx` is probably not installed. Tell
  the user to install uv, or use `resolve_entity` (below).

Rules (they hold for `resolve_entity` too):

- A provider ID is a triple: provider, namespace and external ID. Check the
  namespaces with `providers(provider="<provider>")`; never look up a bare number.
- Check `data.status` before using `data.reep_id`: `found`, `not_found`,
  `ambiguous` or `withdrawn`. A withdrawn ID has no Reep ID; report its reason.
- For a stored Reep ID, `current` says `active`, `retired`, `redirected` (store
  `current_id` instead), `withdrawn` (stop using it) or `unknown` (no current ID
  could be found; report it as unresolved).
- For joins, use only live provider IDs: a target whose `upstream_status` is
  `retired` or `removed` is one the provider no longer uses.
- A target whose `reep_id` differs from the entity's came through an ID merged
  into it (football-docs marks these "(via merged <id>)"). It is a valid ID for the
  entity. The hosted API does not list these; a local register (the catalogue
  from `reep catalog sync`, or the file at `REEP_DUCKDB_PATH`) does.
- `search` is for discovery only. Names are not unique and the register has no
  dates of birth. Confirm a name hit with a provider ID, club or season.
- If a lookup returns no match, report the entity as unresolved. Do not supply
  an ID from memory.
- Keep the release stamp (`release_stamp` in each result) with your output.

Outside an MCP client, the same lookups run from the shell with `--json`, for
example `uvx --from 'reep>=0.1,<0.2' reep translate transfermarkt/spieler/568177 --to fbref --json`.
The documentation is at https://reep.football/docs/python/.

### 2. `resolve_entity` (football-docs, the default)

football-docs ships with the plugin, so this tool is there without extra set-up.
Use it when the reep tools are not available. Without set-up, `resolve_entity`
maps no IDs: it explains the set-up and returns the DuckDB query that would answer
the question. There are two ways to enable it:

- **Local file (free, no key).**
  1. Download the release once: `curl -L -o reep-register-v1.duckdb https://reep.football/downloads/duckdb`
     (one DuckDB file of about 780 MB; a new release comes out each week, and
     `resolve_entity` says when your copy is out of date).
  2. Point the football-docs server at it with the file's absolute path:
     - with the nutmeg plugin, export `REEP_DUCKDB_PATH` in the shell that starts
       Claude Code, then restart it (the plugin's server inherits that environment);
     - with a server you added yourself:
       `claude mcp add football-docs -e REEP_DUCKDB_PATH=/absolute/path/reep-register-v1.duckdb -- npx -y football-docs@0.17.4`
       (or `"env": {"REEP_DUCKDB_PATH": "..."}` in your MCP JSON).
  3. Record the release stamp. `resolve_entity` prints it; the current stamp is at
     `https://data.reep.football/releases/latest.json`.

  Reading the file needs `@duckdb/node-api`, an optional dependency that `npx`
  installs with football-docs; if its native build fails, `resolve_entity` says so.
- **API key.** Set `REEP_API_KEY`. Keys are issued by hand: a free evaluation key
  (30 days, extended on request) is available through https://reep.football/api.

Call `resolve_entity` with a full provider key where you have one:

```text
resolve_entity(provider="transfermarkt", namespace="spieler", id="568177")
resolve_entity(reep_id="rp53af22bbeaa667")
resolve_entity(name="Cole Palmer", type="player")   # shortlist only
```

A name search returns a shortlist, and it can miss players whose register label is
their full legal name.

### Bulk joins

For a join on a data frame or a file, query the release DuckDB directly (its
`bridges` table maps `provider`, `namespace` and `external_id` to `reep_id`), or
pipe one ID per line into `reep resolve - --json`. Follow redirects for merged or
withdrawn IDs as the release documentation describes, keep unmatched rows, and
keep the release stamp with your output.

### Filling a database

When the user keeps provider IDs in their own database (PostgreSQL, MySQL, SQL
Server or SQLite), the `reep sync` command fills a Reep ID column and other
providers' ID columns. It writes to the user's database, so:

1. `reep init` writes a `reep.yml` that names the tables and columns. Help the user
   fill it in.
2. Run `reep sync <target> --json` without `--apply` and show the planned counts.
3. Add `--apply` only when the user agrees.
4. Exit code 4 means rows need review: `reep review --output reep-review.csv`
   writes them for a person to check. Do not resolve them by guessing.

The database drivers are extras: `reep[postgres]`, `reep[mysql]`, `reep[mssql]` or
`reep[db]`.

If `reep sync` stops and asks for a snapshot (its catalogue was updated from
changelogs, which keep stale provider status), run
`uvx --from 'reep>=0.1,<0.2' reep catalog sync --method snapshot`, then sync again.

## Matching Code

When the user needs reusable code rather than a one-off lookup, route them to
`reep-toolkit` (https://github.com/withqwerty/reep-toolkit). It is the public
surface for:

- guides on bridging provider IDs and matching thresholds;
- provider cards with ID semantics and quirks;
- reference schemas and evidence/candidate templates;
- small reference scripts and fixtures.

Nutmeg can explain which surface to use and help wire it into the user's
project, but it should not define a separate evidence schema.

## Private Partner Material

The matching logic pack is partner-facing operating material. Reference it only
when the user says they have access or explicitly provides its contents.

Do not leak or invent private pack doctrine. If the user lacks access, answer
with the public surfaces:

- provider facts: `football-docs`;
- public matching guidance and reference scripts: `reep-toolkit`;
- public IDs and bridges: the Reep Register release (DuckDB/CSV);
- process guidance: public Reep documentation and correction intake.

## Safe Defaults

- Prefer deterministic provider IDs and relationship evidence over fuzzy names.
- Treat relationship evidence as candidate narrowing, not proof by itself.
- Keep provider ontology separate from the user's target world model.
- Leave unresolved residue for review rather than forcing weak matches.
