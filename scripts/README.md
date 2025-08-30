# Scripts Directory

This directory contains all executable scripts and utilities for the AdvancedRules AI Framework.

## 📁 Script Files

### Validation Scripts
- `phase0_safety.sh` - Initial safety checks and environment validation
- `phase1_planning.sh` - Planning phase orchestration
- `phase2_flows.sh` - Workflow execution management
- `phase3_rag.sh` - RAG (Retrieval-Augmented Generation) integration
- `phase4_metrics.sh` - Metrics collection and reporting
- `phase5_queue.sh` - Queue system management

### Utility Scripts
- `validate_prestart.sh` - Pre-start validation and readiness checks
- `end_to_end_simulation.py` - Complete end-to-end workflow simulation demonstrating the full AI team capabilities

## 🚀 Usage

### Running Validation Phases

The validation phases should be run in sequence:

```bash
# Run all phases using Makefile
make validate

# Or run individual phases
bash scripts/phase0_safety.sh
bash scripts/phase1_planning.sh
bash scripts/phase2_flows.sh
AR_ENABLE_RAG=1 bash scripts/phase3_rag.sh
AR_ENABLE_METRICS=1 bash scripts/phase4_metrics.sh
bash scripts/phase5_queue.sh
```

### End-to-End Simulation

The simulation demonstrates the complete AI team workflow:

```bash
python3 scripts/end_to_end_simulation.py
```

This simulation includes:
- Client briefing and requirements analysis
- Product backlog creation
- Technical planning
- Implementation simulation
- Quality assurance checks
- Delivery preparation

## 🔧 Environment Variables

- `AR_ENABLE_RAG` - Enable RAG features (default: disabled)
- `AR_ENABLE_METRICS` - Enable metrics collection (default: disabled)

## ⚠️ Important Notes

- Always run `phase0_safety.sh` before other phases to ensure environment is ready
- The validation scripts are designed to be idempotent and can be run multiple times
- Check logs in the `logs/` directory for detailed execution information

## 📊 Script Dependencies

- **Bash**: Required for shell scripts
- **Python 3.8+**: Required for Python scripts
- **Docker**: Optional, for containerized execution

For more information about the validation pipeline, see the documentation in the `docs/` directory.