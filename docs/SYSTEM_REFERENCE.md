# AdvancedRules System Reference (v1.0.0)

Last updated: 2025-09-01

## Purpose
Single source of truth for system architecture, workflows, dependencies, interfaces, and integration points. This complements detailed policy and runbooks; see `docs/OBSERVABILITY_AND_INSTRUMENTATION.md` for telemetry.

## 1. Architecture Overview
- Orchestrator
  - Trigger: `tools/orchestrator/trigger_next.py`
  - State Engine: `tools/orchestrator/state.py` (backed by `workflow_state.json` / schema: `schemas/workflow_state.schema.json`)
  - Post‑run: policy doc `.cursor/rules/orchestrator_postrun.mdc`, tool `tools/orchestrator_postrun.py`
- Decision Scoring (v3)
  - Scorer: `tools/decision_scoring/advanced_score.py` (weights/thresholds/calibration JSON)
  - Examples & adapters: `tools/decision_scoring/{examples,adapter.py,score.py}`
- Rules Engine
  - Rules: `.cursor/rules/**/*.mdc` (domains/utilities/orchestrator)
  - Roles (docs): `.cursor/rules/roles/*.md`
  - Validator: `tools/rules/{validate.py, mdc_linter.py, index_generator.py}`
- Memory Bank
  - Plans & business: `memory-bank/plan`, `memory-bank/business`
  - Provenance: `memory-bank/artifacts_index.json`
  - Gates: `memory-bank/gate_results.json`
- Flows
  - Registry: `flow/flow_registry.yaml`
  - Engine: `tools/flow/{flow_runner.py,flow_linter.py}`
- Queue/Workers
  - Celery app: `exec_queue/celery_app.py`
  - Worker entry: `workers/flow_worker.py`
- CLI
  - Entry: `cli/main.py` (`arx`)
  - Subcommands: `cli/ar_flow.py`, `cli/ar_tasks.py`, `cli/memory.py`

## 2. Core Workflows
### Minimal Happy Path
```bash
python3 tools/prestart/prestart_composite.py
python3 tools/quickstart.py
```
Produces plan artifacts under `memory-bank/plan/` and runs PO → Planning → Audit → PE.

### Declarative Flows
- Lint: `arx flow lint --flow=feature_request_to_pr`
- Dry‑run: `AR_ENABLE_FLOW_ENGINE=1 arx flow run --flow=feature_request_to_pr --task-id=T-0001 --dry-run`
- Guards include: `branch_not_main`, `dry_run_unless_allowed`, `artifacts_present`, `git_clean`

### Decision + Trigger
- Score: `python3 tools/decision_scoring/advanced_score.py`
- Trigger: `python3 tools/orchestrator/trigger_next.py --dry-run` (allowlist: `arx`, `python3 tools/run_role.py`)
- Registry integrity: `.cursor/commands/registry.sha256` verified by trigger

## 3. Interfaces & Contracts
### CLI Contracts
- `arx flow lint|run|render|list`
- `arx tasks plan|print|export`
- `arx memory index|query|stats|purge`
- `arx obs serve --port=<port> [--addr=<addr>]`

### File/Schema Contracts
- Workflow state: `workflow_state.json` ↔ `schemas/workflow_state.schema.json`
- Flow: `flow/flow_registry.yaml` ↔ `schemas/flow_schema.json`
- Memory docs: `schemas/memory/*.schema.json`
- Candidates: `schemas/candidates.schema.json`
- Registry: `.cursor/commands/registry.yaml` ↔ `schemas/registry.schema.json`

### Event/Trace Contracts
- Events log: `logs/events.jsonl` (JSON Lines)
- Decision traces: `logs/decision_traces.jsonl` (JSON Lines)
- Required fields: `type`, `timestamp`, `correlation_id`, `trace_id`

## 4. Safety & Governance
- Config: `config/advanced_rules.yaml` must include `dry_run_default: true`, `human_approval_required: true`, `branch_only_workflow: true`
- Execution toggles: `ALLOW_RUN=1` (execution), `ALLOW_WRITES=1` (live writes)
- Branch protection: enforced in flows and CI `.github/workflows/governance.yml`
- Gate Evaluator: `tools/gates/gate_evaluator.py` generates `memory-bank/gate_results.json`

## 5. Dependencies & Environment
- Python ≥ 3.8, Node ≥ 18
- Python deps: `requirements.txt`; queue extras via `requirements.queue.txt`
- Redis/Celery env: `AR_REDIS_HOST`, `AR_REDIS_PORT`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- Metrics env: `AR_ENABLE_METRICS`, `AR_METRICS_PORT`, `AR_METRICS_ADDR`

## 6. Integration Points
- Orchestrator ↔ Rules: attach/validate via tools/rules and gate evaluator
- Orchestrator ↔ Scoring: imports `advanced_score.score_candidates`
- Flows ↔ Runner: engine executes commands with guard enforcement
- Memory ↔ Artifacts: `hash_index.record()` updates provenance
- Observability: see `docs/OBSERVABILITY_AND_INSTRUMENTATION.md`

## 7. Testing & CI
- Tests: `tests/` (unit, e2e, smoke)
- CI: `.github/workflows/{ci.yml, governance.yml, rag-check.yml, readme-sync-check.yml}`
- Validation suite: `docs/VALIDATION_SUITE_STRUCTURE.md`; scripts `scripts/phase*.sh`, `scripts/validate_all.sh`

## 8. Personas & Plugins
- Runner plugins (PO/Planning/PE/Auditor): `tools/runner/plugins/*`
- Additional plugins (QA/Security/Deploy): `tools/plugins/*` (via `tools/run_role.py`)

## 9. Glossary
- Correlation ID: execution-scoped UUID linking all events/artifacts
- Trace ID: grouping across correlations (defaults to correlation if unset)
- Dry-run: execution without side effects, enforced by guards and toggles
- Allowlist: permitted commands in trigger (`arx`, `python3 tools/run_role.py`)

## 10. Change Log
- v1.0.0 — Initial consolidated reference