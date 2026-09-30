#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

DEV="$HOME/corvus-dev"
OBJECTIVE="$*"
PLAN="$DEV/plans/current-plan.txt"
JOB=""

cleanup_failure() {
    rc=$?
    [ "$rc" -eq 0 ] && return

    trap - EXIT
    echo "OBJECTIVE CANDIDATE: CLEANUP"

    "$DEV/clear-active-state.sh" || true
    "$DEV/reset-staging.sh" || true

    if [ -n "$JOB" ] && [ -f "$JOB" ]; then
        "$DEV/set-job-status.py" "$JOB" retired || true
    fi

    exit "$rc"
}

trap cleanup_failure EXIT

[ -n "$OBJECTIVE" ] || {
    echo "OBJECTIVE CANDIDATE: BLOCKED - objective required"
    exit 160
}

"$DEV/make-plan.sh" "$OBJECTIVE"

OUTPUT="$("$DEV/plan-to-job.sh" "$OBJECTIVE")"
echo "$OUTPUT"

JOB="$(printf '%s\n' "$OUTPUT" | sed -n 's/^JOB FILE: //p' | tail -n1)"

[ -f "$JOB" ] || {
    echo "OBJECTIVE CANDIDATE: BLOCKED - job missing"
    exit 161
}

"$DEV/development-manager.sh" prepare "$JOB"
"$DEV/run-trusted-operation.sh" "$PLAN"
"$DEV/development-manager.sh" test "$JOB"
"$DEV/development-manager.sh" fingerprint
"$DEV/development-manager.sh" verify

echo "OBJECTIVE CANDIDATE: READY"
echo "JOB: $JOB"
echo "STATUS: awaiting approval"
