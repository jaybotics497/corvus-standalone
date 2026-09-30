#!/data/data/com.termux/files/usr/bin/bash
set -e

JOB="$1"

[ -f "$JOB" ] || { echo "CANDIDATE TEST: job required"; exit 1; }

"$HOME/corvus-dev/dev-manager.py" "$JOB"
CHANGED="$(git -C "$HOME/corvus-dev/staging/corvus" status --porcelain)"
[ -n "$CHANGED" ] || { echo "CANDIDATE TEST: BLOCKED - no changes"; exit 10; }

"$HOME/corvus-dev/check-permissions.py" "$JOB"
"$HOME/corvus-dev/validate.sh"

TEST="$(sed -n 's/^TESTS_REQUIRED:[[:space:]]*//p' "$JOB" | head -n1)"

[ -n "$TEST" ] || {
 echo "CANDIDATE TEST: BLOCKED - trusted test missing"
 exit 124
}

"$HOME/corvus-dev/run-trusted-tests.sh" "$TEST"

echo "CANDIDATE TEST: PASS"
