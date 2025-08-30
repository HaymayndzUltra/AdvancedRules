# tools/

- Purpose: Execution utilities that power the solo-freelancer pipeline (runner, scoring, orchestrator, observability, readiness, audit, provenance).

## Key modules
- runner/: dispatch per role, artifact/event logging
- decision_scoring/: v3 scorer (calibration, exploration, shadow) + metrics
- orchestrator/: state engine + scorer→registry trigger
- prestart/: ensure Upwork readiness + composite preflight
- upwork/: adapter to write offer_status.json
- rule_attach/: deterministic attach detector and log
- observability/: aggregate logs/events into reports
- artifacts/: provenance hashing (SHA-256 index)
- audit/: evidence/citation helpers

- demo/: demo scripts and end-to-end simulation (e.g., `end_to_end_simulation.py`)

## Quick commands
```bash
# One-command happy path
python3 tools/quickstart.py

# Readiness / preflight
python3 tools/prestart/prestart_composite.py

# Role runner (examples)
python3 tools/run_role.py product_owner_ai
python3 tools/run_role.py planning_ai
python3 tools/run_role.py auditor_ai
python3 tools/run_role.py principal_engineer_ai --mode PEER_REVIEW
python3 tools/run_role.py principal_engineer_ai --mode SYNTHESIS

# Scoring v3 demo
python3 tools/decision_scoring/advanced_score.py

# Trigger next command (dry-run)
python3 tools/orchestrator/trigger_next.py --dry-run --candidates tools/decision_scoring/examples/trigger_candidates.json

# Observability summary
python3 tools/observability/aggregate.py
```