#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$HOME/corvus-dev/staging/corvus"

echo "=== API ARCHITECTURE ==="
grep -nE \
'HOST =|PORT =|MAX_PROMPT_LENGTH|ASK_TIMEOUT|def do_GET|def do_POST|"/health"|"/ask", "/develop"|command = "develop"|COMMANDS = ' \
"$ROOT/api/server.py" || true

echo
echo "=== CONTROLLER ROUTES ==="
grep -nE \
'^[[:space:]]*(develop|ask|api|status|library|version|pipeline)\)' \
"$ROOT/bin/corvus" || true

echo
echo "=== CONFIG ==="
grep -E \
'^CORVUS_(VERSION|MODE|CONTEXT|THREADS|LOW_RAM_MB|CRITICAL_RAM_MB)=' \
"$ROOT/config/corvus.env" || true
