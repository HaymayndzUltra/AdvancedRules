#!/usr/bin/env python3
from __future__ import annotations
import os
import io
import time
import glob
from contextlib import contextmanager
from pathlib import Path

try:
	import fcntl  # POSIX
except Exception:  # pragma: no cover
	fcntl = None


ROOT = Path(__file__).resolve().parents[2]


def ensure_parent(p: Path) -> None:
	p.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def file_lock(path: Path):
	"""Exclusive lock using a sibling .lock file (POSIX flock).
	Falls back to no-op if fcntl is unavailable.
	"""
	lock_path = Path(str(path) + ".lock")
	ensure_parent(lock_path)
	fh = lock_path.open("a+")
	try:
		if fcntl is not None:
			fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
		yield
	finally:
		try:
			if fcntl is not None:
				fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
			fh.close()
		except Exception:
			pass


def _rotate_backups(path: Path, keep: int = 5) -> None:
	pattern = f"{path.name}.*.bak"
	existing = sorted(path.parent.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
	for p in existing[keep:]:
		try:
			p.unlink()
		except Exception:
			pass


def atomic_write_text(path: Path, content: str, backup: bool = True, keep: int = 5) -> None:
	"""Write text atomically: temp -> fsync -> rename. Optionally rotate backups."""
	ensure_parent(path)
	with file_lock(path):
		# First write: write directly to ensure file presence
		if not path.exists():
			with path.open("w", encoding="utf-8") as f:
				f.write(content)
				f.flush()
				try:
					os.fsync(f.fileno())
				except Exception:
					pass
			return
		# Subsequent writes: backup + temp replace
		if backup and path.stat().st_size:
			bak = Path(str(path) + f".{int(time.time())}.bak")
			try:
				path.replace(bak)
			except Exception:
				pass
		req = path
		tmp = Path(str(req) + ".tmp")
		with tmp.open("w", encoding="utf-8") as f:
			f.write(content)
			f.flush()
			try:
				os.fsync(f.fileno())
			except Exception:
				pass
		tmp.replace(req)
		# fsync directory to ensure durability/visibility
		try:
			dirfd = os.open(str(req.parent), os.O_DIRECTORY)
			os.fsync(dirfd)
			os.close(dirfd)
		except Exception:
			pass
		_rotate_backups(req, keep=keep)


def append_line_atomic(path: Path, line: str) -> None:
	"""Append a single line with exclusive lock and fsync."""
	ensure_parent(path)
	with file_lock(path):
		with path.open("a", encoding="utf-8") as f:
			f.write(line if line.endswith("\n") else line + "\n")
			f.flush()
			try:
				os.fsync(f.fileno())
			except Exception:
				pass


def read_text(path: Path) -> str:
	try:
		return path.read_text(encoding="utf-8")
	except Exception:
		return ""