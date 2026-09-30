#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

stage = Path.home()/"corvus-dev/staging/corvus"

from git_changes import changed_paths
from repo_fingerprint import fingerprint_paths

files = changed_paths(stage)

if not files:
    print("CANDIDATE HASH: BLOCKED - no candidate")
    raise SystemExit(27)

print(fingerprint_paths(stage, files))
