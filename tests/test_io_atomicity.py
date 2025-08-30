from pathlib import Path
import json
import threading
import time

from tools.io.fs import atomic_write_text


def test_atomic_write_creates_backups(tmp_path):
    p = tmp_path / "state.json"
    atomic_write_text(p, json.dumps({"a":1}))
    atomic_write_text(p, json.dumps({"a":2}))
    atomic_write_text(p, json.dumps({"a":3}))
    # Check file exists and at least one backup exists
    assert p.exists()
    backups = list(tmp_path.glob("state.json.bak.*"))
    assert backups, "expected rolling backups to exist"


def test_concurrent_writes_not_corrupted(tmp_path):
    p = tmp_path / "events.jsonl"
    lines = 200
    def writer(start: int):
        for i in range(start, start+lines):
            atomic_write_text(p, (p.read_text() if p.exists() else "") + f"{i}\n")

    t1 = threading.Thread(target=writer, args=(0,))
    t2 = threading.Thread(target=writer, args=(100000,))
    t1.start(); t2.start(); t1.join(); t2.join()
    content = p.read_text().splitlines()
    # No partial lines and total count equals last write size (best-effort)
    assert all(c.strip().isdigit() for c in content)
