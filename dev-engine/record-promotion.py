#!/data/data/com.termux/files/usr/bin/python
import subprocess, sys
from pathlib import Path

if len(sys.argv) != 2:
    print("PROMOTION RECORD: job required")
    raise SystemExit(1)

job = Path(sys.argv[1])
stage = Path.home()/"corvus-dev/staging/corvus"
out = Path.home()/"corvus-dev/changes/current-promotion"

if not job.is_file():
    print("PROMOTION RECORD: BLOCKED - job missing")
    raise SystemExit(2)

commit = subprocess.check_output(
    ["git", "-C", str(stage), "rev-parse", "HEAD"],
    text=True
).strip()

hashfile = Path.home()/"corvus-dev/changes/current-candidate.sha256"

if not hashfile.is_file():
    print("PROMOTION RECORD: BLOCKED - candidate hash missing")
    raise SystemExit(25)

candidate = hashfile.read_text().strip()

out.write_text(
    f"JOB: {job.name}\n"
    f"BASELINE: {commit}\n" f"CANDIDATE_SHA256: {candidate}\n"
)

print("PROMOTION RECORD: PASS")
