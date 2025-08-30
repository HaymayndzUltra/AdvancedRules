#!/bin/bash
# Run tests for AdvancedRules framework
# Phase 0 - Baseline test runner

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AdvancedRules Test Runner ===${NC}"
echo

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
python3 -c "import pytest" 2>/dev/null || {
    echo -e "${RED}ERROR: pytest not installed${NC}"
    echo "Install with: pip install --break-system-packages pytest pytest-cov"
    exit 1
}

python3 -c "import yaml" 2>/dev/null || {
    echo -e "${RED}ERROR: pyyaml not installed${NC}"
    echo "Install with: pip install --break-system-packages pyyaml"
    exit 1
}

python3 -c "import networkx" 2>/dev/null || {
    echo -e "${RED}ERROR: networkx not installed${NC}"
    echo "Install with: pip install --break-system-packages networkx"
    exit 1
}

echo -e "${GREEN}Dependencies OK${NC}"
echo

# Check if arx CLI is available
echo -e "${YELLOW}Checking arx CLI...${NC}"
if python3 -m cli.main --version >/dev/null 2>&1; then
    echo -e "${GREEN}arx CLI available via Python module${NC}"
elif which arx >/dev/null 2>&1; then
    echo -e "${GREEN}arx CLI installed${NC}"
else
    echo -e "${YELLOW}WARNING: arx CLI not found, using stub for tests${NC}"
fi
echo

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
python3 -m pytest tests/ -v --tb=short --color=yes || {
    EXIT_CODE=$?
    echo
    echo -e "${YELLOW}Test run completed with exit code $EXIT_CODE${NC}"
    echo -e "${YELLOW}Known issue: test_cycle_detection expected to fail (see REPORT_A.md)${NC}"
    exit $EXIT_CODE
}

echo
echo -e "${GREEN}All tests passed!${NC}"