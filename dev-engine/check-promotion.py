#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("PROMOTION CHECK: job required")
    raise SystemExit(1)

job = Path(sys.argv[1])
record = Path.home()/"corvus-dev/changes/current-promotion"

if not record.is_file():
    print("PROMOTION CHECK: BLOCKED - record missing")
    raise SystemExit(22)

data = {}
for line in record.read_text().splitlines():
    if ":" in line:
        k, v = line.split(":", 1)
        data[k.strip()] = v.strip()

if data.get("JOB") != job.name:
    print("PROMOTION CHECK: BLOCKED - job mismatch")
    raise SystemExit(23)

if not data.get("BASELINE"):
    print("PROMOTION CHECK: BLOCKED - baseline missing")
    raise SystemExit(24)

if not data.get("CANDIDATE_SHA256"):
    print("PROMOTION CHECK: BLOCKED - candidate hash missing")
    raise SystemExit(26)

print("PROMOTION CHECK: PASS")
