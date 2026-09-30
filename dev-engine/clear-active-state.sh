#!/data/data/com.termux/files/usr/bin/bash
set -e

BASE="$HOME/corvus-dev/changes"

rm -f \
 "$BASE/current-operation" \
 "$BASE/current-candidate.sha256" \
 "$BASE/current-approval" \
 "$BASE/current-promotion" \
 "$BASE/current-report" \
 "$BASE/last-raw-output.txt"

echo "ACTIVE STATE: CLEARED"
