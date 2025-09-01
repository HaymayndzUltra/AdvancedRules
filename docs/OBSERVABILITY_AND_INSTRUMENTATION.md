# Observability & Instrumentation — Consolidated Guide (v1.0.0)

Last updated: 2025-09-01

## Purpose
This document is the canonical reference for metrics, tracing, event logging, and redaction in AdvancedRules. It consolidates and supersedes: METRICS_RUNBOOK.md and instrumentation_policy.md.

## Components
- Metrics exporter: `arx obs serve` (Prometheus endpoint)
- Instrumentation helpers: `tools/instrumentation.py`
- Collector/Exporter: `observability/collector.py`, `observability/exporters/prometheus.py`
- Event logging utilities: `tools/runner/io_utils.py`
- Decision scoring & orchestrator emitters: `tools/decision_scoring/advanced_score.py`, `tools/orchestrator/trigger_next.py`

## Quick Start
1) Enable metrics
```bash
export AR_ENABLE_METRICS=1
```
2) Start Prometheus endpoint (defaults: port 9108, addr 0.0.0.0)
```bash
arx obs serve --port 9108
# Optional address bind (supported by CLI):
# arx obs serve --port 9108 --addr 0.0.0.0
```
3) Run any flow (dry-run is fine)
```bash
export AR_ENABLE_FLOW_ENGINE=1
arx flow run --flow=feature_request_to_pr --task-id=T-0099 --dry-run
```
4) Verify metrics
```bash
curl -s http://localhost:9108/metrics | grep -E "ar_flow_|ar_step_|ar_tokens_"
```

## Metrics Reference
Flow-level
- ar_flow_started_total{flow_id, persona, exec_mode, branch}
- ar_flow_success_total{flow_id, persona, exec_mode, branch}
- ar_flow_fail_total{flow_id, persona, exec_mode, branch, reason}

Step-level
- ar_step_latency_ms (histogram){flow_id, step_id, persona, model, exec_mode}
- ar_step_retries_total{flow_id, step_id, persona}
- ar_inflight_steps{flow_id}

Resources
- ar_tokens_total{direction, model, persona}

Label policy: PII-free; truncation and sanitation applied.

## Tracing & Events
- Correlation and trace IDs are injected by orchestrator.
  - Env: `CORRELATION_ID`, `TRACE_ID`
- Event sinks (JSON Lines):
  - Events: `logs/events.jsonl`
  - Decision traces: `logs/decision_traces.jsonl`
- Required event fields (auto-filled if missing): `type`, `timestamp`, `correlation_id`, `trace_id`
- Emission helpers: `tools/runner/io_utils.py` → `append_event()`, `append_decision_trace()`

## Redaction Policy
- Enabled by default: `ENABLE_REDACTION=true`
- Redacted categories: API keys, passwords, tokens, secrets, emails, phones, JWTs, and configurable patterns
- Applies to: events, decision traces, and aggregated reports
- Programmatic control:
```python
from tools.runner.io_utils import append_event
append_event({"type":"debug","data":"..."}, redact=False)
```

## Environment Variables
- Metrics: `AR_ENABLE_METRICS`, `AR_METRICS_PORT` (default 9108), `AR_METRICS_ADDR` (default 0.0.0.0)
- Execution Safety: `ALLOW_RUN` (trigger live exec), `ALLOW_WRITES` (enable live writes in flows/Celery)
- Celery/Redis: `AR_REDIS_HOST`, `AR_REDIS_PORT`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- Tracing: `CORRELATION_ID`, `TRACE_ID`
- Redaction: `ENABLE_REDACTION`

## Grafana Integration
- Import `observability/dashboards/flows_overview.json`
- Example PromQL:
```promql
# Flow success rate (5m)
100 * (sum(rate(ar_flow_success_total[5m])) / clamp_min(sum(rate(ar_flow_started_total[5m])), 1e-9))

# Step P95 latency
histogram_quantile(0.95, sum by (le, flow_id, step_id) (rate(ar_step_latency_ms_bucket[5m])))

# Token usage by model (1h)
sum by (model, persona) (increase(ar_tokens_total{direction="out"}[1h]))
```

## Security Notes
- PII-free labels; events redacted by default
- Metrics endpoint has no auth (standard for Prometheus); deploy behind network controls
- Prefer localhost binding or restricted networks

## Testing Checklist
- Metrics on when `AR_ENABLE_METRICS=1`
- Events and traces include correlation/trace IDs
- Redaction removes secrets and PII in emitted artifacts
- Flow run produces expected counters/histograms

## Versioning & Ownership
- Doc version: v1.0.0
- Supersedes: METRICS_RUNBOOK.md, instrumentation_policy.md
- Update cadence: with any changes in metrics, event schemas, or redaction logic

