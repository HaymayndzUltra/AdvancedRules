# memory-bank/

- Purpose: Persistent artifacts produced by roles and pipeline steps.

## Key paths
- plan/: planning artifacts (client_brief.md, product_backlog.yaml, acceptance_criteria.json, Action_Plan.md, technical_plan.md, task_breakdown.yaml, Summary_Report.md, Validation_Report.md, Final_Implementation_Plan.md)
- upwork/: Upwork readiness (offer_status.json)
- business/: business inputs (client_score.json, capacity_report.md, pricing.ratecard.yaml, estimate_brief.md)
- artifacts_index.json: provenance index (auto-updated)

## Related docs
- Validation suite overview: `docs/VALIDATION_SUITE_STRUCTURE.md`
- Test reports: `docs/reports/TEST_SUMMARY.md`, `docs/reports/QUEUE_SYSTEM_TEST_REPORT.md`

## Notes
- Files are auto-indexed with SHA-256 when written by the runner.
- Validate artifact schemas:
```bash
python3 tools/schema/validate_artifacts.py
```
