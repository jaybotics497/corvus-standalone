#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

target = Path.home()/"corvus-dev/staging/corvus/ui/index.html"

if not target.is_file():
    print("OPERATION: BLOCKED - UI target missing")
    raise SystemExit(200)

text = target.read_text()

old = '''<nav>
  <button class="active"><b>◉</b><span>Chat</span></button>
  <button><b>▤</b><span>Library</span></button>
  <button><b>◇</b><span>Study</span></button>
  <button><b>⚙</b><span>Tools</span></button>
</nav>'''

new = '''<nav aria-label="Primary navigation">
  <button class="active" type="button" aria-current="page"><b>◉</b><span>Chat</span></button>
  <button type="button"><b>▤</b><span>Library</span></button>
  <button type="button"><b>◇</b><span>Study</span></button>
  <button type="button"><b>⚙</b><span>Tools</span></button>
</nav>'''

if text.count(old) != 1:
    print("OPERATION: BLOCKED - navigation anchor mismatch")
    raise SystemExit(201)

target.write_text(text.replace(old, new, 1))

print("OPERATION: PASS")
print("TARGET: ui/index.html")
print("CHANGE: improve mobile navigation semantics")
