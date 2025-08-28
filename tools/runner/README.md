# tools/runner/

- Purpose: Execute role logic via `tools/run_role.py` dispatch; write artifacts, provenance, and structured events.

## Files
- io_utils.py: write_text/touch_json/frontmatter + event/provenance hooks
- plugins/: per-role implementations

## Usage
```bash
python3 tools/run_role.py product_owner_ai
python3 tools/run_role.py planning_ai
python3 tools/run_role.py auditor_ai
python3 tools/run_role.py principal_engineer_ai --mode PEER_REVIEW
python3 tools/run_role.py principal_engineer_ai --mode SYNTHESIS
```