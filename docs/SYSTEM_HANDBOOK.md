# AdvancedRules System Handbook — Single Source of Truth (v1.0.0)

Last updated: 2025-09-01

## 0. How to Use This Handbook
- This is the canonical, single-file reference for developers and AI agents.
- Start here, then follow deep links to specific modules/files.

## 1. Architecture & Components
- Orchestrator: `tools/orchestrator/{trigger_next.py,state.py}`; post‑run: `.cursor/rules/orchestrator_postrun.mdc`, `tools/orchestrator_postrun.py`
- Decision Scoring v3: `tools/decision_scoring/{advanced_score.py,weights.json,thresholds.json,calibration.json,adapter.py,score.py}`
- Rules Engine: `.cursor/rules/**` (domains/utilities/orchestrator), validator at `tools/rules/{validate.py,mdc_linter.py,index_generator.py}`
- Flows: `flow/flow_registry.yaml`, engine at `tools/flow/{flow_runner.py,flow_linter.py}`
- Memory Bank: `memory-bank/{plan,business,security,qa,deploy,upwork}`, provenance `artifacts_index.json`, gates `gate_results.json`
- Queue/Workers: `exec_queue/{celery_app.py,tasks.py}`, `workers/flow_worker.py`
- CLI: `cli/main.py` (subcommands: `ar_flow.py`, `ar_tasks.py`, `memory.py`)
- Observability & Instrumentation: see `docs/OBSERVABILITY_AND_INSTRUMENTATION.md`

## 2. End‑to‑End Workflows
- Prestart → Quickstart: `python3 tools/prestart/prestart_composite.py` → `python3 tools/quickstart.py`
- Planning (CLI): `arx tasks plan "<goal>"` → `arx tasks print`
- Declarative Flows: `arx flow lint --flow=feature_request_to_pr` → `AR_ENABLE_FLOW_ENGINE=1 arx flow run --flow=feature_request_to_pr --task-id=T-0001 --dry-run`
- Decision & Trigger: `python3 tools/decision_scoring/advanced_score.py` → `python3 tools/orchestrator/trigger_next.py --dry-run`
- Observability: `arx obs serve --port=<port>`; logs: `logs/events.jsonl`, `logs/decision_traces.jsonl`

## 3. Interfaces & Contracts
- CLI: `flow lint|run|render|list`, `tasks plan|print|export`, `memory index|query|stats|purge`, `obs serve --port [--addr]`
- Schemas: `schemas/{workflow_state.schema.json,flow_schema.json,registry.schema.json,candidates.schema.json}` + `schemas/memory/*.schema.json`
- Registry: `.cursor/commands/registry.yaml` (+ checksum `.cursor/commands/registry.sha256`)
- Events/Traces (JSONL): required fields `type,timestamp,correlation_id,trace_id`

## 4. Safety & Governance
- Config (required): `config/advanced_rules.yaml` must contain `dry_run_default:true`, `human_approval_required:true`, `branch_only_workflow:true`
- Execution toggles: `ALLOW_RUN=1` (enable trigger execution), `ALLOW_WRITES=1` (allow live writes in flows/Celery)
- Allowlist: trigger permits only `arx` and `python3 tools/run_role.py`
- Guardrails: `flow/flow_registry.yaml` guards include `branch_not_main`, `dry_run_unless_allowed`, `artifacts_present`, `git_clean`
- CI/Policy: `.github/workflows/{ci.yml,governance.yml,rag-check.yml,readme-sync-check.yml}`; `tools/gates/gate_evaluator.py`

## 5. Environment & Dependencies
- Python ≥ 3.8, Node ≥ 18; `requirements.txt`, `requirements.queue.txt`
- Redis/Celery: `AR_REDIS_HOST`, `AR_REDIS_PORT`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- Observability: `AR_ENABLE_METRICS`, `AR_METRICS_PORT`, `AR_METRICS_ADDR`; Redaction: `ENABLE_REDACTION`

## 6. Personas & Plugins
- Runner plugins: `tools/runner/plugins/{product_owner.py,planning.py,principal_engineer.py,auditor.py}`
- Additional plugins: `tools/plugins/{qa.py,security.py,deploy.py,codegen.py}` (invoked via `tools/run_role.py`)

## 7. Implementation Artifacts
- Planning: `memory-bank/plan/{client_brief.md,acceptance_criteria.json,task_breakdown.yaml}`
- Provenance: `memory-bank/artifacts_index.json`
- Gate results: `memory-bank/gate_results.json`

## 8. Observability (pointer)
- Canonical reference: `docs/OBSERVABILITY_AND_INSTRUMENTATION.md` (metrics, tracing, events, redaction, PromQL)

## 9. Testing & Validation
- Tests: `tests/` (unit, e2e, smoke); fixtures: `tests/conftest.py`
- Validation Suite: `docs/VALIDATION_SUITE_STRUCTURE.md` + `scripts/validate_all.sh` and `scripts/phase*.sh`

## 10. Developer Onboarding Quickstart
```bash
# Install
pip install -r requirements.txt
pip install -e .

# CLI smoke
arx --help

# Minimal pipeline
python3 tools/prestart/prestart_composite.py
python3 tools/quickstart.py

# Lint + dry-run a flow
arx flow lint --flow=feature_request_to_pr
AR_ENABLE_FLOW_ENGINE=1 arx flow run --flow=feature_request_to_pr --task-id=T-0001 --dry-run
```

## 11. Appendix — File Index (essential)
- Orchestrator: `tools/orchestrator/{trigger_next.py,state.py}`; checksum: `.cursor/commands/registry.sha256`
- Scoring: `tools/decision_scoring/{advanced_score.py,weights.json,thresholds.json,calibration.json}`
- Rules: `.cursor/rules/**` (domains/utilities/orchestrator), roles docs: `.cursor/rules/roles/*.md`
- Flows: `flow/flow_registry.yaml`, engine: `tools/flow/{flow_runner.py,flow_linter.py}`
- Memory Bank: `memory-bank/{plan,business,security,qa,deploy,upwork}` + `artifacts_index.json`, `gate_results.json`
- Queue: `exec_queue/{celery_app.py,tasks.py}`, worker: `workers/flow_worker.py`
- CLI: `cli/main.py`, `cli/ar_flow.py`, `cli/ar_tasks.py`, `cli/memory.py`
- Observability: `docs/OBSERVABILITY_AND_INSTRUMENTATION.md`

## 12. Change Log
- v1.0.0 — Initial handbook (single source of truth)