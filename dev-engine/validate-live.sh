#!/data/data/com.termux/files/usr/bin/bash
set -e

LIVE="$HOME/corvus"

find "$LIVE/bin" "$LIVE/api" -type f -name '*.py' -print0 |
 xargs -0 -n1 python -m py_compile

git -C "$LIVE" diff --check

"$LIVE/bin/corvus" version >/dev/null
"$LIVE/bin/corvus" dev-status >/dev/null

echo "LIVE VALIDATION: PASS"
