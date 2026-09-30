#!/data/data/com.termux/files/usr/bin/python
import sys

text = sys.stdin.read()

fields = ["SUMMARY:", "TARGET:", "CHANGE:", "TEST:", "RISK:"]
positions = []

for field in fields:
    pos = text.rfind(field)
    if pos < 0:
        print("PLAN EXTRACTION: BLOCKED - missing", field)
        raise SystemExit(94)
    positions.append(pos)

if positions != sorted(positions):
    print("PLAN EXTRACTION: BLOCKED - invalid field order")
    raise SystemExit(95)

for i, field in enumerate(fields):
    start = positions[i] + len(field)
    end = positions[i + 1] if i + 1 < len(fields) else len(text)
    value = text[start:end].strip()

    if i == len(fields) - 1:
        for marker in ["[ Prompt:", "Exiting...", "=== PLAN COMPLETE ==="]:
            value = value.split(marker, 1)[0].strip()

    if field == "SUMMARY:" and not value:
        value = "(summary omitted)"

    if field == "TARGET:":
        value = value.strip("`*_ ")

    print(f"{field} {value}")
