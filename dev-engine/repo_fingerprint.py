#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import hashlib

from path_safety import safe_repo_path


def fingerprint_paths(repo, names):
    repo = Path(repo)
    h = hashlib.sha256()

    for name in sorted(set(names)):
        path = safe_repo_path(repo, name)

        h.update(name.encode())
        h.update(b"\0")

        if path.is_file():
            mode = path.stat().st_mode & 0o777
            h.update(f"{mode:o}".encode())
            h.update(b"\0")
            h.update(path.read_bytes())
        elif path.exists():
            h.update(b"<NONFILE>")
        else:
            h.update(b"<DELETED>")

        h.update(b"\0")

    return h.hexdigest()
