#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

from capability_registry import match_capability

if len(sys.argv) != 2:
    print("CAPABILITY TARGET: BLOCKED - plan required")
    raise SystemExit(230)

plan = Path(sys.argv[1])

if not plan.is_file():
    print("CAPABILITY TARGET: BLOCKED - plan missing")
    raise SystemExit(231)

target = None
change = None

for line in plan.read_text().splitlines():
    if line.startswith("TARGET:"):
        target = line.split(":", 1)[1].strip()
    elif line.startswith("CHANGE:"):
        change = line.split(":", 1)[1].strip().strip('"')

if not target or not change:
    print("CAPABILITY TARGET: BLOCKED - target or change missing")
    raise SystemExit(232)

capability = match_capability(target, change)

if capability is None:
    print("CAPABILITY TARGET: BLOCKED - no trusted capability for target")
    print("TARGET:", target)
    print("CHANGE:", change)
    raise SystemExit(233)

print("CAPABILITY TARGET: PASS")
print("TARGET:", target)
print("OPERATION:", capability["operation"])
print("TEST:", capability["test"])
