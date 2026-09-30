#!/usr/bin/env python3
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

DEV = Path.home() / "corvus-dev"
MANAGER = DEV / "staging/corvus/bin/runtime-manager.py"


def run(base, command):
    env = {**os.environ, "CORVUS_BASE": str(base)}
    return subprocess.run(
        [str(MANAGER), command],
        text=True,
        capture_output=True,
        env=env,
        timeout=5,
    )


def expect(name, condition):
    if not condition:
        raise AssertionError(name)
    print(f"PASS: {name}")


tmp = Path(tempfile.mkdtemp(prefix="corvus-runtime-test-"))

try:
    (tmp / "api").mkdir()

    server = tmp / "api/server.py"
    server.write_text(
        """#!/usr/bin/env python3
import signal
import time

running = True

def stop(sig, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, stop)

while running:
    time.sleep(0.1)
"""
    )
    server.chmod(0o755)

    r = run(tmp, "start")
    expect("start exit", r.returncode == 0)
    expect("start output", "STARTED" in r.stdout)

    pid_file = tmp / "tmp/api.pid"
    expect("pid created", pid_file.is_file())
    pid = int(pid_file.read_text().strip())

    r = run(tmp, "status")
    expect("running status", r.returncode == 0)
    expect("running output", "RUNNING" in r.stdout)

    r = run(tmp, "start")
    expect("duplicate exit", r.returncode == 0)
    expect("duplicate blocked", "ALREADY RUNNING" in r.stdout)
    expect("pid unchanged", int(pid_file.read_text().strip()) == pid)

    r = run(tmp, "stop")
    expect("stop exit", r.returncode == 0)
    expect("stop output", "STOPPED" in r.stdout)
    expect("pid removed", not pid_file.exists())

    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(f"{os.getpid()}\n")

    r = run(tmp, "status")
    expect("stale status", r.returncode == 1)
    expect("stale reported stopped", "STOPPED" in r.stdout)
    expect("stale pid removed", not pid_file.exists())

    print()
    print("RUNTIME MANAGER TESTS: PASS")

finally:
    try:
        r = run(tmp, "stop")
    except Exception:
        pass
    shutil.rmtree(tmp, ignore_errors=True)
