#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import shutil
import sys

BASE = Path.home() / "corvus/data"
PROCESSING = BASE / "processing"
ACCEPTED = BASE / "accepted"
LOG = ACCEPTED / "accepted.tsv"

if len(sys.argv) < 2:
    print("USAGE: accept-file.py FILE [SOURCE]")
    sys.exit(1)

src = Path(sys.argv[1]).expanduser()
source = sys.argv[2] if len(sys.argv) > 2 else "unknown"

if not src.is_file():
    print("ERROR: FILE NOT FOUND")
    sys.exit(1)

subject = src.parent.name
dest_dir = ACCEPTED / subject

if not dest_dir.is_dir():
    print(f"ERROR: UNKNOWN SUBJECT: {subject}")
    sys.exit(1)

dest = dest_dir / src.name

if dest.exists():
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = dest_dir / f"{src.stem}_{stamp}{src.suffix}"

shutil.move(str(src), str(dest))

timestamp = datetime.now().isoformat(timespec="seconds")

with LOG.open("a", encoding="utf-8") as f:
    f.write(
        f"{timestamp}\t{subject}\t{dest.name}\t{source}\tACCEPTED\n"
    )

print(f"ACCEPTED: {subject}/{dest.name}")
print("ACCEPTANCE: PASS")
