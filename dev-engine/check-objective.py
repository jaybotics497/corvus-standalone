#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import subprocess, sys

if len(sys.argv) < 2:
    print("OBJECTIVE CHECK: BLOCKED - objective required")
    raise SystemExit(80)

objective = " ".join(sys.argv[1:]).lower()
live = Path.home()/"corvus"

checks = {
    "version": ["version)"],
    "development status": ["dev-status)"],
    "dev status": ["dev-status)"],
    "status": ["status)"],
    "health": ["health)"],
    "diagnostics": ["status|diagnostics)"],
    "library": ["library)"],
    "search": ["search)"],
}

controller = (live/"bin/corvus").read_text()

add_words = ("add ", "create ", "implement ", "introduce ")

for phrase, markers in checks.items():
    requested = any(f"{word}{phrase}" in objective for word in add_words)
    if requested:
        for marker in markers:
            if marker in controller:
                print("OBJECTIVE CHECK: ALREADY EXISTS")
                print("MATCH:", phrase)
                print("FOUND:", marker)
                raise SystemExit(81)

print("OBJECTIVE CHECK: PASS")
