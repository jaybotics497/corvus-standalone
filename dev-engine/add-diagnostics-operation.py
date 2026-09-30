#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

stage = Path.home()/"corvus-dev/staging/corvus"
target = stage/"bin/corvus"

if not target.is_file():
    print("OPERATION: BLOCKED - controller missing")
    raise SystemExit(130)

text = target.read_text()

if "status|diagnostics)" in text:
    print("OPERATION: BLOCKED - diagnostics already exists")
    raise SystemExit(131)

old = "    status)"
new = "    status|diagnostics)"

count = text.count(old)

if count != 1:
    print("OPERATION: BLOCKED - expected exactly one status route")
    print("MATCHES:", count)
    raise SystemExit(132)

target.write_text(text.replace(old, new, 1))

print("OPERATION: PASS")
print("TARGET: bin/corvus")
print("CHANGE: status -> status|diagnostics")
