#!/data/data/com.termux/files/usr/bin/bash
set -e

JOB="$1"

[ -f "$JOB" ] || {
 echo "RUN JOB: valid job required"
 exit 1
}

echo "=== CORVUS DEVELOPMENT RUN ==="

"$HOME/corvus-dev/start-job.sh" "$JOB"
REPORT_OUTPUT="$("$HOME/corvus-dev/write-report.py" "$JOB")"
echo "$REPORT_OUTPUT"
REPORT="$(printf '%s\n' "$REPORT_OUTPUT" | sed -n 's/^REPORT FILE: //p')"
"$HOME/corvus-dev/update-report.py" "$REPORT" ready_for_candidate

TARGET="$("$HOME/corvus-dev/select-target.py" "$JOB" | sed -n 's/^TARGET: //p')"
[ -n "$TARGET" ] || { echo "RUN JOB: TARGET FAILED"; exit 12; }

echo "RUN JOB: TARGET $TARGET"

STAGED_TARGET="$HOME/corvus-dev/staging/corvus/$TARGET"

if [ -f "$STAGED_TARGET" ]; then
    OPERATION="$HOME/corvus-dev/changes/current-operation"
    rm -f "$OPERATION"

    "$HOME/corvus-dev/generate-operation.py" "$JOB" "$TARGET" "$OPERATION"

    echo "RUN JOB: PROPOSAL GENERATED"
    echo "RUN JOB: READY FOR VALIDATION"
else
    echo "RUN JOB: NEW TARGET ROUTE"
    "$HOME/corvus-dev/generate-new-candidate.py" "$JOB" "$TARGET"
fi
