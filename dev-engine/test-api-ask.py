#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

DEV = Path.home() / "corvus-dev"
SERVER = DEV / "staging/corvus/api/server.py"
TOKEN = "test-token"
URL = "http://127.0.0.1:8765"


def request(path, body=None, token=TOKEN, raw=False):
    headers = {}

    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    data = None

    if body is not None:
        headers["Content-Type"] = "application/json"
        data = body if raw else json.dumps(body).encode()

    req = urllib.request.Request(
        URL + path,
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


def expect(name, actual, expected):
    if actual != expected:
        raise AssertionError(
            f"{name}: expected {expected!r}, got {actual!r}"
        )
    print(f"PASS: {name}")

tmp = Path(tempfile.mkdtemp(prefix="corvus-api-test-"))
server = None

try:
    (tmp / "api").mkdir()
    (tmp / "bin").mkdir()

    (tmp / "api/token").write_text(TOKEN)

    fake = tmp / "bin/corvus"
    fake.write_text(
        """#!/data/data/com.termux/files/usr/bin/bash
if [ "$1" = "ask" ]; then
    shift
    if [ "$1" = "FAIL_SUBPROCESS" ]; then
        echo "forced failure" >&2
        exit 9
    fi
    if [ "$1" = "SLOW" ]; then
        sleep 2
        exit 0
    fi
    printf 'FAKE ASK: %s\\n' "$1"
    exit 0
fi
echo "FAKE $1"
"""
    )
    fake.chmod(0o755)

    env = os.environ.copy()
    env["CORVUS_BASE"] = str(tmp)
    env["CORVUS_ASK_TIMEOUT"] = "0.2"

    server = subprocess.Popen(
        ["python", str(SERVER)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(50):
        try:
            urllib.request.urlopen(URL, timeout=0.1)
        except urllib.error.HTTPError:
            break
        except Exception:
            time.sleep(0.1)
    else:
        raise RuntimeError("API server did not start")

    status, data = request("/ask", {"prompt": "hello"}, token=None)
    expect("unauthorized", status, 401)

    status, data = request("/ask", b'{"prompt":', raw=True)
    expect("malformed JSON", status, 400)

    status, data = request("/ask", {})
    expect("missing prompt", status, 400)

    status, data = request("/ask", {"prompt": "x" * 8001})
    expect("oversized prompt", status, 413)

    status, data = request("/ask", {"prompt": "hello"})
    expect("successful ask", status, 200)
    expect("ask command", data["command"], "ask")
    expect("ask routing", data["output"], "FAKE ASK: hello\n")

    status, data = request("/ask", {"prompt": "FAIL_SUBPROCESS"})
    expect("subprocess failure", status, 502)
    expect("failure code", data["code"], 9)

    status, data = request("/ask", {"prompt": "SLOW"})
    expect("inference timeout", status, 504)
    expect("timeout body", data["error"], "inference timeout")

    print()
    print("API ASK TESTS: PASS")

finally:
    if server is not None:
        server.terminate()
        try:
            server.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()

    shutil.rmtree(tmp, ignore_errors=True)
