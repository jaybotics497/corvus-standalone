#!/data/data/com.termux/files/usr/bin/bash
set -e

DEV="$HOME/corvus-dev"
OBJECTIVE="$*"
RAW="$DEV/tmp/current-plan.raw"
PLAN="$DEV/plans/current-plan.txt"
CANDIDATE="$DEV/tmp/current-plan.candidate"

[ -n "$OBJECTIVE" ] || {
 echo "MAKE PLAN: BLOCKED - objective required"
 exit 96
}

"$DEV/objective-plan.sh" "$OBJECTIVE" > "$RAW"

cp "$DEV/last-plan.txt" "$CANDIDATE"
"$DEV/validate-plan.py" "$CANDIDATE" "$OBJECTIVE"
"$DEV/route-objective-capability.py" "$CANDIDATE" "$OBJECTIVE"

if "$DEV/validate-new-target.py" "$CANDIDATE" >/dev/null 2>&1; then
    "$DEV/validate-new-target.py" "$CANDIDATE"
else
    "$DEV/validate-target.py" "$CANDIDATE"
fi

"$DEV/validate-capability-target.py" "$CANDIDATE"
"$DEV/check-plan-objective.py" "$CANDIDATE" "$OBJECTIVE"

mv "$CANDIDATE" "$PLAN"

echo "=== VALIDATED PLAN ==="
cat "$PLAN"
echo "MAKE PLAN: PASS"
