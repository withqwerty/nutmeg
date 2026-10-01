#!/bin/sh
# Print the SessionStart context with the plugin path filled in.
#
# Pure shell, no sed: the path is JSON-escaped (backslashes and quotes) and
# inserted literally, so characters such as & or | in it cannot corrupt the JSON.

root="${CLAUDE_PLUGIN_ROOT:-${0%/hooks/*}}"
file="$root/hooks/session-start.json"

# JSON-escape the path, one character at a time.
escaped=""
rest="$root"
while [ -n "$rest" ]; do
  char="${rest%"${rest#?}"}"
  rest="${rest#?}"
  case "$char" in
    \\) escaped="$escaped\\\\" ;;
    \") escaped="$escaped\\\"" ;;
    *) escaped="$escaped$char" ;;
  esac
done

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
