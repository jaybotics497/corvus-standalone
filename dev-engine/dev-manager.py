#!/usr/bin/env python3
from pathlib import Path
import sys

job=Path(sys.argv[1]) if len(sys.argv)>1 else None

if not job or not job.is_file():
    print("DEV MANAGER: valid job file required")
    raise SystemExit(1)

text=job.read_text()
required=["OBJECTIVE:","REQUIREMENTS:","FILES_ALLOWED:",
          "TESTS_REQUIRED:","APPROVAL_REQUIRED:","STATUS:"]

missing=[x for x in required if x not in text]

if missing:
    print("DEV MANAGER: invalid job")
    raise SystemExit(2)

allowed=""
for line in text.splitlines():
    if line.startswith("FILES_ALLOWED:"):
        allowed=line.split(":",1)[1].strip()
        break

if not allowed:
    print("DEV MANAGER: no files authorized")
    raise SystemExit(3)

print("DEV MANAGER: JOB VALID")
print("FILES AUTHORIZED:",allowed)
