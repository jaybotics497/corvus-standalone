#!/usr/bin/env python3

from pathlib import Path
import hashlib
import json
import os
import sys
import time
import uuid

HOME = Path.home()
DEV = HOME / "corvus-dev"
BRIDGE = DEV / "chatgpt-bridge"

INBOX = BRIDGE / "inbox"
OUTBOX = BRIDGE / "outbox"
ARCHIVE = BRIDGE / "archive"

PROTOCOL = "corvus-chatgpt-bridge"
VERSION = 1

ALLOWED_ACTIONS = {
    "develop",
    "inspect",
    "status",
}

MAX_TASK_BYTES = 32_000
MAX_TEXT_BYTES = 16_000


def fail(message, code=1):
    print(f"BRIDGE: FAIL - {message}")
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


def validate_text(name, value):
    if not isinstance(value, str):
        fail(f"{name} must be text", 20)

    if not value.strip():
        fail(f"{name} is empty", 21)

    if len(value.encode("utf-8")) > MAX_TEXT_BYTES:
        fail(f"{name} too large", 22)

    if "\x00" in value:
        fail(f"{name} contains NUL", 23)

    return value.strip()


def validate_task(task):
    if not isinstance(task, dict):
        fail("task must be object", 30)

    allowed_keys = {
        "protocol",
        "version",
        "task_id",
        "created_at",
        "action",
        "objective",
        "approval_required",
    }

    unknown = set(task) - allowed_keys
    if unknown:
        fail(
            "unknown task fields: " +
            ",".join(sorted(unknown)),
            31,
        )

    if task.get("protocol") != PROTOCOL:
        fail("invalid protocol", 32)

    if task.get("version") != VERSION:
        fail("unsupported version", 33)

    task_id = validate_text(
        "task_id",
        task.get("task_id"),
    )

    action = validate_text(
        "action",
        task.get("action"),
    )

    if action not in ALLOWED_ACTIONS:
        fail("action not allowed", 34)

    objective = validate_text(
        "objective",
        task.get("objective"),
    )

    if task.get("approval_required") is not True:
        fail("approval_required must be true", 35)

    return {
        "task_id": task_id,
        "action": action,
        "objective": objective,
    }


def load_task(path):
    if path.is_symlink():
        fail("task file may not be symlink", 40)

    resolved = path.resolve()

    try:
        resolved.relative_to(INBOX.resolve())
    except ValueError:
        fail("task outside inbox", 41)

    if not resolved.is_file():
        fail("task is not regular file", 42)

    size = resolved.stat().st_size

    if size > MAX_TASK_BYTES:
        fail("task too large", 43)

    raw = resolved.read_bytes()

    if b"\x00" in raw:
        fail("task contains NUL", 44)

    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        fail("task is not strict UTF-8", 45)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        fail("invalid JSON", 46)


def create_task(action, objective):
    if action not in ALLOWED_ACTIONS:
        fail("action not allowed", 50)

    objective = validate_text("objective", objective)

    task_id = (
        time.strftime("%Y%m%d-%H%M%S") +
        "-" +
        uuid.uuid4().hex[:12]
    )

    task = {
        "protocol": PROTOCOL,
        "version": VERSION,
        "task_id": task_id,
        "created_at": int(time.time()),
        "action": action,
        "objective": objective,
        "approval_required": True,
    }

    task["sha256"] = digest(task)

    path = OUTBOX / f"{task_id}.task.json"

    path.write_text(
        json.dumps(task, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    os.chmod(path, 0o600)

    print(f"BRIDGE TASK: CREATED")
    print(f"TASK_ID: {task_id}")
    print(f"FILE: {path}")


def validate_file(filename):
    path = INBOX / filename

    task = load_task(path)

    supplied_hash = task.pop("sha256", None)

    if not isinstance(supplied_hash, str):
        fail("missing sha256", 60)

    expected = digest(task)

    if supplied_hash != expected:
        fail("task digest mismatch", 61)

    parsed = validate_task(task)

    print("BRIDGE TASK: VALID")
    print(f"TASK_ID: {parsed['task_id']}")
    print(f"ACTION: {parsed['action']}")
    print(f"OBJECTIVE: {parsed['objective']}")
    print("APPROVAL_REQUIRED: yes")


def status():
    incoming = len(list(INBOX.glob("*.json")))
    outgoing = len(list(OUTBOX.glob("*.json")))

    print("CORVUS CHATGPT BRIDGE")
    print(f"PROTOCOL: {PROTOCOL}/{VERSION}")
    print(f"INBOX: {incoming}")
    print(f"OUTBOX: {outgoing}")
    print("REMOTE_SHELL: disabled")
    print("AUTO_PROMOTION: disabled")
    print("APPROVAL_REQUIRED: yes")


def main():
    for directory in (INBOX, OUTBOX, ARCHIVE):
        directory.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) < 2:
        fail("command required")

    command = sys.argv[1]

    if command == "status":
        status()
        return

    if command == "create":
        if len(sys.argv) != 4:
            fail("usage: create ACTION OBJECTIVE")
        create_task(sys.argv[2], sys.argv[3])
        return

    if command == "validate":
        if len(sys.argv) != 3:
            fail("usage: validate FILE")
        validate_file(sys.argv[2])
        return

    fail("unknown command")


if __name__ == "__main__":
    main()
