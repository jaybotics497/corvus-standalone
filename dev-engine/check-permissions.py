#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys

if len(sys.argv)!=2:
 print("USAGE: check-permissions.py JOB")
 raise SystemExit(1)

job=Path(sys.argv[1])
stage=Path.home()/"corvus-dev/staging/corvus"

allowed=[]
for line in job.read_text().splitlines():
 if line.startswith("FILES_ALLOWED:"):
  allowed=[x.strip() for x in line.split(":",1)[1].split(",") if x.strip()]

from git_changes import changed_paths

files = changed_paths(stage)
blocked=[x for x in files if x not in allowed]

if blocked:
 print("PERMISSION: BLOCKED")
 print("UNAUTHORIZED:",",".join(blocked))
 raise SystemExit(4)

print("PERMISSION: PASS")
