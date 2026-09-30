#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import sys

if len(sys.argv) != 3:
    print("USAGE: generate-new-candidate.py JOB TARGET")
    raise SystemExit(1)

home = Path.home()
dev = home / "corvus-dev"
stage = dev / "staging/corvus"

job = Path(sys.argv[1])
target = sys.argv[2]

if target != "bin/dev-evidence.py":
    print("NEW CANDIDATE: BLOCKED - unsupported target")
    raise SystemExit(2)

contract = """
Implement Evidence Bridge V1 as a COMPLETE executable Python program.

FUNCTION:
Given 1-6 explicit file paths, return bounded read-only textual evidence.

REQUIRED:
MAX_FILES = 6
MAX_FILE_BYTES = 30000
MAX_TOTAL_BYTES = 90000

ALLOW ONLY:
- regular readable UTF-8 text files
- canonical paths contained under ~/corvus or ~/corvus-dev

REJECT BEFORE CONTENT READ:
- symlinks or path escape
- ~/corvus/api/token
- credentials, tokens, private keys, keystores, .env
- model/database/APK/DEX/CLASS/pyc files
- .git, backups, generated/build artifacts
- directories, binaries, NUL content, oversized files

FORBIDDEN:
- recursion or directory discovery
- shell/subprocess/arbitrary execution
- writes to inspected files
- executing inspected source

OUTPUT DATA:
Accepted item: canonical_path, size_bytes, textual_content
Rejected item: requested_path, status, reason

IMPORTANT:
Write actual implementation code, not specification comments.
All three constants must be executable assignments.
Program must process the requested paths.
Use strict UTF-8.
Safety checks occur before reading content.

Return ONLY:
<CODE>
#!/usr/bin/env python3
[complete executable implementation]
</CODE>
No Markdown fences. No explanation.
"""

prompt = f"""{contract}

DEVELOPMENT JOB:
{job.read_text()}

AUTHORIZED NEW TARGET:
{target}
"""

env = dict(__import__("os").environ)
env["CORVUS_MAX_TOKENS"] = "2048"

result = subprocess.run(
    [str(home / "corvus/bin/infer"), prompt],
    capture_output=True,
    text=True,
    env=env,
)

raw = dev / "changes/last-new-candidate-raw.txt"
raw.parent.mkdir(parents=True, exist_ok=True)
raw.write_text(result.stdout)

matches = re.findall(r"<CODE>\s*(.*?)\s*</CODE>", result.stdout, re.DOTALL)

if matches:
    candidate = matches[-1].strip() + "\n"
else:
    fenced = re.findall(
        r"```(?:python)?\s*\n(.*?)\n```",
        result.stdout,
        re.DOTALL |
 re.IGNORECASE,
    )

    if len(fenced) != 1:
        print("NEW CANDIDATE: FAILED - no unambiguous code block")
        print(f"RAW OUTPUT: {raw}")
        raise SystemExit(3)

    candidate = fenced[0].strip() + "\n"
    print("NEW CANDIDATE: USING FENCED FALLBACK")

if not candidate.startswith("#!/usr/bin/env python3"):
    print("NEW CANDIDATE: FAILED - invalid Python candidate")
    raise SystemExit(4)

destination = stage / target
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(candidate)
destination.chmod(0o700)

print("NEW CANDIDATE: CORVUS GENERATED")
print(f"TARGET: {target}")
print(f"BYTES: {len(candidate.encode('utf-8'))}")
print("NEW CANDIDATE: STAGED")
