#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

from git_changes import changed_paths
from repo_fingerprint import fingerprint_paths

stage = Path.home()/"corvus-dev/staging/corvus"
live = Path.home()/"corvus"
hashfile = Path.home()/"corvus-dev/changes/current-candidate.sha256"

if not hashfile.is_file():
    print("LIVE FINGERPRINT: BLOCKED - candidate hash missing")
    raise SystemExit(30)

files = changed_paths(stage)

if not files:
    print("LIVE FINGERPRINT: BLOCKED - no candidate")
    raise SystemExit(31)

expected = hashfile.read_text().strip()
actual = fingerprint_paths(live, files)

if actual != expected:
    print("LIVE FINGERPRINT: BLOCKED - live content differs from approved candidate")
    raise SystemExit(32)

print("LIVE FINGERPRINT: PASS")
