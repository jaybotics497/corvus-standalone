#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys

if len(sys.argv) != 4:
    print("USAGE: generate-operation.py JOB TARGET OUTPUT")
    raise SystemExit(1)

job = Path(sys.argv[1])
target = sys.argv[2]
output = Path(sys.argv[3])
stage = Path.home()/"corvus-dev/staging/corvus"

source = (stage/target).read_text()
prompt = (Path.home()/"corvus-dev/edit-operation-prompt.txt").read_text()

anchor = 'case "$1" in'

if target != "bin/corvus" or source.count(anchor) != 1:
    print("OPERATION GENERATION: BLOCKED - unsupported target/anchor")
    raise SystemExit(2)

full = f"""{prompt}

JOB:
{job.read_text()}

AUTHORIZED FILE:
{target}

CURRENT FILE:
{source}
"""

r = subprocess.run(
    [str(Path.home()/"corvus/bin/infer"), full],
    capture_output=True,
    text=True
)

import re

matches = re.findall(r"<CODE>\\s*(.*?)\\s*</CODE>", r.stdout, re.DOTALL)

if not matches:
    raw = Path.home()/"corvus-dev/changes/last-raw-output.txt"
    raw.write_text(r.stdout)
    print("OPERATION GENERATION: FAILED - CODE markers missing")
    print(f"RAW OUTPUT: {raw}")
    raise SystemExit(3)

candidate = matches[-1].strip()

if not candidate:
    print("OPERATION GENERATION: FAILED - empty proposal")
    raise SystemExit(4)

operation = f"""ANCHOR: {anchor}
INSERT_AFTER:
{candidate}
END_EDIT
"""

output.write_text(operation)
print("OPERATION GENERATION: PASS")
