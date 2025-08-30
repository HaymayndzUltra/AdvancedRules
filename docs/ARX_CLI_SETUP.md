# ARX CLI Setup Guide

## Overview
The `arx` command is the main CLI interface for AdvancedRules. It's defined in `pyproject.toml` and requires proper installation to work.

## Installation

### Local Development
```bash
# Install in editable mode (recommended for development)
pip install -e .

# Verify installation
which arx
arx --help
```

### CI/CD Environment
```yaml
# In GitHub Actions workflow
- name: Install package
  run: |
    pip install -e .
    which arx
    arx --help
```

## Configuration

### Entry Point Definition
The `arx` command is defined in `pyproject.toml`:
```toml
[project.scripts]
arx = "cli.main:main"
advancedrules = "cli.main:main"
```

This creates two equivalent commands:
- `arx` - Primary command
- `advancedrules` - Alternative name

### Required Files
1. `pyproject.toml` - Package configuration with entry points
2. `setup.py` - Minimal setup file for compatibility
3. `cli/main.py` - Main CLI module with `main()` function

## Usage Examples

### Basic Commands
```bash
# Show help
arx --help

# Show version
arx --version

# Memory operations
arx memory --help
arx memory index --src=. --namespaces=coder --reindex
arx memory query --persona=CODER_AI --query "test" --k=3

# Flow operations
arx flow list
arx flow lint --flow=feature_request_to_pr
arx flow run --flow=feature_request_to_pr

# Task operations
arx tasks plan "implement feature X"
arx tasks print
```

### With Environment Variables
```bash
# Enable RAG for memory operations
AR_ENABLE_RAG=1 AR_EMBED_MODEL="BAAI/bge-m3" arx memory index --src=. --namespaces=coder --persona=CODER_AI --reindex

# Set metrics port for observability
AR_METRICS_PORT=9108 arx obs serve
```

## Troubleshooting

### Command Not Found
If `arx` command is not found after installation:

1. **Check installation:**
   ```bash
   pip list | grep advancedrules
   ```

2. **Reinstall in editable mode:**
   ```bash
   pip uninstall advancedrules-domain-lab -y
   pip install -e .
   ```

3. **Use fallback method:**
   ```bash
   # If arx doesn't work, use Python module directly
   PYTHONPATH=. python -m cli.main --help
   ```

### Virtual Environment Issues
In some environments (like GitHub Actions), you may need to use a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
which arx  # Should show .venv/bin/arx
```

### Permission Issues
If you get permission errors:

```bash
# Install for current user only
pip install --user -e .

# Or use virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Test ARX CLI
on: [push, pull_request]

jobs:
  test-cli:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -U pip setuptools wheel
          pip install -r requirements.txt
          pip install -e .
      
      - name: Verify CLI
        run: |
          which arx
          arx --help
      
      - name: Run CLI commands
        env:
          AR_ENABLE_RAG: "1"
        run: |
          arx memory index --src=. --namespaces=coder --reindex
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

# Verify installation
RUN which arx && arx --help

CMD ["arx", "--help"]
```

## Testing Installation

Use the provided test script:
```bash
# Run installation test
./scripts/test_arx_installation.sh
```

Or manually test:
```bash
# Test installation
pip install -e .
which arx
arx --help

# Test memory commands
AR_ENABLE_RAG=1 arx memory index --src=. --namespaces=coder --persona=CODER_AI --reindex

# Test with sample query
AR_ENABLE_RAG=1 arx memory query --persona=CODER_AI --query "flow_runner" --k=3
```

## Development Tips

1. **Always use editable install during development:**
   ```bash
   pip install -e .
   ```
   This allows changes to take effect immediately without reinstalling.

2. **Use environment variables for configuration:**
   ```bash
   export AR_ENABLE_RAG=1
   export AR_EMBED_MODEL="BAAI/bge-m3"
   ```

3. **Test in clean environment:**
   ```bash
   python -m venv test_env
   source test_env/bin/activate
   pip install -e .
   arx --help
   deactivate
   rm -rf test_env
   ```

## Summary

The `arx` CLI is properly configured when:
1. ✅ `pip install -e .` completes successfully
2. ✅ `which arx` shows the command location
3. ✅ `arx --help` displays help information
4. ✅ All subcommands (memory, flow, tasks, obs) are accessible

For CI/CD, always include these verification steps to ensure proper installation before running commands.