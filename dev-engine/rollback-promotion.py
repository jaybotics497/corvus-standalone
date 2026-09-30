#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil
import sys

from git_changes import changed_paths
from path_safety import safe_repo_path

home = Path.home()
dev = home / "corvus-dev"
stage = dev / "staging/corvus"
live = home / "corvus"
backup = dev / "tmp/promotion-backup"
record = dev / "changes/current-promotion"

if not record.is_file():
    print("ROLLBACK: BLOCKED - promotion record missing")
    raise SystemExit(40)

if not backup.is_dir():
    print("ROLLBACK: BLOCKED - promotion backup missing")
    raise SystemExit(41)

changed = changed_paths(stage)

if not changed:
    print("ROLLBACK: BLOCKED - no promoted changes")
    raise SystemExit(42)

for name in changed:
    dst = safe_repo_path(live, name)
    saved = safe_repo_path(backup, name)

    if saved.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(saved, dst)
    elif dst.exists():
        if dst.is_dir():
            print(f"ROLLBACK: BLOCKED - unexpected directory: {name}")
            raise SystemExit(43)
        dst.unlink()

shutil.rmtree(backup)
record.unlink(missing_ok=True)

print("ROLLBACK: PASS")
for name in changed:
    print("RESTORED:", name)
