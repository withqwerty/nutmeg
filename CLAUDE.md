# nutmeg

A Claude Code plugin for football data analytics. 12 skills, 3 agents, powered by the football-docs MCP server.

## Structure

```
skills/           # Slash commands (/nutmeg-*)
  acquire/        # Fetch data from providers
  analyse/        # Explore and interpret data
  brainstorm/     # Visualisation ideation with research + style options
    references/   # chart-canon.md (conventions), viz-styles.md (4 aesthetic styles)
  compute/        # Derived metrics (xG, PPDA, xT, etc.)
  credentials/    # API key management
  heal/           # Fix broken scrapers
  init/           # User profile setup
  learn/          # Concepts, papers, courses
  providers/      # Search provider documentation
  review/         # Dispatch data-reviewer + chart-reviewer agents
  store/          # Storage format and publishing
  wrangle/        # Transform, filter, reshape data

agents/           # Specialised sub-agents
  data-reviewer.md      # Reviews data code (coordinates, xG, filtering, sample sizes)
  chart-reviewer.md     # Reviews chart code (3 modes: code, visual, interactive)
  pipeline-builder.md   # Designs end-to-end data pipelines

docs/
  accuracy-guardrail.md # Shared guardrail: always use search_docs, never guess from training

.mcp.json         # Declares football-docs MCP server dependency
```

## Key conventions

- Every provider-touching skill includes the accuracy guardrail section
- Skills use `search_docs` from the football-docs MCP server for all provider-specific facts
- User profile lives at `.nutmeg.user.md` (created by /nutmeg-init)
- Skills adapt to user's language (Python/R/JS), experience level, and available data sources
- Reference docs in skills/brainstorm/references/ are loaded on-demand, not all upfront

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
