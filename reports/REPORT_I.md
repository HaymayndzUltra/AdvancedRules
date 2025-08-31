Table: Topic | Report G | Report H | Final Verdict | Evidence (if any) | Confidence
Runtime gates/contexts enforced before trigger | Calls out (not enforced) | Calls out (not enforced) | Not enforced; trigger runs top candidate without preflight gates/context/state checks. | /workspace/tools/orchestrator/trigger_next.py L34–41, L66–75 | High
Scoring schemas consistency (scores vs metrics) | Calls out (dual schemas) | Divergent: advanced vs legacy | Divergent; standardize one schema or add adapter. | /workspace/tools/decision_scoring/advanced_score.py L32–34; /workspace/tools/decision_scoring/score.py L33–41 | High
Registry validity and loader | Calls out (heredoc, unicode IDs, regex loader) | Same | Invalid for programmatic use; regex-only loader ignores requires/contexts; unicode IDs present. | /workspace/.cursor/commands/registry.yaml L1–13, L26–31; /workspace/tools/orchestrator/trigger_next.py L13–31 | High
Execution safety defaults | Calls out (defaults to run) | Same | Executes unless --dry-run; no allowlist/sandbox/signing. | /workspace/tools/orchestrator/trigger_next.py L34–38 | High
Filesystem state/events atomicity | Calls out (no locks/atomicity) | Same | Naive read/overwrite; no atomic rename/locks. | /workspace/tools/orchestrator/state.py L24–26; /workspace/tools/runner/io_utils.py L14–17 | High
Domain attachments used at runtime | Calls out (referenced, not wired) | Not wired | .mdc attachments not used by trigger. | /workspace/.cursor/rules/orchestrator/scenario_router.mdc L29–33, L91–95; /workspace/tools/orchestrator/trigger_next.py | High
Scenario router enforcement | Calls out (advisory only) | Implicit via missing gate enforcement | Advisory-only; not enforced by trigger. | /workspace/.cursor/rules/orchestrator/scenario_router.mdc L29–33; /workspace/tools/orchestrator/trigger_next.py | High
Observability correlation | Calls out (no correlation IDs) | Missing correlation IDs | Counts/durations only; no correlation threading. | /workspace/tools/observability/aggregate.py L120–129 | High
Orchestrator postrun scoring import | Calls out (class missing) | Called out explicitly | DecisionScoringTool not present in score.py; import fails. | /workspace/tools/orchestrator_postrun.py L21–24; /workspace/tools/decision_scoring/score.py | High
Cycle detection in planning | Resolved: root cause is ID vs description | Says A correct, B incorrect (test fails) | Test fails due to dependency key mismatch; no cycle message emitted. | /workspace/tools/planning/task_decomposer.py L259–265; /workspace/tests/test_planning_pipeline.py L77–98 | High
CI and arx availability | CI installs arx; local may miss | CI installs arx | CI installs arx; local runs fail without local arx. | .github/workflows/rag-check.yml L77–82; /workspace/pyproject.toml L85–88 | High
Registry template substitution in trigger | Calls out (missing substitution) | Called out | Placeholders like {{flow_id}} not substituted. | /workspace/.cursor/commands/registry.yaml L62–67, L80–85; /workspace/tools/orchestrator/trigger_next.py L13–31 | High
Workflow state schema mismatch (writer vs reader) | Calls out | Called out | Writer uses state/prev_state/history; reader expects status/current_goal. | /workspace/tools/orchestrator/state.py L28–41; /workspace/tools/orchestrator_postrun.py L39–49, L196–205 | High
Non-deterministic scoring via explore flag | Calls out | Called out | explore=True can flip near‑ties, undermining determinism. | /workspace/tools/orchestrator/trigger_next.py L66; /workspace/tools/decision_scoring/advanced_score.py L88–95 | High
Postrun evidence scan extension mismatch | Calls out (.json vs repo .md) | Called out | Scans only reports/*.json and misses .md. | /workspace/tools/orchestrator_postrun.py L82–93 | High
Postrun evidence scan non-recursive | Not mentioned | Called out | Shallow glob("*.md"/"*.json") misses nested files. | /workspace/tools/orchestrator_postrun.py L77–92 | Medium
Duplicated IO helpers | Calls out (dup append_event) | Called out | Confirmed duplication. | /workspace/tools/runner/io_utils.py L14–17; /workspace/tools/run_role.py L50–53 | High
Guard/DRY-RUN asymmetry (flow vs trigger) | Not mentioned | Called out | Flows use --dry-run; trigger lacks centralized guard. | /workspace/.cursor/commands/registry.yaml L62–67; /workspace/tools/orchestrator/trigger_next.py | Medium
Postrun decisions siloed from events | Calls out | Called out | Decisions logged to logs/decisions/ and not unified with events stream. | /workspace/tools/orchestrator_postrun.py L235–264; /workspace/tools/observability/aggregate.py L7–10 | Medium
Registry emits not applied by trigger | Calls out | Called out | Trigger never applies emits.sets_state or add_completed_step. | /workspace/.cursor/commands/registry.yaml L19–23, L55–58, L73–75; /workspace/tools/orchestrator/trigger_next.py L69–75 | High
Registry defaults.one_step_policy not enforced | Not mentioned | Called out | Policy present in registry defaults but never evaluated at runtime. | /workspace/.cursor/commands/registry.yaml L2–6; /workspace/tools/orchestrator/trigger_next.py | High
Registry governance (schema/ID validation) absent | Called out | Implicit (via recs) | No schema/ID validation; regex parsing only. | /workspace/.cursor/commands/registry.yaml L1–13, L26–31; loader logic in /workspace/tools/orchestrator/trigger_next.py | High
Postrun candidate schema mismatches both scorers | Called out | Not mentioned | Candidate shape incompatible with both scorers’ expectations. | /workspace/tools/orchestrator_postrun.py L104–169; /workspace/tools/decision_scoring/advanced_score.py L32–34; /workspace/tools/decision_scoring/score.py L33–41 | High
Blind-Spot: Idempotency/safe retries | Not explicitly listed | Listed | Keep as blind spot. | N/A | Low
Blind-Spot: Rollback/compensation | Not explicitly listed | Listed | Keep as blind spot. | N/A | Low
Blind-Spot: Schema versioning/migrations | Not explicitly listed | Listed | Keep as blind spot. | N/A | Low
Final Consolidated Summary
Strong alignment between G and H across all listed topics; wording differs minimally.
No unresolved contradictions; differences are coverage/emphasis only.
Blind spots consolidated: idempotency/safe retries, rollback/compensation, schema versioning.
Scope Validation (A–H)
Coverage remains partial. A–F focused on orchestrator, scoring, registry, observability, and planning tests; G–H confirm the same areas.
Missing: cli/*, exec_queue/*, workers/*, tools/flow/*, deeper observability/* ingestion, schemas/, schema/ validations, tools/runner/plugins/*, tools/artifacts/*, tools/rule_attach/*, tools/instrumentation.py, broader tools/rules/*.
Blockers preventing Final Ground Truth:
Partial system coverage with significant runtime paths unreviewed.
Concurrency/locking and policy enforcement not validated in flows/queues/CLI.