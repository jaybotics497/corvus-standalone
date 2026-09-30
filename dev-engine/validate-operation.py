#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv)!=3:
 print("USAGE: validate-operation.py TARGET OPERATION")
 raise SystemExit(1)

target=Path(sys.argv[1])
op=Path(sys.argv[2]).read_text()
source=target.read_text()

try:
 anchor=op.split("ANCHOR:",1)[1].split("INSERT_AFTER:",1)[0].strip()
 insert=op.split("INSERT_AFTER:",1)[1].split("END_EDIT",1)[0].strip()
except IndexError:
 print("OPERATION VALIDATION: BLOCKED - malformed")
 raise SystemExit(2)

if source.count(anchor)!=1:
 print("OPERATION VALIDATION: BLOCKED - anchor not unique/existing")
 raise SystemExit(3)

if not insert:
 print("OPERATION VALIDATION: BLOCKED - empty edit")
 raise SystemExit(4)

if "<" in insert or ">" in insert:
 print("OPERATION VALIDATION: BLOCKED - placeholder")
 raise SystemExit(7)

for forbidden in ["cd ", "source ", "jq ", ".meta", "rm ", "curl ", "wget "]:
 if forbidden in insert:
  print("OPERATION VALIDATION: BLOCKED - forbidden operation")
  raise SystemExit(6)

print("OPERATION VALIDATION: PASS")
