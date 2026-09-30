#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import sys

home = Path.home()
dev = home / "corvus-dev"
stage = dev / "staging/corvus"
target = stage / "bin/dev-evidence.py"
plan = dev / "plans/current-plan.txt"

MAX_REPAIRS = 3

def run(args, **kwargs):
    return subprocess.run(args, text=True, **kwargs)

def validate(candidate, output):
    result = run(
        [str(dev / "validate-dev-evidence.py"), str(candidate)],
        capture_output=True,
    )
    text = (result.stdout or "") + (result.stderr or "")
    output.write_text(text, encoding="utf-8")
    return result.returncode, text

if not plan.is_file():
    print("EVIDENCE OPERATION: BLOCKED - plan missing")
    raise SystemExit(170)

job_candidates = sorted(
    dev.glob("jobs/*.txt"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)

job = None
for candidate in job_candidates:
    text = candidate.read_text(encoding="utf-8")
    if (
        "FILES_ALLOWED: bin/dev-evidence.py" in text
        and "STATUS: retired" not in text
    ):
        job = candidate
        break

if job is None:
    print("EVIDENCE OPERATION: BLOCKED - active evidence job missing")
    raise SystemExit(171)

print("EVIDENCE OPERATION: GENERATE")

result = run(
    [
        str(dev / "generate-new-candidate.py"),
        str(job),
        "bin/dev-evidence.py",
    ]
)

if result.returncode != 0:
    print("EVIDENCE OPERATION: FAILED - generation")
    raise SystemExit(result.returncode)

validation = dev / "changes/evidence-bridge.validation.txt"
code, details = validate(target, validation)

if code == 0:
    print(details, end="")
    print("EVIDENCE OPERATION: PASS")
    raise SystemExit(0)

for attempt in range(1, MAX_REPAIRS + 1):
    print(f"EVIDENCE OPERATION: REPAIR {attempt}/{MAX_REPAIRS}")

    repaired = dev / f"changes/evidence-bridge-repair-{attempt}.py"

    result = run(
        [
            str(dev / "repair-new-candidate.py"),
            str(target),
            str(validation),
            str(repaired),
        ]
    )

    if result.returncode != 0:
        print("EVIDENCE OPERATION: FAILED - repair generation")
        raise SystemExit(result.returncode)

    shutil.copy2(repaired, target)
    target.chmod(0o700)

    code, details = validate(target, validation)

    if code == 0:
        print(details, end="")
        print("EVIDENCE OPERATION: PASS")
        raise SystemExit(0)

print(details, end="")
print("EVIDENCE OPERATION: FAILED - repair limit reached")
raise SystemExit(172)
