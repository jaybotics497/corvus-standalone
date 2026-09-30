#!/data/data/com.termux/files/usr/bin/bash
set -e
[ -n "$*" ] || { echo "USAGE: plan.sh OBJECTIVE"; exit 1; }

CONTEXT="$("$HOME/corvus-dev/repo-context.sh")"
PROMPT="$(cat "$HOME/corvus-dev/planner-prompt.txt")

$CONTEXT

DEVELOPMENT OBJECTIVE:
$*"

"$HOME/corvus/bin/infer" "$PROMPT"
