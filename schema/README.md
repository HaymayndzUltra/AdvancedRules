# schema/

- Purpose: JSON and frontmatter schemas for artifact validation.

## Files
- acceptance_criteria.schema.json: JSON schema for `memory-bank/plan/acceptance_criteria.json`
- validation_report.frontmatter.schema.json: frontmatter schema for `Validation_Report.md`
- final_implementation_plan.frontmatter.schema.json: frontmatter schema for `Final_Implementation_Plan.md`

## Validate
```bash
python3 tools/schema/validate_artifacts.py
```