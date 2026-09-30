#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

DEV="$HOME/corvus-dev"
LIVE="$DEV/android/corvus-0.5"
STAGE="$DEV/staging/android/corvus"

fail() {
    echo "ANDROID STAGING: BLOCKED - $1"
    exit "${2:-190}"
}

[ -d "$LIVE" ] || fail "live project missing" 190

FILES=(
    "AndroidManifest.xml"
    "assets/index.html"
    "assets/style.css"
    "res/values/strings.xml"
    "res/values/styles.xml"
    "src/com/corvus/app/CorvusBridge.java"
    "src/com/corvus/app/CorvusEngineService.java"
    "src/com/corvus/app/MainActivity.java"
)

for file in "${FILES[@]}"; do
    [ -f "$LIVE/$file" ] ||
        fail "required source missing: $file" 191
done

rm -rf "$STAGE"

for file in "${FILES[@]}"; do
    mkdir -p "$STAGE/$(dirname "$file")"
    cp "$LIVE/$file" "$STAGE/$file"
done

echo "ANDROID STAGING: PASS"
echo "LIVE: $LIVE"
echo "STAGE: $STAGE"
echo "FILES: ${#FILES[@]}"
