#!/usr/bin/env python3
from pathlib import Path
import ast
import sys

if len(sys.argv) != 2:
    print("USAGE: validate-dev-evidence.py FILE")
    raise SystemExit(1)

p = Path(sys.argv[1])

if not p.is_file():
    print("DEV EVIDENCE VALIDATION: FAIL - candidate missing")
    raise SystemExit(2)

try:
    text = p.read_text(encoding="utf-8")
    tree = ast.parse(text)
except Exception as e:
    print(f"DEV EVIDENCE VALIDATION: FAIL - invalid Python: {e}")
    raise SystemExit(3)

failures = []

# Immutable numeric limits.
required_constants = {
    "MAX_FILES": 6,
    "MAX_FILE_BYTES": 30000,
    "MAX_TOTAL_BYTES": 90000,
}

found_constants = {}

for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target = node.targets[0]
        if isinstance(target, ast.Name):
            try:
                found_constants[target.id] = ast.literal_eval(node.value)
            except Exception:
                pass

for name, expected in required_constants.items():
    if found_constants.get(name) != expected:
        failures.append(f"{name} must equal {expected}")

# Forbidden execution machinery.
for node in ast.walk(tree):
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        names = (
            [x.name for x in node.names]
            if isinstance(node, ast.Import)
            else [node.module or ""]
        )
        for name in names:
            if name == "subprocess" or name.startswith("subprocess."):
                failures.append("subprocess is forbidden")

    if isinstance(node, ast.Call):
        fn = node.func
        name = ""

        if isinstance(fn, ast.Name):
            name = fn.id
        elif isinstance(fn, ast.Attribute):
            name = fn.attr

        if name in {
            "system", "popen", "spawnl", "spawnle", "spawnlp",
            "spawnlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe",
            "execv", "execve", "execvp", "execvpe",
        }:
            failures.append(f"execution function forbidden: {name}")

# Required contract evidence in implementation.
required_fragments = {
    "corvus root": "corvus",
    "corvus-dev root": "corvus-dev",
    "token exclusion": "api/token",
    "canonical resolution": "resolve",
    "symlink rejection": "symlink",
    "strict UTF-8": "utf-8",
    "NUL rejection": "\\x00",
    "accepted canonical_path": "canonical_path",
    "accepted size_bytes": "size_bytes",
    "accepted textual_content": "textual_content",
    "requested_path": "requested_path",
    "status": "status",
    "reason": "reason",
}

lower = text.lower()

for label, fragment in required_fragments.items():
    if fragment.lower() not in lower:
        failures.append(f"missing {label}")

# No obvious recursive traversal APIs.
for forbidden in ("os.walk(", ".rglob(", ".glob("):
    if forbidden in lower:
        failures.append(f"recursive/discovery API forbidden: {forbidden[:-1]}")

# Deduplicate while preserving order.
failures = list(dict.fromkeys(failures))

if failures:
    print("DEV EVIDENCE VALIDATION: FAIL")
    for failure in failures:
        print(f"FAIL: {failure}")
    raise SystemExit(10)

print("DEV EVIDENCE VALIDATION: PASS")
