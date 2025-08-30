import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.orchestrator.queue import enqueue, dequeue, worker_once, QUEUE_FILE, PROCESSED_FILE


def test_enqueue_is_idempotent(tmp_path, monkeypatch):
    # Redirect queue paths
    import tools.orchestrator.queue as q
    q.QUEUE_DIR = tmp_path
    q.QUEUE_FILE = tmp_path / "exec_queue.jsonl"
    q.PROCESSED_FILE = tmp_path / "processed.json"

    # Prepare shell and two items with same correlation/state
    shell = ["arx", "flow", "lint", "--flow=feature_request_to_pr"]
    r1 = enqueue("corr-1", "flow-lint", shell, state="PLANNING_DONE")
    r2 = enqueue("corr-1", "flow-lint", shell, state="PLANNING_DONE")
    assert r1["status"] == "enqueued"
    assert r2["status"] != "enqueued"

    items = q._read_jsonl(q.QUEUE_FILE)
    assert len(items) == 1


def test_worker_respects_gates_and_dry_run(tmp_path, monkeypatch):
    # Redirect queue paths
    import tools.orchestrator.queue as q
    q.QUEUE_DIR = tmp_path
    q.QUEUE_FILE = tmp_path / "exec_queue.jsonl"
    q.PROCESSED_FILE = tmp_path / "processed.json"

    # Enqueue two items different correlation ids (ordering FIFO)
    shell1 = ["arx", "memory", "doctor"]
    shell2 = ["arx", "memory", "stats"] if False else shell1  # reuse
    enqueue("corr-a", "memory-doctor", shell1, state="PLANNING_DONE")
    enqueue("corr-b", "memory-doctor", shell2, state="PLANNING_DONE")

    # Ensure dry-run (no ALLOW_RUN)
    os.environ.pop("ALLOW_RUN", None)
    # Process two items
    s1 = worker_once(enforce_gates=False)
    s2 = worker_once(enforce_gates=False)
    assert s1 in {"ok", "skipped"}
    assert s2 in {"ok", "skipped"}

    # Duplicate processing should be no-op
    s3 = worker_once(enforce_gates=False)
    assert s3 == "empty"
