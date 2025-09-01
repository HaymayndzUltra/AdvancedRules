# AdvancedRules End-to-End Setup and Execution Plan

## Executive Summary
This document provides a comprehensive, step-by-step plan to set up and run the AdvancedRules framework end-to-end. It is based exclusively on the repository contents and follows the established patterns defined in the codebase.

## Prerequisites Check

### System Requirements
- **Python**: Version ≥ 3.8 (verify with `python3 --version`)
- **Node.js**: Version ≥ 18 (for auxiliary tools, verify with `node --version`)
- **Git**: For version control and branch management
- **Redis**: Optional for Celery queue (can skip for dry-run testing)

### Key Files Verification
Ensure these critical files exist and are properly configured:
- ✅ `pyproject.toml` - Package configuration with CLI entry points
- ✅ `requirements.txt` - Python dependencies 
- ✅ `config/advanced_rules.yaml` - Safety configuration (must have `dry_run_default: true`)
- ✅ `.cursor/commands/registry.yaml` - Command registry
- ✅ `flow/flow_registry.yaml` - Flow definitions

## Phase 1: Environment Setup

### Step 1.1: Create Virtual Environment
```bash
# Create and activate a fresh virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel
```

### Step 1.2: Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install optional queue dependencies (if using Celery)
pip install -r requirements.queue.txt

# Install the package in editable mode (creates 'arx' CLI command)
pip install -e .
```

### Step 1.3: Verify CLI Installation
```bash
# Verify the arx command is available
which arx
# Expected output: /path/to/.venv/bin/arx

# Test CLI help
arx --help
# Should display available subcommands: flow, tasks, memory, obs

# Alternative if arx doesn't work
python -m cli.main --help
```

### Step 1.4: Configure Environment Variables
```bash
# Set default environment variables (add to .env or shell profile)
export AR_ENABLE_FLOW_ENGINE=0  # Start with disabled, enable when ready
export ALLOW_RUN=0              # Dry-run mode by default
export ALLOW_WRITES=0           # No live writes initially
export AR_ENABLE_RAG=0          # RAG memory disabled initially
export AR_METRICS_PORT=9108     # Metrics server port
export ENABLE_REDACTION=true    # Enable PII redaction in logs
```

## Phase 2: Initial Setup and Prestart Pipeline

### Step 2.1: Run Prestart Composite
```bash
# Creates default business artifacts and checks readiness
python3 tools/prestart/prestart_composite.py
```

**Expected Outputs:**
- `memory-bank/business/client_score.json` - Client scoring template
- `memory-bank/business/capacity_report.md` - Capacity planning template  
- `memory-bank/business/pricing.ratecard.yaml` - Pricing configuration
- `memory-bank/business/estimate_brief.md` - Estimate template
- `memory-bank/plan/proposal.md` - Proposal template

**Verification:**
```bash
# Check preflight status
python3 tools/run_role.py readiness
```

### Step 2.2: Run Quickstart Pipeline
```bash
# Executes the minimal happy path through all major roles
python3 tools/quickstart.py
```

**What It Does:**
1. Creates `memory-bank/plan/client_brief.md` (minimal stub)
2. Runs Product Owner AI role → generates `product_backlog.yaml`
3. Runs Planning AI role → generates `Action_Plan.md`
4. Runs Auditor AI role → generates `Summary_Report.md`
5. Runs Principal Engineer AI (PEER_REVIEW) → generates `Validation_Report.md`
6. Runs Principal Engineer AI (SYNTHESIS) → generates synthesis artifacts

**Expected State Transitions:**
- `null` → `BACKLOG_READY` → `PLANNING_DONE` → `AUDIT_DONE` → `VALIDATION_DONE` → `SYNTHESIS_DONE`

## Phase 3: Task Planning and Orchestration

### Step 3.1: Create a New Plan
```bash
# Create a plan for a specific goal
arx tasks plan "Build a REST API with user authentication and CRUD operations"

# View the generated plan
arx tasks print
```

**Expected Outputs:**
- `memory-bank/plan/Action_Plan.md` - Detailed action plan
- `memory-bank/plan/acceptance_criteria.json` - Success criteria
- `memory-bank/plan/task_breakdown.yaml` - Task decomposition

### Step 3.2: Check Workflow State
```bash
# Examine current system state
cat workflow_state.json | jq '.state'

# View completed steps
cat workflow_state.json | jq '.completed_steps'
```

## Phase 4: Flow Linting and Dry-Run Execution

### Step 4.1: List Available Flows
```bash
# Show all registered flows
arx flow list
```

**Available Flows (from registry):**
- `feature_request_to_pr` - Complete feature development workflow
- `bugfix_ci_loop` - Iterative bugfix with CI validation

### Step 4.2: Lint Flow Definition
```bash
# Validate flow structure and references
arx flow lint --flow=feature_request_to_pr
```

**What It Checks:**
- Schema compliance
- Node references validity
- Edge consistency
- Guard function availability
- DAG structure (no cycles)

### Step 4.3: Dry-Run Flow Execution
```bash
# Enable flow engine and run in dry-run mode
AR_ENABLE_FLOW_ENGINE=1 arx flow run \
  --flow=feature_request_to_pr \
  --task-id=T-0001 \
  --dry-run
```

**Safety Guards Applied:**
- `branch_not_main` - Prevents execution on main branch
- `dry_run_unless_allowed` - Enforces dry-run unless ALLOW_WRITES=1
- `artifacts_present` - Checks required files exist
- `git_clean` - Ensures clean working directory

### Step 4.4: Render Flow Diagram (Optional)
```bash
# Generate visual flow diagram
arx flow render --flow=feature_request_to_pr --out=.artifacts/flow.mmd
```

## Phase 5: Decision Scoring and Orchestration

### Step 5.1: Run Decision Scoring
```bash
# Process candidate tasks and generate scores
python3 tools/decision_scoring/advanced_score.py
```

**Input:** Reads from `decision_candidates.json` or `candidates_next.json`
**Output:** Scored decisions with types:
- `NEXT_STEP` - High confidence, proceed
- `OPTION_SET` - Multiple viable options
- `ASK_CLARIFY` - Low confidence, need clarification
- `RISK_ALERT` - Elevated risk detected

### Step 5.2: Trigger Next Action (Dry-Run)
```bash
# Orchestrator determines and suggests next action
python3 tools/orchestrator/trigger_next.py --dry-run
```

**What It Does:**
1. Verifies registry checksum
2. Loads current workflow state
3. Evaluates gate conditions
4. Scores candidate commands
5. Outputs suggested command (doesn't execute in dry-run)

### Step 5.3: Check Gate Results
```bash
# Review gate evaluation results
cat memory-bank/gate_results.json | jq '.'
```

## Phase 6: Role Execution

### Step 6.1: Execute Individual Roles
```bash
# Product Owner role
python3 tools/run_role.py product_owner_ai

# Planning role
python3 tools/run_role.py planning_ai

# Auditor role
python3 tools/run_role.py auditor_ai

# Principal Engineer peer review
python3 tools/run_role.py principal_engineer_ai --mode PEER_REVIEW

# Principal Engineer synthesis
python3 tools/run_role.py principal_engineer_ai --mode SYNTHESIS

# Code generation (scaffold mode)
python3 tools/run_role.py codegen_ai --mode SCAFFOLD

# QA validation
python3 tools/run_role.py qa_ai --mode VALIDATE

# Security scanning
python3 tools/run_role.py security_ai --mode SAST

# Deployment packaging
python3 tools/run_role.py deploy_ai --mode PACKAGE
```

## Phase 7: Memory and RAG System (Optional)

### Step 7.1: Enable and Index Memory
```bash
# Enable RAG system
export AR_ENABLE_RAG=1

# Index codebase into vector memory
arx memory index \
  --src=. \
  --namespaces=coder \
  --persona=CODER_AI \
  --reindex
```

### Step 7.2: Query Memory
```bash
# Query for relevant context
arx memory query \
  --persona=CODER_AI \
  --query="How does the flow runner work?" \
  --k=5
```

### Step 7.3: Check Memory Statistics
```bash
arx memory stats
```

## Phase 8: Observability and Monitoring

### Step 8.1: Start Metrics Server
```bash
# Start Prometheus metrics endpoint
export AR_ENABLE_METRICS=1
arx obs serve --port=9108 --addr=0.0.0.0
```

### Step 8.2: Verify Metrics Collection
```bash
# Check metrics endpoint
curl -s http://localhost:9108/metrics | grep -E "ar_flow_|ar_step_|ar_tokens_"
```

### Step 8.3: Review Event Logs
```bash
# Check event logs
tail -f logs/events.jsonl | jq '.'

# Check decision traces
tail -f logs/decision_traces.jsonl | jq '.'
```

## Phase 9: Configuration Verification

### Step 9.1: Validate Configuration
```bash
# Check safety settings in config
cat config/advanced_rules.yaml | grep -E "dry_run_default|human_approval_required|branch_only_workflow"
```

**Required Settings:**
```yaml
safety:
  dry_run_default: true
  human_approval_required: true
  branch_only_workflow: true
```

### Step 9.2: Verify Registry Checksum
```bash
# Compute and verify checksum
sha256sum .cursor/commands/registry.yaml
# Compare with .cursor/commands/registry.sha256
```

## Phase 10: Live Execution (Advanced)

### Step 10.1: Enable Live Mode
```bash
# CAUTION: Only after thorough testing
export ALLOW_RUN=1
export ALLOW_WRITES=1
export AR_ENABLE_FLOW_ENGINE=1

# Ensure on feature branch (not main)
git checkout -b feature/test-execution
```

### Step 10.2: Execute Live Flow
```bash
# Run with live execution enabled
arx flow run \
  --flow=feature_request_to_pr \
  --task-id=T-0002 \
  --no-dry-run  # Note: if this flag exists
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: `arx` command not found
```bash
# Solution: Reinstall in editable mode
pip uninstall advancedrules-domain-lab -y
pip install -e .
# Or use direct module execution
python -m cli.main --help
```

#### Issue: Flow execution blocked by guards
```bash
# Check which guard is failing
cat logs/events.jsonl | grep "guard_failed"

# Common fixes:
# - Switch to feature branch: git checkout -b feature/test
# - Clean working directory: git stash
# - Create required artifacts: python3 tools/prestart/prestart_composite.py
```

#### Issue: Gate evaluation failures
```bash
# Check gate results
cat memory-bank/gate_results.json | jq '.[] | select(.passed == false)'

# Fix missing prerequisites
python3 tools/prestart/ensure_readiness.py
```

#### Issue: Memory/RAG not working
```bash
# Ensure ChromaDB is installed
pip install chromadb sentence-transformers

# Enable RAG explicitly
export AR_ENABLE_RAG=1

# Run memory doctor
arx memory doctor
```

## Validation Checklist

### Phase Completion Criteria

✅ **Environment Setup**
- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] `pip install -e .` successful
- [ ] `arx --help` displays help

✅ **Prestart & Quickstart**
- [ ] `tools/prestart/prestart_composite.py` runs without errors
- [ ] Business artifacts created in `memory-bank/business/`
- [ ] `tools/quickstart.py` completes successfully
- [ ] Planning artifacts exist in `memory-bank/plan/`

✅ **Flow Execution**
- [ ] Flow linting passes
- [ ] Dry-run execution completes
- [ ] Guards properly enforce safety
- [ ] State transitions logged in `workflow_state.json`

✅ **Orchestration**
- [ ] Decision scoring generates valid decisions
- [ ] Orchestrator suggests appropriate next steps
- [ ] Gate evaluations complete successfully

✅ **Observability**
- [ ] Metrics server starts on configured port
- [ ] Events logged to `logs/events.jsonl`
- [ ] Decision traces captured
- [ ] Redaction working (no PII in logs)

## Notes on Repository-Specific Patterns

### Command Registry
- Only commands in `.cursor/commands/registry.yaml` are valid
- Registry checksum must match for security
- Commands follow strict schema with guards and requirements

### State Management  
- System state tracked in `workflow_state.json`
- State transitions managed by `tools/orchestrator/state.py`
- Each role execution triggers automatic state transition

### Safety-First Design
- All operations default to dry-run mode
- Multiple layers of guards and gates
- Branch protection prevents main branch modifications
- Human approval required for critical operations

### Plugin Architecture
- Role plugins in `tools/runner/plugins/`
- Additional plugins in `tools/plugins/`
- Safe wrapper with timeout and idempotency checks

## Conclusion

This plan provides a complete, repository-accurate guide to setting up and running the AdvancedRules framework. Follow the phases sequentially, always starting with dry-run mode and safety checks enabled. The system is designed with multiple safety layers - respect these guardrails and only override them when absolutely necessary and after thorough testing.

For any deviations or customizations, refer to the actual code in the repository as the source of truth. The framework is highly configurable through environment variables and configuration files, allowing adaptation to specific workflows while maintaining safety and governance standards.