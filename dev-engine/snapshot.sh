#!/data/data/com.termux/files/usr/bin/bash
set -e

STAGE="$HOME/corvus-dev/staging/corvus"
OUT="$HOME/corvus-dev/snapshots/current-baseline.txt"

git -C "$STAGE" rev-parse HEAD > "$OUT"

[ -z "$(git -C "$STAGE" status --porcelain)" ] || {
 echo "SNAPSHOT: BLOCKED - staging not clean"
 exit 11
}

echo "SNAPSHOT: PASS"
echo "BASELINE: $(cat "$OUT")"
