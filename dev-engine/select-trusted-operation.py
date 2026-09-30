#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

from capability_registry import match_capability

if len(sys.argv) != 2:
    print("USAGE: select-trusted-operation.py PLAN")
    raise SystemExit(140)

plan = Path(sys.argv[1])

if not plan.is_file():
    print("OPERATION SELECT: BLOCKED - plan missing")
    raise SystemExit(141)

target = ""
plan_text = plan.read_text()
change = ""

for line in plan_text.splitlines():
    if line.startswith("CHANGE:"):
        change = line.split(":", 1)[1].strip().lower()
        break

for line in plan_text.splitlines():
    if line.startswith("TARGET:"):
        target = line.split(":", 1)[1].strip()

capability = match_capability(target, change)

if capability is None:
    print("OPERATION SELECT: BLOCKED - no trusted operation")
    raise SystemExit(142)

operation = capability["operation"]

path = Path.home()/"corvus-dev"/operation

if not path.is_file():
    print("OPERATION SELECT: BLOCKED - trusted operation missing")
    raise SystemExit(143)

print(operation)
