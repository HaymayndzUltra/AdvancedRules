# AdvancedRules Test Suite

This directory contains all tests for the AdvancedRules framework.

## Structure

- `test_memory_basic.py` - Basic memory/RAG tests
- `test_planning_pipeline.py` - Planning pipeline tests
- `smoke/` - Smoke tests
- `e2e/` - End-to-end tests
- `conftest.py` - Test configuration and fixtures

## Prerequisites

### Required Dependencies

Install test dependencies:
```bash
pip install -r requirements.txt
pip install -e .  # Install package in editable mode for arx CLI
```

Required packages:
- pytest >= 7.0.0
- pyyaml >= 6.0
- networkx >= 2.8
- Other dependencies listed in requirements.txt

### ARX CLI

Some tests require the `arx` CLI to be available. The test suite handles this in two ways:

1. **Automatic Stub**: Tests that require `arx` will use a stub implementation if the real CLI is not available
2. **Skip Tests**: Tests can be skipped if `arx` is not installed using the `@requires_arx` decorator

To install the real `arx` CLI:
```bash
pip install -e .
# Verify installation
arx --version
# Or use Python module directly
python -m cli.main --version
```

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run with verbose output:
```bash
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/test_memory_basic.py
```

### Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

### Skip tests requiring arx:
```bash
pytest tests/ -m "not requires_arx"
```

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

- `arx_stub`: Provides a stub implementation of the arx CLI for testing
- `arx_command`: Returns the appropriate command to invoke arx (either installed or via Python module)
- `temp_workspace`: Creates a temporary workspace with basic structure
- `mock_arx_env`: Sets up test environment variables

## CI/CD Integration

Tests are automatically run in CI via GitHub Actions. The CI pipeline:
1. Lints code with flake8 and black
2. Runs tests across Python 3.8-3.11
3. Validates YAML schemas
4. Checks memory/RAG system
5. Runs integration tests

See `.github/workflows/ci.yml` for full CI configuration.

## Writing New Tests

When adding new tests:
1. Use the `arx_stub` fixture for tests that call the arx CLI
2. Use `pytest.skip()` for tests that require specific conditions
3. Add appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`, etc.)
4. Follow existing test patterns for consistency