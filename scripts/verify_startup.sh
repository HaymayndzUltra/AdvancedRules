#!/bin/bash
# AdvancedRules Framework - Startup Verification Script
# Run this to verify complete setup before starting workflow

set -e  # Exit on any error

echo "🛠️  AdvancedRules Framework - Startup Verification"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        echo -e "${YELLOW}   Fix: $3${NC}"
    fi
}

# 1. Environment Variables Check
echo "1. Environment Variables:"
ALLOW_RUN_CHECK=1
ALLOW_WRITES_CHECK=1
AR_METRICS_CHECK=1
AR_FLOW_CHECK=1

if [ "$ALLOW_RUN" = "1" ]; then
    print_status 0 "ALLOW_RUN is set"
    ALLOW_RUN_CHECK=0
else
    print_status 1 "ALLOW_RUN not set or incorrect" "export ALLOW_RUN=1"
fi

if [ "$ALLOW_WRITES" = "1" ]; then
    print_status 0 "ALLOW_WRITES is set"
    ALLOW_WRITES_CHECK=0
else
    print_status 1 "ALLOW_WRITES not set or incorrect" "export ALLOW_WRITES=1"
fi

if [ "$AR_ENABLE_METRICS" = "1" ]; then
    print_status 0 "AR_ENABLE_METRICS is set"
    AR_METRICS_CHECK=0
else
    print_status 1 "AR_ENABLE_METRICS not set or incorrect" "export AR_ENABLE_METRICS=1"
fi

if [ "$AR_ENABLE_FLOW_ENGINE" = "1" ]; then
    print_status 0 "AR_ENABLE_FLOW_ENGINE is set"
    AR_FLOW_CHECK=0
else
    print_status 1 "AR_ENABLE_FLOW_ENGINE not set or incorrect" "export AR_ENABLE_FLOW_ENGINE=1"
fi

# 2. Dependencies Check
echo ""
echo "2. Python Dependencies:"
python3 -c "
import sys
deps_ok = True

# Core dependencies
try:
    import yaml, networkx, pyyaml
    print('✅ Core dependencies: OK')
except ImportError as e:
    print('❌ Core dependencies missing:', e)
    deps_ok = False

# AI/ML dependencies (optional)
try:
    import chromadb, sentence_transformers
    print('✅ AI/ML dependencies: OK')
except ImportError as e:
    print('⚠️  AI/ML dependencies missing (optional):', e)

# Observability dependencies (optional)
try:
    import prometheus_client, celery, redis
    print('✅ Observability dependencies: OK')
except ImportError as e:
    print('⚠️  Observability dependencies missing (optional):', e)

sys.exit(0 if deps_ok else 1)
" 2>/dev/null
DEPS_STATUS=$?

# 3. File System Check
echo ""
echo "3. Required Files & Directories:"
if [ -f "config/advanced_rules.yaml" ]; then
    print_status 0 "Configuration file exists"
else
    print_status 1 "Configuration file missing" "Check config/advanced_rules.yaml"
fi

if [ -f "cli/main.py" ]; then
    print_status 0 "CLI script exists"
else
    print_status 1 "CLI script missing" "Check cli/main.py"
fi

if [ -d "memory-bank" ]; then
    print_status 0 "Memory bank directory exists"
else
    print_status 1 "Memory bank directory missing" "Check memory-bank/ directory"
fi

if [ -d "tools" ]; then
    print_status 0 "Tools directory exists"
else
    print_status 1 "Tools directory missing" "Check tools/ directory"
fi

# 4. CLI Functionality Check
echo ""
echo "4. CLI Functionality:"
if python3 cli/main.py --help >/dev/null 2>&1; then
    print_status 0 "CLI is functional"
else
    print_status 1 "CLI is not working" "Run: python3 cli/main.py --help"
fi

# 5. Pre-start Readiness Check
echo ""
echo "5. Pre-start Readiness:"
if python3 tools/run_role.py readiness >/dev/null 2>&1; then
    print_status 0 "Pre-start checks pass"
else
    print_status 1 "Pre-start checks fail" "Run: python3 tools/prestart/prestart_composite.py"
fi

# 6. Git Safety Check
echo ""
echo "6. Git Safety:"
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    print_status 1 "On main/master branch (unsafe)" "Switch to development branch: git checkout -b development"
else
    print_status 0 "Safe branch: $CURRENT_BRANCH"
fi

# 7. Overall Assessment
echo ""
echo "=================================================="
echo "🎯 OVERALL ASSESSMENT:"

CRITICAL_ISSUES=$((ALLOW_RUN_CHECK + ALLOW_WRITES_CHECK + AR_METRICS_CHECK + AR_FLOW_CHECK + DEPS_STATUS))

if [ $CRITICAL_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ READY TO START!${NC}"
    echo ""
    echo "🚀 You can now run:"
    echo "   python3 tools/quickstart.py"
    echo ""
    echo "Expected completion: SYNTHESIS_DONE state"
    echo "Expected artifacts: memory-bank/plan/* files"
else
    echo -e "${RED}❌ NOT READY - Fix critical issues first${NC}"
    echo ""
    echo "🔧 Critical issues to fix: $CRITICAL_ISSUES"
    echo ""
    echo "💡 Quick fix commands:"
    echo "   export ALLOW_RUN=1"
    echo "   export ALLOW_WRITES=1"
    echo "   export AR_ENABLE_METRICS=1"
    echo "   export AR_ENABLE_FLOW_ENGINE=1"
    echo "   pip install -r requirements.txt"
fi

echo ""
echo "📊 Verification completed at: $(date)"
echo "=================================================="

