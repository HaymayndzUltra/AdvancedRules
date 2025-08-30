#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

try:
    import fcntl  # POSIX
except Exception:  # pragma: no cover
    fcntl = None  # type: ignore


def _lock_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".lock")


class FileLock:
    def __init__(self, target: Path) -> None:
        self.target = Path(target)
        self.lock_file = _lock_path(self.target)
        self._fh = None

    def __enter__(self):
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.lock_file, "a+")
        if fcntl:
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._fh and fcntl:
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        finally:
            if self._fh:
                self._fh.close()


def _rotate_backups(path: Path, keep: int) -> None:
    if keep <= 0 or not path.exists():
        return
    # Shift existing backups: .bak.(n-1) -> .bak.n
    for n in range(keep, 0, -1):
        older = path.with_suffix(path.suffix + f".bak.{n}")
        newer = path.with_suffix(path.suffix + f".bak.{n+1}")
        if older.exists():
            if n == keep:
                try:
                    older.unlink()
                except Exception:
                    pass
            else:
                try:
                    if newer.exists():
                        newer.unlink()
                except Exception:
                    pass
                try:
                    older.rename(newer)
                except Exception:
                    pass
    # Create .bak.1 from current
    try:
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak.1"))
    except Exception:
        pass


def atomic_write_text(path: Path, content: str, backup_keep: int = 3) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(path):
        tmp_fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmp:
                tmp.write(content)
                tmp.flush()
                os.fsync(tmp.fileno())
            # rotate backups then replace
            if path.exists():
                _rotate_backups(path, backup_keep)
            os.replace(tmp_name, path)
        finally:
            try:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            except Exception:
                pass


def atomic_write_json(path: Path, data: Any, backup_keep: int = 3, indent: int = 2) -> None:
    atomic_write_text(Path(path), json.dumps(data, indent=indent), backup_keep=backup_keep)


def append_jsonl(path: Path, obj: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(path):
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj) + "\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass

