# nutmeg

A Claude Code plugin for football data analytics. 10 skills (2 entry points + 8 sub-skills), 3 agents, powered by the football-docs MCP server.

## Architecture: progressive disclosure

Users interact through **two entry points**. Sub-skills are dispatched automatically or invoked directly by power users.

| Layer | Skills | How invoked |
|-------|--------|-------------|
| **Entry** | `/nutmeg` (router) | User describes any football analytics task — routes automatically |
| **Teaching** | `/nutmeg-learn` | Concepts, resources, provider docs, learning paths |
| **Sub-skills** | `acquire`, `wrangle`, `compute`, `analyse`, `brainstorm`, `store`, `review`, `heal` | Auto-dispatched by router, or directly by power users |

## Structure

```
skills/
  nutmeg/          # Router — single entry point, handles init + dispatch
  learn/           # Teaching + provider documentation (merged from old providers/)
  acquire/         # Fetch data + credential management (merged from old credentials/)
  analyse/         # Explore and interpret data
  brainstorm/      # Visualisation ideation with research + style options
    references/    # chart-canon.md (conventions), viz-styles.md (4 aesthetic styles)
  compute/         # Derived metrics (xG, PPDA, xT, etc.)
  heal/            # Fix broken scrapers
  review/          # Dispatch data-reviewer + chart-reviewer agents
  store/           # Storage format and publishing
  wrangle/         # Transform, filter, reshape data

agents/            # Specialised sub-agents
  data-reviewer.md       # Reviews data code (coordinates, xG, filtering, sample sizes)
  chart-reviewer.md      # Reviews chart code (3 modes: code, visual, interactive)
  pipeline-builder.md    # Designs end-to-end data pipelines

docs/
  accuracy-guardrail.md  # Shared guardrail: always use search_docs, never guess from training

.mcp.json          # Declares football-docs MCP server dependency
```

## Key conventions

- Every provider-touching skill includes the accuracy guardrail section
- Skills use `search_docs` from the football-docs MCP server for all provider-specific facts
- User profile lives at `.nutmeg.user.md` (created by `/nutmeg` on first run)
- Skills adapt to user's language (Python/R/JS), experience level, and available data sources
- Reference docs in skills/brainstorm/references/ are loaded on-demand, not all upfront
- The router mentions sub-skill names during dispatch so users learn the vocabulary naturally

## Related projects

**football-docs** (npm: `football-docs`, repo: `withqwerty/football-docs`)
- MCP server providing searchable documentation for 16 football data providers
- Connected via `.mcp.json` — starts automatically when the plugin loads
- Skills query it via `mcp__football-docs__search_docs`, `list_providers`, `compare_providers`

**nutmeg-site** (local: `../nutmeg-site`)
- Marketing/landing page for the plugin, built with Astro 6 (static output)
- Components: Hero, SkillsGrid, ProvidersGrid, ExampleQueries, InstallRow, etc.

**plugins** (repo: `withqwerty/plugins`, local: `../plugins`)
- Plugin marketplace listing — nutmeg is registered here for discovery via `/plugin marketplace`
