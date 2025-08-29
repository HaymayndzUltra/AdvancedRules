import os
import time
import json
import hashlib
import random
import redis
from celery import states
from celery.exceptions import Ignore, Retry
from .celery_app import app, HOST, PORT
from tools.instrumentation import instr
from observability.collector import metrics_enabled


REDIS_URL = os.getenv("REDIS_URL", f"redis://{HOST}:{PORT}/0")
r = redis.from_url(REDIS_URL)

# simple per-persona rate limits (fixed window)
RATE_LIMITS = {
    "CODER_AI": (30, 60),
    "AUDITOR_AI": (10, 60),
    "PO_AI": (6, 60),
}  # (N per seconds)


def _idempotency_key(flow_id, task_id, step_id, payload_hash):
    base = f"{flow_id}:{task_id}:{step_id}:{payload_hash}"
    return f"arx:idemp:{hashlib.blake2b(base.encode(), digest_size=12).hexdigest()}"


def _payload_hash(payload: dict):
    s = json.dumps(payload, sort_keys=True)[:4096]
    return hashlib.blake2b(s.encode(), digest_size=16).hexdigest()


def _rate_limited(persona: str) -> bool:
    n, window = RATE_LIMITS.get(persona, (20, 60))
    key = f"arx:rl:{persona}:{int(time.time() // window)}"
    v = r.incr(key, 1)
    if v == 1:
        r.expire(key, window)
    return v > n


def _assert_writes_ok(exec_mode: str):
    if exec_mode != "live":
        return
    if os.getenv("ALLOW_WRITES") != "1":
        raise PermissionError("Writes blocked: set ALLOW_WRITES=1 to perform live changes")


@app.task(
    bind=True,
    name="exec_queue.tasks.execute_step",
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def execute_step(
    self,
    flow_id: str,
    task_id: str,
    step_id: str,
    persona: str,
    exec_mode: str,
    branch: str,
    model: str = "unknown",
    payload: dict | None = None,
    allow_destructive: bool = False,
):
    """
    Execute a single step; idempotent; rate-limited. payload is step-specific (no PII).
    """
    payload = payload or {}

    # Per-persona rate limit (retry later)
    if _rate_limited(persona):
        raise self.retry(countdown=5, exc=Retry("persona rate limit"))

    ph = _payload_hash(payload)
    key = _idempotency_key(flow_id, task_id, step_id, ph)

    # SETNX lock for idempotency (expires in 24h)
    if not r.set(key, "running", nx=True, ex=60 * 60 * 24):
        # Already processed: skip
        self.update_state(state=states.IGNORED, meta={"reason": "duplicate"})
        raise Ignore()

    # Guard destructive ops
    _assert_writes_ok(exec_mode)
    if not allow_destructive and exec_mode == "live":
        # double-guard live writes unless explicitly allowed for this step
        raise PermissionError("Live destructive op not allowed without allow_destructive=True")

    instr.flow_start(flow_id, persona, exec_mode, branch)
    try:
        with instr.step(flow_id, step_id, persona, model=model, exec_mode=exec_mode):
            # ---- EXECUTE THE STEP BODY ----
            dur = random.randint(100, 800) / 1000.0
            time.sleep(dur)
            if random.random() < 0.03:
                raise RuntimeError("simulated_step_error")
            # --------------------------------

        instr.flow_end(flow_id, persona, exec_mode, branch, success=True)
        return {"status": "ok", "flow_id": flow_id, "step_id": step_id, "t": time.time()}
    except Exception as e:
        instr.retry(flow_id, step_id, persona)
        instr.flow_end(
            flow_id, persona, exec_mode, branch, success=False, reason=type(e).__name__
        )
        # Re-raise for Celery autoretry
        raise
    finally:
        # mark as done (idempotent): overwrite short TTL (observability)
        r.set(key, "done", ex=60 * 60 * 24)

