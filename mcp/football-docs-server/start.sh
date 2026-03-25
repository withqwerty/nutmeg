#!/bin/bash
# Bootstrap and start the football-docs MCP server.
# Handles npm install on first run and builds the docs index if needed.

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Install deps if needed
if [ ! -d "node_modules" ]; then
  npm install --no-audit --no-fund --loglevel=error >&2
fi

# Build docs index if needed
if [ ! -f "data/docs.db" ]; then
  npx tsx src/ingest.ts >&2
fi

# Start the server
exec npx tsx src/index.ts
