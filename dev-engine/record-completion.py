#!/data/data/com.termux/files/usr/bin/python
import subprocess, sys
from pathlib import Path

if len(sys.argv) != 2:
    print("COMPLETION: job required")
    raise SystemExit(1)

job = Path(sys.argv[1])

if not job.is_file():
    print("COMPLETION: BLOCKED - job missing")
    raise SystemExit(2)

text = job.read_text()

if "STATUS: completed" not in text:
    print("COMPLETION: BLOCKED - job not completed")
    raise SystemExit(21)

commit = subprocess.check_output(
    ["git", "-C", str(Path.home()/"corvus"), "rev-parse", "HEAD"],
    text=True
).strip()

lines = [x for x in text.splitlines()
         if not x.startswith("LIVE_COMMIT:")]

lines.append(f"LIVE_COMMIT: {commit}")
job.write_text("\n".join(lines) + "\n")

print(f"COMPLETION RECORDED: {commit}")
