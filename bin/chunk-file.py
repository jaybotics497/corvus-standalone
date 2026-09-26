#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import sys
import re

BASE = Path.home() / "corvus/data"
CHUNKS = BASE / "chunks"
LOG = CHUNKS / "chunks.tsv"
CHUNK_SIZE = 1200
OVERLAP = 200

if len(sys.argv) != 2:
    print("USAGE: chunk-file.py FILE")
    sys.exit(1)

src = Path(sys.argv[1]).expanduser()

if not src.is_file():
    print("ERROR: FILE NOT FOUND")
    sys.exit(1)

subject = src.parent.name
dest_dir = CHUNKS / subject

if not dest_dir.is_dir():
    print(f"ERROR: UNKNOWN SUBJECT: {subject}")
    sys.exit(1)

text = src.read_text(encoding="utf-8", errors="replace")
text = re.sub(r"\s+", " ", text).strip()

if not text:
    print("ERROR: EMPTY TEXT")
    sys.exit(1)

doc_dir = dest_dir / src.stem
doc_dir.mkdir(parents=True, exist_ok=True)

for old in doc_dir.glob("chunk_*.txt"):
    old.unlink()

chunks = []
start = 0

while start < len(text):
    end = min(start + CHUNK_SIZE, len(text))
    chunk = text[start:end].strip()
    if chunk:
        chunks.append(chunk)
    if end >= len(text):
        break
    start = end - OVERLAP

for number, chunk in enumerate(chunks, 1):
    path = doc_dir / f"chunk_{number:05d}.txt"
    path.write_text(chunk, encoding="utf-8")

timestamp = datetime.now().isoformat(timespec="seconds")

with LOG.open("a", encoding="utf-8") as f:
    f.write(f"{timestamp}\t{subject}\t{src.name}\t{len(chunks)}\tCHUNKED\n")

print(f"CHUNKED: {subject}/{src.name}")
print(f"CHUNKS CREATED: {len(chunks)}")
print("CHUNKING: PASS")
