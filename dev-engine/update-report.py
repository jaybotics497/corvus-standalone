#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv)!=3:
 print("USAGE: update-report.py REPORT STATUS")
 raise SystemExit(1)

report=Path(sys.argv[1])
status=sys.argv[2]

if not report.is_file():
 print("REPORT UPDATE: missing report")
 raise SystemExit(2)

lines=report.read_text().splitlines()
lines=[
 f"STATUS: {status}" if x.startswith("STATUS:") else x
 for x in lines
]

report.write_text("\n".join(lines)+"\n")
print("REPORT UPDATE: PASS")
