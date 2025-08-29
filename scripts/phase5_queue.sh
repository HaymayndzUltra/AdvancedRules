#!/usr/bin/env bash
set -euo pipefail
echo "[PHASE 5] Queue / Concurrency"

set +e
docker compose -f docker/docker-compose.queue.yaml up -d --build redis exporter worker-coder worker-auditor
dc=$?
set -e

if [ $dc -ne 0 ]; then
  echo "ℹ️ Docker failed; falling back to host-mode"
  # Host fallback: assumes Redis on localhost:6379 (run docker redis alone or system redis)
  if ! docker ps 2>/dev/null | grep -q redis; then
    docker run -d --rm --name arx-redis -p 6379:6379 redis:7
    sleep 1
  fi
  export CELERY_BROKER_URL=redis://127.0.0.1:6379/0
  export CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
  AR_ENABLE_METRICS=1 python -m observability.exporters.prometheus --port 9108 >/dev/null 2>&1 &
  # Start workers in bg shells
  (celery -A exec_queue.celery_app worker -Q q.coder   -n coder@%h   -c 4 -l INFO) >/dev/null 2>&1 &
  (celery -A exec_queue.celery_app worker -Q q.auditor -n auditor@%h -c 2 -l INFO) >/dev/null 2>&1 &
  sleep 2
else
  echo "✓ docker-compose up"
fi

# Enqueue 30 CODER + 10 AUDITOR
python3 scripts/enqueue_load.py --coder 30 --auditor 10 --flow flow_demo --branch feature/queue-demo

# Give workers a moment
sleep 5

# Metrics assertion (counters must move; P95 <= 1200ms)
python3 scripts/assert_metrics.py --url http://localhost:9108/metrics --p95-ms 1200 > .artifacts/metrics_phase5.txt
cat .artifacts/metrics_phase5.txt

echo "✓ PHASE 5 PASS"
