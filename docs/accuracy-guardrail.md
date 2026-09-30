# Accuracy Guardrail

**CRITICAL: Do not rely on training knowledge for provider-specific facts.**

Football data providers change their APIs, schemas, event types, qualifier IDs, coordinate systems, rate limits, and endpoints frequently. Your training data may be outdated.

**Always use `search_docs` for:**
- Qualifier IDs and type IDs (e.g., Opta qualifier 214, StatsBomb type 30)
- API endpoint URLs and request/response schemas
- Provider ID grains, identity surfaces, URL handles, and bridge quirks
- Field names, data types, and value ranges
- Coordinate system origins, ranges, and conversion formulas
- Rate limits, authentication methods, and access requirements
- Library method signatures, parameter names, and return types
- Package version-specific features or breaking changes

**Never:**
- Guess or recall an ID, endpoint, or field name from training data
- Assume a coordinate system or conversion formula without checking
- Cite a specific version number or release date from memory
- State a rate limit or pricing tier without verification

**When search_docs returns no results, or says a term is not indexed:**
- Tell the user the information is not in the docs index
- Suggest they check the provider's official documentation directly
- Do NOT fill the gap with training knowledge — say "I don't have this indexed"

**When search_docs marks results as partial:**
- A result marked `**Match:** partial` does not contain every term of the query
- If the reply says "No indexed doc mentions ..." for a term the question is about, that topic is not indexed
- Use a partial result only if it answers the question on its own terms; otherwise treat the topic as not indexed
- Older football-docs versions do not mark partial matches. Read each result's **Provider** line and content: if no result is from the provider or about the topic the user asked about, treat the topic as not indexed. Use `resolve_provider_id` to check whether a provider is covered at all.

**When the football-docs tools fail:**
- If a football-docs tool returns an error or does not load (for example a `better-sqlite3` or `NODE_MODULE_VERSION` error), tell the user that the docs server did not start and point them to the football-docs README for the fix.
- Do not answer provider-specific questions from training knowledge while the server is down. Say what you would have looked up.

**When you state a provider fact:**
- Say where it came from: the provider and doc title from the result's **Source** line (or its URL), for example "Opta qualifiers (football-docs)".
- If the fact came from the user's own files or a live API response, say that instead.

**When writing code that uses provider data:**
- Look up the exact field names and types via `search_docs` before writing access patterns
- Verify coordinate system before any spatial calculation
- Check the provider's event type IDs before filtering or mapping

**When handling entity resolution:**
- Use `entity-resolution-routing.md` (in this folder) to route the request.
- Use `football-docs` for provider facts and quirks.
- Use the Reep Register (`resolve_entity`, or the release DuckDB) for public ID lookup.
- Never state a provider ID from memory. An ID comes from the Reep Register, the user's data, or a provider response.
- "No match" in Reep is not evidence that the entity does not exist. Say it is unresolved; do not fill the gap from memory.
- Point reusable matching/candidate code to `reep-toolkit`.
- Do not duplicate private Reep doctrine or matching logic pack material inside
  Nutmeg.
