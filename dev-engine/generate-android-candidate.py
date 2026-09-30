#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import os
import re
import subprocess
import sys

HOME = Path.home()
DEV = HOME / "corvus-dev"
STAGE = (DEV / "staging/android/corvus").resolve()
INFER = HOME / "corvus/bin/infer"

ALLOWED = (
    "AndroidManifest.xml",
    "assets/index.html",
    "assets/style.css",
    "res/values/strings.xml",
    "res/values/styles.xml",
    "src/com/corvus/app/CorvusBridge.java",
    "src/com/corvus/app/CorvusEngineService.java",
    "src/com/corvus/app/MainActivity.java",
)

if len(sys.argv) < 2:
    print("ANDROID GENERATOR: BLOCKED - objective required")
    raise SystemExit(230)

objective = " ".join(sys.argv[1:]).strip()

if not objective:
    print("ANDROID GENERATOR: BLOCKED - objective required")
    raise SystemExit(230)

if not STAGE.is_dir():
    print("ANDROID GENERATOR: BLOCKED - staging missing")
    raise SystemExit(231)

sources = []

for relative in ALLOWED:
    path = (STAGE / relative).resolve()

    try:
        path.relative_to(STAGE)
    except ValueError:
        print("ANDROID GENERATOR: BLOCKED - path escape")
        raise SystemExit(232)

    if not path.is_file():
        print("ANDROID GENERATOR: BLOCKED - source missing:", relative)
        raise SystemExit(233)

    sources.append(
        f"<CURRENT_FILE path=\"{relative}\">\n"
        f"{path.read_text()}\n"
        f"</CURRENT_FILE>"
    )

contract = f"""
You are CORVUS performing a bounded Android development task.

OBJECTIVE:
{objective}

CURRENT VERSION:
0.5

REQUIRED DEVELOPMENT RULES:
- Inspect the supplied Android source.
- Choose one useful, realistic next capability that advances the objective.
- Produce Android version 0.6.
- android:versionName must become 0.6.
- android:versionCode must become 16.
- Work only with the authorized files supplied below.
- Do not create additional files.
- Do not modify package identity com.corvus.app.
- Do not modify signing configuration or keystores.
- Do not use root.
- Do not assume systemd, sudo, Gradle, Android Studio, or network access.
- Preserve the existing local CORVUS architecture unless the chosen change requires a bounded modification.
- Keep the implementation small enough to compile on this device.
- Do not output shell commands.
- Do not output patches or diffs.
- Return complete replacement contents only for files you actually change.
- AndroidManifest.xml MUST be returned because the version must change.
- Do not claim anything was built or tested. External trusted tooling performs those steps.

OUTPUT FORMAT IS STRICT.

For every changed file return exactly:

<FILE path="AUTHORIZED_PATH">
complete replacement file
</FILE>

After all files return:

<REPORT>
SUMMARY: concise description
CAPABILITY: capability implemented
FILES_CHANGED: comma-separated paths
</REPORT>

No text outside FILE and REPORT blocks.

AUTHORIZED PATHS:
""" + "\n".join(f"- {x}" for x in ALLOWED)

prompt = (
    contract
    + "\n\nCURRENT ANDROID SOURCE:\n\n"
    + "\n\n".join(sources)
)

env = dict(os.environ)
env["CORVUS_MAX_TOKENS"] = "4096"

result = subprocess.run(
    [str(INFER), prompt],
    capture_output=True,
    text=True,
    env=env,
)

raw = DEV / "changes/android-last-raw-output.txt"
raw.parent.mkdir(parents=True, exist_ok=True)
raw.write_text(result.stdout)

if result.returncode != 0:
    print("ANDROID GENERATOR: FAILED - inference")
    print("RAW OUTPUT:", raw)
    raise SystemExit(234)

pattern = re.compile(
    r'<FILE path="([^"]+)">\s*(.*?)\s*</FILE>',
    re.DOTALL,
)

matches = pattern.findall(result.stdout)

if not matches:
    print("ANDROID GENERATOR: FAILED - FILE markers missing")
    print("RAW OUTPUT:", raw)
    raise SystemExit(235)

seen = set()
proposals = {}

for relative, content in matches:
    if relative not in ALLOWED:
        print("ANDROID GENERATOR: BLOCKED - unauthorized file:", relative)
        raise SystemExit(236)

    if relative in seen:
        print("ANDROID GENERATOR: BLOCKED - duplicate file:", relative)
        raise SystemExit(237)

    seen.add(relative)

    if not content.strip():
        print("ANDROID GENERATOR: BLOCKED - empty file:", relative)
        raise SystemExit(238)

    proposals[relative] = content.rstrip() + "\n"

if "AndroidManifest.xml" not in proposals:
    print("ANDROID GENERATOR: BLOCKED - manifest not returned")
    raise SystemExit(239)

manifest = proposals["AndroidManifest.xml"]

if 'package="com.corvus.app"' not in manifest:
    print("ANDROID GENERATOR: BLOCKED - package identity changed")
    raise SystemExit(240)

if 'android:versionName="0.6"' not in manifest:
    print("ANDROID GENERATOR: BLOCKED - versionName must be 0.6")
    raise SystemExit(241)

if 'android:versionCode="16"' not in manifest:
    print("ANDROID GENERATOR: BLOCKED - versionCode must be 16")
    raise SystemExit(242)

report_match = re.search(
    r"<REPORT>\s*(.*?)\s*</REPORT>",
    result.stdout,
    re.DOTALL,
)

if not report_match:
    print("ANDROID GENERATOR: BLOCKED - report missing")
    raise SystemExit(243)

# All validation happens before any staged file is changed.
for relative, content in proposals.items():
    destination = (STAGE / relative).resolve()

    try:
        destination.relative_to(STAGE)
    except ValueError:
        print("ANDROID GENERATOR: BLOCKED - destination escape")
        raise SystemExit(244)

    destination.write_text(content)

report = DEV / "changes/android-current-report.txt"
report.write_text(report_match.group(1).strip() + "\n")

print("ANDROID GENERATOR: CORVUS GENERATED")
print("FILES CHANGED:", len(proposals))

for relative in proposals:
    print("CHANGED:", relative)

print("REPORT:", report)
