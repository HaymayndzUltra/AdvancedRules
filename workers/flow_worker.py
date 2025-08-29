import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so `exec_queue` is importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exec_queue.celery_app import app  # noqa: F401  # ensure app is discoverable


def main():
    # Worker options: queue & concurrency bound via env
    q = os.getenv("ARX_WORKER_QUEUE", "q.coder")
    c = os.getenv("ARX_WORKER_CONCURRENCY", "4")
    os.execvp(
        "celery",
        [
            "celery",
            "-A",
            "exec_queue.celery_app",
            "worker",
            "-Q",
            q,
            "-c",
            c,
            "--loglevel=INFO",
        ],
    )


if __name__ == "__main__":
    main()

