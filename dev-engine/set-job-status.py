#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("STATUS: usage: set-job-status.py JOB NEW_STATUS")
    raise SystemExit(1)

job = Path(sys.argv[1])
new = sys.argv[2]

allowed = {
    "pending": {"approved", "retired"},
    "approved": {"completed", "retired"},
}

if not job.is_file():
    print("STATUS: BLOCKED - job missing")
    raise SystemExit(2)

lines = job.read_text().splitlines()
old = next((x.split(":",1)[1].strip()
            for x in lines if x.startswith("STATUS:")), None)

if new not in allowed.get(old, set()):
    print(f"STATUS: BLOCKED - {old} -> {new}")
    raise SystemExit(20)

lines = [
    f"STATUS: {new}" if x.startswith("STATUS:") else x
    for x in lines
]

job.write_text("\n".join(lines) + "\n")
print(f"STATUS: {old} -> {new}")
