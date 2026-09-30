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
| "Resolve this public player/team/coach ID." | Use the Reep Register lookup via `resolve_entity` (see "Looking up IDs" below). |
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

The Reep Register is published as a CC0 release (DuckDB and CSV). The
`resolve_entity` tool reads a local copy of the release DuckDB; API keys are
issued only to data partners.

Set up a local copy once:

1. Download the release: `curl -L -o reep-register-v1.duckdb https://reep.football/downloads/duckdb`
   (several hundred MB).
2. Set `REEP_DUCKDB_PATH` to the file's absolute path in the shell that starts
   Claude Code, then restart it.
3. Record the release stamp. `resolve_entity` prints it and says when a newer
   release exists; the current stamp is at
   `https://data.reep.football/releases/latest.json`.

Call `resolve_entity` with a full provider key where you have one:

```text
resolve_entity(provider="transfermarkt", namespace="spieler", id="568177")
resolve_entity(reep_id="rp53af22bbeaa667")
resolve_entity(name="Cole Palmer", type="player")   # shortlist only
```

- Provider + namespace + id is the reliable path. Check the provider's
  namespaces with `search_docs(query="identity surfaces", provider="<provider>")`.
- A name search returns a shortlist, and it can miss players whose register
  label is their full legal name. Confirm a name hit with a provider ID, club or
  season before you use it.
- If a lookup returns no match, report the entity as unresolved. Do not supply
  an ID from memory.

For bulk joins, query the release DuckDB directly (its `bridges` table maps
`provider`, `namespace` and `external_id` to `reep_id`). Follow redirects for
merged or withdrawn IDs as the release documentation describes, and keep the
release stamp with your output.

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
