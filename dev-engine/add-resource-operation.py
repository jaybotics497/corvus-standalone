#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

target = Path.home()/"corvus-dev/staging/corvus/bin/corvus"

if not target.is_file():
    print("OPERATION: BLOCKED - controller missing")
    raise SystemExit(180)

text = target.read_text()

if "  resource)" in text:
    print("OPERATION: BLOCKED - resource already exists")
    raise SystemExit(181)

anchor = '''  runtime)
    echo "Context: $CORVUS_CONTEXT"
    echo "Threads: $CORVUS_THREADS"
    ;;'''

addition = '''  runtime)
    echo "Context: $CORVUS_CONTEXT"
    echo "Threads: $CORVUS_THREADS"
    ;;
  resource)
    echo "=== CORVUS RESOURCES ==="
    awk '/MemAvailable:/ {printf "RAM available: %d MB\\n", $2/1024}' /proc/meminfo
    awk '/SwapTotal:/ {t=$2} /SwapFree:/ {printf "Swap available: %d / %d MB\\n", $2/1024, t/1024}' /proc/meminfo
    df -k "$HOME/storage/shared" | awk 'NR==2 {printf "Internal storage: %d MB free / %d MB total\\n", $4/1024, $2/1024}'
    du -sm "$BASE" | awk '{printf "CORVUS storage usage: %d MB\\n", $1}'
    ;;'''

if text.count(anchor) != 1:
    print("OPERATION: BLOCKED - runtime anchor mismatch")
    raise SystemExit(182)

target.write_text(text.replace(anchor, addition, 1))

print("OPERATION: PASS")
print("TARGET: bin/corvus")
print("CHANGE: add resource command")
