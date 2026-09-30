#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

DEV="$HOME/corvus-dev"

[ "$#" -eq 1 ] || {
    echo "USAGE: run-trusted-operation.sh PLAN"
    exit 150
}

PLAN="$1"
OPERATION="$("$DEV/select-trusted-operation.py" "$PLAN")"

[[ "$OPERATION" != */* ]] || {
    echo "OPERATION RUN: BLOCKED - invalid operation path"
    exit 151
}

[ -x "$DEV/$OPERATION" ] || {
    echo "OPERATION RUN: BLOCKED - operation not executable"
    exit 152
}

exec "$DEV/$OPERATION"
