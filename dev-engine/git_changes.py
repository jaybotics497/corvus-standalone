#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import subprocess


def changed_paths(repo):
    repo = Path(repo)

    data = subprocess.check_output([
        "git", "-C", str(repo),
        "status", "--porcelain=v1", "-z"
    ])

    entries = data.split(b"\0")
    paths = []
    i = 0

    while i < len(entries):
        entry = entries[i]

        if not entry:
            i += 1
            continue

        if len(entry) < 4 or entry[2:3] != b" ":
            raise RuntimeError("invalid git status entry")

        status = entry[:2]
        path = entry[3:]

        if b"R" in status or b"C" in status:
            raise RuntimeError("rename/copy changes are not supported")

        paths.append(path.decode("utf-8", errors="surrogateescape"))
        i += 1

    return sorted(set(paths))
