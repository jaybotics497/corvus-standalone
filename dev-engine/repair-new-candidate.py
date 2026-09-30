#!/usr/bin/env python3
from pathlib import Path
import os, re, subprocess, sys

if len(sys.argv) != 4:
    print("USAGE: repair-new-candidate.py CANDIDATE VALIDATION OUTPUT")
    raise SystemExit(1)

home = Path.home()
candidate_file = Path(sys.argv[1])
validation_file = Path(sys.argv[2])
output_file = Path(sys.argv[3])

if not candidate_file.is_file() or not validation_file.is_file():
    print("REPAIR: BLOCKED - input missing")
    raise SystemExit(2)

candidate = candidate_file.read_text(encoding="utf-8")
validation = validation_file.read_text(encoding="utf-8")

prompt = f"""Repair this Python program. Return a COMPLETE replacement program, not explanations.

VALIDATOR FAILURES:
{validation}

CURRENT PROGRAM:
{candidate}

MANDATORY IMPLEMENTATION:

Constants:
MAX_FILES = 6
MAX_FILE_BYTES = 30000
MAX_TOTAL_BYTES = 90000

Input:
- use sys.argv[1:] as the requested paths
- reject requests above MAX_FILES
- never use hard-coded example paths

Allowed roots:
- Path.home() / "corvus"
- Path.home() / "corvus-dev"
- canonicalize using Path.resolve()
- after resolution verify containment using Path.relative_to() or equivalent

Before reading content reject:
- any symlink using is_symlink()
- path escape outside both allowed roots
- exact Path.home() / "corvus/api/token"
- secret/credential/token/private-key/keystore/.env paths
- .git, backup, generated or build artifacts
- model/database/APK/DEX/CLASS/pyc files
- non-files and unreadable files
- files larger than MAX_FILE_BYTES

Content:
- read bytes only after path safety checks
- reject b"\\x00" before decoding
- decode with data.decode("utf-8", errors="strict")
- enforce MAX_TOTAL_BYTES across accepted files

Output:
For every accepted request include literal keys:
canonical_path
size_bytes
textual_content

For every rejected request include literal keys:
requested_path
status
reason

Security:
- read-only
- no recursion or directory discovery
- no subprocess
- no shell
- no eval/exec
- never execute inspected source
- never modify inspected files

IMPORTANT:
Implement every requirement in executable Python code.
Do not merely describe a fix in prose or comments.
Do not claim a check exists unless the code actually performs it.
Include required imports such as sys when used.

Return ONLY:
<CODE>
#!/usr/bin/env python3
[complete replacement program]
</CODE>
"""
env = dict(os.environ)
env["CORVUS_MAX_TOKENS"] = "2048"
result = subprocess.run(
    [str(home / "corvus/bin/infer"), prompt],
    capture_output=True, text=True, env=env
)
raw = output_file.with_suffix(".raw.txt")
raw.write_text(result.stdout, encoding="utf-8")
matches = re.findall(r"<CODE>\s*(.*?)\s*</CODE>", result.stdout, re.DOTALL)
if not matches:
    matches = re.findall(r"```python\s*(.*?)\s*```", result.stdout, re.DOTALL)
if not matches:
    print("REPAIR: FAILED - code block missing")
    print(f"RAW OUTPUT: {raw}")
    raise SystemExit(3)
repaired = matches[-1].strip() + "\n"
if not repaired.startswith("#!/usr/bin/env python3"):
    print("REPAIR: FAILED - script header")
    raise SystemExit(4)
output_file.write_text(repaired, encoding="utf-8")
output_file.chmod(0o700)
print("REPAIR: CORVUS GENERATED")
print(f"OUTPUT: {output_file}")
