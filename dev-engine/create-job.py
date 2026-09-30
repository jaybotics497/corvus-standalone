#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import sys,re

if len(sys.argv)<4:
 print("USAGE: create-job.py OBJECTIVE FILES TESTS")
 raise SystemExit(1)

objective=sys.argv[1].strip()
files=sys.argv[2].strip()
tests=sys.argv[3].strip()

if not objective or not files or not tests:
 print("CREATE JOB: BLOCKED - missing fields")
 raise SystemExit(2)

name=re.sub(r'[^a-z0-9]+','-',objective.lower()).strip('-')[:40]
stamp=datetime.now().strftime("%Y%m%d-%H%M%S")

out=Path.home()/"corvus-dev/jobs"/f"{stamp}-{name}.txt"

out.write_text(
 f"OBJECTIVE: {objective}\n"
 f"REQUIREMENTS: {objective}\n"
 f"FILES_ALLOWED: {files}\n"
 f"TESTS_REQUIRED: {tests}\n"
 f"APPROVAL_REQUIRED: yes\n"
 f"STATUS: pending\n"
)

print("CREATE JOB: PASS")
print("JOB FILE:",out)
