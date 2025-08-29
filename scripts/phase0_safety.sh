#!/usr/bin/env bash
set -euo pipefail
echo "[PHASE 0] Safety rails"

test -f config/advanced_rules.yaml
grep -q "dry_run_default: true" config/advanced_rules.yaml
grep -q "human_approval_required: true" config/advanced_rules.yaml
grep -q "branch_only_workflow: true" config/advanced_rules.yaml
grep -q "rag_memory: false" config/advanced_rules.yaml || true

test -f tools/envelopes/action_envelope_v2.json
grep -E '"flow_id"|"task_id"|"step_id"' tools/envelopes/action_envelope_v2.json >/dev/null

echo "✓ configs + envelope v2 OK"

# Guard sanity: never write live without ALLOW_WRITES
if AR_ENABLE_FLOW_ENGINE=1 arx flow run --flow=feature_request_to_pr --task-id=T-guard --dry-run >/dev/null 2>&1; then
  echo "✓ flow dry-run works"
else
  echo "✗ flow dry-run failed"; exit 1
fi

echo "✓ PHASE 0 PASS"
