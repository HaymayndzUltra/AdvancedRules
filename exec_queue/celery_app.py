import os
from celery import Celery

BROKER = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

app = Celery("arx", broker=BROKER, backend=BACKEND)

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

