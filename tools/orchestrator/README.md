# tools/orchestrator/

- Purpose: Orchestration helpers (state engine and scoring→registry trigger).

## Files
- state.py: idempotent transitions, workflow_state.json
- trigger_next.py: map Decision Scoring v3 output to registry commands

## Usage
```bash
python3 tools/orchestrator/state.py --set PLANNING
python3 tools/orchestrator/state.py --resume

python3 tools/orchestrator/trigger_next.py --dry-run --candidates tools/decision_scoring/examples/trigger_candidates.json
```