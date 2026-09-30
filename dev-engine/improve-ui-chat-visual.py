#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

target = Path.home()/"corvus-dev/staging/corvus/ui/style.css"

if not target.is_file():
    print("OPERATION: BLOCKED - CSS target missing")
    raise SystemExit(220)

text = target.read_text()

marker = "/* Chat v1 visual system */"

if marker in text:
    print("OPERATION: BLOCKED - Chat visual system already present")
    raise SystemExit(221)

required = (
    ".welcome {",
    ".messages {",
    ".message.corvus {",
    ".composer {",
    ".raven-mark {",
)

if not all(anchor in text for anchor in required):
    print("OPERATION: BLOCKED - required CSS baseline missing")
    raise SystemExit(222)

addition = r'''

/* Chat v1 visual system */
.welcome {
  padding:18px 0 10px;
}

.welcome .raven-mark {
  margin:0 auto 10px;
  width:34px;
  height:27px;
  filter:drop-shadow(0 0 10px rgba(184,154,97,.16));
}

.welcome h2 {
  margin:0 0 5px;
  font-size:14px;
  letter-spacing:5px;
}

.welcome p {
  font-size:9px;
  letter-spacing:2px;
}

.messages {
  display:flex;
  flex-direction:column;
  justify-content:flex-end;
  padding:18px 0;
}

.message.corvus {
  position:relative;
  padding:15px 16px;
  background:linear-gradient(145deg,#151a1e,#101416);
  border-color:#292d2e;
}

.message.corvus small {
  display:block;
  margin-bottom:7px;
  color:var(--gold);
  font-size:8px;
  font-weight:700;
  letter-spacing:2px;
}

.composer {
  box-shadow:0 12px 35px rgba(0,0,0,.28);
}

.composer:focus-within {
  border-color:#5b4d34;
}
'''

target.write_text(text.rstrip() + addition)

print("OPERATION: PASS")
print("TARGET: ui/style.css")
print("CHANGE: improve CORVUS chat visual system")
