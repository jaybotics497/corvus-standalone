#!/data/data/com.termux/files/usr/bin/python

CAPABILITIES = (
    {
        "target": "bin/dev-evidence.py",
        "keyword": "development evidence bridge",
        "aliases": ("evidence bridge", "dev evidence"),
        "operation": "build-dev-evidence-operation.py",
        "test": "dev-evidence",
        "files": ("bin/dev-evidence.py",),
        "new_target": True,
    },
    {
        "target": "bin/corvus",
        "keyword": "diagnostics",
        "operation": "add-diagnostics-operation.py",
        "test": "controller-diagnostics",
    },
    {
        "target": "bin/corvus",
        "keyword": "runtime",
        "operation": "add-runtime-operation.py",
        "test": "controller-runtime",
    },
    {
        "target": "bin/corvus",
        "keyword": "resource",
        "operation": "add-resource-operation.py",
        "test": "controller-resource",
    },
    {
        "target": "ui/index.html",
        "keyword": "home interface",
        "operation": "improve-ui-operation.py",
        "test": "ui-home",
    },
    {
        "target": "ui/index.html",
        "keyword": "navigation",
        "operation": "improve-ui-navigation.py",
        "test": "ui-navigation",
    },
    {
        "target": "ui/index.html",
        "keyword": "chat interface",
        "operation": "improve-ui-chat.py",
        "test": "ui-chat",
    },
    {
        "target": "ui/style.css",
        "keyword": "chat visual system",
        "operation": "improve-ui-chat-visual.py",
        "test": "ui-chat-visual",
    },
    {
        "target": "ui/index.html",
        "keyword": "pwa installation",
        "aliases": (
            "pwa",
            "progressive web app",
            "service worker",
        ),
        "operation": "add-ui-pwa.py",
        "test": "ui-pwa",
        "files": (
            "ui/index.html",
            "ui/manifest.webmanifest",
            "ui/service-worker.js",
        ),
    },
)

def capability_files(capability):
    files = capability.get("files")
    if files:
        return tuple(files)
    return (capability["target"],)

def match_capability(target, text):
    text = text.lower()

    matches = [
        capability
        for capability in CAPABILITIES
        if (
            target == capability["target"]
            and capability["keyword"] in text
        )
    ]

    if not matches:
        return None

    return max(matches, key=lambda capability: len(capability["keyword"]))

def match_objective_capability(text):
    text = text.lower()

    matches = []

    for capability in CAPABILITIES:
        terms = (capability["keyword"],) + tuple(
            capability.get("aliases", ())
        )

        matched = [
            term for term in terms
            if term in text
        ]

        if matched:
            matches.append((capability, matched))

    if len(matches) != 1:
        return None

    return matches[0][0]

def capability_allows_new_target(capability):
    return bool(capability and capability.get("new_target", False))
