#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

DEV="$HOME/corvus-dev"
POINTER="$DEV/changes/current-report"
STATUS="${1:-}"

[ -n "$STATUS" ] || {
 echo "CURRENT REPORT: BLOCKED - status required"
 exit 1
}

[ -f "$POINTER" ] || {
 echo "CURRENT REPORT: BLOCKED - pointer missing"
 exit 2
}

REPORT="$(cat "$POINTER")"

[ -f "$REPORT" ] || {
 echo "CURRENT REPORT: BLOCKED - report missing"
 exit 3
}

"$DEV/update-report.py" "$REPORT" "$STATUS"
echo "CURRENT REPORT: $STATUS"
