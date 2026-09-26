from pathlib import Path
import csv, re

H = Path.home()
LIB = H/"corvus/data/library"
OUT = H/"corvus/data/index/chunks"
INDEX = H/"corvus/data/index/chunk-index.tsv"

OUT.mkdir(parents=True, exist_ok=True)

rows = []
chunk_count = 0

for src in sorted(LIB.rglob("*.txt")):
    text = src.read_text(errors="ignore")
    words = text.split()

    if not words:
        continue

    source_id = src.name.split("_",1)[0]
    subject = src.parent.name

    for n, start in enumerate(range(0, len(words), 300), 1):
        chunk_words = words[start:start+350]
        chunk_id = f"{source_id}_C{n:04d}"
        path = OUT/f"{chunk_id}.txt"

        path.write_text(" ".join(chunk_words))

        rows.append([
            chunk_id,
            source_id,
            subject,
            str(src),
            str(path),
            len(chunk_words)
        ])
        chunk_count += 1

with INDEX.open("w", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["CHUNK_ID","SOURCE_ID","SUBJECT","SOURCE_PATH","CHUNK_PATH","WORDS"])
    w.writerows(rows)

print("=== CORVUS CHUNK ENGINE ===")
print("Chunks:", chunk_count)
print("Index:", INDEX)
print("CHUNK ENGINE: PASS")
