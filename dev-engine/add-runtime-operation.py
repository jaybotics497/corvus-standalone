#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

target = Path.home()/"corvus-dev/staging/corvus/bin/corvus"

if not target.is_file():
    print("OPERATION: BLOCKED - controller missing")
    raise SystemExit(170)

text = target.read_text()

if "  runtime)" in text:
    print("OPERATION: BLOCKED - runtime already exists")
    raise SystemExit(171)

anchor = "  version)\n    echo \"$CORVUS_VERSION\"\n    ;;"

addition = """  version)
    echo "$CORVUS_VERSION"
    ;;
  runtime)
    echo "Context: $CORVUS_CONTEXT"
    echo "Threads: $CORVUS_THREADS"
    ;;"""

if text.count(anchor) != 1:
    print("OPERATION: BLOCKED - version anchor mismatch")
    raise SystemExit(172)

target.write_text(text.replace(anchor, addition, 1))

print("OPERATION: PASS")
print("TARGET: bin/corvus")
print("CHANGE: add runtime command")
