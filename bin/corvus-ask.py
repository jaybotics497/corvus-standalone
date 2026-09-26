#!/usr/bin/env python3
from pathlib import Path
import sqlite3,sys,subprocess,re

BASE=Path.home()/"corvus"
DB=BASE/"data/index/corvus.db"

query=" ".join(sys.argv[1:]).strip()
if not query:
 print("USAGE: corvus-ask.py QUESTION")
 sys.exit(1)

terms=re.findall(r"[A-Za-z0-9_]+",query)
fts_query=" OR ".join(terms)

con=sqlite3.connect(DB)
rows=con.execute("""
 SELECT c.source,c.page,c.section,c.content
 FROM chunks_fts f
 JOIN chunks c ON c.id=f.rowid
 WHERE chunks_fts MATCH ?
 ORDER BY bm25(chunks_fts)
 LIMIT 3
""",(fts_query,)).fetchall()
con.close()

print(f"RETRIEVED: {len(rows)}")

if not rows:
 print("CORVUS: no relevant library sources found.")
 print("ANSWER BLOCKED: no supporting source.")
 sys.exit(2)

context=[]

for i,(source,page,section,content) in enumerate(rows,1):
 cite=f"[SOURCE {i}: {source}"
 if page is not None:
  cite+=f", page {page}"
 if section:
  cite+=f", section {section}"
 cite+="]"
 context.append(f"{cite}\n{content}")

evidence="\n\n".join(context)

prompt=f"""Answer the question using ONLY the supplied library evidence.
If the evidence is insufficient, state that clearly.
Every factual claim MUST include its supporting label such as [SOURCE 1]. Begin your final answer with <ANSWER> and end it with </ANSWER>.

QUESTION:
{query}

LIBRARY EVIDENCE:
{evidence}
"""

print("GROUNDING: READY")
result=subprocess.run(
 [str(BASE/"bin/infer"),prompt],
 text=True,
 capture_output=True
)
raw=result.stdout
matches=re.findall(r"<ANSWER>\s*(.*?)\s*</ANSWER>",raw,re.DOTALL)
answer=matches[-1].strip() if matches else raw.strip()

if result.returncode!=0:
 print(result.stderr.strip())
 sys.exit(result.returncode)

print(answer)

if "[SOURCE " not in answer:
 source,page,section,_=rows[0]
 cite=f"[SOURCE 1: {source}"
 if page is not None:
  cite+=f", page {page}"
 if section:
  cite+=f", section {section}"
 cite+="]"
 print(cite)

sys.exit(0)
