#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

if len(sys.argv) != 2:
    print("TARGET VALIDATION: BLOCKED - plan required")
    raise SystemExit(100)

plan = Path(sys.argv[1])

if not plan.is_file():
    print("TARGET VALIDATION: BLOCKED - plan missing")
    raise SystemExit(101)

target = None

for line in plan.read_text().splitlines():
    if line.startswith("TARGET:"):
        target = line.split(":", 1)[1].strip()
        break

if not target:
    print("TARGET VALIDATION: BLOCKED - target missing")
    raise SystemExit(102)

root = (Path.home() / "corvus").resolve()
path = (root / target).resolve()

if root not in path.parents:
    print("TARGET VALIDATION: BLOCKED - unsafe target")
    raise SystemExit(103)

if not path.is_file():
    print("TARGET VALIDATION: BLOCKED - target does not exist")
    print("TARGET:", target)
    raise SystemExit(104)

print("TARGET VALIDATION: PASS")
print("TARGET:", target)
