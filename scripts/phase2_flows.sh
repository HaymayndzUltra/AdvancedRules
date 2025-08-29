#!/usr/bin/env bash
set -euo pipefail
echo "[PHASE 2] Declarative flows"

arx flow lint --flow=feature_request_to_pr
echo "✓ lint feature_request_to_pr"

# Expect the buggy flow to fail lint (if present)
if arx flow lint --flow=bugfix_ci_loop >/dev/null 2>&1; then
  echo "ℹ️ bugfix_ci_loop lint passed (ok if you fixed it)"
else
  echo "✓ bugfix_ci_loop correctly failed lint"
fi

AR_ENABLE_FLOW_ENGINE=1 arx flow run --flow=feature_request_to_pr --task-id=T-2001 --dry-run
echo "✓ dry-run execution OK"

# Branch guard (only if current branch == main)
cur=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
if [ "$cur" = "main" ] || [ "$cur" = "master" ]; then
  if AR_ENABLE_FLOW_ENGINE=1 arx flow run --flow=feature_request_to_pr --task-id=T-2002 --dry-run >/dev/null 2>&1; then
    echo "✗ should block on main"; exit 1
  else
    echo "✓ blocked on main branch"
  fi
else
  echo "ℹ️ not on main, branch guard skipped"
fi

echo "✓ PHASE 2 PASS"
