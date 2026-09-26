#!/usr/bin/env python3
from pathlib import Path
import sys,re

BASE=Path.home()/"corvus/data"
PAGES=BASE/"pages"
CHUNKS=BASE/"chunks"
CHUNK_SIZE=1200
OVERLAP=200

if len(sys.argv)!=2:
 print("USAGE: chunk-pages.py PAGE_DIRECTORY")
 sys.exit(1)

src=Path(sys.argv[1]).expanduser()

if not src.is_dir():
 print("ERROR: PAGE DIRECTORY NOT FOUND")
 sys.exit(1)

subject=src.parent.name
document=src.name
page_files=sorted(src.glob("page_*.txt"))

if not page_files:
 print("ERROR: NO PAGE FILES")
 sys.exit(1)

dest=CHUNKS/subject/document
dest.mkdir(parents=True,exist_ok=True)

print(f"PAGES FOUND: {len(page_files)}")

total=0

for page_file in page_files:
 m=re.search(r"page_(\d+)",page_file.stem)
 if not m:
  continue

 page=int(m.group(1))
 text=page_file.read_text(encoding="utf-8",errors="replace")
 text=re.sub(r"\s+"," ",text).strip()

 if not text:
  continue

 start=0
 part=1
 while start<len(text):
  end=min(start+CHUNK_SIZE,len(text))
  chunk=text[start:end]

  out=dest/f"page_{page:05d}_chunk_{part:05d}.txt"
  out.write_text(chunk,encoding="utf-8")
  total+=1

  if end==len(text):
   break

  start=end-OVERLAP
  part+=1

print(f"CHUNKS CREATED: {total}")
print("PAGE CHUNKING: PASS")
