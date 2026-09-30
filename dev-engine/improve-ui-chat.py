#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

target = Path.home()/"corvus-dev/staging/corvus/ui/index.html"

if not target.is_file():
    print("OPERATION: BLOCKED - UI target missing")
    raise SystemExit(210)

text = target.read_text()

old_welcome = '''    <div class="welcome">
      <div class="raven"><img src="assets/corvus-emblem.png" alt="CORVUS emblem"></div>
      <h2>CORVUS</h2>
      <p>Local intelligence ready.</p>
    </div>'''

new_welcome = '''    <div class="welcome">
      <div class="raven-mark" aria-hidden="true"></div>
      <h2>CORVUS</h2>
      <p>PRIVATE · LOCAL · READY</p>
    </div>'''

old_message = '''      <div class="message corvus">
        Systems operational. What are we working on?
      </div>'''

new_message = '''      <div class="message corvus">
        <small>CORVUS</small>
        Systems operational. What are we working on?
      </div>'''

if text.count(old_welcome) != 1:
    print("OPERATION: BLOCKED - welcome anchor mismatch")
    raise SystemExit(211)

if text.count(old_message) != 1:
    print("OPERATION: BLOCKED - message anchor mismatch")
    raise SystemExit(212)

text = text.replace(old_welcome, new_welcome, 1)
text = text.replace(old_message, new_message, 1)

target.write_text(text)

print("OPERATION: PASS")
print("TARGET: ui/index.html")
print("CHANGE: improve CORVUS chat interface")
