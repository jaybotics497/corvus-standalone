#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import subprocess,sys

if len(sys.argv)!=2:
 print("USAGE: write-report.py JOB")
 raise SystemExit(1)

job=Path(sys.argv[1])
stage=Path.home()/"corvus-dev/staging/corvus"
reports=Path.home()/"corvus-dev/reports"
reports.mkdir(exist_ok=True)

stamp=datetime.now().strftime("%Y%m%d-%H%M%S")
commit=subprocess.check_output(
 ["git","-C",str(stage),"rev-parse","HEAD"],text=True
).strip()

out=reports/f"{stamp}-{job.stem}.txt"
out.write_text(
 f"JOB: {job.name}\n"
 f"BASELINE: {commit}\n"
 f"TIME: {stamp}\n"
 f"STATUS: initialized\n"
)

active=Path.home()/"corvus-dev/changes/current-report"
active.write_text(str(out) + "\n")

print("REPORT: PASS")
print("REPORT FILE:",out)
