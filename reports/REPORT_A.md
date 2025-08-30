TASK TO AI = VERIFY THIS EXECUTIVE ASSESSMENT REPORT — check if all findings are valid, consistent, and aligned with the system’s actual design and runtime. Highlight mismatches, blind spots, or overstatements. Confirm strengths, weaknesses, and whether the recommendations are truly actionable



Executive assessment
The .mdc model is clear and powerful (always-on vs auto-attach vs agent-requested), but runtime enforcement and safety around orchestration are inconsistent. This creates a “docs say X, runtime does Y” risk.
The system’s biggest weaknesses are: unenforced gates, dual/fragmented decision-scoring schemas, brittle registry parsing/IDs, missing safety guardrails on command execution, and tests depending on a non-existent external CLI.
Inputs, outputs, constraints (by subsystem)
Orchestrator router (.mdc)
Inputs: presence of artifacts in memory-bank/plan/**, optional domain attachments.
Outputs: suggestions only (not execution).
Constraints: currently advisory; no runtime validator consumes these gates before executing.
Decision scoring
Inputs: candidates with either metrics or scores (inconsistent across two pipelines).
Outputs: ranked candidates and a decision type; optional shadow/explore modes.
Constraints: schema divergence causes real risk of mis-interpretation downstream.
Trigger/registry execution
Inputs: scorer result + .cursor/commands/registry.yaml.
Outputs: selected command invocation.
Constraints: registry file isn’t valid YAML (heredoc content), IDs contain unicode arrows/spaces, brittle regex parsing; no strong runtime guard for contexts/gates.
Runner/plugins
Inputs: memory-bank/* artifacts.
Outputs: artifacts (with provenance) and state transitions.
Constraints: file-system based; lacks locking for concurrent runs and recovery semantics.
Observability/provenance
Inputs: events.jsonl and emitted artifacts.
Outputs: summary reports and hash index.
Constraints: limited correlation; hard to trace decision → command → state → artifacts.
Tests/CI
Inputs: pytest, networkx (ok), arx CLI (missing).
Outputs: smoke and integration checks.
Constraints: tests relying on arx will fail in a clean environment; CI not defined.
Top gaps, conflicts, blind spots
Enforced gates are missing at runtime
Router is advisory; trigger_next.py does not validate “must_exist” preconditions or router gates. A candidate can be selected even if prerequisites are absent.
Two decision pipelines with incompatible schemas
score.py expects metrics; advanced_score.py expects scores (+calibration/sigmoid). This can silently mis-rank or drop candidates.
Registry “YAML” is not valid YAML; IDs mismatch scoring candidates
File contains heredoc preface; parsed via regex; many IDs (e.g., “planning → audit”) don’t match scorer candidate IDs (“planning_from_backlog”), so mapping fails.
Safety and execution guardrails are weak by default
trigger_next.py runs real commands unless --dry-run is passed; no allowlist, no environment gate, no contained sandbox, no checksum validation.
Tests depend on a missing external CLI (arx)
Causes failing tests in clean environments; reduces signal.
Concurrency and integrity risks around filesystem state
No file locks on workflow_state.json; backups are ad-hoc; partial writes or concurrent runs can corrupt state.
Cycle detection in planning appears incomplete
Test expecting cycle detection fails; indicates a logic gap in TaskDecomposer.validate_task_graph.
“Attached domain” is referenced but not codified
Rules use attached("domain_python")/("domain_node") but runtime attachment evidence isn’t produced/consumed programmatically.
Observability lacks correlation
No correlation ID carried across decision → trigger → state → artifact; difficult to audit causality.
Registry governance
No schema validation for registry entries; no pre-flight validation of arguments/side effects.
Edge cases to address now
Multiple valid candidates with near-tie scores → deterministic tie-break that respects cost/risk policies.
Partially present artifacts (e.g., Action_Plan.md exists but empty) → guard on size/content schema, not just existence.
Concurrent triggers opening/overwriting workflow_state.json without atomic write → use write-temp→fsync→rename.
Platform paths and unicode in registry IDs → normalize before mapping (ASCII-only IDs).
Dry-run documented but forgotten in scripts → centralize default to “dry-run unless ALLOW_RUN=1”.
Recommendations (prioritized, actionable)
1) Enforce gates and contexts in the trigger path
Add a gate evaluator that produces gate_results.json from .mdc router + current artifacts.
In trigger_next.py, before running any command:
Validate: must_exist paths, required states, gates (PLANNING_GATE, AUDIT_GATE…), and domain attachment predicates.
Refuse execution with a crisp error listing the missing inputs.
2) Standardize on one scoring schema and adapter
Adopt advanced_score.py as the canonical scorer.
Add a thin adapter that converts legacy “metrics” candidates into canonical “scores”.
Validate input with a Pydantic/JSONSchema; reject unknown keys or missing required dimensions.
3) Fix the registry format and IDs; load with YAML
Replace heredoc content with valid YAML (no shell preface). Load via yaml.safe_load.
Normalize command IDs to ASCII kebab (e.g., planning-to-audit, audit-to-verify).
Add a preflight validator for registry schema (id uniqueness; shell as array of strings; contexts/gates/states typed).
4) Harden execution safety
Default to dry-run unless ALLOW_RUN=1.
Enforce command allowlist (e.g., only python3, arx subcommands; deny destructive utilities unless explicitly allowed).
Optionally sandbox with a profile (e.g., Docker/Firejail) for COMMAND_TRIGGER executions.
Require a checksum or signature over the registry (tamper detection).
5) Make gates programmatic and observable
Implement a “gate evaluator” module (inputs: router.mdc + artifacts + state; output: gate_results.json).
Emit a correlation ID on decision → trigger → state transition → artifact writes; aggregate by ID in observability.
6) Stabilize tests and CI
Provide a local stub for arx CLI (no-op responses) used by tests, or mark those tests as skipped when arx is not on PATH.
Add GitHub Actions that run: lint, unit tests, gate evaluator, schema validation, and scorer smoke.
Ensure test deps are declared (pytest, networkx, pyyaml).
7) Improve state integrity and concurrency
Use file locks (fcntl or portalocker) for workflow_state.json reads/writes; adopt atomic write (temp→fsync→rename) and keep a rolling backup.
Consider migrating provenance and decisions to SQLite with indexed tables while keeping file artifacts as the canonical source.
8) Observability and auditability
Extend aggregate.py to report per-correlation metrics, decision distributions (NEXT_STEP vs OPTION_SET), and gate-failure reasons.
Emit decision traces with reasons and include them in reports.
9) Developer experience and maintainability
Replace regex parsing with structured parsers everywhere (registry, candidates).
Add type hints across tools; enable mypy in CI.
Consolidate duplicate utilities (write_text/append_event appear in multiple modules) to a single IO layer.
10) .mdc hygiene and runtime parity
Add a linter for .mdc rules: check frontmatter completeness, valid globs, and prohibited patterns.
Generate a machine-readable index (rules → gates → required artifacts) and compare it against the gate evaluator to keep docs and runtime aligned.
Questions to de-risk scope (answer to finalize plan)
Domain attachments: What is the canonical source of “attached(domain_)”? Should this be derived (e.g., via .cursor/rules/domains/ presence) or explicitly configured?
Command execution policy: Which commands are permitted for COMMAND_TRIGGER? Can we formalize an allowlist and a sandbox profile?
Registry change control: Should registry changes require review/signoff? Do we want a checksum/signature?
Runner concurrency: Is parallel persona execution expected? If yes, we need explicit locking semantics and queueing.
Artifact validation: Should artifact existence checks be upgraded to schema/content checks? If so, which artifacts must be strongly validated (e.g., acceptance_criteria.json)?
CI policy: Which gates (prestart, planning, audit) must pass before merging to main?
UX polish (fast wins)
Consistently default all CLI helpers to dry-run and print “How to enable execution” hints.
On any rejection (missing artifact/gate), print the exact file and the one-liner to create/validate it.
Provide arx test stub or a “developer mode” that replaces arx with local functions to keep tests green out-of-the-box.
Normalize messages and IDs: ASCII-only, kebab-case, predictable mapping from router → scorer → registry.
If you want, I can draft:
A canonical YAML schema for candidates, decisions, and registry entries.
A gate evaluator spec and a minimal reference implementation.
A migration PR that: fixes registry YAML, normalizes IDs, enforces dry-run default, and adds command allowlist + unit tests.






AI REPORT = 


Executive Assessment Verification Report
Scope: Verify if all findings in the assessment are valid, consistent, and aligned with the system’s actual design and runtime. Highlight mismatches, blind spots, overstatements; confirm strengths/weaknesses; judge actionability of recommendations.

Verdict
- Overall: The assessment is largely accurate. Most issues are confirmed in code. No major overstatements found. A few extra blind spots exist and are added below.

Validated Findings (with brief evidence)
- Router/gates are not enforced at runtime
  - The trigger executes top candidate directly; no programmatic evaluation of .mdc gates or must_exist contexts before execution. Defaults to “map id → shell” and run.
  - Consequence: “docs say X, runtime does Y” risk is real.

- Two decision pipelines with incompatible schemas
  - advanced_score.py expects candidates.scores; score.py expects candidates.metrics.
  - Consequence: Mixed inputs can mis-rank or get dropped if the wrong scorer is used.

- Registry format invalid + ID and parsing issues
  - Registry has a heredoc header (not valid YAML) and IDs include unicode arrows/spaces.
  - Trigger uses regex to parse only id and shell, ignores contexts/gates/requires entirely; no YAML loader; no templating for {{vars}}.
  - Mapping likely fails when scorer returns IDs that don’t exist verbatim (e.g., planning_from_backlog vs “planning → audit”).

- Safety guardrails weak by default
  - Real execution happens unless --dry-run is passed; no allowlist, no sandbox, no checksum/tamper detection.

- Tests depend on external arx CLI; CI doesn’t install it
  - Tests call arx directly; package.json CI doesn’t install the Python package or expose arx. Clean environments will fail.

- Concurrency/integrity risks (filesystem state)
  - State/events are written without locks (append/overwrite), no atomic write (temp→fsync→rename), no recovery scheme.

- Cycle detection mismatch in planning
  - Validation builds edges between dependency string and step.description. Tests use step IDs in dependencies, so cycles may be missed; test designed to catch cycles can fail.

- Domain “attached” is not consumed by orchestrator
  - Rule-attach logs matches to a JSONL, but trigger does not consult that log or enforce domains/gates.

- Observability lacks correlation
  - Events aggregated by type/module and simple durations; no correlation ID across decision → trigger → state → artifacts.

- Registry governance and validation missing
  - No YAML schema validation; no preflight checks for ID uniqueness, shell as array, contexts/gates/states typing; no normalization.

Additional Blind Spots (noted during review)
- No variable substitution for registry templating (e.g., {{flow_id}}) at trigger time.
- Duplicated IO helpers for events/artifacts across modules (maintenance risk).
- Registry defaults (e.g., one_step_policy) are not enforced in runtime.
- Some rule files and docs imply flows/queues and gating but no corresponding runtime implementations exist in the trigger path.

Confirmed Strengths
- .mdc rule structure is clear; globs and alwaysApply are parsed and attachments are logged (programmatic evidence of “attached” rules).
- Scoring v3 supports calibrated weights, exploration (eps), shadow mode, and risk-based dampening for command triggers.
- Artifact provenance: file hashing recorded to memory-bank/artifacts_index.json for emitted artifacts.
- Runner/plugins and state transitions exist for core roles; planning pipeline is modular with NetworkX for graph reasoning.

Actionability of Recommendations
- All major recommendations are actionable with clear loci of change (primarily tools/orchestrator/trigger_next.py, .cursor/commands/registry.yaml, tools/decision_scoring/*, tools/observability/*, tests/CI).

Prioritized, Actionable Recommendations (crisp next steps)
1) Enforce gates and contexts in trigger path
   - Implement a gate evaluator module: inputs (.mdc router, current artifacts/state) → gate_results.json (pass/fail + reasons).
   - In trigger, before execution: validate must_exist paths, required states, and named gates; fail fast with a precise error.
   - Wire domain attachment predicates (from rule_attach log) into gating.

2) Standardize on one scoring schema (+ adapter)
   - Canonicalize advanced_score.py.
   - Provide an adapter that maps legacy metrics to scores shape.
   - Add strict input validation (pydantic/jsonschema) to reject unknown/missing fields.

3) Fix the registry format and IDs; parse with YAML
   - Remove heredoc header; keep valid YAML only.
   - Normalize IDs to ASCII kebab-case; keep a stable mapping from router → scorer → registry.
   - Load via yaml.safe_load; validate registry schema (id uniqueness, typed fields, shell as list of strings).

4) Harden execution safety
   - Default to dry-run unless ALLOW_RUN=1 is present.
   - Enforce a command allowlist (e.g., python3 tools/run_role.py, arx subcommands).
   - Optional: sandbox COMMAND_TRIGGER (Docker/Firejail profile).
   - Add a signed checksum for the registry to detect tampering.

5) Make gates programmatic and observable
   - Emit per-decision correlation_id; carry it through trigger → state transitions → artifact writes.
   - Aggregate observability by correlation_id; include gate failure reasons and decision traces.

6) Stabilize tests and CI
   - Install the package in CI (pip install -e .) or provide a local arx stub; skip arx tests if CLI not available.
   - Ensure requirements include pytest, networkx, pyyaml.
   - Add a job to run gate evaluator, schema validation, and scorer smoke.

7) Improve state integrity and concurrency
   - Add file locks (fcntl/portalocker) around workflow_state.json and events; adopt atomic write (temp→fsync→rename) and rolling backups.
   - Consider SQLite for decisions/provenance (indexed) while keeping file artifacts canonical.

8) Observability and auditability
   - Extend aggregate to compute per-correlation metrics, decision distribution, and gate reasons; emit decision traces with explanations.

9) Developer experience and maintainability
   - Replace regex parsing with structured parsers for registry and candidates.
   - Deduplicate IO utilities; add type hints; enable mypy in CI.

10) .mdc hygiene and runtime parity
   - Add .mdc linter (frontmatter completeness, valid globs, prohibited patterns).
   - Generate a machine-readable index (rules → gates → required artifacts) and compare against the gate evaluator to ensure docs/runtime alignment.

Open Questions to De-risk Scope (confirm to finalize plan)
- Domain attachments: Canonical source of attached(domain_)? Derive from .cursor/rules/domains/* presence or explicit config?
- Command execution policy: Which commands are allowed for COMMAND_TRIGGER? Approve an allowlist and sandboxing profile?
- Registry change control: Require review/signoff? Adopt checksum/signature policy?
- Runner concurrency: Expect parallel persona runs? If yes, define locking semantics and queueing.
- Artifact validation: Which artifacts merit schema/content validation beyond existence (e.g., acceptance_criteria.json)?
- CI policy: Which gates (prestart, planning, audit) must pass before merging to main?

Quick UX Wins
- Default all CLIs to dry-run and print “How to enable execution” hints.
- On rejection, print the exact missing file and one-liner to create/validate it.
- Provide arx test stub or developer mode to keep tests green by default.
- Normalize all IDs/messages: ASCII-only, kebab-case, deterministic mapping across router → scorer → registry.

Notable Mismatches to Call Out
- Registry IDs and scorer candidate IDs do not align; current trigger will frequently print “No registry mapping for id”.
- Cycle detection checks step descriptions, while tests set dependencies by step IDs; actual cycles may slip through.
- The “one_step_policy” and similar registry defaults have no runtime enforcement.

Summary (what this means)
- The current system prioritizes documentation and scaffolding over strict runtime enforcement. The most critical runtime gaps are gate enforcement, registry correctness, and execution safety. Addressing the five highest-priority items (gates, single-scoring schema, valid YAML + normalization, safety defaults/allowlist, and CI CLI setup) will eliminate the primary “docs vs runtime” mismatch and stabilize end-to-end orchestration.

