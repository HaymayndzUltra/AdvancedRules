#!/bin/bash
# Test script to verify arx CLI installation

echo "==================================="
echo "Testing ARX CLI Installation"
echo "==================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check command
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 found at: $(which $1)"
        return 0
    else
        echo -e "${RED}✗${NC} $1 not found"
        return 1
    fi
}

# Function to run command and check result
run_command() {
    echo -e "\n${YELLOW}Running:${NC} $1"
    if eval $1; then
        echo -e "${GREEN}✓${NC} Command succeeded"
        return 0
    else
        echo -e "${RED}✗${NC} Command failed"
        return 1
    fi
}

# Step 1: Check Python
echo -e "\n1. Checking Python installation..."
check_command python3

# Step 2: Install package in editable mode
echo -e "\n2. Installing package in editable mode..."
run_command "pip install -e . --quiet"

# Step 3: Check if arx command is available
echo -e "\n3. Checking arx command..."
if check_command arx; then
    # Step 4: Test arx help
    echo -e "\n4. Testing arx --help..."
    run_command "arx --help | head -5"
    
    # Step 5: Test arx memory subcommand
    echo -e "\n5. Testing arx memory --help..."
    run_command "arx memory --help | head -5"
else
    echo -e "${YELLOW}Falling back to python module invocation...${NC}"
    
    # Test with python -m
    echo -e "\n4. Testing python -m cli.main --help..."
    run_command "PYTHONPATH=. python3 -m cli.main --help | head -5"
    
    echo -e "\n5. Testing python -m cli.main memory --help..."
    run_command "PYTHONPATH=. python3 -m cli.main memory --help | head -5"
fi

# Step 6: Test with environment variable
echo -e "\n6. Testing with AR_ENABLE_RAG environment variable..."
export AR_ENABLE_RAG=1
export AR_EMBED_MODEL="BAAI/bge-m3"

if command -v arx &> /dev/null; then
    echo "Would run: AR_ENABLE_RAG=1 arx memory index --src=. --namespaces=coder --persona=CODER_AI --reindex"
else
    echo "Would run: AR_ENABLE_RAG=1 PYTHONPATH=. python3 -m cli.main memory index --src=. --namespaces=coder --persona=CODER_AI --reindex"
fi

echo -e "\n${GREEN}==================================="
echo "Test Complete!"
echo "===================================${NC}"