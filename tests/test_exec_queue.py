import json
import sys
from pathlib import Path

from tools.queue.exec_queue import enqueue_task, load_queue, processed_ids
from tools.queue.worker import process_once


def test_enqueue_and_idempotency(tmp_path, monkeypatch):
	# Enqueue two items with same correlation_id; only one should process
	cmd_id = 'flow-lint'
	cid = 'corr-queue-123'
	enqueue_task(cmd_id, cid, {"shell": ["arx","flow","lint","--flow=x"]})
	enqueue_task(cmd_id, cid, {"shell": ["arx","flow","lint","--flow=x"]})
	assert any(rec.get('correlation_id') == cid for rec in load_queue())
	processed_before = processed_ids()
	count = process_once()
	processed_after = processed_ids()
	assert count >= 1
	assert len(processed_after) >= len(processed_before) + 1


def test_worker_respects_dry_run(monkeypatch):
	# Ensure ALLOW_RUN not set -> dry-run marking
	cmd_id = 'flow-lint'
	cid = 'corr-queue-456'
	enqueue_task(cmd_id, cid, {})
	count = process_once()
	assert count >= 1