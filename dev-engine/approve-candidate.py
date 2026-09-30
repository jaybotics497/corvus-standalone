#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("APPROVE: job required")
    raise SystemExit(1)

job = Path(sys.argv[1])
base = Path.home()/"corvus-dev/changes"
hashfile = base/"current-candidate.sha256"
approval = base/"current-approval"

if not job.is_file():
    print("APPROVE: BLOCKED - job missing")
    raise SystemExit(2)

if not hashfile.is_file():
    print("APPROVE: BLOCKED - candidate hash missing")
    raise SystemExit(28)

candidate = hashfile.read_text().strip()

approval.write_text(
    f"JOB: {job.name}\n"
    f"CANDIDATE_SHA256: {candidate}\n"
    f"STATUS: approved\n"
)

print("CANDIDATE APPROVAL: RECORDED")
