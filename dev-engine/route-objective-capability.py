#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

from capability_registry import match_objective_capability

if len(sys.argv) < 3:
    print("OBJECTIVE ROUTE: BLOCKED - plan and objective required")
    raise SystemExit(245)

plan = Path(sys.argv[1])
objective = " ".join(sys.argv[2:])

if not plan.is_file():
    print("OBJECTIVE ROUTE: BLOCKED - plan missing")
    raise SystemExit(246)

capability = match_objective_capability(objective)

if capability is None:
    print("OBJECTIVE ROUTE: BLOCKED - objective capability unknown or ambiguous")
    raise SystemExit(247)

lines = plan.read_text().splitlines()
out = []
found_target = False
found_change = False

for line in lines:
    if line.startswith("TARGET:"):
        out.append(f"TARGET: {capability['target']}")
        found_target = True
    elif line.startswith("CHANGE:"):
        out.append(f"CHANGE: {capability['keyword']}")
        found_change = True
    else:
        out.append(line)

if not found_target or not found_change:
    print("OBJECTIVE ROUTE: BLOCKED - plan fields missing")
    raise SystemExit(248)

plan.write_text("\n".join(out) + "\n")

print("OBJECTIVE ROUTE: PASS")
print("CAPABILITY:", capability["keyword"])
print("TARGET:", capability["target"])
