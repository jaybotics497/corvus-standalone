#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

if len(sys.argv) != 4:
    print("USAGE: build-candidate.py JOB TARGET TEMPLATE")
    raise SystemExit(1)

job = Path(sys.argv[1])
target = sys.argv[2]
template = Path(sys.argv[3])

stage = Path.home()/"corvus-dev/staging/corvus"

allowed = []
for line in job.read_text().splitlines():
    if line.startswith("FILES_ALLOWED:"):
        allowed = [
            x.strip()
            for x in line.split(":",1)[1].split(",")
            if x.strip()
        ]

if target not in allowed:
    print("BUILDER: BLOCKED - target not authorized")
    raise SystemExit(40)

root = stage.resolve()
dest = (stage/target).resolve()

if root not in dest.parents:
    print("BUILDER: BLOCKED - unsafe target path")
    raise SystemExit(41)

if not template.is_file():
    print("BUILDER: BLOCKED - template missing")
    raise SystemExit(42)

dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_bytes(template.read_bytes())
dest.chmod(template.stat().st_mode & 0o777)

print("BUILDER: PASS")
print("BUILT:", target)
