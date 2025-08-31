#!/bin/bash
# Test all three methods of running the CLI

echo "============================================="
echo "Testing All CLI Invocation Methods"
echo "============================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "\n${BLUE}Method A: Console Script (arx command)${NC}"
echo "----------------------------------------"
if command -v arx >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} arx found at: $(which arx)"
    echo "Running: arx --help | head -3"
    arx --help | head -3
else
    echo -e "${YELLOW}⚠${NC} arx not in PATH"
fi

echo -e "\n${BLUE}Method B: Module Run (python -m)${NC}"
echo "----------------------------------------"
echo "Running: PYTHONPATH=\$PWD python3 -m cli.main --help | head -3"
PYTHONPATH=$PWD python3 -m cli.main --help | head -3
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Module invocation works"
else
    echo -e "${RED}✗${NC} Module invocation failed"
fi

echo -e "\n${BLUE}Method C: Direct Function Call${NC}"
echo "----------------------------------------"
echo "Running direct Python function call..."
python3 - <<'PY'
import sys, os
sys.path.insert(0, os.getcwd())
try:
    from cli.main import main
    print("✓ Successfully imported cli.main")
    # Simulate: arx --help
    sys.argv = ["arx", "--help"]
    # Don't actually run main() in test, just verify it's callable
    if callable(main):
        print("✓ main() is callable")
    else:
        print("✗ main() is not callable")
except ImportError as e:
    print(f"✗ Import failed: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
PY

echo -e "\n${BLUE}Testing Memory Command with All Methods${NC}"
echo "============================================="

# Test command
TEST_CMD="memory --help"

echo -e "\n1. Using arx (if available):"
if command -v arx >/dev/null 2>&1; then
    arx $TEST_CMD | head -3
else
    echo "   Skipped (arx not available)"
fi

echo -e "\n2. Using module invocation:"
PYTHONPATH=$PWD python3 -m cli.main $TEST_CMD | head -3

echo -e "\n3. Using direct function call:"
python3 - <<'PY'
import sys, os
sys.path.insert(0, os.getcwd())
from cli.main import main
sys.argv = ["arx", "memory", "--help"]
try:
    # Capture output instead of exiting
    import io
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            main()
        except SystemExit:
            pass  # Ignore exit
    
    output = f.getvalue()
    # Print first 3 lines
    lines = output.split('\n')[:3]
    for line in lines:
        if line:
            print(line)
except Exception as e:
    print(f"Error: {e}")
PY

echo -e "\n${GREEN}============================================="
echo "Test Complete!"
echo "=============================================${NC}"

echo -e "\n${YELLOW}Recommended for CI/CD:${NC}"
echo "Use Method B (module invocation) as fallback:"
echo -e "${BLUE}if command -v arx >/dev/null 2>&1; then"
echo "    arx memory index --src=. --namespaces=coder --reindex"
echo "else"
echo "    PYTHONPATH=\$PWD python3 -m cli.main memory index --src=. --namespaces=coder --reindex"
echo -e "fi${NC}"