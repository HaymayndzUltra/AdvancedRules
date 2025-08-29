#!/usr/bin/env python3
"""
PII-SAFE METRICS COLLECTOR
Thin wrapper over Prometheus client with strict, PII-free labels.
"""

import os
import re
import time
from contextlib import contextmanager
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, REGISTRY

# Sanitization regex - only allow alphanumeric, underscore, dash, dot, forward slash
_ALLOWED = re.compile(r"[^a-zA-Z0-9_\-./]")
MAXLEN = 64


def _san(v):
    """Sanitize label values to be PII-free and Prometheus-safe"""
    if v is None:
        return "unknown"
    v = str(v)
    v = _ALLOWED.sub("_", v)[:MAXLEN]
    return v or "unknown"


def metrics_enabled():
    """Check if metrics collection is enabled"""
    if os.getenv("AR_ENABLE_METRICS") == "1":
        return True
    # Optional: read from config file if needed
    # try:
    #     from config import features
    #     return features.get("metrics_v2", False)
    # except:
    #     pass
    return False


# Global metrics registry (using default)
# Flow-level metrics
FLOW_STARTED = Counter(
    "ar_flow_started_total", 
    "Flows started",
    ["flow_id", "persona", "exec_mode", "branch"]
)

FLOW_SUCCESS = Counter(
    "ar_flow_success_total", 
    "Flows succeeded",
    ["flow_id", "persona", "exec_mode", "branch"]
)

FLOW_FAIL = Counter(
    "ar_flow_fail_total", 
    "Flows failed",
    ["flow_id", "persona", "exec_mode", "branch", "reason"]
)

# Step-level metrics
STEP_LAT_MS = Histogram(
    "ar_step_latency_ms",
    "Step latency in milliseconds",
    ["flow_id", "step_id", "persona", "model", "exec_mode"],
    # Buckets tuned for LLM steps (ms) - from 50ms to 40s
    buckets=(50, 100, 200, 400, 800, 1500, 3000, 5000, 8000, 12000, 20000, 40000)
)

STEP_RETRIES = Counter(
    "ar_step_retries_total", 
    "Retries per step",
    ["flow_id", "step_id", "persona"]
)

# Token tracking
TOKENS = Counter(
    "ar_tokens_total", 
    "Tokens used",
    ["direction", "model", "persona"]
)

# Inflight tracking
INFLIGHT = Gauge(
    "ar_inflight_steps", 
    "Steps currently running", 
    ["flow_id"]
)


def flow_start(flow_id, persona, exec_mode, branch):
    """Record flow start event"""
    if not metrics_enabled():
        return
    FLOW_STARTED.labels(
        _san(flow_id), 
        _san(persona), 
        _san(exec_mode), 
        _san(branch)
    ).inc()


def flow_end(flow_id, persona, exec_mode, branch, success: bool, reason: str = "ok"):
    """Record flow completion event"""
    if not metrics_enabled():
        return
    
    if success:
        FLOW_SUCCESS.labels(
            _san(flow_id), 
            _san(persona), 
            _san(exec_mode), 
            _san(branch)
        ).inc()
    else:
        FLOW_FAIL.labels(
            _san(flow_id), 
            _san(persona), 
            _san(exec_mode), 
            _san(branch), 
            _san(reason)
        ).inc()


@contextmanager
def step_timer(flow_id, step_id, persona, model="unknown", exec_mode="dry_run"):
    """Context manager to time step execution and track inflight status"""
    started = time.perf_counter()
    if metrics_enabled():
        INFLIGHT.labels(_san(flow_id)).inc()
    
    try:
        yield
    finally:
        if metrics_enabled():
            dur_ms = (time.perf_counter() - started) * 1000.0
            STEP_LAT_MS.labels(
                _san(flow_id), 
                _san(step_id), 
                _san(persona), 
                _san(model), 
                _san(exec_mode)
            ).observe(dur_ms)
            INFLIGHT.labels(_san(flow_id)).dec()


def add_retry(flow_id, step_id, persona):
    """Record a step retry event"""
    if not metrics_enabled():
        return
    STEP_RETRIES.labels(
        _san(flow_id), 
        _san(step_id), 
        _san(persona)
    ).inc()


def add_tokens(direction, model, persona, n):
    """Record token usage"""
    if not metrics_enabled():
        return
    TOKENS.labels(
        _san(direction), 
        _san(model), 
        _san(persona)
    ).inc(n)


# Test/debug utilities
def get_metric_families():
    """Get all metric families for debugging"""
    return REGISTRY.collect()


def reset_metrics():
    """Reset all metrics (for testing only)"""
    for collector in list(REGISTRY._collector_to_names.keys()):
        if hasattr(collector, '_value'):
            collector._value.clear()
        elif hasattr(collector, '_samples'):
            collector._samples.clear()