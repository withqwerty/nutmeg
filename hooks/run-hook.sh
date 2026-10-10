#!/bin/sh
# Run a nutmeg research hook only when a research project is active.
#
#   sh run-hook.sh <hook script in this folder>   (hook JSON on stdin)
#
# With no active project this exits at once, before Python starts, so
# ordinary nutmeg use and Claude Code's normal permission flow are unchanged.
# Without python3 >= 3.10 it warns once per repository and exits 0.
# It uses only shell built-ins until it knows a project is active.

script="$1"
here="${0%/*}"

# Find research/.active from the project folder up to the repository root.
# Stop at the filesystem root, a drive root (C:) or after 64 steps.
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
steps=0
while :; do
  if [ -f "$dir/research/.active" ]; then
    break
  fi
  if [ -e "$dir/.git" ]; then
    exit 0
  fi
  parent="${dir%/*}"
  if [ "$parent" = "$dir" ]; then
    parent="${dir%\\*}"
  fi
  steps=$((steps + 1))
  if [ -z "$parent" ] || [ "$parent" = "$dir" ] || [ "$steps" -gt 64 ]; then
    exit 0
  fi
  dir="$parent"
done

if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
  marker="$dir/research/.python-warned"
  if [ ! -f "$marker" ]; then
    : > "$marker" 2>/dev/null
    printf '%s\n' '{"systemMessage": "nutmeg: a research project is active, but python3 3.10 or newer was not found, so the run gate and checks are off. Install Python 3.10+ to turn them on."}'
  fi
  exit 0
fi

NUTMEG_REPO_ROOT="$dir" exec python3 "$here/$script"
