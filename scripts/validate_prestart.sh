#!/usr/bin/env bash
set -Eeuo pipefail

# PRE-START Artifact Validator
# Quick check before running /preflight

req=(
  "memory-bank/business/client_score.json"
  "memory-bank/business/capacity_report.md"
  "memory-bank/business/pricing.ratecard.yaml"
  "memory-bank/business/estimate_brief.md"
  "memory-bank/plan/proposal.md"
  "memory-bank/upwork/offer_status.json"
)

echo "🔍 PRE-START Artifact Validator"
echo "================================"
echo "Checking required artifacts..."
echo ""

missing=0
for f in "${req[@]}"; do
  if [[ -f "$f" ]]; then
    echo "✅ $f"
  else
    echo "⛔ $f"
    missing=1
  fi
done

echo ""
if [[ $missing -eq 1 ]]; then
  echo "❌ PRE-START incomplete. Fix missing artifacts before running /preflight."
  echo ""
  echo "Commands to run:"
  echo "  /pricing      → pricing.ratecard.yaml"
  echo "  /screen_client → client_score.json, red_flags.md"
  echo "  /capacity     → capacity_report.md"
  echo "  /estimate     → estimate_brief.md"
  echo "  /proposal     → proposal.md"
  echo "  /upwork_checks → offer_status.json"
  exit 1
else
  echo "✅ All required artifacts present!"
  echo "🚀 Ready to run /preflight"
  echo ""
  echo "Next steps:"
  echo "  1. Run /preflight to validate gate"
  echo "  2. If PASS → phase = PLAN"
  echo "  3. If BLOCK → check error message"
fi
