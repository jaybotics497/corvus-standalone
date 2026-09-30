#!/data/data/com.termux/files/usr/bin/bash
set -e

LIVE="$HOME/corvus"

if [ -n "$(git -C "$LIVE" status --porcelain)" ]; then
 echo "LIVE TREE: DIRTY"
 git -C "$LIVE" status --short
 exit 31
fi

COMMIT="$(git -C "$LIVE" rev-parse HEAD)"

echo "LIVE TREE: CLEAN"
echo "LIVE COMMIT: $COMMIT"
echo "LIVE COMMIT VERIFY: PASS"
