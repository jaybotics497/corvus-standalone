#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil
import subprocess

home = Path.home()
dev = home / "corvus-dev"
live = home / "corvus"
record = dev / "changes/current-promotion"
backup = dev / "tmp/promotion-backup"

if not record.is_file():
    print("GIT ROLLBACK: BLOCKED - promotion record missing")
    raise SystemExit(44)

data = {}
for line in record.read_text().splitlines():
    if ":" in line:
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()

baseline = data.get("BASELINE", "")

if not baseline:
    print("GIT ROLLBACK: BLOCKED - baseline missing")
    raise SystemExit(45)

check = subprocess.run(
    ["git", "-C", str(live), "cat-file", "-e", f"{baseline}^{{commit}}"]
)

if check.returncode:
    print("GIT ROLLBACK: BLOCKED - baseline commit invalid")
    raise SystemExit(46)

subprocess.run(
    ["git", "-C", str(live), "reset", "--hard", baseline],
    check=True
)

if backup.exists():
    shutil.rmtree(backup)

record.unlink(missing_ok=True)

print("GIT ROLLBACK: PASS")
print("RESTORED BASELINE:", baseline)
