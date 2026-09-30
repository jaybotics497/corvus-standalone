#!/data/data/com.termux/files/usr/bin/bash
set -e

PROMPT="$*"

if [ -z "$PROMPT" ]; then
    echo "CORVUS PLANNER: prompt required" >&2
    exit 1
fi

INFER="$HOME/corvus/bin/infer"

if [ ! -x "$INFER" ]; then
    echo "CORVUS PLANNER: local inference unavailable" >&2
    exit 2
fi

exec "$INFER" "$PROMPT"
