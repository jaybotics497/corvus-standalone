#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import re, sys

if len(sys.argv) < 3:
    print("PLAN OBJECTIVE: BLOCKED - objective and plan required")
    raise SystemExit(105)

plan = Path(sys.argv[1])
objective = " ".join(sys.argv[2:]).lower()

if not plan.is_file():
    print("PLAN OBJECTIVE: BLOCKED - plan missing")
    raise SystemExit(106)

text = plan.read_text().lower()

words = re.findall(r"[a-z0-9_-]+", objective)

ignore = {
    "add", "create", "a", "an", "the", "command", "named",
    "that", "reports", "report", "basic", "current", "corvus",
    "information", "runtime"
}

meaningful = [w for w in words if w not in ignore and len(w) >= 4]

if not meaningful:
    print("PLAN OBJECTIVE: BLOCKED - no objective key available")
    raise SystemExit(107)

if not any(word in text for word in meaningful):
    print("PLAN OBJECTIVE: BLOCKED - plan does not match objective")
    print("KEYS:", ",".join(meaningful))
    raise SystemExit(108)

print("PLAN OBJECTIVE: PASS")
print("MATCHED:", ",".join(w for w in meaningful if w in text))
