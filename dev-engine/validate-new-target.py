#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys
from capability_registry import match_capability, capability_allows_new_target

if len(sys.argv) != 2:
    print("NEW TARGET: BLOCKED - plan required")
    raise SystemExit(150)

plan = Path(sys.argv[1])
if not plan.is_file():
    print("NEW TARGET: BLOCKED - plan missing")
    raise SystemExit(151)

target = ""
change = ""
for line in plan.read_text().splitlines():
    if line.startswith("TARGET:"):
        target = line.split(":", 1)[1].strip()
    elif line.startswith("CHANGE:"):
        change = line.split(":", 1)[1].strip().lower()

if not target:
    print("NEW TARGET: BLOCKED - target missing")
    raise SystemExit(152)

cap = match_capability(target, change)
if not capability_allows_new_target(cap):
    print("NEW TARGET: BLOCKED - unauthorized capability")
    raise SystemExit(153)

root = (Path.home()/"corvus-dev/staging/corvus").resolve()
raw = root/target

current = raw
while current != root:
    if current.is_symlink():
        print("NEW TARGET: BLOCKED - symlink path")
        raise SystemExit(154)
    parent = current.parent
    if parent == current:
        print("NEW TARGET: BLOCKED - unsafe path")
        raise SystemExit(155)
    current = parent

resolved = raw.resolve(strict=False)
try:
    resolved.relative_to(root)
except ValueError:
    print("NEW TARGET: BLOCKED - staging escape")
    raise SystemExit(156)

if resolved == root:
    print("NEW TARGET: BLOCKED - staging root")
    raise SystemExit(157)

if raw.exists() or raw.is_symlink():
    print("NEW TARGET: BLOCKED - target exists")
    raise SystemExit(158)

print("NEW TARGET VALIDATION: PASS")
print("TARGET:", target)
