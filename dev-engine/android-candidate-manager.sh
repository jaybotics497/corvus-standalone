#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

DEV="$HOME/corvus-dev"
LIVE="$DEV/android/corvus-0.5"
STAGE="$DEV/staging/android/corvus"
STATE="$DEV/changes/android"
BUILD="$DEV/tmp/android-trusted-candidate"

mkdir -p "$STATE"

allowed_files=(
    "AndroidManifest.xml"
    "assets/index.html"
    "assets/style.css"
    "res/values/strings.xml"
    "res/values/styles.xml"
    "src/com/corvus/app/CorvusBridge.java"
    "src/com/corvus/app/CorvusEngineService.java"
    "src/com/corvus/app/MainActivity.java"
)

fail() {
    echo "ANDROID MANAGER: BLOCKED - $1"
    exit "${2:-200}"
}

candidate_hash() {
    (
        cd "$STAGE"

        for file in "${allowed_files[@]}"; do
            [ -f "$file" ] ||
                fail "candidate file missing: $file" 201

            sha256sum "$file"
        done
    ) | sha256sum | cut -d' ' -f1
}

case "${1:-}" in

    reset)
        "$DEV/reset-android-staging.sh"
        rm -rf "$BUILD"
        rm -f \
            "$STATE/current-candidate.sha256" \
            "$STATE/current-apk.sha256"
        echo "ANDROID MANAGER: RESET PASS"
        ;;

    test)
        [ -d "$STAGE" ] ||
            fail "staging missing" 202

        "$DEV/build-android-apk.sh" \
            "$STAGE" \
            "$BUILD"

        APK="$(
            find "$BUILD" \
                -maxdepth 1 \
                -type f \
                -name 'CORVUS-*.apk' \
                | head -n1
        )"

        [ -n "$APK" ] ||
            fail "candidate APK missing" 203

        apksigner verify "$APK" ||
            fail "signature verification failed" 204

        unzip -t "$APK" >/dev/null ||
            fail "APK archive verification failed" 205

        echo "ANDROID MANAGER: TEST PASS"
        echo "APK: $APK"
        ;;

    fingerprint)
        [ -d "$STAGE" ] ||
            fail "staging missing" 206

        HASH="$(candidate_hash)"
        printf '%s\n' "$HASH" \
            > "$STATE/current-candidate.sha256"

        APK="$(
            find "$BUILD" \
                -maxdepth 1 \
                -type f \
                -name 'CORVUS-*.apk' \
                | head -n1
        )"

        [ -n "$APK" ] ||
            fail "tested APK missing" 207

        APK_HASH="$(sha256sum "$APK" | cut -d' ' -f1)"
        printf '%s\n' "$APK_HASH" \
            > "$STATE/current-apk.sha256"

        echo "ANDROID CANDIDATE SHA256: $HASH"
        echo "ANDROID APK SHA256: $APK_HASH"
        echo "ANDROID MANAGER: FINGERPRINT PASS"
        ;;

    verify)
        [ -s "$STATE/current-candidate.sha256" ] ||
            fail "candidate fingerprint missing" 208

        [ -s "$STATE/current-apk.sha256" ] ||
            fail "APK fingerprint missing" 209

        EXPECTED="$(
            cat "$STATE/current-candidate.sha256"
        )"

        CURRENT="$(candidate_hash)"

        [ "$EXPECTED" = "$CURRENT" ] ||
            fail "candidate changed after fingerprint" 210

        APK="$(
            find "$BUILD" \
                -maxdepth 1 \
                -type f \
                -name 'CORVUS-*.apk' \
                | head -n1
        )"

        [ -n "$APK" ] ||
            fail "candidate APK missing" 211

        EXPECTED_APK="$(
            cat "$STATE/current-apk.sha256"
        )"

        CURRENT_APK="$(
            sha256sum "$APK" | cut -d' ' -f1
        )"

        [ "$EXPECTED_APK" = "$CURRENT_APK" ] ||
            fail "APK changed after fingerprint" 212

        apksigner verify "$APK" ||
            fail "APK signature invalid" 213

        echo "ANDROID MANAGER: VERIFY PASS"
        echo "CANDIDATE SHA256: $CURRENT"
        echo "APK SHA256: $CURRENT_APK"
        ;;

    status)
        echo "=== CORVUS ANDROID CANDIDATE ==="
        echo "LIVE: $LIVE"
        echo "STAGE: $STAGE"

        if [ -s "$STATE/current-candidate.sha256" ]; then
            echo "Fingerprint: PRESENT"
        else
            echo "Fingerprint: NONE"
        fi

        if [ -s "$STATE/current-apk.sha256" ]; then
            echo "APK fingerprint: PRESENT"
        else
            echo "APK fingerprint: NONE"
        fi
        ;;

    *)
        echo "Usage: android-candidate-manager.sh reset|test|fingerprint|verify|status"
        exit 1
        ;;
esac
