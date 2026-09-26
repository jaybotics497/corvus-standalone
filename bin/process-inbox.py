#!/usr/bin/env python3

from pathlib import Path
import shutil

HOME = Path.home()
INBOX = HOME / "corvus/data/inbox"
PROCESSING = HOME / "corvus/data/processing"

moved = 0

for src in INBOX.rglob("*"):
    if not src.is_file() or src.name.startswith("."):
        continue

    subject = src.parent.name
    dest_dir = PROCESSING / subject

    if not dest_dir.is_dir():
        print(f"SKIP UNKNOWN SUBJECT: {subject}")
        continue

    dest = dest_dir / src.name

    if dest.exists():
        print(f"SKIP EXISTS: {src.name}")
        continue

    shutil.move(str(src), str(dest))
    print(f"MOVED: {subject}/{src.name}")
    moved += 1

print(f"FILES MOVED: {moved}")
print("PROCESSING MOVE: PASS")
