from pathlib import Path
import re

H=Path.home()
B=H/"corvus/data/library/book_test"
C=H/"corvus/data/index/chunks"
I=H/"corvus/data/index/citations.tsv"
C.mkdir(parents=True,exist_ok=True)

rows=["CHUNK_ID\tSOURCE\tCHAPTER\tPATH"]

for b in sorted(B.glob("book_*.txt")):
    text=b.read_text()
    for m in re.finditer(r"(?ms)^CHAPTER (\d+)\n(.*?)(?=^CHAPTER \d+\n|\Z)",text):
        ch=m.group(1)
        out=C/f"{b.stem}_ch{ch}.txt"
        out.write_text(m.group(0))
        rows.append(f"{b.stem}_CH{ch}\t{b.stem}\t{ch}\t{out}")

I.write_text("\n".join(rows)+"\n")
print("Chunks:",len(rows)-1)
