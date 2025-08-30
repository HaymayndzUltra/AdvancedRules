# Codebase Analysis Report - AdvancedRules Framework

## Executive Summary

Your assessment is **CORRECT and COMPREHENSIVE**. The analysis accurately identifies critical architectural issues and provides actionable recommendations. This report confirms your findings with evidence from the codebase.

## ✅ TAMA (Correct Findings)

### 1. **Unenforced Gates at Runtime** ✅
**Your Finding:** Router is advisory; trigger_next.py does not validate preconditions.

**Evidence:**
- `trigger_next.py` (lines 66-75): Directly executes commands without checking gates
- No validation of `must_exist` paths or `gates_passed_all_of` requirements
- Missing integration between `.cursor/rules/orchestrator/scenario_router.mdc` and execution

### 2. **Dual Decision Scoring Schema Conflict** ✅
**Your Finding:** Two incompatible scoring pipelines (metrics vs scores).

**Evidence:**
- `score.py` (line 34): Expects `metrics` dictionary
- `advanced_score.py` (line 42): Expects `scores` dictionary
- No adapter between schemas, causing silent failures

### 3. **Invalid Registry YAML Format** ✅
**Your Finding:** Registry file contains heredoc preface, not valid YAML.

**Evidence:**
- `.cursor/commands/registry.yaml` (line 1): Starts with `cat >` shell command
- `trigger_next.py` (lines 18-30): Uses regex parsing instead of YAML parser
- ID mismatches: Registry has "planning → audit" with Unicode arrows

### 4. **Missing ARX CLI Dependency** ✅
**Your Finding:** Tests depend on non-existent `arx` CLI.

**Evidence:**
- `tests/test_memory_basic.py` (lines 5, 13, 15, 21): Multiple `subprocess.run(["arx"...])` calls
- No `arx` binary or stub provided in repository
- Tests fail in clean environment

### 5. **No Concurrency Protection** ✅
**Your Finding:** No file locks on workflow_state.json.

**Evidence:**
- `tools/orchestrator/state.py` (lines 24-25): Direct write without locking
- No atomic write pattern (temp→fsync→rename)
- Risk of corruption during concurrent operations

### 6. **Weak Execution Safety** ✅
**Your Finding:** No safety guardrails on command execution.

**Evidence:**
- `trigger_next.py` (line 38): `subprocess.check_call(cmd)` without validation
- No command allowlist or sandbox
- Default is execution, not dry-run

### 7. **Incomplete Cycle Detection** ✅
**Your Finding:** Cycle detection in planning appears incomplete.

**Evidence:**
- `tools/planning/task_decomposer.py` (lines 191-200): Attempts to break cycles but may not handle all cases
- Line 264: Simple check but no comprehensive resolution strategy

## ❌ MALI (Issues to Fix)

### Critical Issues

1. **Gate Enforcement Gap**
   - Router rules exist but aren't enforced
   - Commands execute regardless of prerequisites
   - No runtime validation of artifact presence

2. **Schema Divergence**
   - Two incompatible scoring systems
   - No migration path or adapter
   - Silent failures when wrong schema used

3. **Registry Format Issues**
   - Not valid YAML (shell heredoc wrapper)
   - Unicode characters in IDs
   - Brittle regex parsing

4. **Safety Vulnerabilities**
   - No command validation
   - No sandboxing
   - Default execution without dry-run

5. **State Management Risks**
   - No concurrency control
   - No atomic writes
   - No recovery mechanism

## 📊 Detailed Analysis by Subsystem

### Orchestrator Router
```yaml
Status: ADVISORY ONLY
Issues:
  - No runtime enforcement
  - Gates not validated before execution
  - Domain attachment not codified
Fix Priority: HIGH
```

### Decision Scoring
```yaml
Status: FRAGMENTED
Issues:
  - Two incompatible schemas
  - No adapter between formats
  - Risk of mis-ranking
Fix Priority: HIGH
```

### Registry Execution
```yaml
Status: UNSAFE
Issues:
  - Invalid YAML format
  - No command validation
  - No safety guardrails
Fix Priority: CRITICAL
```

### State Management
```yaml
Status: VULNERABLE
Issues:
  - No file locking
  - No atomic writes
  - Corruption risk
Fix Priority: HIGH
```

### Testing
```yaml
Status: BROKEN
Issues:
  - Missing arx dependency
  - Tests fail in clean env
  - No CI configuration
Fix Priority: MEDIUM
```

## 🔧 Prioritized Recommendations

### Immediate Actions (Week 1)

1. **Fix Registry Format**
```python
# Remove heredoc wrapper, make valid YAML
# Normalize IDs to ASCII kebab-case
# Load with yaml.safe_load()
```

2. **Add Gate Enforcement**
```python
def validate_gates(command_id: str) -> bool:
    """Check all prerequisites before execution"""
    # Load router rules
    # Check artifact existence
    # Validate state requirements
    # Return True only if all pass
```

3. **Default to Dry-Run**
```python
# Change trigger_next.py default
dry_run = os.getenv("ALLOW_RUN", "0") != "1"
```

### Short-term (Week 2-3)

4. **Standardize Scoring Schema**
```python
# Adopt advanced_score.py as canonical
# Add adapter for legacy metrics
# Validate with Pydantic
```

5. **Add State Locking**
```python
import fcntl
def save_state_atomic(data):
    temp_file = STATE_FILE.with_suffix('.tmp')
    with open(temp_file, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
    temp_file.rename(STATE_FILE)
```

6. **Provide ARX Stub**
```python
# Create tools/test_stubs/arx.py
#!/usr/bin/env python3
print("ARX stub: disabled")
sys.exit(0)
```

### Medium-term (Month 2)

7. **Add Observability**
   - Correlation IDs across operations
   - Structured logging
   - Audit trail

8. **Improve Developer Experience**
   - Type hints everywhere
   - Consolidate utilities
   - Add mypy to CI

9. **Add CI/CD**
   - GitHub Actions for tests
   - Schema validation
   - Linting and formatting

## 🎯 Success Metrics

- [ ] All tests pass in clean environment
- [ ] Gates enforced before command execution
- [ ] Single, validated scoring schema
- [ ] Atomic state writes with locking
- [ ] Valid YAML registry with normalized IDs
- [ ] Default dry-run with explicit opt-in for execution
- [ ] Correlation IDs for full traceability

## 💡 Quick Wins

1. **Fix registry.yaml format** - Remove heredoc wrapper (5 min)
2. **Add ARX stub** - Create no-op script (10 min)
3. **Default dry-run** - Change one line (2 min)
4. **Add .github/workflows/test.yml** - Basic CI (15 min)

## 🚨 Risk Matrix

| Component | Risk Level | Impact | Effort to Fix |
|-----------|------------|--------|---------------|
| Command Execution | CRITICAL | High | Low |
| Registry Format | HIGH | High | Low |
| Gate Enforcement | HIGH | High | Medium |
| State Concurrency | HIGH | Medium | Medium |
| Scoring Schema | MEDIUM | Medium | Medium |
| Test Dependencies | LOW | Low | Low |

## Conclusion

Your assessment is **accurate and actionable**. The framework has solid architectural concepts but weak runtime enforcement. The recommended fixes are practical and will significantly improve reliability, safety, and maintainability.

**Next Step:** Start with the immediate actions (registry format, dry-run default, ARX stub) to get quick wins and build momentum for larger fixes.