#!/data/data/com.termux/files/usr/bin/bash
set -e

DEV="$HOME/corvus-dev"
JOB="$1"

[ -f "$JOB" ] || {
 echo "AUTO FINISH: BLOCKED - valid job required"
 exit 60
}

"$DEV/check-approval.py" "$JOB"
"$DEV/check-candidate-hash.sh"
"$DEV/check-candidate-approval.py" "$JOB"
"$DEV/development-manager.sh" promote "$JOB"

if ! "$DEV/development-manager.sh" live-test "$JOB"; then
 echo "AUTO FINISH: live test failed - rolling back"
 "$DEV/rollback-promotion.py"
 "$DEV/update-current-report.sh" rolled_back
 exit 61
fi

if ! "$DEV/commit-promotion.py" "$JOB"; then
 echo "AUTO FINISH: commit failed - rolling back"
 "$DEV/rollback-promotion.py"
 "$DEV/update-current-report.sh" rolled_back
 exit 62
fi
if ! "$DEV/verify-live-commit.sh"; then
 echo "AUTO FINISH: live commit verification failed - restoring baseline"
 "$DEV/rollback-live-commit.py"
 "$DEV/update-current-report.sh" rolled_back
 exit 63
fi

if ! "$DEV/finalize-job.sh" "$JOB"; then
 echo "AUTO FINISH: finalization failed - restoring baseline"
 "$DEV/rollback-live-commit.py"
 "$DEV/update-current-report.sh" rolled_back
 exit 64
fi

rm -rf "$DEV/tmp/promotion-backup"
"$DEV/reset-staging.sh"

echo
echo "=== CORVUS AUTO DEVELOPMENT COMPLETE ==="
"$DEV/development-manager.sh" status
echo "JOB: $JOB"
echo "AUTO FINISH: PASS"
