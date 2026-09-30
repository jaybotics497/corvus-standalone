#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import subprocess, sys

if len(sys.argv) != 2:
    print("USAGE: commit-promotion.py JOB")
    raise SystemExit(1)

home = Path.home()
dev = home/"corvus-dev"
live = home/"corvus"
job = Path(sys.argv[1])

subprocess.run([str(dev/"check-promotion.py"), str(job)], check=True)
subprocess.run([str(dev/"validate-live.sh")], check=True)

allowed = []
objective = ""

for line in job.read_text().splitlines():
    if line.startswith("FILES_ALLOWED:"):
        allowed = [x.strip() for x in line.split(":",1)[1].split(",") if x.strip()]
    elif line.startswith("OBJECTIVE:"):
        objective = line.split(":",1)[1].strip()

from git_changes import changed_paths

changed = changed_paths(live)

if not changed:
    print("COMMIT: BLOCKED - no live changes")
    raise SystemExit(32)

blocked = [name for name in changed if name not in allowed]

if blocked:
    print("COMMIT: BLOCKED - unauthorized live changes")
    print("UNAUTHORIZED:", ",".join(blocked))
    raise SystemExit(33)

for name in changed:
    subprocess.run(
        ["git","-C",str(live),"add","--",name],
        check=True
    )

message = objective or "CORVUS controlled promotion"

subprocess.run(
    ["git","-C",str(live),"commit","-m",message],
    check=True
)

print("COMMIT: PASS")
print("LIVE COMMIT:", subprocess.check_output(
    ["git","-C",str(live),"rev-parse","HEAD"],
    text=True
).strip())
