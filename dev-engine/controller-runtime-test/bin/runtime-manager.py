#!/usr/bin/env python3
from pathlib import Path
import os
import signal
import subprocess
import sys
import time

BASE = Path(os.environ.get("CORVUS_BASE", str(Path.home() / "corvus")))
PID_FILE = BASE / "tmp/api.pid"
LOG_FILE = BASE / "logs/api.log"
SERVER = BASE / "api/server.py"


def read_pid():
    try:
        return int(PID_FILE.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def process_exists(pid):
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def process_matches(pid):
    cmdline = Path(f"/proc/{pid}/cmdline")
    try:
        args = cmdline.read_bytes().split(b"\0")
    except OSError:
        return False

    expected = str(SERVER).encode()
    return expected in args


def managed_pid():
    pid = read_pid()

    if pid is None:
        return None

    if not process_exists(pid) or not process_matches(pid):
        PID_FILE.unlink(missing_ok=True)
        return None

    return pid


def start():
    pid = managed_pid()

    if pid is not None:
        print(f"CORVUS API: ALREADY RUNNING (PID {pid})")
        return 0

    if not SERVER.is_file():
        print(f"CORVUS API: SERVER MISSING: {SERVER}")
        return 2

    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with LOG_FILE.open("ab") as log:
        proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            cwd=str(BASE),
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env={**os.environ, "CORVUS_BASE": str(BASE)},
        )

    PID_FILE.write_text(f"{proc.pid}\n")
    time.sleep(0.3)

    if not process_exists(proc.pid) or not process_matches(proc.pid):
        PID_FILE.unlink(missing_ok=True)
        print("CORVUS API: FAILED TO START")
        return 3

    print(f"CORVUS API: STARTED (PID {proc.pid})")
    return 0


def stop():
    pid = managed_pid()

    if pid is None:
        print("CORVUS API: STOPPED")
        return 0

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        PID_FILE.unlink(missing_ok=True)
        print("CORVUS API: STOPPED")
        return 0

    for _ in range(30):
        if not process_exists(pid):
            PID_FILE.unlink(missing_ok=True)
            print("CORVUS API: STOPPED")
            return 0
        time.sleep(0.1)

    print(f"CORVUS API: STOP TIMEOUT (PID {pid})")
    return 4


def status():
    pid = managed_pid()

    if pid is None:
        print("CORVUS API: STOPPED")
        return 1

    print(f"CORVUS API: RUNNING (PID {pid})")
    return 0


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"start", "stop", "status"}:
        print("Usage: runtime-manager.py start|stop|status")
        return 1

    command = sys.argv[1]

    if command == "start":
        return start()
    if command == "stop":
        return stop()
    return status()


if __name__ == "__main__":
    sys.exit(main())
