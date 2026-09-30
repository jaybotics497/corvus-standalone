#!/data/data/com.termux/files/usr/bin/bash
set -e

DEV="$HOME/corvus-dev"
PLAN="$DEV/plans/current-plan.txt"
OBJECTIVE="$*"

[ -n "$OBJECTIVE" ] || {
 echo "PLAN TO JOB: BLOCKED - objective required"
 exit 110
}

"$DEV/validate-plan.py" "$PLAN"

if "$DEV/validate-new-target.py" "$PLAN" >/dev/null 2>&1; then
    "$DEV/validate-new-target.py" "$PLAN"
else
    "$DEV/validate-target.py" "$PLAN"
fi
"$DEV/check-plan-objective.py" "$PLAN" "$OBJECTIVE"

TARGET="$(sed -n 's/^TARGET:[[:space:]]*//p' "$PLAN" | head -n1)"
FILES="$("$DEV/select-capability-files.py" "$PLAN")"
TEST="$("$DEV/select-trusted-test.py" "$PLAN")"

[ -n "$TARGET" ] || {
 echo "PLAN TO JOB: BLOCKED - target missing"
 exit 111
}

[ -n "$TEST" ] || {
 echo "PLAN TO JOB: BLOCKED - test missing"
 exit 112
}

[ -n "$FILES" ] || {
 echo "PLAN TO JOB: BLOCKED - capability files missing"
 exit 113
}

"$DEV/create-job.py" \
 "$OBJECTIVE" \
 "$FILES" \
 "$TEST"

echo "PLAN TO JOB: PASS"
