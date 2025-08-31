# System Inventory

Roots: cli, tools, tools/io, tools/orchestrator, tools/runner, tools/observability, tools/decision_scoring, tools/gates, tools/plugins, tools/artifacts, schemas, schemas/memory, tests, docs, .github/workflows, scripts, memory-bank

## cli
- 📄 README.md
- 📄 __init__.py
- 📄 ar_flow.py
- 📄 ar_memory.py
- 📄 ar_tasks.py
- 📄 main.py
- 📄 memory.py

## tools
- 📄 README.md
- 📄 instrumentation.py
- 📄 orchestrator_postrun.py
- 📄 quickstart.py
- 📄 run_role.py
- 📁 artifacts
- 📁 audit
- 📁 decision_scoring
- 📁 demo
- 📁 envelopes
- 📁 flow
- 📁 gates
- 📁 instrumentation
- 📁 io
- 📁 observability
- 📁 orchestrator
- 📁 planning
- 📁 plugins
- 📁 postrun
- 📁 prestart
- 📁 queue
- 📁 rule_attach
- 📁 rules
- 📁 runner
- 📁 schema
- 📁 upwork

## tools/io
- 📄 README.md
- 📄 fs.py
- 📄 safe_read.py

## tools/orchestrator
- 📄 README.md
- 📄 state.py
- 📄 trigger_next.py

## tools/runner
- 📄 README.md
- 📄 io_utils.py
- 📁 plugins

## tools/observability
- 📄 README.md
- 📄 aggregate.py

## tools/decision_scoring
- 📄 README.md
- 📄 adapter.py
- 📄 advanced_score.py
- 📄 calibrate.py
- 📄 calibration.json
- 📄 compute_metrics.py
- 📄 execute_envelope.sh
- 📄 metrics.py
- 📄 score.py
- 📄 thresholds.json
- 📄 weights.json
- 📁 examples

## tools/gates
- 📄 README.md
- 📄 gate_evaluator.py

## tools/plugins
- 📄 README.md
- 📄 test_plugins.py
- 📄 wrapper.py

## tools/artifacts
- 📄 README.md
- 📄 auditor.py
- 📄 hash_index.py

## schemas
- 📄 README.md
- 📄 candidates.schema.json
- 📄 events_envelope.schema.json
- 📄 flow_schema.json
- 📄 memory_doc_schema.json
- 📄 metrics_schema.json
- 📄 registry.schema.json
- 📄 task_schema.json
- 📄 workflow_state.schema.json
- 📁 memory

## schemas/memory
- 📄 README.md
- 📄 capacity_report.schema.json
- 📄 client_score.schema.json
- 📄 generic_json.schema.json
- 📄 generic_markdown.schema.json
- 📄 proposal.schema.json

## tests
- 📄 README.md
- 📄 conftest.py
- 📄 test_artifact_audit.py
- 📄 test_cli_entrypoints.py
- 📄 test_exec_queue.py
- 📄 test_execution_policy.py
- 📄 test_gates_enforcement.py
- 📄 test_instrumentation_redaction.py
- 📄 test_io_atomicity.py
- 📄 test_io_locking.py
- 📄 test_mdc_parity.py
- 📄 test_memory_basic.py
- 📄 test_memory_cli.py
- 📄 test_memory_crash_safety.py
- 📄 test_observability_correlation.py
- 📄 test_planning_pipeline.py
- 📄 test_plugins_timeouts_idempotency.py
- 📄 test_postrun_consistency.py
- 📄 test_state_schema_alignment.py
- 📁 e2e
- 📁 smoke

## docs
- 📄 ARX_CLI_SETUP.md
- 📄 CI_CLI_FIX.md
- 📄 INTEGRATION_GUIDE.md
- 📄 METRICS_RUNBOOK.md
- 📄 README.md
- 📄 README_POLICY.md
- 📄 SYSTEM_INVENTORY.md
- 📄 VALIDATION_SUITE_STRUCTURE.md
- 📄 governance_policy.md
- 📄 instrumentation_policy.md
- 📁 ADRs
- 📁 checklists
- 📁 reports

## .github/workflows
- 📄 README.md
- 📄 ci.yml
- 📄 governance.yml
- 📄 rag-check.yml
- 📄 readme-sync-check.yml

## scripts
- 📄 README.md
- 📄 assert_metrics.py
- 📄 docs_readme_sync.py
- 📄 enqueue_load.py
- 📄 migrate_state.py
- 📄 phase0_safety.sh
- 📄 phase1_planning.sh
- 📄 phase2_flows.sh
- 📄 phase3_rag.sh
- 📄 phase4_metrics.sh
- 📄 phase5_queue.sh
- 📄 run_tests.sh
- 📄 setup_branch_protection.sh
- 📄 test_arx_installation.sh
- 📄 test_cli_methods.sh
- 📄 test_memory_smoke.sh
- 📄 update_registry_checksum.py
- 📄 validate_all.sh
- 📄 validate_prestart.sh
- 📄 validate_registry.py
- 📄 validate_safety_rails.py

## memory-bank
- 📄 README.md
- 📄 artifacts_index.json
- 📄 gate_results.json
- 📄 mdc_lint_report.json
- 📄 mdc_lint_report.json.lock
- 📄 postrun_consistency.json
- 📄 postrun_consistency.json.lock
- 📄 rules_index.json
- 📄 rules_index.json.1756588935.bak
- 📄 rules_index.json.1756588942.bak
- 📄 rules_index.json.lock
- 📁 business
- 📁 checklists
- 📁 plan
- 📁 upwork
