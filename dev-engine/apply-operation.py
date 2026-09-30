#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv)!=3:
 print("USAGE: apply-operation.py TARGET OPERATION")
 raise SystemExit(1)

target=Path(sys.argv[1])
op=Path(sys.argv[2]).read_text()

if "ANCHOR:" not in op or "INSERT_AFTER:" not in op or "END_EDIT" not in op:
 print("OPERATION: INVALID")
 raise SystemExit(2)

anchor=op.split("ANCHOR:",1)[1].split("INSERT_AFTER:",1)[0].strip()
insert=op.split("INSERT_AFTER:",1)[1].split("END_EDIT",1)[0].strip("\n")

text=target.read_text()

if text.count(anchor)!=1:
 print("OPERATION: ANCHOR REJECTED")
 raise SystemExit(3)

if not insert:
 print("OPERATION: EMPTY")
 raise SystemExit(4)

text=text.replace(anchor,anchor+"\n"+insert,1)
target.write_text(text)

print("OPERATION: PASS")
