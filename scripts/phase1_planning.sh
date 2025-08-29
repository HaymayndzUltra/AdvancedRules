#!/usr/bin/env bash
set -euo pipefail
echo "[PHASE 1] Planning pipeline"

out=$(arx tasks plan "Bootstrap smoke plan" 2>&1 || true)
echo "$out" | grep -E "planned|Task|Steps" >/dev/null || { echo "✗ planning failed"; exit 1; }

arx tasks print >/dev/null 2>&1
echo "✓ planning/print OK"
echo "✓ PHASE 1 PASS"
