#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path


def safe_repo_path(repo, name):
    repo = Path(repo).resolve()
    raw = repo / name

    if raw.is_symlink():
        raise RuntimeError(f"symlink path is not supported: {name}")

    current = raw.parent
    while current != repo:
        if current.is_symlink():
            raise RuntimeError(f"symlink parent is not supported: {name}")
        if current == current.parent:
            raise RuntimeError(f"path escapes repository: {name}")
        current = current.parent

    resolved = raw.resolve(strict=False)

    try:
        resolved.relative_to(repo)
    except ValueError:
        raise RuntimeError(f"path escapes repository: {name}")

    return raw
