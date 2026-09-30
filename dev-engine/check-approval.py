#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv)!=2:
 print("USAGE: check-approval.py JOB")
 raise SystemExit(1)

job=Path(sys.argv[1])
status=""
approval=""

for line in job.read_text().splitlines():
 if line.startswith("APPROVAL_REQUIRED:"):
  approval=line.split(":",1)[1].strip().lower()
 if line.startswith("STATUS:"):
  status=line.split(":",1)[1].strip().lower()

if approval=="yes" and status!="approved":
 print("APPROVAL: BLOCKED")
 raise SystemExit(7)

print("APPROVAL: PASS")
