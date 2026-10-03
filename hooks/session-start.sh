#!/bin/sh
# Print the SessionStart context with the plugin path filled in.
#
# Pure shell, no sed: the path is JSON-escaped (backslashes and quotes) and
# inserted literally, so characters such as & or | in it cannot corrupt the JSON.

root="${CLAUDE_PLUGIN_ROOT:-${0%/hooks/*}}"
file="$root/hooks/session-start.json"

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

text=$(cat "$file") || exit 0
out=""
while :; do
  case "$text" in
    *@PLUGIN_ROOT@*)
      out="$out${text%%@PLUGIN_ROOT@*}$escaped"
      text="${text#*@PLUGIN_ROOT@}"
      ;;
    *)
      break
      ;;
  esac
done
printf '%s\n' "$out$text"
