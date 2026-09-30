#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

from capability_registry import CAPABILITIES

if len(sys.argv) != 2:
    print("TRUSTED ROUTE: BLOCKED - plan required")
    raise SystemExit(240)

plan = Path(sys.argv[1])

if not plan.is_file():
    print("TRUSTED ROUTE: BLOCKED - plan missing")
    raise SystemExit(241)

lines = plan.read_text().splitlines()
change = None

for line in lines:
    if line.startswith("CHANGE:"):
        change = line.split(":", 1)[1].strip().strip('"')
        break

if not change:
    print("TRUSTED ROUTE: BLOCKED - change missing")
    raise SystemExit(242)

matches = [
    capability
    for capability in CAPABILITIES
    if capability["keyword"] in change.lower()
]

if not matches:
    print("TRUSTED ROUTE: BLOCKED - no trusted capability")
    raise SystemExit(243)

capability = max(matches, key=lambda item: len(item["keyword"]))
target = capability["target"]

out = []
found = False

for line in lines:
    if line.startswith("TARGET:"):
        out.append(f"TARGET: {target}")
        found = True
    else:
        out.append(line)

if not found:
    print("TRUSTED ROUTE: BLOCKED - target missing")
    raise SystemExit(244)

plan.write_text("\n".join(out) + "\n")

print("TRUSTED ROUTE: PASS")
print("TARGET:", target)
print("KEYWORD:", capability["keyword"])
