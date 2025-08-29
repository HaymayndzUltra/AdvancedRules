import os
import socket
from celery import Celery


def _default_redis_host():
    # If running in CI/host, prefer localhost
    if os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true":
        return "127.0.0.1"
    # Allow explicit override
    host = os.getenv("AR_REDIS_HOST", "redis")
    # Best effort: if 'redis' not resolvable, fall back to localhost
    try:
        socket.gethostbyname(host)
        return host
    except Exception:
        return "127.0.0.1"


HOST = _default_redis_host()
PORT = os.getenv("AR_REDIS_PORT", "6379")

BROKER = os.getenv("CELERY_BROKER_URL", f"redis://{HOST}:{PORT}/0")
BACKEND = os.getenv("CELERY_RESULT_BACKEND", f"redis://{HOST}:{PORT}/1")

app = Celery("arx", broker=BROKER, backend=BACKEND)

# Force import tasks
from . import tasks

# Hard backpressure + reliability
app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_time_limit=60 * 10,
    task_soft_time_limit=60 * 8,
    broker_transport_options={"visibility_timeout": 60 * 30},
)

# Route by persona → queue
PERSONA_QUEUE = {"CODER_AI": "q.coder", "AUDITOR_AI": "q.auditor", "PO_AI": "q.po"}


def route_for_task(name, args, kwargs, options, task=None, **_):
    persona = (kwargs or {}).get("persona") or "CODER_AI"
    q = PERSONA_QUEUE.get(persona, "q.coder")
    return {"queue": q}


app.conf.task_routes = (route_for_task,)

# Default per-task rate limit (coarse). Fine rate in code (per persona).
app.conf.task_annotations = {
    "exec_queue.tasks.execute_step": {"rate_limit": "60/m"}
}

