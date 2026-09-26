#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,re
from datetime import datetime

BASE=Path.home()/"corvus/data"
PAGES=BASE/"pages"
LOG=PAGES/"pages.tsv"

if len(sys.argv)!=2:
 print("USAGE: extract-pages.py PDF")
 sys.exit(1)

src=Path(sys.argv[1]).expanduser()
if not src.is_file() or src.suffix.lower()!=".pdf":
 print("ERROR: VALID PDF REQUIRED")
 sys.exit(1)
subject=src.parent.name
dest=PAGES/subject/src.stem
dest.mkdir(parents=True,exist_ok=True)

info=subprocess.run(["pdfinfo",str(src)],capture_output=True,text=True,check=True).stdout
m=re.search(r"^Pages:\s+(\d+)",info,re.MULTILINE)
if not m:
 print("ERROR: PAGE COUNT NOT FOUND")
 sys.exit(1)

count=int(m.group(1))
print(f"PAGES FOUND: {count}")
for page in range(1,count+1):
 out=dest/f"page_{page:05d}.txt"
 subprocess.run([
  "pdftotext","-layout","-f",str(page),"-l",str(page),str(src),str(out)
 ],check=True)
 with LOG.open("a",encoding="utf-8") as f:
  ts=datetime.now().isoformat(timespec="seconds")
  f.write(f"{ts}\t{subject}\t{src.name}\t{page}\t{out}\tOK\n")

print(f"PAGES EXTRACTED: {count}")
print("PAGE EXTRACTION: PASS")
