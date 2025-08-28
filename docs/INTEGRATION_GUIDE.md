# Decision Scoring + Safe Execution Integration Guide

## Overview
This guide documents the hand-off implementation of the Decision Scoring + Safe Execution system for GPT-5 orchestration.

## Architecture

### Core Components
- **Decision Scorer** (`tools/decision_scoring/score.py`): Evaluates candidates using weighted metrics
- **Safety Runner** (`tools/decision_scoring/execute_envelope.sh`): Executes actions in controlled environment
- **Envelope Builder**: Creates execution envelopes based on scoring decisions
- **Logging System**: Maintains decision logs in `logs/decisions/`

### Decision Flow
```mermaid
graph TD
    A[Merge Role Candidates] --> B[Execute Decision Scorer]
    B --> C[Generate Decision Log]
    C --> D[Build Execution Envelope]
    D --> E{Decision Type}
    E -->|NEXT_STEP| F[Execute via Safety Runner]
    E -->|OPTION_SET| G[Present Options to User]
    E -->|ASK_CLARIFY| H[Request Missing Information]
```

## Usage

### 1. Prepare Candidates
Create `decision_candidates.json` with the following schema:
```json
{
  "context": {
    "summary": "Brief description of current context",
    "evidence_paths": ["file://path/to/evidence"]
  },
  "candidates": [
    {
      "id": "unique_action_id",
      "action_type": "NATURAL_STEP|COMMAND_TRIGGER",
      "explanation": "Why this action is appropriate",
      "preconds": ["condition1", "condition2"],
      "metrics": {
        "intent": 0.0,
        "state": 0.0,
        "evidence": 0.0,
        "recency": 0.0,
        "pref": 0.0
      },
      "command": "optional command for COMMAND_TRIGGER"
    }
  ]
}
```

### 2. Execute Decision Scoring
```bash
mkdir -p logs/decisions
TS="$(date +%Y%m%d_%H%M%S)"
python3 tools/decision_scoring/score.py tools/decision_scoring/weights.json < decision_candidates.json | tee logs/decisions/$TS.json
```

### 3. Build Execution Envelope
Based on decision type:
- **NATURAL_STEP**: Create PLAN_ONLY envelope, update `next_prompt_for_cursor.md`
- **COMMAND_TRIGGER**: Create DRY_RUN envelope with `echo DRY_RUN:` prefix

### 4. Execute via Safety Runner
```bash
tools/decision_scoring/execute_envelope.sh action_envelope.json
```

## Scoring System

### Metrics (0.0 - 1.0 scale)
- **Intent**: Alignment with user goals and context
- **State**: Current system state compatibility
- **Evidence**: Supporting documentation and artifacts
- **Recency**: Temporal relevance of information
- **Preference**: User/system preferences and priorities

### Weights Configuration
```json
{
  "w_intent": 0.30,
  "w_state": 0.25,
  "w_evidence": 0.20,
  "w_recency": 0.15,
  "w_pref": 0.10,
  "lambda_command_bias": 0.03,
  "epsilon": 0.05,
  "t_high": 0.75,
  "t_mid": 0.55
}
```

### Decision Gates
- **CONF_HIGH** (≥0.75): Execute NEXT_STEP
- **CONF_MID** (0.55-0.75) with gap ≤ ε: Present OPTION_SET
- **CONF_LOW** (<0.55): ASK_CLARIFY

## Safety Features

### DRY_RUN Mode
- Commands prefixed with `echo DRY_RUN:`
- Preview execution without side effects
- Manual approval required for real execution

### Envelope Validation
- Precondition checking before execution
- Command sanitization and validation
- Execution environment isolation

## Implementation Example

### Current Hand-off Results
- **Decision**: NEXT_STEP
- **Chosen Action**: validate_system_readiness
- **Score**: 0.873 (CONF_HIGH)
- **Execution Mode**: DRY_RUN

### Generated Artifacts
- Decision Log: `logs/decisions/20250828_142955.json`
- Execution Envelope: `action_envelope.json`
- Safety Runner Output: Command preview without execution

## Best Practices

### Candidate Creation
1. Ensure metrics are calibrated [0,1]
2. Cite real file paths for evidence
3. Include specific preconditions
4. Use descriptive, actionable IDs

### Execution Safety
1. Always use safety runner for command execution
2. Validate envelopes before execution
3. Log all decisions and outcomes
4. Implement fail-closed for destructive operations

### Monitoring
1. Track decision quality metrics
2. Monitor scoring distribution
3. Audit execution outcomes
4. Update weights based on performance

## Troubleshooting

### Common Issues
- **No candidates provided**: Ensure `decision_candidates.json` exists and is valid JSON
- **Missing tools**: Verify `tools/decision_scoring/` directory structure
- **Precondition failures**: Check file paths and system state
- **Scoring errors**: Validate metrics are numeric [0,1]

### Debug Commands
```bash
# Test scoring system
python3 tools/decision_scoring/score.py tools/decision_scoring/weights.json < tools/decision_scoring/examples/test_input.json | jq '.decision'

# Validate envelope
tools/decision_scoring/execute_envelope.sh action_envelope.json

# Check artifacts
ls -la memory-bank/business/
```

## Integration Points

### With Existing Systems
- **Memory Bank**: Provides context and evidence
- **Rules Engine**: Supplies candidate generation logic
- **Orchestrator**: Coordinates multi-step workflows
- **Logging**: Centralized audit trail

### Extension Points
- Custom scoring algorithms
- Additional safety checks
- Alternative execution environments
- Integration with external tools

---

**Status**: ✅ IMPLEMENTED AND VALIDATED
**Decision Log**: `logs/decisions/20250828_142955.json`
**Safety**: ✅ DRY_RUN execution confirmed
**Documentation**: Complete integration guide created
