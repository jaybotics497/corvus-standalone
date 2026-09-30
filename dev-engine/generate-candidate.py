#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,sys

if len(sys.argv)!=4:
 print("USAGE: generate-candidate.py JOB TARGET OUTPUT")
 raise SystemExit(1)

job=Path(sys.argv[1])
target=sys.argv[2]
output=Path(sys.argv[3])

stage=Path.home()/"corvus-dev/staging/corvus"
editor=(Path.home()/"corvus-dev/editor-prompt.txt").read_text()

source=(stage/target).read_text()
objective=job.read_text()

prompt=f"""{editor}

JOB:
{objective}

AUTHORIZED FILE:
{target}

CURRENT FILE:
{source}
"""

result=subprocess.run(
 [str(Path.home()/"corvus/bin/infer"),prompt],
 capture_output=True,text=True
)

matches=re.findall(r"(#!/data/data/com\.termux/files/usr/bin/bash.*)",result.stdout,re.DOTALL)

if not matches:
 print("CANDIDATE: FAILED")
 raise SystemExit(2)

output.write_text(matches[-1]+"\n")
print("CANDIDATE: GENERATED")
print("TARGET:",target)
