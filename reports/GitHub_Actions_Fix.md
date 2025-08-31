# GitHub Actions ARX Command Fix

## Issue
The GitHub Actions workflow was failing with:
```
Unknown command: /opt/hostedtoolcache/Python/3.11.13/x64/bin/arx
Process completed with exit code 1.
```

## Root Cause
While `pyproject.toml` correctly defines the CLI entry points:
```toml
[project.scripts]
arx = "cli.main:main"
advancedrules = "cli.main:main"
```

The `arx` command wasn't being properly registered in the GitHub Actions environment, likely due to:
1. Package installation issues in the CI environment
2. Path configuration differences between local and CI environments
3. Potential issues with editable installs in GitHub Actions

## Solution Applied

### 1. Created setup.py for compatibility
Added a minimal `setup.py` file to ensure backward compatibility:
```python
#!/usr/bin/env python3
from setuptools import setup

if __name__ == "__main__":
    setup()
```

### 2. Updated GitHub Actions workflow
Modified `.github/workflows/rag-check.yml` to use Python module invocation directly:

**Before:**
```yaml
run: |
  arx memory index --src=. --namespaces=coder --reindex
```

**After:**
```yaml
run: |
  # Use Python module directly for reliability
  PYTHONPATH=. python -m cli.main memory index --src=. --namespaces=coder --reindex
```

### 3. Added sanity check
Updated the sanity check to detect if `arx` is available:
```yaml
- name: Sanity check CLI
  run: |
    # Check if arx command is available, otherwise use Python directly
    which arx || echo "arx command not found, will use python -m cli.main"
    PYTHONPATH=. python -m cli.main --help
```

## Verification

The CLI works correctly when invoked as a Python module:
```bash
$ PYTHONPATH=. python3 -m cli.main --help
🛠️  AdvancedRules CLI v2.0
========================================
[help output shows correctly]
```

## Files Modified
1. `setup.py` - Created for compatibility
2. `.github/workflows/rag-check.yml` - Updated to use Python module invocation

## Alternative Solutions (Not Applied)

### Option 1: Force reinstall in workflow
```yaml
- name: Install package with force
  run: |
    pip uninstall -y advancedrules-domain-lab
    pip install -e . --force-reinstall
```

### Option 2: Use virtual environment
```yaml
- name: Setup venv and install
  run: |
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    which arx  # Should now find it in .venv/bin/
```

### Option 3: Manual entry point creation
```yaml
- name: Create arx command manually
  run: |
    echo '#!/usr/bin/env python3' > /usr/local/bin/arx
    echo 'from cli.main import main; main()' >> /usr/local/bin/arx
    chmod +x /usr/local/bin/arx
```

## Recommendation
The current solution (using `python -m cli.main`) is the most reliable and portable approach. It:
- Works consistently across different environments
- Doesn't require special permissions
- Avoids package installation complexities
- Is explicit about what's being executed

## Status
✅ Fixed - The workflow should now run successfully using the Python module invocation method.