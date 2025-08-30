# CI/CD CLI Fix - Proper Module Invocation

## The Problem
The error `Unknown command: /opt/hostedtoolcache/Python/3.11.13/x64/bin/arx` or `Unknown command: /workspace/cli/main.py` happens when:
1. The CLI is invoked as a file path instead of a module
2. The `arx` command isn't properly installed in PATH

## The Solution

### ✅ CORRECT: Module Invocation (Fallback)
```bash
# Module run - NOT file path!
PYTHONPATH=$PWD python -m cli.main memory index --src=. --namespaces=coder --persona=CODER_AI --reindex
```

### ❌ WRONG: File Path Invocation
```bash
# DON'T DO THIS - triggers "Unknown command" error
python /path/to/cli/main.py memory ...
arx /path/to/cli/main.py ...
```

## GitHub Actions Workflow Fix

Replace your failing steps with this pattern:

```yaml
- name: Install deps + package
  run: |
    set -euxo pipefail
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -r requirements.txt
    pip install -e .

- name: Sanity check CLI
  run: |
    # Verify module import works
    python -c "import cli, sys; from cli.main import main; print('OK: import main')"
    
    # Check if arx command is available
    if command -v arx >/dev/null 2>&1; then
      echo "✓ arx command found at: $(which arx)"
      arx --help | head -3
    else
      echo "⚠ arx not in PATH, using module fallback"
      PYTHONPATH=$PWD python -m cli.main --help | head -3
    fi

- name: RAG index
  env:
    AR_ENABLE_RAG: "1"
    AR_EMBED_MODEL: "BAAI/bge-m3"
  run: |
    set -euxo pipefail
    if command -v arx >/dev/null 2>&1; then
      arx memory index --src=. --namespaces=coder --persona=CODER_AI --reindex
    else
      # Module run fallback (NOT file path!)
      PYTHONPATH=$PWD python -m cli.main memory index --src=. --namespaces=coder --persona=CODER_AI --reindex
    fi
```

## Three Methods of CLI Invocation

### Method A: Console Script (Best when available)
```bash
pip install -e .
arx memory index --src=. --namespaces=coder --reindex
```

### Method B: Module Run (Best fallback for CI)
```bash
PYTHONPATH=$PWD python -m cli.main memory index --src=. --namespaces=coder --reindex
```

### Method C: Direct Function Call (Most reliable but verbose)
```python
python - <<'PY'
import sys, os
sys.path.insert(0, os.getcwd())
from cli.main import main
sys.argv = ["arx", "memory", "index", "--src=.", "--namespaces=coder", "--persona=CODER_AI", "--reindex"]
raise SystemExit(main())
PY
```

## Quick Sanity Checks

Run these to verify your setup:

```bash
# 1. Check package installation
pip install -e .

# 2. Verify module import
python -c "import cli, sys; from cli.main import main; print('OK: import main')"

# 3. Test with arx (if available)
arx --help | head -3

# 4. Test with module invocation (fallback)
PYTHONPATH=$PWD python -m cli.main --help | head -3
```

## Key Requirements

1. **`cli/__init__.py`** must exist (makes it a package)
2. **`cli/main.py`** must have a `main()` function
3. **`pyproject.toml`** must define entry points:
   ```toml
   [project.scripts]
   arx = "cli.main:main"
   ```

## Environment Variables for RAG

Always set these when using memory commands:

```bash
export AR_ENABLE_RAG=1
export AR_EMBED_MODEL="BAAI/bge-m3"
```

## Complete Working Example

```bash
#!/bin/bash
set -euxo pipefail

# Install
pip install -e .

# Set environment
export AR_ENABLE_RAG=1
export AR_EMBED_MODEL="BAAI/bge-m3"

# Run with fallback
if command -v arx >/dev/null 2>&1; then
    echo "Using arx command"
    arx memory index --src=. --namespaces=coder --persona=CODER_AI --reindex
else
    echo "Using module fallback"
    PYTHONPATH=$PWD python -m cli.main memory index --src=. --namespaces=coder --persona=CODER_AI --reindex
fi
```

## Summary

The key fix is:
- **Use `python -m cli.main`** (module invocation)
- **NOT `python /path/to/cli/main.py`** (file path)
- **Set `PYTHONPATH=$PWD`** to ensure modules are found

This prevents the "Unknown command" error and ensures the CLI works in CI/CD environments where `arx` might not be in PATH.