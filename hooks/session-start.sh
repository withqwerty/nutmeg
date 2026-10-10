#!/bin/sh
# Print the SessionStart context with the plugin path filled in.
#
# The research-project rules (session-start-research.txt, stored JSON-escaped) are added only when the project has a
# research/ folder, so sessions without research projects do not pay for them.
#
# Pure shell, no sed: the path is JSON-escaped (backslashes and quotes) and
# inserted literally, so characters such as & or | in it cannot corrupt the JSON.

root="${CLAUDE_PLUGIN_ROOT:-${0%/hooks/*}}"
file="$root/hooks/session-start.json"
fragment="$root/hooks/session-start-research.txt"
project="${CLAUDE_PROJECT_DIR:-$PWD}"

# JSON-escape the path, one character at a time.
newline='
'
tab=$(printf '\t')
cr=$(printf '\r')
escaped=""
rest="$root"
while [ -n "$rest" ]; do
  char="${rest%"${rest#?}"}"
  rest="${rest#?}"
  case "$char" in
    \\) escaped="$escaped\\\\" ;;
    \") escaped="$escaped\\\"" ;;
    "$newline") escaped="$escaped\\n" ;;
    "$tab") escaped="$escaped\\t" ;;
    "$cr") escaped="$escaped\\r" ;;
    *) escaped="$escaped$char" ;;
  esac
done
# Any other control character: leave the placeholder for a variable name rather than emit invalid JSON.
case "$escaped" in
  *[[:cntrl:]]*) escaped='$CLAUDE_PLUGIN_ROOT' ;;
esac

# replace MARKER VALUE: every MARKER in $text becomes VALUE (no pattern characters are interpreted).
replace() {
  out=""
  while :; do
    case "$text" in
      *"$1"*)
        out="$out${text%%"$1"*}$2"
        text="${text#*"$1"}"
        ;;
      *)
        break
        ;;
    esac
  done
  text="$out$text"
}

research=""
if [ -d "$project/research" ] && [ -f "$fragment" ]; then
  research=$(cat "$fragment") || research=""
fi
text=$(cat "$file") || exit 0
replace "@RESEARCH@" "$research"
replace "@PLUGIN_ROOT@" "$escaped"
printf '%s\n' "$text"
