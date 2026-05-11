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
| "Resolve this public player/team/coach ID." | Use the Reep Register lookup via `resolve_entity` when available. |
| "Write matching or candidate-recovery code." | Point to `reep-scripts` for public reusable schemas, loaders, matchers, and templates. |
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

## Matching Code

When the user needs reusable code rather than a one-off lookup, route them to
`reep-scripts`. That is the public toolkit surface for:

- evidence and candidate schemas;
- provider bridge/candidate records;
- loaders for Reep exports;
- public-safe matching helpers;
- non-mutating recipe templates and fixtures.

Nutmeg can explain which surface to use and help wire it into the user's
project, but it should not define a separate evidence schema.

## Private Partner Material

The matching logic pack is partner-facing operating material. Reference it only
when the user says they have access or explicitly provides its contents.

Do not leak or invent private pack doctrine. If the user lacks access, answer
with the public surfaces:

- provider facts: `football-docs`;
- public matching code: `reep-scripts`;
- public IDs and bridges: Reep Register exports/API;
- process guidance: public Reep documentation and correction intake.

## Safe Defaults

- Prefer deterministic provider IDs and relationship evidence over fuzzy names.
- Treat relationship evidence as candidate narrowing, not proof by itself.
- Keep provider ontology separate from the user's target world model.
- Leave unresolved residue for review rather than forcing weak matches.
