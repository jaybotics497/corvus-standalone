#!/usr/bin/env python3
import sys
from pathlib import Path

if len(sys.argv) not in (2, 3):
    print("PLAN VALIDATION: BLOCKED - plan file required")
    sys.exit(70)

plan_path = Path(sys.argv[1])
objective = sys.argv[2] if len(sys.argv) == 3 else ""

if not plan_path.is_file():
    print("PLAN VALIDATION: BLOCKED - plan file missing")
    sys.exit(71)

text = plan_path.read_text().strip()
lines = [line.strip() for line in text.splitlines() if line.strip()]

required = ["SUMMARY:", "TARGET:", "CHANGE:", "TEST:", "RISK:"]

if len(lines) != 5:
    print(f"PLAN VALIDATION: FAIL - expected 5 fields, got {len(lines)}")
    sys.exit(72)

for line, prefix in zip(lines, required):
    if not line.startswith(prefix):
        print(f"PLAN VALIDATION: FAIL - expected {prefix}")
        sys.exit(73)

target = lines[1].split(":", 1)[1].strip()

if not target:
    print("PLAN VALIDATION: FAIL - empty target")
    sys.exit(74)

repo = Path.home() / "corvus-dev" / "staging" / "corvus"
resolved = repo / target

if not resolved.is_file():
    from capability_registry import match_capability, capability_allows_new_target

    change = next(line.split(":", 1)[1].strip().lower() for line in lines if line.startswith("CHANGE:"))
    capability = match_capability(target, change)

    if not capability_allows_new_target(capability):
        print(f"PLAN VALIDATION: FAIL - target does not exist: {target}")
        sys.exit(75)

objective_lower = objective.lower()

api_objective = (
    "endpoint" in objective_lower
    and (
        "api" in objective_lower
        or "post /" in objective_lower
        or "get /" in objective_lower
    )
)

if api_objective:
    api_server = repo / "api" / "server.py"

    if api_server.is_file() and target != "api/server.py":
        print(
            "PLAN VALIDATION: FAIL - API endpoint objective must target "
            "api/server.py"
        )
        print(f"REJECTED TARGET: {target}")
        sys.exit(76)

print("PLAN VALIDATION: PASS")
print(f"TARGET: {target}")
sys.exit(0)
