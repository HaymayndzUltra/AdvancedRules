#!/usr/bin/env python3
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from tools.io.fs import ensure_parent, file_lock
import os

ROOT = Path(__file__).resolve().parents[2]
QUEUE_DIR = ROOT / 'exec_queue'
QUEUE_FILE = QUEUE_DIR / 'exec_queue.jsonl'
PROCESSED_FILE = QUEUE_DIR / 'processed.jsonl'


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
	items: List[Dict[str, Any]] = []
	if not path.exists():
		return items
	for line in path.read_text(encoding='utf-8').splitlines():
		line = line.strip()
		if not line:
			continue
		try:
			items.append(json.loads(line))
		except Exception:
			pass
	return items


def processed_ids() -> Set[str]:
	return {str(x.get('correlation_id')) for x in _load_jsonl(PROCESSED_FILE)}


def load_queue() -> List[Dict[str, Any]]:
	return _load_jsonl(QUEUE_FILE)


def enqueue_task(cmd_id: str, correlation_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
	ensure_parent(QUEUE_FILE)
	payload = payload or {}
	rec = {
		"ts": time.time(),
		"correlation_id": correlation_id,
		"cmd_id": cmd_id,
		"status": "queued",
		"payload": payload,
	}
	with file_lock(QUEUE_FILE):
		# Don't use append_line_atomic here as it tries to acquire the lock again
		with QUEUE_FILE.open("a", encoding="utf-8") as f:
			line = json.dumps(rec)
			f.write(line if line.endswith("\n") else line + "\n")
			f.flush()
			try:
				os.fsync(f.fileno())
			except Exception:
				pass
	return {"status": "queued", "correlation_id": correlation_id, "cmd_id": cmd_id}


def mark_processed(correlation_id: str, result: Dict[str, Any] | None = None) -> None:
	ensure_parent(PROCESSED_FILE)
	res = {"ts": time.time(), "correlation_id": correlation_id, **(result or {})}
	with file_lock(PROCESSED_FILE):
		# Don't use append_line_atomic here as it tries to acquire the lock again
		with PROCESSED_FILE.open("a", encoding="utf-8") as f:
			line = json.dumps(res)
			f.write(line if line.endswith("\n") else line + "\n")
			f.flush()
			try:
				os.fsync(f.fileno())
			except Exception:
				pass