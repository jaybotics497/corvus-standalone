#!/data/data/com.termux/files/usr/bin/python3

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

DEV = Path.home() / "corvus-dev"
STAGE = (DEV / "staging/android/corvus").resolve()

ALLOWED = {
    "AndroidManifest.xml",
    "assets/index.html",
    "assets/style.css",
    "res/values/strings.xml",
    "res/values/styles.xml",
    "src/com/corvus/app/CorvusBridge.java",
    "src/com/corvus/app/CorvusEngineService.java",
    "src/com/corvus/app/MainActivity.java",
}

def fail(status, message, code):
    print(json.dumps({
        "status": status,
        "message": message
    }))
    raise SystemExit(code)

def safe_path(relative):
    if not isinstance(relative, str) or not relative:
        fail("FAIL_PATH", "empty path", 70)

    if os.path.isabs(relative):
        fail("FAIL_PATH", "absolute path rejected", 70)

    if relative not in ALLOWED:
        fail("FAIL_PATH", f"unauthorized path: {relative}", 70)

    target = STAGE / relative

    # Reject symlink components before resolution.
    current = STAGE
    for part in Path(relative).parts:
        current = current / part
        if current.exists() and current.is_symlink():
            fail("FAIL_PATH", f"symlink rejected: {relative}", 70)

    resolved = target.resolve(strict=False)

    try:
        resolved.relative_to(STAGE)
    except ValueError:
        fail("FAIL_PATH", "path escape rejected", 70)

    return resolved

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument("operation_file")
args = parser.parse_args()

operation_path = Path(args.operation_file)

try:
    operation = json.loads(operation_path.read_text())
except Exception as e:
    fail("FAIL_INSPECT", f"invalid operation JSON: {e}", 71)

kind = operation.get("operation")
relative = operation.get("path")

target = safe_path(relative)

before_hash = sha256(target) if target.is_file() else None

if kind in {"replace_exact", "insert_before", "insert_after"}:
    if not target.is_file():
        fail("FAIL_INSPECT", "target does not exist", 71)

    text = target.read_text()
    expected = operation.get("expected")

    if not isinstance(expected, str) or expected == "":
        fail("FAIL_EDIT", "expected text required", 73)

    count = text.count(expected)

    if count == 0:
        fail("FAIL_EDIT", "expected text not found", 73)

    if count != 1:
        fail("FAIL_EDIT", f"ambiguous match count: {count}", 73)

    value = operation.get("value", "")

    if not isinstance(value, str):
        fail("FAIL_EDIT", "value must be string", 73)

    if kind == "replace_exact":
        result = text.replace(expected, value, 1)

    elif kind == "insert_before":
        result = text.replace(expected, value + expected, 1)

    else:
        result = text.replace(expected, expected + value, 1)

    # Validate proposed XML before committing it to staging.
    if target.suffix.lower() == ".xml":
        try:
            ET.fromstring(result)
        except Exception as e:
            fail("FAIL_VALIDATE", f"XML invalid: {e}", 74)

    target.write_text(result)

elif kind == "create_file":
    if target.exists():
        fail("FAIL_EDIT", "create target already exists", 73)

    value = operation.get("value")

    if not isinstance(value, str):
        fail("FAIL_EDIT", "value must be string", 73)

    if target.suffix.lower() == ".xml":
        try:
            ET.fromstring(value)
        except Exception as e:
            fail("FAIL_VALIDATE", f"XML invalid: {e}", 74)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value)

elif kind == "delete_staged_file":
    if not target.is_file():
        fail("FAIL_EDIT", "delete target missing", 73)

    target.unlink()

else:
    fail("FAIL_EDIT", f"unsupported operation: {kind}", 73)

# Structural XML validation.
if target.exists() and target.suffix.lower() == ".xml":
    try:
        ET.parse(target)
    except Exception as e:
        fail("FAIL_VALIDATE", f"XML invalid: {e}", 74)

after_hash = sha256(target) if target.is_file() else None

if before_hash == after_hash:
    fail("FAIL_VALIDATE", "operation produced no change", 74)

print(json.dumps({
    "status": "PASS",
    "operation": kind,
    "path": relative,
    "before_sha256": before_hash,
    "after_sha256": after_hash
}, sort_keys=True))
