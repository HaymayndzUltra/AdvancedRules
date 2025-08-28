# Tools Directory

The `tools/` directory contains the execution utilities and automation scripts that power the AdvancedRules AI orchestration framework. These tools provide the operational backbone for the solo-freelancer pipeline, enabling seamless AI persona coordination, decision scoring, and workflow management.

## 📁 Directory Structure

```
tools/
├── artifacts/                   # Provenance and artifact management
│   ├── hash_index.py           # SHA-256 hashing and indexing
│   └── __pycache__/            # Python bytecode cache
├── audit/                       # Audit and evidence management
│   └── diff_evidence.py        # Evidence collection and citation
├── decision_scoring/            # Advanced decision scoring system
│   ├── advanced_score.py       # V3 scorer with calibration
│   ├── calibrate.py            # Scoring calibration tools
│   ├── calibration.json        # Calibration data
│   ├── compute_metrics.py      # Metrics computation
│   ├── execute_envelope.sh     # Envelope execution script
│   ├── metrics.py              # Scoring metrics
│   ├── score.py                # Core scoring engine
│   ├── thresholds.json         # Scoring thresholds
│   ├── weights.json            # Scoring weights configuration
│   ├── examples/               # Example configurations
│   └── README.md               # Decision scoring documentation
├── observability/               # Monitoring and logging
│   └── aggregate.py            # Log aggregation and reporting
├── orchestrator/                # Workflow orchestration
│   ├── state.py                # Workflow state management
│   ├── trigger_next.py         # Next action triggering
│   └── README.md               # Orchestrator documentation
├── prestart/                    # Pre-project readiness
│   ├── ensure_readiness.py     # Readiness validation
│   ├── prestart_composite.py   # Composite preflight checks
│   └── __pycache__/            # Python bytecode cache
├── rule_attach/                 # Rule attachment detection
│   └── detect.py               # Deterministic rule attachment
├── runner/                      # AI role execution engine
│   ├── io_utils.py             # Input/output utilities
│   ├── plugins/                # Role-specific plugins
│   └── README.md               # Runner documentation
├── schema/                      # Schema validation tools
│   └── validate_artifacts.py   # Artifact schema validation
├── upwork/                      # Upwork platform integration
│   └── adapter.py              # Upwork API adapter
├── orchestrator_postrun.py     # Post-run orchestration
├── quickstart.py               # One-command execution pipeline
├── run_role.py                 # Individual role execution
└── README.md                   # This documentation
```

## 🎯 Core Components

### 🤖 Role Execution Engine (`runner/`)
- **Purpose**: Execute individual AI personas with proper context and logging
- **Capabilities**: Artifact generation, event logging, error handling
- **Integration**: Works with all framework personas and maintains state

### 🧠 Decision Scoring System (`decision_scoring/`)
- **Purpose**: Advanced scoring system for action selection and prioritization
- **Features**: V3 scorer with calibration, exploration, and shadow scoring
- **Capabilities**: Multi-criteria evaluation, threshold management, metrics computation

### 🎼 Workflow Orchestrator (`orchestrator/`)
- **Purpose**: Coordinate complex multi-step workflows and state transitions
- **Features**: State engine, trigger system, idempotent operations
- **Capabilities**: Workflow state management, next-action triggering, error recovery

### 📊 Observability & Monitoring (`observability/`)
- **Purpose**: Aggregate logs, events, and metrics into comprehensive reports
- **Features**: Real-time monitoring, trend analysis, performance metrics
- **Capabilities**: Log aggregation, observability summaries, alerting

### 🔍 Audit & Provenance (`artifacts/`, `audit/`)
- **Purpose**: Maintain data integrity and provide audit trails
- **Features**: SHA-256 hashing, evidence collection, citation management
- **Capabilities**: Provenance tracking, integrity verification, compliance logging

## 🚀 Quick Start Commands

### One-Command Pipeline
```bash
# Execute complete happy path (readiness → roles → audit → scoring)
python3 tools/quickstart.py
```

### Individual Component Execution
```bash
# Pre-project readiness validation
python3 tools/prestart/prestart_composite.py

# Individual AI role execution
python3 tools/run_role.py product_owner_ai
python3 tools/run_role.py planning_ai
python3 tools/run_role.py auditor_ai
python3 tools/run_role.py principal_engineer_ai --mode PEER_REVIEW
python3 tools/run_role.py principal_engineer_ai --mode SYNTHESIS

# Decision scoring with advanced features
python3 tools/decision_scoring/advanced_score.py

# Trigger next workflow step (dry run)
python3 tools/orchestrator/trigger_next.py --dry-run --candidates tools/decision_scoring/examples/trigger_candidates.json

# Generate observability summary
python3 tools/observability/aggregate.py
```

## 🔧 Advanced Operations

### Decision Scoring Calibration
```bash
# Calibrate scoring system
python3 tools/decision_scoring/calibrate.py

# Compute scoring metrics
python3 tools/decision_scoring/compute_metrics.py

# Execute action envelope
bash tools/decision_scoring/execute_envelope.sh
```

### State Management & Orchestration
```bash
# Check current workflow state
python3 tools/orchestrator/state.py --status

# Trigger next action based on scoring
python3 tools/orchestrator/trigger_next.py --execute

# Run post-execution orchestration
python3 tools/orchestrator_postrun.py
```

### Validation & Quality Assurance
```bash
# Validate all artifacts against schemas
python3 tools/schema/validate_artifacts.py

# Verify artifact integrity
python3 tools/artifacts/hash_index.py --verify

# Run comprehensive audit
python3 tools/audit/diff_evidence.py --comprehensive
```

### Upwork Integration
```bash
# Update offer status
python3 tools/upwork/adapter.py --update-status

# Sync with Upwork platform
python3 tools/upwork/adapter.py --sync
```

## 📊 Tool Capabilities Matrix

| Component | Execution | Scoring | State Mgmt | Observability | Validation |
|-----------|-----------|---------|------------|---------------|------------|
| `runner/` | ✅ | ❌ | ✅ | ✅ | ❌ |
| `decision_scoring/` | ❌ | ✅ | ❌ | ✅ | ❌ |
| `orchestrator/` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `observability/` | ❌ | ❌ | ❌ | ✅ | ❌ |
| `artifacts/` | ❌ | ❌ | ❌ | ✅ | ✅ |
| `audit/` | ❌ | ❌ | ❌ | ✅ | ✅ |
| `schema/` | ❌ | ❌ | ❌ | ❌ | ✅ |
| `prestart/` | ✅ | ❌ | ✅ | ✅ | ✅ |

## 🔄 Integration Patterns

### Pipeline Execution Flow
1. **Prestart Phase**: `prestart_composite.py` validates readiness
2. **Role Execution**: `run_role.py` executes AI personas sequentially
3. **Scoring Phase**: `advanced_score.py` evaluates action candidates
4. **Orchestration**: `trigger_next.py` determines next workflow step
5. **Validation**: `validate_artifacts.py` ensures quality standards
6. **Observation**: `aggregate.py` generates monitoring reports

### Error Handling & Recovery
- **Automatic Retry**: Failed operations automatically retry with backoff
- **State Persistence**: Workflow state survives interruptions
- **Rollback Support**: Failed operations can be rolled back
- **Logging Integration**: All errors are logged with full context

### Performance Optimization
- **Parallel Execution**: Compatible operations run concurrently
- **Caching**: Frequently accessed data is cached for performance
- **Resource Management**: Automatic resource allocation and cleanup
- **Monitoring**: Real-time performance metrics and alerting

## 🛠️ Development & Extension

### Adding New Tools
1. **Create Tool Module**: Add new directory under `tools/`
2. **Implement Core Logic**: Create main Python script with proper error handling
3. **Add Configuration**: Include necessary config files (JSON/YAML)
4. **Update Documentation**: Add README.md with usage examples
5. **Integrate with Pipeline**: Update quickstart.py if needed

### Tool Standards
- **Error Handling**: All tools must handle errors gracefully
- **Logging**: Comprehensive logging with appropriate log levels
- **Configuration**: External configuration via JSON/YAML files
- **Documentation**: Inline documentation and usage examples
- **Testing**: Unit tests for critical functionality

## 📋 Maintenance Procedures

### Regular Maintenance
```bash
# Clean Python bytecode cache
find tools/ -name "__pycache__" -type d -exec rm -rf {} +

# Validate all tool configurations
python3 tools/schema/validate_artifacts.py --tools-only

# Update tool dependencies
pip install -r requirements.txt --upgrade
```

### Health Checks
```bash
# Run tool health diagnostics
python3 tools/observability/aggregate.py --health-check

# Verify tool integrity
python3 tools/artifacts/hash_index.py --verify-tools

# Check configuration consistency
python3 tools/audit/diff_evidence.py --config-check
```

## 🚨 Troubleshooting

### Common Issues
- **Import Errors**: Check Python path and dependencies
- **Permission Issues**: Ensure proper file system permissions
- **Configuration Errors**: Validate JSON/YAML configuration files
- **Network Timeouts**: Check network connectivity for external services

### Debug Mode
```bash
# Enable debug logging for any tool
DEBUG=1 python3 tools/run_role.py product_owner_ai

# Run with verbose output
VERBOSE=1 python3 tools/decision_scoring/advanced_score.py
```

## 🔗 Dependencies & Requirements

### Python Dependencies
- Python 3.8+ required
- Dependencies listed in `requirements.txt`
- Virtual environment recommended for isolation

### System Requirements
- Unix-like operating system (Linux/macOS)
- Sufficient disk space for logs and artifacts
- Network connectivity for external integrations

### Framework Integration
- **Memory Bank**: Reads from and writes to `memory-bank/` directory
- **Rules Engine**: Integrates with `.cursor/rules/` framework
- **Logging System**: Uses `logs/` directory for comprehensive logging

---

**Tools Directory** - The operational powerhouse of AdvancedRules AI orchestration! ⚙️🔧