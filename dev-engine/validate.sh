#!/data/data/com.termux/files/usr/bin/bash
set -e
ROOT="$HOME/corvus-dev/staging/corvus"
find "$ROOT/bin" "$ROOT/api" -type f -name '*.py' -print0 | xargs -0 -n1 python -m py_compile
git -C "$ROOT" diff --check
echo "VALIDATION: PASS"
