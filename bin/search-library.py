#!/usr/bin/env python3
from pathlib import Path
import sqlite3,sys

db=Path.home()/"corvus/data/index/corvus.db"

if len(sys.argv)<2:
 print("USAGE: search-library.py TERMS")
 sys.exit(1)

q=" ".join(sys.argv[1:]).strip()
con=sqlite3.connect(db)
rows=con.execute("""
SELECT c.subject,c.source,c.chunk_file,c.content,c.page,c.section,bm25(chunks_fts)
FROM chunks_fts
JOIN chunks c ON c.id=chunks_fts.rowid
WHERE chunks_fts MATCH ?
ORDER BY bm25(chunks_fts)
LIMIT 5
""",(q,)).fetchall()

con.close()
print(f"QUERY: {q}")
print(f"RESULTS: {len(rows)}")

for i,r in enumerate(rows,1):
 print(f"[{i}] {r[0]} | {r[1]} | {r[2]}")
 print(r[3][:500])
 print(f"CITATION: page={r[4] or chr(45)} | section={r[5] or chr(45)}")
 print(f"RANK: {r[6]:.4f}")

print("SEARCH: PASS")
