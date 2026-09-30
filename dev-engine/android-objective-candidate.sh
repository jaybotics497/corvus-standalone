#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

DEV="$HOME/corvus-dev"
MANAGER="$DEV/android-candidate-manager.sh"
GENERATOR="$DEV/generate-android-candidate.py"
STAGE="$DEV/staging/android/corvus"
OBJECTIVE="$*"

[ -n "$OBJECTIVE" ] || {
    echo "ANDROID OBJECTIVE: BLOCKED - objective required"
    exit 250
}

cleanup_failure() {
    rc=$?

    [ "$rc" -eq 0 ] && return

    trap - EXIT

    echo
    echo "ANDROID OBJECTIVE: FAILURE - resetting candidate state"

    "$MANAGER" reset >/dev/null 2>&1 || true

    exit "$rc"
}

trap cleanup_failure EXIT

echo "=== ANDROID OBJECTIVE CANDIDATE ==="
echo "OBJECTIVE: $OBJECTIVE"

echo
echo "=== RESET ==="
"$MANAGER" reset

echo
echo "=== CORVUS DEVELOPMENT ==="
"$GENERATOR" "$OBJECTIVE"

echo
echo "=== VERIFY VERSION ==="
grep -q 'android:versionName="0.6"' \
    "$STAGE/AndroidManifest.xml"

grep -q 'android:versionCode="16"' \
    "$STAGE/AndroidManifest.xml"

grep -q 'package="com.corvus.app"' \
    "$STAGE/AndroidManifest.xml"

echo "ANDROID VERSION CONTRACT: PASS"

echo
echo "=== TRUSTED BUILD / TEST ==="
"$MANAGER" test

echo
echo "=== FINGERPRINT ==="
"$MANAGER" fingerprint

echo
echo "=== VERIFY CANDIDATE ==="
"$MANAGER" verify

echo
echo "=== CORVUS REPORT ==="
cat "$DEV/changes/android-current-report.txt"

echo
echo "=== RESULT ==="
echo "ANDROID OBJECTIVE: CANDIDATE READY"
echo "STATUS: AWAITING HUMAN APPROVAL"
echo "LIVE 0.5: UNCHANGED"
