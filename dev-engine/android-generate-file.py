#!/data/data/com.termux/files/usr/bin/python
import os
import subprocess
import sys
from pathlib import Path

DEV = Path.home() / "corvus-dev"
STAGE = DEV / "staging/android/corvus"
INFER = Path.home() / "corvus/bin/infer"
RAW = DEV / "changes/android-file-generation-raw.txt"

ALLOWED = {
    "assets/index.html",
    "assets/style.css",
    "src/com/corvus/app/CorvusBridge.java",
    "src/com/corvus/app/CorvusEngineService.java",
    "src/com/corvus/app/MainActivity.java",
}

if len(sys.argv) < 3:
    print("ANDROID GENERATOR: BLOCKED - file and objective required")
    raise SystemExit(80)

relative = sys.argv[1]
objective = " ".join(sys.argv[2:]).strip()

if relative not in ALLOWED:
    print("ANDROID GENERATOR: BLOCKED - unauthorized file")
    raise SystemExit(81)

target = STAGE / relative

if not target.is_file():
    print("ANDROID GENERATOR: BLOCKED - target missing")
    raise SystemExit(82)

source = target.read_text()

prompt = f"""
You are modifying one authorized source file in CORVUS Android.

OBJECTIVE:
{objective}

AUTHORIZED FILE:
{relative}

CURRENT FILE:
<FILE>
{source}
</FILE>

RULES:
- Modify only this file.
- Return the complete replacement file.
- Preserve existing working behavior unless the objective requires changing it.
- Do not invent external services, SDKs, libraries, credentials, databases, or APIs.
- Do not output shell commands.
- Do not output explanations.
- Do not output markdown fences.
- Output exactly:

<FILE>
complete replacement contents
</FILE>
"""

env = os.environ.copy()
env["CORVUS_MAX_TOKENS"] = "1536"

result = subprocess.run(
    [str(INFER), prompt],
    text=True,
    capture_output=True,
    env=env,
)

RAW.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(result.stdout)

if result.returncode != 0:
    print("ANDROID GENERATOR: BLOCKED - inference failed")
    raise SystemExit(83)

out = result.stdout.strip()

if not out.startswith("<FILE>") or not out.endswith("</FILE>"):
    print("ANDROID GENERATOR: BLOCKED - invalid output")
    raise SystemExit(84)

replacement = out[len("<FILE>"):-len("</FILE>")].strip() + "\n"

if not replacement.strip():
    print("ANDROID GENERATOR: BLOCKED - empty replacement")
    raise SystemExit(85)

# Required compatibility invariants.
if relative == "src/com/corvus/app/CorvusBridge.java":
    required = [
        "public void ask(String prompt)",
        "activity.performAsk(prompt)",
    ]
    for marker in required:
        if marker not in replacement:
            print("ANDROID GENERATOR: BLOCKED - existing bridge behavior removed")
            raise SystemExit(86)

target.write_text(replacement)

print("ANDROID GENERATOR: PASS")
print("FILE:", relative)
