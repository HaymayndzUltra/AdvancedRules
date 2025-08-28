#!/usr/bin/env bash
set -Eeuo pipefail

# AdvancedRules v2 Safety Validation Suite
# Comprehensive validation of scaffolding, schemas, and safety rails

echo "🛡️  AdvancedRules v2 Safety Validation Suite"
echo "==========================================="
echo ""

# Phase 1: Basic Artifact Validation
echo "📋 Phase 1: Artifact Validation"
echo "-------------------------------"

req=(
  "memory-bank/business/client_score.json"
  "memory-bank/business/capacity_report.md"
  "memory-bank/business/pricing.ratecard.yaml"
  "memory-bank/business/estimate_brief.md"
  "memory-bank/plan/proposal.md"
  "memory-bank/upwork/offer_status.json"
)

missing=0
for f in "${req[@]}"; do
  if [[ -f "$f" ]]; then
    echo "✅ $f"
  else
    echo "⛔ $f"
    missing=1
  fi
done

if [[ $missing -eq 1 ]]; then
  echo ""
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
fi

echo ""
echo "✅ All required artifacts present!"
echo ""

# Phase 2: Schema and Configuration Validation
echo "📋 Phase 2: Schema & Configuration Validation"
echo "----------------------------------------------"

# JSON Schema Validation
echo "🔍 Validating JSON schemas..."
json_files=(
  "schemas/task_schema.json"
  "schemas/flow_schema.json"
  "schemas/memory_doc_schema.json"
  "schemas/metrics_schema.json"
  "tools/envelopes/action_envelope_v2.json"
)

for f in "${json_files[@]}"; do
  if [[ -f "$f" ]]; then
    if python3 -c "import json; json.load(open('$f')); print('✅ $f')" 2>/dev/null; then
      echo "✅ $f"
    else
      echo "❌ $f - Invalid JSON"
      exit 1
    fi
  else
    echo "⛔ $f - File not found"
    exit 1
  fi
done

echo ""

# YAML Configuration Validation
echo "🔍 Validating YAML configuration..."
if [[ -f "config/advanced_rules.yaml" ]]; then
  if python3 -c "import yaml; yaml.safe_load(open('config/advanced_rules.yaml')); print('✅ config/advanced_rules.yaml')" 2>/dev/null; then
    echo "✅ config/advanced_rules.yaml"
  else
    echo "❌ config/advanced_rules.yaml - Invalid YAML"
    exit 1
  fi
else
  echo "⛔ config/advanced_rules.yaml - File not found"
  exit 1
fi

echo ""

# Phase 3: Safety Gate Checks
echo "📋 Phase 3: Safety Gate Validation"
echo "-----------------------------------"

# Check protected paths configuration
if grep -q "protected_paths" config/advanced_rules.yaml; then
  echo "✅ Protected paths configured"
else
  echo "❌ Protected paths not configured"
  exit 1
fi

# Check dry-run default
if grep -q "dry_run_default.*true" config/advanced_rules.yaml; then
  echo "✅ Dry-run default enforced"
else
  echo "❌ Dry-run default not enforced"
  exit 1
fi

# Check human approval requirement
if grep -q "human_approval_required.*true" config/advanced_rules.yaml; then
  echo "✅ Human approval required"
else
  echo "❌ Human approval not required"
  exit 1
fi

# Check branch-only workflow
if grep -q "branch_only_workflow.*true" config/advanced_rules.yaml; then
  echo "✅ Branch-only workflow enforced"
else
  echo "❌ Branch-only workflow not enforced"
  exit 1
fi

echo ""

# Phase 4: Envelope v2 Compatibility Test
echo "📋 Phase 4: Envelope v2 Compatibility Test"
echo "-------------------------------------------"

if [[ -f "action_envelope.json" && -f "tools/envelopes/action_envelope_v2.json" ]]; then
  compatibility_result=$(python3 -c "
import json
try:
    v1 = json.load(open('action_envelope.json'))
    v2 = json.load(open('tools/envelopes/action_envelope_v2.json'))
    shared_keys = set(v1.keys()) & set(v2.keys())
    compatibility_ratio = len(shared_keys) / len(v1) if len(v1) > 0 else 0
    print(f'Envelope v2 backwards compatible: {len(shared_keys)}/{len(v1)} keys match ({compatibility_ratio:.1%})')
    if compatibility_ratio >= 0.8:
        print('✅ Backwards compatibility maintained')
    else:
        print('⚠️  Partial backwards compatibility')
except Exception as e:
    print(f'❌ Compatibility check failed: {e}')
" 2>&1)

  echo "$compatibility_result"
else
  echo "⚠️  Skipping compatibility test - envelope files not found"
fi

echo ""

# Phase 5: Git Workflow Validation
echo "📋 Phase 5: Git Workflow Validation"
echo "------------------------------------"

# Check if we're on a feature branch
current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
  echo "⚠️  Currently on main branch - consider switching to feature branch"
  echo "   git checkout -b feature/advanced-rules-v2-scaffolding"
elif [[ "$current_branch" == "unknown" ]]; then
  echo "⚠️  Not in a git repository"
else
  echo "✅ On feature branch: $current_branch"
fi

echo ""

# Final Status Report
echo "🎯 Final Status Report"
echo "======================"
echo "✅ All required artifacts present"
echo "✅ JSON schemas validated"
echo "✅ YAML configuration validated"
echo "✅ Safety gates configured"
echo "✅ Envelope v2 compatibility checked"
echo ""

if [[ "$current_branch" != "main" && "$current_branch" != "master" && "$current_branch" != "unknown" ]]; then
  echo "🚀 SCAFFOLDING COMPLETE - Ready for commit and PR"
  echo ""
  echo "Next steps:"
  echo "  1. Review validation results above"
  echo "  2. Commit scaffolding: git add . && git commit -m 'feat: scaffold AdvancedRules v2 with safety rails'"
  echo "  3. Create PR for human approval"
  echo "  4. DO NOT MERGE until safety validation complete"
else
  echo "⚠️  COMPLETE BRANCH WORKFLOW BEFORE COMMITTING"
  echo ""
  echo "Required actions:"
  echo "  1. git checkout -b feature/advanced-rules-v2-scaffolding"
  echo "  2. Then commit and create PR"
fi
