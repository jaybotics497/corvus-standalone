#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

from capability_registry import match_capability

if len(sys.argv) != 2:
    print("TEST SELECT: BLOCKED - plan required")
    raise SystemExit(121)

plan = Path(sys.argv[1])

if not plan.is_file():
    print("TEST SELECT: BLOCKED - plan missing")
    raise SystemExit(122)

target = None

for line in plan.read_text().splitlines():
    if line.startswith("TARGET:"):
        target = line.split(":", 1)[1].strip()
        break

plan_text = plan.read_text()
change = ""

for line in plan_text.splitlines():
    if line.startswith("CHANGE:"):
        change = line.split(":", 1)[1].strip().lower()
        break

capability = match_capability(target, change)
test = capability["test"] if capability else None

if not test:
    print("TEST SELECT: BLOCKED - no trusted test for target")
    print("TARGET:", target)
    raise SystemExit(123)

print(test)
