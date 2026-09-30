#!/usr/bin/env python3
from pathlib import Path
import sys

from capability_registry import CAPABILITIES, capability_allows_new_target

if len(sys.argv) != 2:
    print("USAGE: select-target.py JOB")
    raise SystemExit(1)

job = Path(sys.argv[1])
stage = Path.home() / "corvus-dev/staging/corvus"

allowed = []
objective = ""

for line in job.read_text().splitlines():
    if line.startswith("FILES_ALLOWED:"):
        allowed = [
            x.strip()
            for x in line.split(":", 1)[1].split(",")
            if x.strip()
        ]
    elif line.startswith("OBJECTIVE:"):
        objective = line.split(":", 1)[1].strip().lower()

existing = [x for x in allowed if (stage / x).is_file()]

if existing:
    print("TARGET:", existing[0])
    raise SystemExit(0)

for target in allowed:
    for capability in CAPABILITIES:
        authorized = capability.get("files", (capability["target"],))
        if target in authorized and capability_allows_new_target(capability):
            print("TARGET:", target)
            raise SystemExit(0)

print("TARGET: BLOCKED - no authorized target")
raise SystemExit(2)
