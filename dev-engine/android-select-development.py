#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import os
import re
import subprocess
import sys

HOME = Path.home()
DEV = HOME / "corvus-dev"
STAGE = DEV / "staging/android/corvus"
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
    print("ANDROID SELECTOR: BLOCKED - objective required")
    raise SystemExit(60)

objective = " ".join(sys.argv[1:]).strip()

manifest = (STAGE / "AndroidManifest.xml").read_text()
bridge = (STAGE / "src/com/corvus/app/CorvusBridge.java").read_text()
service = (STAGE / "src/com/corvus/app/CorvusEngineService.java").read_text()

summary = f"""
CURRENT ANDROID APP MAP

Package: com.corvus.app
Version: 0.5
Version code: 15

Architecture:
- MainActivity.java: owns the WebView, installs CorvusBridge as a JavaScript interface, starts CorvusEngineService, sends prompts to the local CORVUS API at /ask, and returns results to the WebView with evaluateJavascript.
- CorvusBridge.java: exposes ask(prompt) to JavaScript. It forwards the prompt directly to MainActivity.performAsk(prompt).
- CorvusEngineService.java: currently only starts as a sticky Android Service and logs startup. It has no WebView messaging, API communication, broadcast receiver, binder, or other message path.
- assets/index.html: chat interface. sendMessage() calls CorvusBridge.ask(prompt).
- assets/style.css: presentation only.
- Existing message path: index.html -> CorvusBridge.ask(prompt) -> MainActivity.performAsk(prompt) -> local CORVUS API /ask -> MainActivity -> WebView evaluateJavascript.
- There is currently no direct communication path between the WebView and CorvusEngineService.
- strings.xml and styles.xml: Android resources.
- AndroidManifest.xml: package, version, permissions, activity and service declaration.

Current manifest:
{manifest}

Current bridge:
{bridge}

Current service:
{service}
"""

prompt = f"""
You are CORVUS choosing the next bounded development step for your Android application.

USER OBJECTIVE:
{objective}

{summary}

Choose ONE useful capability for version 0.6.

Constraints:
- The change must be realistic for this existing architecture.
- It must be implementable using only the authorized files below.
- Prefer a meaningful functional improvement over cosmetic changes.
- Keep scope small enough for local compilation and testing.
- Do not write implementation code yet.
- Do not claim the capability is already implemented.
- Select no more than 3 implementation files, plus AndroidManifest.xml.
- AndroidManifest.xml is mandatory for the version bump.
- Do not request new files.
- Do not request signing files.
- Do not request shell access.

AUTHORIZED FILES:
""" + "\n".join(f"- {x}" for x in ALLOWED) + """

Before choosing, perform an internal feasibility check.

A valid capability MUST satisfy all of these:
- The selected files must actually be capable of implementing the capability.
- UI-only files cannot implement native Android platform behavior by themselves.
- Native Android behavior normally requires an appropriate Java source file.
- Do not assume Firebase, Google Play Services, third-party SDKs, remote servers, new libraries, or unavailable infrastructure.
- Do not choose a capability that requires files outside AUTHORIZED FILES.
- Prefer functionality that can be implemented completely with the existing local architecture.
- If your first idea fails these rules, reject it internally and choose another.
- Do not include the internal rejected ideas in your answer.
- IMPLEMENTATION must name the concrete mechanism and the file responsible for it.
- Do not use vague explanations such as "use an authorized path", "add support", or "implement functionality".
- HTML and CSS may provide interface behavior and presentation, but they do not by themselves provide native Android security, authentication, notifications, services, storage, or operating-system integration.
- A capability involving native Android behavior must select the appropriate Java source file.
- A security or authentication capability must identify a real existing mechanism available in the supplied architecture. If none exists, choose a different capability.
- Do not invent backend services, authentication providers, credentials, APIs, databases, SDKs, or infrastructure that are not present in the supplied architecture.

Return exactly:

<CHOICE>
CAPABILITY: one concise capability
REASON: one concise reason
IMPLEMENTATION: one concise sentence explaining how the selected files implement it
FILES:
AndroidManifest.xml
authorized/path
authorized/path
</CHOICE>

No text outside CHOICE.
"""

env = dict(os.environ)
env["CORVUS_MAX_TOKENS"] = "256"

result = subprocess.run(
    [str(INFER), prompt],
    capture_output=True,
    text=True,
    env=env,
)

raw = DEV / "changes/android-selection-raw.txt"
raw.parent.mkdir(parents=True, exist_ok=True)
raw.write_text(result.stdout)

if result.returncode != 0:
    print("ANDROID SELECTOR: FAILED - inference")
    raise SystemExit(61)

match = re.search(
    r"<CHOICE>\s*(.*?)\s*</CHOICE>",
    result.stdout,
    re.DOTALL,
)

if not match:
    print("ANDROID SELECTOR: FAILED - CHOICE markers missing")
    print("RAW:", raw)
    raise SystemExit(62)

choice = match.group(1).strip()

cap = re.search(r"^CAPABILITY:\s*(.+)$", choice, re.MULTILINE)
reason = re.search(r"^REASON:\s*(.+)$", choice, re.MULTILINE)
implementation = re.search(r"^IMPLEMENTATION:\s*(.+)$", choice, re.MULTILINE)
files_block = re.search(
    r"^FILES:\s*\n(.*)$",
    choice,
    re.MULTILINE | re.DOTALL,
)

if not cap or not reason or not implementation or not files_block:
    print("ANDROID SELECTOR: BLOCKED - malformed choice")
    raise SystemExit(63)

files = [
    line.strip()
    for line in files_block.group(1).splitlines()
    if line.strip()
]

if not files:
    print("ANDROID SELECTOR: BLOCKED - no files selected")
    raise SystemExit(64)

if "AndroidManifest.xml" not in files:
    print("ANDROID SELECTOR: BLOCKED - manifest required")
    raise SystemExit(65)

if len(files) > 4:
    print("ANDROID SELECTOR: BLOCKED - too many files")
    raise SystemExit(66)

if len(files) != len(set(files)):
    print("ANDROID SELECTOR: BLOCKED - duplicate files")
    raise SystemExit(67)

for path in files:
    if path not in ALLOWED:
        print("ANDROID SELECTOR: BLOCKED - unauthorized file:", path)
        raise SystemExit(68)

selection = DEV / "changes/android-selection.txt"

selection.write_text(
    f"CAPABILITY: {cap.group(1).strip()}\n"
    f"REASON: {reason.group(1).strip()}\n"
    f"IMPLEMENTATION: {implementation.group(1).strip()}\n"
    "FILES:\n"
    + "\n".join(files)
    + "\n"
)

print("ANDROID SELECTOR: PASS")
print(selection.read_text(), end="")
