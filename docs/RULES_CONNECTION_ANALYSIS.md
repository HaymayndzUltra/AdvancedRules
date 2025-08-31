# `.cursor/rules` Connection Analysis

## Summary: YES, IT IS CONNECTED! ✅

The `.cursor/rules` directory is **fully integrated** into the framework's execution flow. Here's how:

## 1. **Rules Index Generation** 📚
- **Tool**: `tools/rules/index_generator.py`
- **Output**: `memory-bank/rules_index.json` 
- **What it does**: Scans all `.mdc` files and creates a machine-readable index with:
  - Rule metadata (description, globs, always_apply)
  - Gates defined by each rule
  - Required artifacts for each rule
  - Attachment references between rules

## 2. **Gate Evaluator Integration** 🚪
- **Tool**: `tools/gates/gate_evaluator.py`
- **How it works**:
  1. Loads `memory-bank/rules_index.json`
  2. Checks if required artifacts exist (from `required_artifacts` in rules)
  3. Validates domain attachments
  4. Returns pass/fail for each gate
  
## 3. **Trigger Enforcement** 🔒
- **Tool**: `tools/orchestrator/trigger_next.py`
- **Integration point** (line 176):
  ```python
  gates = evaluate_gates()
  gate_entry = next((r for r in gates.get("results", []) if _normalize_id(r.get("command_id","")) == cmd_id), None)
  if gate_entry and not gate_entry.get("passed", False):
      print("Refusing execution: gate checks failed for", cmd_id)
  ```
- **Effect**: Commands in `registry.yaml` are blocked if their required gates don't pass

## 4. **Command Registry Mapping** 🗺️
- **File**: `.cursor/commands/registry.yaml`
- **Key fields that connect to rules**:
  - `requires.gates_passed_all_of`: Must match gates from rules
  - `contexts.must_exist`: Files that rules check for
  - `requires.states_any_of`: States that rules can set
  - `requires.completed_steps_all_of`: Steps that rules track

## 5. **Active Rules in Your System** 📋

### High-Impact Rules (with gates/artifacts):
1. **readiness_check.mdc**
   - Gates: None defined but checks many artifacts
   - Required artifacts: 13 files (client_score, capacity_report, etc.)
   - Actions: attach_rules, suggest, set_state
   
2. **scenario_router.mdc** 
   - Controls which commands are available based on artifacts
   - Required artifacts: 8 files (client_brief, Action_Plan, etc.)
   - Enables: run_product_owner, run_planning, run_auditor flows

3. **orchestrator_postrun.mdc**
   - Gates: `results`
   - Applied to: All files (`**/*`)
   
4. **scope_guard.mdc**
   - Gates: `scope`
   - Validates scope changes against baseline

### Domain Detection Rules:
- **python.mdc**: Activates for `requirements.txt`, `pyproject.toml`
- **node.mdc**: Activates for `package.json`, `tsconfig.json`
- **devops.mdc**: Activates for CI/CD files (`.yml`, `.yaml`, `Dockerfile`)
- Plus 20+ other domain-specific rules

### Always-Apply Rules:
1. **next_step_suggester.mdc** - Suggests next steps after each command
2. **CURSOR USAGE STANDARDS.mdc** - Coding standards enforcement
3. **typescript-base.mdc** - TypeScript base configuration

## 6. **Execution Flow** 🔄

```mermaid
graph TD
    A[User runs command] --> B[trigger_next.py]
    B --> C[Load registry.yaml]
    B --> D[evaluate_gates()]
    D --> E[Load rules_index.json]
    E --> F[Check required artifacts]
    E --> G[Check domain attachments]
    F --> H{Gates Pass?}
    G --> H
    H -->|Yes| I[Execute command via run_shell()]
    H -->|No| J[Block execution with reasons]
    I --> K[Plugin/Role execution]
    K --> L[State transitions]
    K --> M[Create artifacts]
    M --> N[Trigger rules again]
```

## 7. **Evidence of Connection** 🔍

### From `rules_index.json`:
- **50 rules indexed**
- **10 unique gates defined**
- **40 required artifacts tracked**
- **3 always-apply rules active**

### From Registry:
- Commands reference gates like `PLANNING_GATE`, `AUDIT_GATE`
- Commands check artifacts that rules validate
- Commands transition states that rules set

## 8. **How to Add Your Own Rule** ➕

1. Create `.cursor/rules/my_rule.mdc`:
```yaml
---
description: "My custom rule"
globs: ["**/*.py"]  # When to apply
alwaysApply: false
---

<rule>
name: my_gate
actions:
  - type: reject
    when: missing("required_file.txt")
    message: "Missing required file!"
</rule>
```

2. Regenerate index:
```bash
python3 tools/rules/index_generator.py
```

3. Reference in registry:
```yaml
commands:
  - id: my-command
    requires:
      gates_passed_all_of: ["my_gate"]
```

## Conclusion

The `.cursor/rules` directory is **deeply integrated** into the framework through:
- Automated indexing → Gate evaluation → Command blocking
- File existence checks → State management → Domain detection
- Always-apply rules for continuous governance

Every command execution passes through this rule system, making it a core part of the framework's governance model.