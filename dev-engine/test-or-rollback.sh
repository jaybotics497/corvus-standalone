#!/data/data/com.termux/files/usr/bin/bash

JOB="$1"

 "$HOME/corvus-dev/test-candidate.sh" "$JOB"
CODE=$?

if [ "$CODE" -eq 0 ]; then
 echo "DEVELOPMENT TEST: PASS"
 exit 0
fi
echo "DEVELOPMENT TEST: FAILED"
"$HOME/corvus-dev/reset-staging.sh"
"$HOME/corvus-dev/validate.sh"
echo "ROLLBACK: PASS"
exit "$CODE"
