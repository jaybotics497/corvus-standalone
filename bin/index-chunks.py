#!/usr/bin/env python3
from pathlib import Path
import sqlite3,sys,re

base=Path.home()/"corvus/data"
chunks=base/"chunks"
db=base/"index/corvus.db"

if len(sys.argv)!=2:
 print("USAGE: index-chunks.py DIRECTORY");sys.exit(1)

d=Path(sys.argv[1]).expanduser()
if not d.is_dir():
 print("ERROR: DIRECTORY NOT FOUND");sys.exit(1)

files=sorted(set(d.glob("chunk_*.txt")) | set(d.glob("page_*_chunk_*.txt")))
if not files:
 print("ERROR: NO CHUNKS FOUND");sys.exit(1)

con=sqlite3.connect(db)
for p in files:
 rel=str(p.relative_to(chunks))
 text=p.read_text(encoding="utf-8",errors="replace")
 m=re.match(r"page_(\d+)_chunk_",p.name)
 page=int(m.group(1)) if m else None
 con.execute("INSERT INTO chunks(subject,source,chunk_file,content,page) VALUES(?,?,?,?,?) ON CONFLICT(chunk_file) DO UPDATE SET content=excluded.content",(d.parent.name,d.name,rel,text,page))

con.commit()
con.close()

print(f"INDEXED: {d.parent.name}/{d.name}")
print(f"CHUNKS INDEXED: {len(files)}")
print("INDEXING: PASS")
