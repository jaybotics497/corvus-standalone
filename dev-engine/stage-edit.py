#!/usr/bin/env python3
from pathlib import Path
import sys

STAGE=(Path.home()/"corvus-dev/staging/corvus").resolve()

if len(sys.argv)!=4:
 print("USAGE: stage-edit.py JOB FILE CONTENT_FILE")
 raise SystemExit(1)

job=Path(sys.argv[1])
target=sys.argv[2]
content=Path(sys.argv[3])

allowed=[]
for line in job.read_text().splitlines():
 if line.startswith("FILES_ALLOWED:"):
  allowed=[x.strip() for x in line.split(":",1)[1].split(",") if x.strip()]

if target not in allowed:
 print("EDIT: BLOCKED")
 raise SystemExit(4)

dest=(STAGE/target).resolve()
if STAGE not in dest.parents:
 print("EDIT: PATH BLOCKED")
 raise SystemExit(5)

dest.write_text(content.read_text())
print("EDIT: PASS",target)
