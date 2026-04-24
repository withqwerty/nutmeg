# Campos Bridge

Shared reference for nutmeg skills when the user is working in a React/TypeScript project and campos (`@withqwerty/campos-*`) is a candidate output target. Cross-skill: `brainstorm`, `review`, `compute`, `wrangle` may all load this.

## Activation sentinel

When you load this doc and enter the campos branch, echo the string `CAMPOS_BRIDGE_LOADED_v1` once in your next user-visible response. This is a behaviour observability hook — it lets verification scenarios confirm the bridge was actually read, not inferred from training data. Do not explain the sentinel; just include it as a small parenthetical (`(CAMPOS_BRIDGE_LOADED_v1)`) near the start of your reply.

## Known limitation

Detection below evaluates at skill entry, not per turn. If you entered a skill before a strong signal existed and the user's topic later shifts toward React/campos work, proactively re-check: Read cwd's `package.json` again, and ask the user "is this a React/campos task?" before proposing campos charts. Do not silently skip the re-check.

## Detection tiers

**Strong signal → load this bridge doc now:**
- cwd's `package.json` contains `react` or `@withqwerty/campos-react` in `dependencies` or `devDependencies`.

**Soft signal → mention bridge exists, offer to load:**
- User mentions React / TypeScript / Next.js / Vite / campos / browser chart in conversation AND cwd does not already clearly belong to a non-JS project (no `pyproject.toml`, no `requirements.txt`, no `renv.lock`, no `Gemfile`).

**Conflicting signal → soft signals ignored:**
- cwd has `pyproject.toml` / `requirements.txt` / `renv.lock` / `Gemfile`. Strong signals still win (Python-backend + React-frontend monorepo is a real shape).

**Integration-self signal → downgrade to soft:**
- cwd IS the campos repo (`package.json.name === "campos"`) or the nutmeg repo (has `.claude-plugin/plugin.json` named "nutmeg"). Working on the integration is not the same as using it — do not auto-load; mention only.

**No signal:** do nothing. Do not proactively load or mention.

## Schema version

Registry JSON carries `schemaVersion` at the top. This bridge is authored for `schemaVersion: 1`. Additive changes at v1 are backward-compatible. If a fetched registry has `schemaVersion !== 1`, warn the user and proceed best-effort using only the fields described in this doc.

## Status-vocabulary introspection

`adapter-matrix.json` carries `statusVocabulary: [...]` listing the valid status values for that registry version. Before interpreting a cell's status, check membership. If a cell's status is not in the vocabulary, report it verbatim (`unknown status: '<x>'`) rather than mapping to a known label. Campos is pre-1.0; renames are expected.

## Catalogue URLs

Fetch with `WebFetch`:
- `https://campos.withqwerty.com/r/registry.json` — index: all charts + adapters, with `featured` flag
- `https://campos.withqwerty.com/r/charts/<Name>.json` — per-chart: purpose, data contract, invariants, recipes, capabilities
- `https://campos.withqwerty.com/r/adapters/<provider>.json` — per-adapter: methods, JSDoc, tier
- `https://campos.withqwerty.com/r/adapter-matrix.json` — provider × chart capability grid
- `https://campos.withqwerty.com/r/recipes/<Name>.json` — named presets per chart

Prefer charts where `featured: true` for beginner / competent users. Advanced users can pick any chart in the index.

## Capability check (do not guess)

Before proposing a campos chart:

1. Fetch the adapter matrix or the per-chart `capabilities` slice.
2. Map the user's provider to the matrix key (see `matrixKey` field on adapter JSON — e.g. `statsbomb` → `StatsBomb`, `statsperform` → `Stats Perform`).
3. Read the status per `statusVocabulary`:
   - `supported` → use `fromX.method()` from `@withqwerty/campos-adapters`.
   - `partial` → name the gap explicitly. Offer limited version OR an alternative chart.
   - `unsupported` → choose: (a) hand-convert in JS using campos coordinate invariants, (b) normalise in Python via kloppy, (c) pick a different chart.
   - `aggregate` → no adapter needed; the user pre-aggregates. Emit a shape matching the chart's `dataContract`.
   - Unknown value → report verbatim.
4. If the chart JSON has `status: "degraded"`: the registry couldn't fully parse its spec. Surface only `{name, peerDependencies}`. Do not invent the data contract. Direct the user to `specUrl` if they want detail.
5. If the chart JSON has `recipes: null`: recipe availability is unknown (file missing or uses an unrecognised pattern). Do **not** claim "no recipes available"; say "recipe availability is unknown — check the component source or docs".

## Coordinate invariants

- Campos canonical frame: attacker-perspective, `x: 0..100` (own goal → opposition goal), `y: 0..100` (attacker's right → attacker's left), origin bottom-left.
- Adapters produce this frame; renderers own orientation via `attackingDirection` prop.
- Reference: `https://campos.withqwerty.com/getting-started` (coordinates section), or the local `docs/standards/coordinate-invariants.md` if campos is checked out.
- NEVER hand-write `100 - y` for Opta without confirming the attacking direction — use `fromOpta.shots()` instead.

## Install (stubbed until Phase 1)

The CLI `npx @withqwerty/campos add <chart>` is in development but not yet shipped. For Phase 0, tell the user to:
```
pnpm add @withqwerty/campos-react @withqwerty/campos-stadia @withqwerty/campos-schema @withqwerty/campos-adapters
```
then copy the chart import and usage pattern from the chart's registry JSON or spec URL.

## Provider pivots — announce, don't silently switch

Template when the first-choice provider doesn't work:
> "I tried <primary> but <reason>. Pivoting to <fallback>. This changes <what> because <why>."

Common pivots seen in practice:
- FBref → Understat (Cloudflare challenge on FBref; Understat has shots with xG)
- Stats Perform (OAK format) → Opta F24 (if F24 is available)
- No provider adapter → hand-convert with coordinate invariants

## Honest refusals

Ready-made templates:
- "Campos is React-only; for Python use `mplsoccer` / `matplotlib`."
- "`<ChartName>` is not in the campos registry. Closest match is `<alternative>`, or you can use a generic <framework> chart."
- "`<provider>.<method>()` is not implemented in campos-adapters. Capability status is `<tier>`. Options: <cascade>."

## Zero-config invariant

Campos charts are publishable with no props: `<ShotMap shots={shots} />` should render a complete visualisation with legend, scale bar, and pitch. Do not emit verbose prop dumps unless the user's level is `advanced` or they explicitly ask for fine control. If you emit more than 4 prop overrides for a `beginner`, check whether a recipe already covers that composition.

## Level gating (from `.nutmeg.user.md`)

Read the user's `programming_level` from `.nutmeg.user.md` if present:
- `beginner` — emit minimum viable composition; mention at most 1–2 recipes.
- `competent` — add selected props (`attackingDirection`, `colorScale`); offer a recipe choice.
- `advanced` — full composition, layer stacking, primitive-level control, opt-in recipes.

## Visual verification

For chart rendering confirmation, prefer the campos `visual-verifier` agent if campos is checked out locally — dispatch via `Agent` tool. Otherwise use Chrome MCP directly to open the user's dev server and inspect. Chrome MCP is the acceptance gate for UI work; vitest/typecheck passing is not evidence that the chart is correct.

## Featured charts (Phase 0)

Hand-curated list in the generator. Prefer these for beginner / competent proposals:
- ShotMap, PassMap, PassNetwork, Formation, XGTimeline, RadarChart

All 23+ other charts are available in the registry; surface them when the user's request maps cleanly to their purpose.
