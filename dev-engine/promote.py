#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,shutil

if len(sys.argv)!=2:
 print("USAGE: promote.py JOB")
 raise SystemExit(1)

job=Path(sys.argv[1])
home=Path.home()
stage=home/"corvus-dev/staging/corvus"
live=home/"corvus"

def run_check(args):
 result=subprocess.run(args)
 if result.returncode:
  raise SystemExit(result.returncode)

run_check([str(home/"corvus-dev/check-approval.py"),str(job)])
run_check([str(home/"corvus-dev/check-permissions.py"),str(job)])
run_check([str(home/"corvus-dev/check-candidate-hash.sh")])
run_check([str(home/"corvus-dev/check-candidate-approval.py"),str(job)])
run_check([str(home/"corvus-dev/validate.sh")])

allowed=[]
for line in job.read_text().splitlines():
 if line.startswith("FILES_ALLOWED:"):
  allowed=[x.strip() for x in line.split(":",1)[1].split(",") if x.strip()]

from git_changes import changed_paths
from path_safety import safe_repo_path

changed = changed_paths(stage)

if not changed:
 print("PROMOTION: BLOCKED - no changes")
 raise SystemExit(8)

for name in changed:
 if name not in allowed:
  print("PROMOTION: BLOCKED - unauthorized file")
  raise SystemExit(9)

backup=home/"corvus-dev/tmp/promotion-backup"

if backup.exists():
 shutil.rmtree(backup)

backup.mkdir(parents=True)

for name in changed:
 src=safe_repo_path(live, name)
 if src.exists():
  dst=safe_repo_path(backup, name)
  dst.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(src,dst)

try:
 for name in changed:
  src=safe_repo_path(stage, name)
  dst=safe_repo_path(live, name)

  if src.is_file():
   dst.parent.mkdir(parents=True,exist_ok=True)
   shutil.copy2(src,dst)
  elif not src.exists():
   if dst.is_file():
    dst.unlink()
   elif dst.exists():
    raise RuntimeError(f"cannot delete non-file: {name}")
  else:
   raise RuntimeError(f"candidate is not a regular file: {name}")

 result=subprocess.run([
  str(home/"corvus-dev/verify-live-fingerprint.py")
 ])

 if result.returncode:
  raise RuntimeError(result.returncode)

 result=subprocess.run([
  str(home/"corvus-dev/record-promotion.py"),
  str(job)
 ])

 if result.returncode:
  raise RuntimeError(result.returncode)

except Exception as e:
 for name in changed:
  dst=safe_repo_path(live, name)
  saved=safe_repo_path(backup, name)

  if saved.exists():
   dst.parent.mkdir(parents=True,exist_ok=True)
   shutil.copy2(saved,dst)
  elif dst.exists():
   dst.unlink()

 print("PROMOTION: ROLLED BACK")
 code=e.args[0] if e.args and isinstance(e.args[0],int) else 30
 raise SystemExit(code)

print("PROMOTION BACKUP: PRESERVED")

print("PROMOTION RECORD: VERIFIED")
print("PROMOTION: PASS")

for name in changed:
 print("PROMOTED:",name)
