# Action Plan

## Purpose
- Align planning and audit artifacts with the latest repository changes and ensure gates and reports are current.

## Inputs
- docs/SYSTEM_HANDBOOK.md (v1.0.0 — single-source developer reference)
- docs/SYSTEM_REFERENCE.md (system architecture overview)
- docs/README.md (canonical docs index; consolidated observability docs)
- config/advanced_rules.yaml (safety and execution toggles)
- memory-bank/gate_results.json (latest gates evaluation)
- memory-bank/artifacts_index.json (artifact provenance)
- workflow_state.json (current lifecycle state)

## Outputs
- Updated planning/audit reports:
  - memory-bank/plan/Summary_Report.md
  - memory-bank/plan/Validation_Report.md
  - memory-bank/plan/Final_Implementation_Plan.md

## Constraints
- Safety-first: dry_run_default=true, human_approval_required=true, branch_only_workflow=true (see config/advanced_rules.yaml)
- No live destructive actions; all execution remains dry-run unless explicitly allowed.
- Respect gate sequencing (planning → audit → validation → synthesis).

## Steps
1) Scan repository for recent changes (git log, docs additions/updates).
2) Verify presence of planning artifacts (acceptance_criteria.json, task_breakdown.yaml, product_backlog.yaml, user_stories.md, product_vision.md).
3) Update Summary_Report.md with: recent changes, current state, gate results, verified artifacts, and next steps.
4) Update Validation_Report.md with structured findings mapped to inputs and gates.
5) Update Final_Implementation_Plan.md with actionable next steps to progress from PLANNING_DONE → AUDIT_DONE.
6) Optional: Index memory (arx memory index …) and lint flows (arx flow lint …) before running any flows in dry-run.
