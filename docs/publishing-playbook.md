# Publishing Playbook

Reference for creating, documenting, distributing, and maintaining plugins, skills, and MCP servers across the AI coding tool ecosystem. Based on 2025-2026 best practices from Anthropic docs, the MCP spec, the Agent Skills standard, and community patterns.

Last updated: 2026-03-27

---

## Distribution channels (where to publish what)

| Channel | What it's for | How to publish |
|---|---|---|
| **Claude Code plugin marketplace** | Full plugin (skills + agents + MCP + hooks) | Submit at `claude.ai/settings/plugins/submit` or host your own marketplace repo |
| **Agent Skills (`npx skills add`)** | Portable skills (work in 33+ agents) | Public GitHub repo with `skills/*/SKILL.md` files |
| **npm** | MCP servers, CLI tools | `npm publish` with `bin` field for `npx` execution |
| **GitHub MCP Registry** | Official MCP server listing | `mcp-publisher publish` with `server.json` |
| **Third-party registries** | Broader discovery | Smithery.ai, Glama.ai, mcp.run — auto-scraped or manual submission |
| **skills.sh** | Agent Skills directory | Auto-discovered from `npx skills add` install telemetry |
| **SkillsMP** | Skills marketplace | Auto-discovered from public GitHub repos with 2+ stars |

### For nutmeg specifically

1. Plugin install (Claude Code): `/plugin marketplace add withqwerty/plugins` then `/plugin install nutmeg@withqwerty`
2. Skills only (33+ agents): `npx skills add withqwerty/nutmeg`
3. MCP only (any MCP client): `npx -y football-docs`

---

## Plugin structure

```
my-plugin/
  .claude-plugin/
    plugin.json           # ONLY this file here (+ marketplace.json if this IS the marketplace)
  skills/
    skill-name/
      SKILL.md            # Required. Keep under 500 lines.
      references/         # Loaded on demand, not upfront
      scripts/            # Executable helpers (deterministic tasks)
  agents/
    agent-name.md
  .mcp.json               # MCP server declarations
  CLAUDE.md               # Internal docs for Claude
  README.md               # External docs for humans
  CHANGELOG.md            # Version history
```

**Rules:**
- Never put skills/, agents/, or hooks/ inside `.claude-plugin/`
- All paths must be relative (plugins are copied to cache)
- No references to files outside the plugin directory

### plugin.json

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Brief description",
  "author": { "name": "Name", "url": "https://github.com/..." },
  "repository": "https://github.com/...",
  "homepage": "https://...",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"]
}
```

### Versioning

- Follow semver: MAJOR (breaking), MINOR (new features), PATCH (fixes)
- **Always bump version when you change code** — Claude Code caches by version; no bump = no update
- Set version in ONE place: `plugin.json` for GitHub-sourced plugins, `marketplace.json` for relative-path plugins. Never both — `plugin.json` wins silently.

---

## Skills (SKILL.md)

### Frontmatter

```yaml
---
name: my-skill                       # Lowercase, hyphens, max 64 chars
description: "What it does and WHEN to use it. Third person. Max 1024 chars."
argument-hint: "[what to provide]"   # Shown during autocomplete
allowed-tools: ["Read", "Write"]     # Pre-approved tools (reduces permission prompts)
disable-model-invocation: true       # Only user can invoke (for dangerous operations)
user-invocable: false                # Only agent can invoke (background knowledge)
model: sonnet                        # Model override
---
```

### Description writing (most important field)

The description determines whether the agent activates the skill. Current failure mode: agents **under-trigger** skills.

**Do:**
- Write in third person: "This skill should be used when..."
- Include specific trigger phrases users would say
- Be generous about when to activate — slightly pushy is better than missed triggers
- Include both "what" and "when"

**Don't:**
- Be vague: "Provides data guidance"
- Use first/second person
- Omit trigger phrases

### Progressive disclosure (core architecture principle)

| Level | When loaded | Size target |
|---|---|---|
| Frontmatter (name + description) | Always in context | ~100 words |
| SKILL.md body | When skill triggers | 1,500-2,000 words (max 500 lines) |
| references/*.md | On demand from SKILL.md | 2,000-5,000+ words each |
| scripts/*.sh | Executed, not read into context | Any size |

**If your SKILL.md exceeds 500 lines, split into reference files.**

### Writing style

- Imperative form: "Parse the file. Validate the output." Not "You should parse the file."
- Explain the why: "Cache API responses because FBref rate-limits to 10 req/min" not "ALWAYS cache"
- Include gotchas: domain-specific facts that defy assumptions are the highest-value content

### Cross-agent compatibility

- Avoid agent-specific tool names: write "Read the file" not "Use the Read tool"
- Use relative paths for bundled resources
- Test on at least Claude Code + one other agent

---

## Agents (agent.md)

### Frontmatter

```yaml
---
name: agent-name
description: "When to delegate to this agent"
model: sonnet                        # sonnet (default), opus, haiku, inherit
maxTurns: 20                         # Prevent runaway agents
tools:
  - Read
  - Grep
  - Glob
  - mcp__server__tool
---
```

### Model selection

| Model | Use for | Cost |
|---|---|---|
| haiku | Fast read-only tasks, code search, simple reviews | Lowest |
| sonnet | Balanced analysis, review, most agent work | Medium |
| opus | Complex reasoning, architecture, multi-step tasks | Highest |

### Security restrictions (plugin agents)

`hooks`, `mcpServers`, and `permissionMode` are **silently ignored** in plugin-shipped agents. Users must copy to `.claude/agents/` to use these.

---

## MCP servers

### Architecture

- Keep tool count small (2-6 tools). Each tool consumes context.
- Follow the **discovery + retrieval** pattern: one tool to find resources, one to fetch content
- Return semantic names, not UUIDs
- Use `isError: true` for user-facing errors with actionable messages
- Never `console.log()` in stdio servers — use `console.error()` for debug

### npm package structure

```json
{
  "name": "my-mcp-server",
  "bin": { "my-mcp-server": "./bin/serve.js" },
  "type": "module",
  "engines": { "node": ">=20" },
  "files": ["dist/", "bin/", "data/"],
  "keywords": ["mcp", "mcp-server", "your-domain"],
  "scripts": {
    "prepublishOnly": "npm run build"
  }
}
```

### Tool descriptions

- Start with a verb: "Search...", "List...", "Compare..."
- Include 2-3 concrete examples in parameter `.describe()`
- Specify what gets returned
- Mention filters and defaults
- Cross-reference other tools: "Use list_providers first to see what's available"

### Tool annotations (MCP spec 2025-03-26)

```typescript
annotations: {
  readOnlyHint: true,      // No side effects
  destructiveHint: false,   // Non-destructive
  openWorldHint: false,     // Closed domain
}
```

### Client config differences

| Client | Config key | Format |
|---|---|---|
| Claude Desktop / Cursor | `mcpServers` | Object |
| VS Code | `servers` | Object |
| Windsurf | `mcpServers` | Object |
| Zed | `context_servers` | Object (nested `command.path`) |
| Continue | `mcpServers` | **Array** (not object) |
| Claude Code | N/A | `claude mcp add <name>` CLI |

### Testing

Three levels:
1. **Unit tests** for business logic (vitest)
2. **In-memory transport tests** using MCP SDK's `InMemoryTransport`
3. **Smoke test** for the compiled binary (send JSON-RPC initialize)

---

## Documentation standards

### README structure

```markdown
# Name

One-sentence description.

**Who it's for:** Target audience.
**What it does:** Core value proposition.
**Why not just ask the AI directly?** What makes this better than raw LLM knowledge.

## Install

[Per-tool config blocks for Claude Code, Cursor, VS Code, Windsurf, Claude Desktop]

## Skills / Tools

[Table with name + description]

## License
```

### CLAUDE.md (internal, for the agent)

- Plugin structure (directory map)
- Key conventions
- Cross-cutting concerns
- Related projects

### CHANGELOG.md

Follow Keep a Changelog format. Maintain for every version bump.

---

## Publishing checklist

### Before first publish

- [ ] `plugin.json` has name, version, description, author, repository, license
- [ ] Every SKILL.md has name + description in frontmatter
- [ ] Every agent .md has name + description in frontmatter
- [ ] README has install instructions for multiple tools
- [ ] CLAUDE.md exists with structure overview
- [ ] CHANGELOG.md started
- [ ] `.mcp.json` tested (MCP server starts and responds)
- [ ] GitHub topics added (claude-code, agent-skills, mcp, domain tags)

### Before each version bump

- [ ] Version bumped in the correct file (plugin.json OR marketplace.json, not both)
- [ ] CHANGELOG.md updated
- [ ] All skills trigger correctly (test 5-10 prompts)
- [ ] MCP server builds and passes tests
- [ ] `npm publish` (for MCP server)
- [ ] Push to GitHub (for plugin)

### Distribution targets

- [ ] Claude Code plugin marketplace (submit or self-host)
- [ ] npm (MCP server)
- [ ] GitHub MCP Registry (`mcp-publisher publish`)
- [ ] GitHub repo with topics for auto-discovery
- [ ] `npx skills add` path tested

---

## Common mistakes

| Mistake | Fix |
|---|---|
| Not bumping version | Users never see updates due to caching |
| Version in both plugin.json and marketplace.json | Set in one place only |
| SKILL.md over 500 lines | Split to references/ |
| Vague skill description | Include specific trigger phrases, be slightly pushy |
| Writing descriptions in first person | Use third person |
| Missing `allowed-tools` | Causes permission prompt spam |
| `console.log()` in MCP server | Corrupts stdio. Use `console.error()` |
| Skills inside `.claude-plugin/` | Must be at plugin root |
| Absolute paths in plugin | Breaks after cache copy |
| Using skills when you need MCP | Skills can't make API calls; MCP can |
| Using MCP when you need skills | MCP is overkill for teaching procedures |
| Not testing trigger behavior | Test 5-10 prompts per skill |
| Publishing to only one channel | Miss 33+ agents if plugin-only |
