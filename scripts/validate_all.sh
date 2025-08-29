#!/usr/bin/env bash
set -euo pipefail
echo "== AdvancedRules Validation Suite =="
make validate
echo "✅ ALL PHASES PASSED"
