#!/data/data/com.termux/files/usr/bin/bash
set -e

DEV="$HOME/corvus-dev"
HASHFILE="$DEV/changes/current-candidate.sha256"

[ -f "$HASHFILE" ] || {
 echo "CANDIDATE HASH: BLOCKED - fingerprint missing"
 exit 13
}

EXPECTED="$(cat "$HASHFILE")"
CURRENT="$("$DEV/candidate-hash.py")"

[ "$EXPECTED" = "$CURRENT" ] || {
 echo "CANDIDATE HASH: BLOCKED - candidate changed"
 exit 14
}

echo "CANDIDATE HASH: PASS"
