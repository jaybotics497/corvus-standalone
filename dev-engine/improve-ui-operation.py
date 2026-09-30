#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

target = Path.home()/"corvus-dev/staging/corvus/ui/index.html"

if not target.is_file():
    print("OPERATION: BLOCKED - UI target missing")
    raise SystemExit(190)

text = target.read_text()

old = '<p>Local intelligence ready.</p>'
new = '<p>Private. Local. Ready.</p>'

if text.count(old) != 1:
    print("OPERATION: BLOCKED - UI anchor mismatch")
    raise SystemExit(191)

text = text.replace(old, new, 1)

if '<nav aria-label="Primary navigation">' not in text or 'class="composer"' not in text:
    print("OPERATION: BLOCKED - required UI structure missing")
    raise SystemExit(192)

target.write_text(text)

print("OPERATION: PASS")
print("TARGET: ui/index.html")
print("CHANGE: improve CORVUS home interface")
