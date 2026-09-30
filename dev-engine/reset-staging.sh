#!/data/data/com.termux/files/usr/bin/bash
set -e
STAGE="$HOME/corvus-dev/staging/corvus"
rm -rf "$STAGE"
git clone -q "$HOME/corvus" "$STAGE"
echo "STAGING RESET: PASS"
