# Testing Framework

The `tests/` directory contains the comprehensive testing suite for the AdvancedRules AI orchestration framework. This testing framework ensures the reliability, correctness, and quality of all framework components through automated validation.

## 🎯 Testing Philosophy

AdvancedRules employs a multi-layered testing approach that validates:
- **End-to-End Workflows**: Complete pipeline execution from planning to synthesis
- **Component Integration**: Individual component functionality and interactions
- **Critical Invariants**: Core system properties that must always hold
- **Regression Prevention**: Automated detection of functionality regressions

## 📁 Directory Structure

```
tests/
├── README.md                    # This testing framework overview
├── e2e/                        # End-to-end test suite
│   └── test_pipeline.py        # Golden path pipeline validation
└── smoke/                      # Smoke test suite
    └── test_scoring_validator.py # Scoring system validation
```

## 🧪 Test Suites Overview

### End-to-End Tests (`e2e/`)
**Purpose**: Validate complete workflow execution from start to finish

**Coverage**:
- **Pipeline Flow**: Complete execution from planning through synthesis
- **Artifact Generation**: All required artifacts are created correctly
- **Quality Gates**: All validation checkpoints pass
- **Integration Points**: Component interactions work seamlessly

**Key Test**: `test_pipeline.py`
- Executes the golden path: plan → audit → peer_review → synthesis
- Validates artifact creation and quality standards
- Ensures end-to-end workflow completion

### Smoke Tests (`smoke/`)
**Purpose**: Quick validation of critical system components

**Coverage**:
- **Decision Scoring**: Advanced scoring system functionality
- **Governance Validation**: Framework rules and compliance
- **Core Components**: Essential system capabilities
- **Configuration**: System setup and configuration validation

**Key Test**: `test_scoring_validator.py`
- Validates decision scoring v3 functionality
- Tests governance validator operations
- Ensures core system invariants

## 🚀 Running Tests

### Prerequisites
```bash
# Ensure Python dependencies are installed
pip install -r requirements.txt

# Install pytest if not already available
pip install pytest pytest-cov pytest-xdist
```

### Quick Test Execution
```bash
# Run all tests quietly
pytest -q

# Run with verbose output
pytest -v

# Run specific test suite
pytest tests/e2e/ -v
pytest tests/smoke/ -v

# Run specific test
pytest tests/e2e/test_pipeline.py -v
```

### Advanced Test Options
```bash
# Run with coverage report
pytest --cov=tools --cov-report=html

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run tests with debugging
pytest -v -s --pdb

# Generate test report
pytest --junitxml=test-results.xml
```

## 📊 Test Architecture

### Test Organization
- **Modular Design**: Tests are organized by functionality and scope
- **Independent Execution**: Tests can run independently without side effects
- **Clear Naming**: Test files and functions have descriptive names
- **Documentation**: Each test includes comprehensive documentation

### Test Data Management
- **Isolated Environments**: Tests run in isolated environments
- **Mock Data**: Uses mock data to avoid external dependencies
- **Cleanup**: Automatic cleanup of test artifacts
- **Reproducibility**: Tests produce consistent, reproducible results

## 🔧 Test Development

### Adding New Tests
1. **Identify Test Scope**: Determine what functionality to test
2. **Choose Test Type**: Select appropriate test suite (e2e/smoke/unit)
3. **Create Test File**: Follow naming conventions and structure
4. **Implement Test Logic**: Write clear, focused test functions
5. **Add Documentation**: Include comprehensive test documentation

### Test File Structure
```python
"""
Test module for [component/functionality]

This module contains tests for [specific functionality].
Tests ensure [what the tests validate].
"""

import pytest
from pathlib import Path
from tools.[component] import [functionality]


class Test[ComponentName]:
    """Test suite for [component] functionality."""

    def test_[specific_functionality](self):
        """Test that [specific functionality] works correctly."""
        # Test implementation
        pass

    def test_[edge_case](self):
        """Test [edge case] handling."""
        # Test implementation
        pass
```

### Best Practices
- **One Assertion Per Test**: Each test should validate one specific behavior
- **Descriptive Names**: Test names should clearly describe what they validate
- **Arrange-Act-Assert**: Structure tests with clear setup, execution, and validation phases
- **Independent Tests**: Tests should not depend on each other
- **Fast Execution**: Tests should execute quickly for frequent running

## 📈 Test Metrics & Reporting

### Coverage Analysis
```bash
# Generate coverage report
pytest --cov=tools --cov-report=html

# View coverage by component
pytest --cov=tools --cov-report=term-missing
```

### Test Results
- **Pass/Fail Status**: Clear indication of test success or failure
- **Execution Time**: Performance monitoring for test efficiency
- **Error Details**: Comprehensive error reporting for failed tests
- **Coverage Metrics**: Code coverage statistics and analysis

## 🔄 Continuous Integration

### CI/CD Integration
```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=tools --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Quality Gates
- **Test Execution**: All tests must pass before merge
- **Coverage Threshold**: Minimum code coverage requirements
- **Performance Benchmarks**: Test execution time limits
- **Artifact Validation**: Generated artifacts meet quality standards

## 🚨 Troubleshooting

### Common Test Issues
- **Import Errors**: Check Python path and dependencies
- **Environment Issues**: Ensure test environment is properly configured
- **Data Dependencies**: Verify test data is available and correct
- **Timing Issues**: Tests should not depend on specific timing

### Debug Mode
```bash
# Run tests with debugging output
pytest -v -s --pdb

# Run specific failing test
pytest tests/e2e/test_pipeline.py::TestPipeline::test_golden_path -v -s

# Run with logging
pytest --log-cli-level=INFO
```

## 📋 Maintenance & Evolution

### Regular Maintenance
- **Test Updates**: Keep tests current with code changes
- **Dependency Updates**: Update test dependencies and frameworks
- **Performance Monitoring**: Track and optimize test execution time
- **Coverage Analysis**: Maintain and improve code coverage

### Test Evolution
- **New Feature Tests**: Add tests for new framework capabilities
- **Regression Tests**: Create tests for identified bugs
- **Integration Tests**: Expand integration test coverage
- **Performance Tests**: Add performance and load testing

## 🔗 Integration with Framework

### Framework Components
- **Decision Scoring**: Tests validate scoring accuracy and calibration
- **Workflow Orchestration**: Tests verify state transitions and triggers
- **Memory Bank**: Tests ensure artifact integrity and management
- **Tools Suite**: Tests validate operational utilities

### External Systems
- **File System**: Tests validate file operations and permissions
- **Configuration**: Tests verify configuration loading and validation
- **External APIs**: Tests validate external service integrations
- **Database**: Tests ensure data persistence and retrieval

---

**Testing Framework** - Ensuring AdvancedRules reliability through comprehensive automated validation! 🧪✅

*For framework usage, see the main [README](../README.md). For test development guidelines, refer to the framework's testing standards.*