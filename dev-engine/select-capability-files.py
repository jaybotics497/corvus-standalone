#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

from capability_registry import match_capability, capability_files

if len(sys.argv) != 2:
    print("FILES SELECT: BLOCKED - plan required")
    raise SystemExit(240)

plan = Path(sys.argv[1])

if not plan.is_file():
    print("FILES SELECT: BLOCKED - plan missing")
    raise SystemExit(241)

target = ""
change = ""

for line in plan.read_text().splitlines():
    if line.startswith("TARGET:"):
        target = line.split(":", 1)[1].strip()
    elif line.startswith("CHANGE:"):
        change = line.split(":", 1)[1].strip().lower()

capability = match_capability(target, change)

if capability is None:
    print("FILES SELECT: BLOCKED - no trusted capability")
    raise SystemExit(242)

print(",".join(capability_files(capability)))
