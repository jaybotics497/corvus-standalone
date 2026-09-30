#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

APP="$HOME/corvus-dev/staging/android/corvus"
MANIFEST="$APP/AndroidManifest.xml"

[ -f "$MANIFEST" ] || {
    echo "0.6 PREP: BLOCKED - manifest missing"
    exit 70
}

grep -q 'android:versionCode="15"' "$MANIFEST" || {
    echo "0.6 PREP: BLOCKED - expected versionCode 15"
    exit 71
}

grep -q 'android:versionName="0.5"' "$MANIFEST" || {
    echo "0.6 PREP: BLOCKED - expected versionName 0.5"
    exit 72
}

sed -i \
    -e 's/android:versionCode="15"/android:versionCode="16"/' \
    -e 's/android:versionName="0.5"/android:versionName="0.6"/' \
    "$MANIFEST"

echo "ANDROID 0.6 PREP: PASS"
grep -E 'versionCode|versionName' "$MANIFEST"
