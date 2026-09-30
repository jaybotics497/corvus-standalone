#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import json

ui = Path.home() / "corvus-dev/staging/corvus/ui"
index = ui / "index.html"
manifest = ui / "manifest.webmanifest"
worker = ui / "service-worker.js"

if not index.is_file():
    raise SystemExit("OPERATION: BLOCKED - UI target missing")

text = index.read_text()

if 'rel="manifest"' in text or "serviceWorker.register" in text:
    raise SystemExit("OPERATION: BLOCKED - PWA already present")

if "</head>" not in text or "</body>" not in text:
    raise SystemExit("OPERATION: BLOCKED - HTML anchors missing")

head = '''  <meta name="theme-color" content="#0b0d0e">
  <meta name="mobile-web-app-capable" content="yes">
  <link rel="manifest" href="manifest.webmanifest">
'''

registration = '''  <script>
    if ("serviceWorker" in navigator) {
      window.addEventListener("load", () => {
        navigator.serviceWorker.register("service-worker.js");
      });
    }
  </script>
'''

index.write_text(
    text.replace("</head>", head + "</head>", 1)
        .replace("</body>", registration + "</body>", 1)
)

manifest.write_text(json.dumps({
    "name": "CORVUS",
    "short_name": "CORVUS",
    "description": "Private local-first CORVUS interface",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#0b0d0e",
    "theme_color": "#0b0d0e"
}, indent=2) + "\n")

worker.write_text('''const CACHE = "corvus-ui-v1";
const ASSETS = [
  "./",
  "./index.html",
  "./style.css",
  "./manifest.webmanifest"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(ASSETS))
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(key => key !== CACHE)
            .map(key => caches.delete(key))
      )
    )
  );
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    fetch(event.request)
      .catch(() => caches.match(event.request))
  );
});
''')

print("PWA OPERATION: READY")
