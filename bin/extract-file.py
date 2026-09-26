#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import subprocess
import sys

BASE = Path.home() / "corvus/data"
ACCEPTED = BASE / "accepted"
EXTRACTED = BASE / "extracted"

if len(sys.argv) != 2:
    print("USAGE: extract-file.py FILE")
    sys.exit(1)

src = Path(sys.argv[1]).expanduser()

if not src.is_file():
    print("ERROR: FILE NOT FOUND")
    sys.exit(1)

subject = src.parent.name
dest_dir = EXTRACTED / subject

if not dest_dir.is_dir():
    print(f"ERROR: UNKNOWN SUBJECT: {subject}")
    sys.exit(1)

dest = dest_dir / f"{src.stem}.txt"
ext = src.suffix.lower()

try:
    if ext == ".pdf":
        subprocess.run(
            ["pdftotext", "-layout", str(src), str(dest)],
            check=True
        )
    elif ext in {".txt", ".md"}:
        dest.write_text(
            src.read_text(encoding="utf-8", errors="replace"),
            encoding="utf-8"
        )
    else:
        print(f"ERROR: UNSUPPORTED FORMAT: {ext}")
        sys.exit(1)

except Exception as e:
    print(f"ERROR: EXTRACTION FAILED: {e}")
    sys.exit(1)
timestamp = datetime.now().isoformat(timespec="seconds")
log = EXTRACTED / "extracted.tsv"

with log.open("a", encoding="utf-8") as f:
    f.write(
        f"{timestamp}\t{subject}\t{src.name}\t{dest.name}\tEXTRACTED\n"
    )

print(f"EXTRACTED: {subject}/{dest.name}")
print("EXTRACTION: PASS")
