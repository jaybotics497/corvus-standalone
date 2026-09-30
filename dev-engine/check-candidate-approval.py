#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    print("USAGE: check-candidate-approval.py JOB")
    raise SystemExit(1)

job = Path(sys.argv[1])
base = Path.home()/"corvus-dev/changes"
approval = base/"current-approval"
hashfile = base/"current-candidate.sha256"

if not approval.is_file() or not hashfile.is_file():
    print("CANDIDATE APPROVAL: BLOCKED - record missing")
    raise SystemExit(15)

data = {}
for line in approval.read_text().splitlines():
    if ":" in line:
        k, v = line.split(":", 1)
        data[k.strip()] = v.strip()

expected_job = job.name
expected_hash = hashfile.read_text().strip()

if data.get("STATUS") != "approved":
    print("CANDIDATE APPROVAL: BLOCKED - not approved")
    raise SystemExit(16)

if data.get("JOB") != expected_job:
    print("CANDIDATE APPROVAL: BLOCKED - wrong job")
    raise SystemExit(17)

if data.get("CANDIDATE_SHA256") != expected_hash:
    print("CANDIDATE APPROVAL: BLOCKED - hash mismatch")
    raise SystemExit(18)

print("CANDIDATE APPROVAL: PASS")
