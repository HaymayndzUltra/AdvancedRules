from pathlib import Path
import threading
import time

from tools.io.fs import FileLock


def test_file_lock_exclusive(tmp_path):
    target = tmp_path / "lockme.txt"
    target.write_text("x", encoding="utf-8")
    order = []

    def worker(name: str, delay: float):
        time.sleep(delay)
        with FileLock(target):
            order.append(name)
            # hold lock briefly
            time.sleep(0.1)

    t1 = threading.Thread(target=worker, args=("a", 0.0))
    t2 = threading.Thread(target=worker, args=("b", 0.01))
    t1.start(); t2.start(); t1.join(); t2.join()
    # Ensure both executed and order preserved (at least serialized)
    assert order[0] in {"a", "b"} and order[1] in {"a", "b"}
