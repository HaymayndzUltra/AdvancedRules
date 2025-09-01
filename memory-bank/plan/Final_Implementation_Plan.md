---
{"title": "Final Implementation Plan", "version": 1, "tasks": []}
---
# Final Implementation Plan

## Objective
Progress from PLANNING_DONE to AUDIT_DONE and VALIDATION_DONE using safety-first, dry-run execution.

## Prerequisites
- Ensure `docs/SYSTEM_HANDBOOK.md` and `docs/SYSTEM_REFERENCE.md` are present
- Confirm gates status in `memory-bank/gate_results.json`
- Verify planning artifacts: `acceptance_criteria.json`, `task_breakdown.yaml`, `product_backlog.yaml`, `user_stories.md`, `product_vision.md`
- Respect `config/advanced_rules.yaml` safety toggles (dry_run_default=true)

## Execution Plan (dry-run)
1) Audit
```bash
python3 tools/run_role.py auditor_ai --inputs memory-bank/plan/Action_Plan.md
```
2) Validation
```bash
python3 tools/run_role.py principal_engineer_ai --inputs memory-bank/plan/Summary_Report.md
```
3) Optional Flow Preflight
```bash
arx flow lint --flow=feature_request_to_pr
AR_ENABLE_FLOW_ENGINE=1 arx flow run --flow=feature_request_to_pr --task-id=T-0001 --dry-run
```
4) Optional Memory Refresh
```bash
AR_ENABLE_RAG=1 arx memory index --src=. --namespaces=coder --persona=CODER_AI --reindex
```

## Expected Outputs
- Updated `Summary_Report.md` and `Validation_Report.md`
- Gate `audit-to-verify` transitions to PASS once `AUDIT_DONE` is achieved
- Logs: entries in `logs/events.jsonl`

