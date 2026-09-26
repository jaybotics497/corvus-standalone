#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import shutil
import sys

BASE = Path.home() / "corvus/data"
QUARANTINE = BASE / "quarantine"
LOG = QUARANTINE / "rejected.tsv"

if len(sys.argv) != 3:
    print("USAGE: quarantine-file.py FILE REASON")
    sys.exit(1)

src = Path(sys.argv[1]).expanduser()
reason = sys.argv[2].replace("\t", " ").replace("\n", " ")

if not src.is_file():
    print("ERROR: FILE NOT FOUND")
    sys.exit(1)

subject = src.parent.name
dest_dir = QUARANTINE / subject
dest_dir.mkdir(parents=True, exist_ok=True)

dest = dest_dir / src.name

if dest.exists():
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = dest_dir / f"{src.stem}_{stamp}{src.suffix}"

shutil.move(str(src), str(dest))

timestamp = datetime.now().isoformat(timespec="seconds")

with LOG.open("a", encoding="utf-8") as f:
    f.write(f"{timestamp}\t{subject}\t{dest.name}\t{reason}\n")

print(f"QUARANTINED: {subject
}/{dest.name}")
print("QUARANTINE: PASS")
