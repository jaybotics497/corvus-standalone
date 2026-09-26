#!/usr/bin/env python3

from pathlib import Path

INBOX = Path.home() / "corvus/data/inbox"

print("=== CORVUS INBOX SCAN ===")

files = [
    f for f in INBOX.rglob("*")
    if f.is_file() and not f.name.startswith(".")
]

print(f"FILES WAITING: {len(files)}")

for f in files:
    subject = f.parent.name
    print(f"{subject}\t{f.name}")

print("INBOX SCAN: PASS")
