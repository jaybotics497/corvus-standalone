#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv)!=2:
 print("USAGE: validate-candidate.py FILE")
 raise SystemExit(1)

p=Path(sys.argv[1])

if not p.is_file():
 print("CANDIDATE VALIDATION: MISSING")
 raise SystemExit(2)

text=p.read_text()

if len(text)<100:
 print("CANDIDATE VALIDATION: BLOCKED - suspiciously short")
 raise SystemExit(3)

if text.strip()=="complete file contents":
 print("CANDIDATE VALIDATION: BLOCKED - placeholder")
 raise SystemExit(4)

if not text.startswith("#!"):
 print("CANDIDATE VALIDATION: BLOCKED - missing script header")
 raise SystemExit(5)

print("CANDIDATE VALIDATION: PASS")
