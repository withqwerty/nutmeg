# Accuracy Guardrail

**CRITICAL: Do not rely on training knowledge for provider-specific facts.**

Football data providers change their APIs, schemas, event types, qualifier IDs, coordinate systems, rate limits, and endpoints frequently. Your training data may be outdated.

**Always use `search_docs` for:**
- Qualifier IDs and type IDs (e.g., Opta qualifier 76, StatsBomb type 30)
- API endpoint URLs and request/response schemas
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

**When search_docs returns no results:**
- Tell the user the information is not in the docs index
- Suggest they check the provider's official documentation directly
- Do NOT fill the gap with training knowledge — say "I don't have this indexed"

**When writing code that uses provider data:**
- Look up the exact field names and types via `search_docs` before writing access patterns
- Verify coordinate system before any spatial calculation
- Check the provider's event type IDs before filtering or mapping
