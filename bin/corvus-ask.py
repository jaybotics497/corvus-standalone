#!/usr/bin/env python3

from pathlib import Path
import sqlite3
import sys
import subprocess
import re

BASE = Path.home() / "corvus"
DB = BASE / "data/index/corvus.db"
INFER = BASE / "bin/infer"

args = sys.argv[1:]

if not args:
    print("USAGE: corvus ask [general|grounded|dev] QUESTION")
    sys.exit(1)

mode = "general"

if args[0].lower() in ("general", "grounded", "dev"):
    mode = args.pop(0).lower()

query = " ".join(args).strip()

if not query:
    print("CORVUS: question required.")
    sys.exit(1)


def infer(prompt):
    result = subprocess.run(
        [str(INFER), prompt],
        text=True,
        capture_output=True
    )

    if result.stdout:
        print(result.stdout.strip())

    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        sys.exit(result.returncode)


# --------------------------------------------------
# GENERAL MODE
# --------------------------------------------------

if mode == "general":

    prompt = f"""You are CORVUS, a local AI assistant running on Android through Termux.

Answer the user's request directly and concisely.
Do not invent system capabilities, files, commands, or facts you do not know.
If the request depends on CORVUS-specific implementation details that were not supplied, state that those details must be inspected.

USER:
{query}

ANSWER:
"""

    infer(prompt)
    sys.exit(0)


# --------------------------------------------------
# DEV MODE
# --------------------------------------------------

if mode == "dev":

    prompt = f"""You are CORVUS operating in DEVELOPMENT MODE.

Known environment:
- Android device
- Termux user-space environment
- CORVUS base directory: ~/corvus
- CORVUS development directory: ~/corvus-dev
- Local Python HTTP API: 127.0.0.1:8765
- Local inference uses llama.cpp
- Model: Qwen2.5 1.5B Instruct GGUF
- Do NOT assume systemd, sudo, apt, apk, root access, or a conventional Linux init system.
- Proposed commands must be appropriate for Android and Termux.
- Do not claim you inspected a file unless its contents were supplied.
- Prefer diagnosis and reversible changes before destructive modifications.

Development request:

{query}

Provide a concrete technical answer. Clearly identify anything that requires inspecting the actual CORVUS source before implementation.
"""

    infer(prompt)
    sys.exit(0)


# --------------------------------------------------
# GROUNDED MODE
# --------------------------------------------------

terms = re.findall(r"[A-Za-z0-9_]+", query)

if not terms:
    print("CORVUS: no searchable terms.")
    sys.exit(2)

fts_query = " OR ".join(terms)

con = sqlite3.connect(DB)

rows = con.execute(
    """
    SELECT c.source,c.page,c.section,c.content
    FROM chunks_fts f
    JOIN chunks c ON c.id=f.rowid
    WHERE chunks_fts MATCH ?
    ORDER BY bm25(chunks_fts)
    LIMIT 3
    """,
    (fts_query,)
).fetchall()

con.close()

print(f"RETRIEVED: {len(rows)}")

if not rows:
    print("CORVUS: no relevant library sources found.")
    print("ANSWER BLOCKED: no supporting source.")
    sys.exit(2)

context = []

for i, (source, page, section, content) in enumerate(rows, 1):

    cite = f"[SOURCE {i}: {source}"

    if page is not None:
        cite += f", page {page}"

    if section:
        cite += f", section {section}"

    cite += "]"

    context.append(f"{cite}\n{content}")

evidence = "\n\n".join(context)

prompt = f"""Answer the question using ONLY the supplied library evidence.
If the evidence is insufficient, state that clearly.
Every factual claim must include its supporting source label.

QUESTION:
{query}

LIBRARY EVIDENCE:
{evidence}
"""

print("GROUNDING: READY")

infer(prompt)
