#!/data/data/com.termux/files/usr/bin/bash
set -e

JOB="$1"

[ -f "$JOB" ] || {
 echo "FINALIZE: BLOCKED - job missing"
 exit 1
}

"$HOME/corvus-dev/check-promotion.py" "$JOB"
"$HOME/corvus-dev/verify-live-commit.sh"
"$HOME/corvus-dev/set-job-status.py" "$JOB" completed
"$HOME/corvus-dev/record-completion.py" "$JOB"
"$HOME/corvus-dev/update-current-report.sh" completed
"$HOME/corvus-dev/clear-active-state.sh"

echo "FINALIZE JOB: PASS"
