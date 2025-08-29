#!/usr/bin/env bash
set -euo pipefail
echo "[PHASE 4] Observability"

# Start /metrics exporter (background)
pkill -f "observability.exporters.prometheus" || true
AR_ENABLE_METRICS=1 python -m observability.exporters.prometheus --port 9108 >/dev/null 2>&1 &
sleep 1

# Nudge metrics by running a flow
AR_ENABLE_FLOW_ENGINE=1 arx flow run --flow=feature_request_to_pr --task-id=T-metrics --dry-run

# Assert counters & P95
python3 scripts/assert_metrics.py --url http://localhost:9108/metrics --p95-ms 1200 > .artifacts/metrics_phase4.txt
cat .artifacts/metrics_phase4.txt
echo "✓ PHASE 4 PASS"
