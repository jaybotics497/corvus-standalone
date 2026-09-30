#!/usr/bin/env python3

from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HOME = Path.home()
DEV = HOME / "corvus-dev"
BRIDGE = DEV / "chatgpt-bridge"

INBOX = BRIDGE / "inbox"
OUTBOX = BRIDGE / "outbox"
ARCHIVE = BRIDGE / "archive"

PROTOCOL = "corvus-chatgpt-bridge"
VERSION = 1

MAX_TASK_BYTES = 32000
MAX_RESULT_BYTES = 64000

MAX_TASK_AGE_SECONDS = 86400
MAX_FUTURE_SKEW_SECONDS = 300

TASK_ID_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"
)

ALLOWED_ACTIONS = {
    "status",
    "develop",
}

def die(message, code=1):
    print(f"BRIDGE RUNNER: FAIL - {message}")
    raise SystemExit(code)

def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

def digest(value):
    return hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()

def load_task(filename):
    requested = INBOX / filename

    if requested.is_symlink():
        die("symlink task rejected", 20)

    path = requested.resolve()

    try:
        path.relative_to(INBOX.resolve())
    except ValueError:
        die("task outside inbox", 21)

    if not path.is_file():
        die("task missing", 22)

    if path.stat().st_size > MAX_TASK_BYTES:
        die("task too large", 23)

    raw = path.read_bytes()

    if b"\x00" in raw:
        die("task contains NUL", 24)

    try:
        task = json.loads(
            raw.decode("utf-8", errors="strict")
        )
    except (UnicodeDecodeError, json.JSONDecodeError):
        die("invalid task encoding/JSON", 25)

    if not isinstance(task, dict):
        die("task must be an object", 26)

    supplied = task.pop("sha256", None)

    if not isinstance(supplied, str):
        die("missing task digest", 27)

    if supplied != digest(task):
        die("task digest mismatch", 28)

    required = {
        "protocol",
        "version",
        "task_id",
        "created_at",
        "action",
        "objective",
        "approval_required",
    }

    if set(task) != required:
        die("unexpected task schema", 29)

    if task["protocol"] != PROTOCOL:
        die("invalid protocol", 30)

    if task["version"] != VERSION:
        die("invalid version", 31)

    if task["action"] not in ALLOWED_ACTIONS:
        die("action not executable", 32)

    if task["approval_required"] is not True:
        die("approval requirement missing", 33)

    for field in ("task_id", "objective"):
        value = task[field]

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            die(f"invalid {field}", 34)

        if "\x00" in value:
            die(f"NUL in {field}", 35)

    task_id = task["task_id"]

    if not TASK_ID_RE.fullmatch(task_id):
        die("invalid task_id format", 36)

    expected_name = f"{task_id}.task.json"

    if path.name != expected_name:
        die(
            "task filename does not match task_id",
            37,
        )

    created_at = task["created_at"]

    if (
        isinstance(created_at, bool)
        or not isinstance(created_at, int)
    ):
        die("invalid created_at", 38)

    now = int(time.time())

    if created_at > now + MAX_FUTURE_SKEW_SECONDS:
        die("task timestamp too far in future", 39)

    if created_at < now - MAX_TASK_AGE_SECONDS:
        die("task expired", 40)

    archived = ARCHIVE / expected_name
    result = OUTBOX / f"{task_id}.result.json"

    if archived.exists() or result.exists():
        die(
            "replayed/completed task rejected",
            41,
        )

    return path, task

def bounded(text):
    data = text.encode("utf-8", errors="replace")

    if len(data) <= MAX_RESULT_BYTES:
        return text

    clipped = data[:MAX_RESULT_BYTES]
    return clipped.decode("utf-8", errors="ignore") + \
        "\n[BRIDGE OUTPUT TRUNCATED]\n"

def run_status():
    validation = subprocess.run(
        [str(DEV / "validate.sh")],
        capture_output=True,
        text=True,
        timeout=60,
    )

    staging = subprocess.run(
        [
            "git",
            "-C",
            str(DEV / "staging/corvus"),
            "status",
            "--short",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    return (
        max(validation.returncode, staging.returncode),
        (
            "=== VALIDATION ===\n" +
            validation.stdout +
            validation.stderr +
            "\n=== STAGING ===\n" +
            staging.stdout +
            staging.stderr
        ),
    )

def run_develop(objective):
    # No shell=True. Objective is passed as one argv item.
    process = subprocess.run(
        [
            str(DEV / "objective-candidate.sh"),
            objective,
        ],
        capture_output=True,
        text=True,
        timeout=900,
    )

    return (
        process.returncode,
        process.stdout + process.stderr,
    )

def write_result(task, exit_code, output):
    result = {
        "protocol": PROTOCOL,
        "version": VERSION,
        "task_id": task["task_id"],
        "action": task["action"],
        "completed_at": int(time.time()),
        "exit_code": int(exit_code),
        "approval_required": True,
        "auto_promoted": False,
        "output": bounded(output),
    }

    result["sha256"] = digest(result)

    destination = (
        OUTBOX /
        f"{task['task_id']}.result.json"
    )

    destination.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    os.chmod(destination, 0o600)

    return destination

def claim_task(path, task_id):
    destination = ARCHIVE / f"{task_id}.task.json"
    result = OUTBOX / f"{task_id}.result.json"

    if destination.exists():
        die("replayed task rejected", 50)

    if result.exists():
        die("completed task rejected", 51)

    try:
        path.replace(destination)
    except FileExistsError:
        die("task claim collision", 52)

    os.chmod(destination, 0o600)
    return destination

def main():
    if len(sys.argv) != 2:
        die(
            "usage: corvus-bridge-runner.py TASK.json"
        )

    path, task = load_task(sys.argv[1])

    print("BRIDGE RUNNER: TASK VALID")
    print(f"TASK_ID: {task['task_id']}")
    print(f"ACTION: {task['action']}")

    claimed = claim_task(
        path,
        task["task_id"],
    )

    print(f"CLAIMED: {claimed}")

    try:
        if task["action"] == "status":
            exit_code, output = run_status()

        elif task["action"] == "develop":
            exit_code, output = run_develop(
                task["objective"]
            )

        else:
            die("unreachable action", 60)

    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        output = (
            "BRIDGE TASK TIMEOUT\n"
            f"COMMAND: {exc.cmd!r}\n"
            f"TIMEOUT: {exc.timeout}\n"
        )

    result = write_result(
        task,
        exit_code,
        output,
    )

    print("BRIDGE RUNNER: COMPLETE")
    print(f"EXIT_CODE: {exit_code}")
    print(f"RESULT: {result}")
    print("AUTO_PROMOTION: no")
    print("APPROVAL_REQUIRED: yes")

if __name__ == "__main__":
    main()
