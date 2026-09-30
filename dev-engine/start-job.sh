#!/data/data/com.termux/files/usr/bin/bash
set -e

JOB="$1"

[ -f "$JOB" ] || {
 echo "START JOB: valid job required"
 exit 1
}

STATUS="$(sed -n 's/^STATUS: //p' "$JOB")"
[ "$STATUS" = "pending" ] || {
 echo "START JOB: BLOCKED - job is not pending"
 exit 19
}

"$HOME/corvus-dev/clear-active-state.sh"
"$HOME/corvus-dev/reset-staging.sh"
"$HOME/corvus-dev/validate.sh"
"$HOME/corvus-dev/snapshot.sh"
"$HOME/corvus-dev/dev-manager.py" "$JOB"
"$HOME/corvus-dev/write-report.py" "$JOB"
"$HOME/corvus-dev/update-current-report.sh" prepared

echo "START JOB: PASS"
