COMPARE AND VERIFY — Report A vs Report B vs Codebase

Side‑by‑side comparison
| Finding | Report A | Report B | Codebase verdict |
|---|---|---|---|
| Runtime gates not enforced before trigger | Calls it out | Calls it out | Confirmed: trigger runs top candidate without validating gates/contexts/states |
| Dual scoring schemas (metrics vs scores) | Calls it out | Calls it out | Confirmed: advanced_score expects scores; score.py expects metrics |
| Registry invalid YAML + regex loader + non‑ASCII IDs | Calls it out | Calls it out | Confirmed: heredoc, unicode IDs, regex-only loader ignores gates/contexts |
| Execution safety defaults to run; no allowlist/sandbox/signing | Calls it out | Calls it out | Confirmed: executes unless --dry-run; no guardrails |
| Filesystem state/events: no locks or atomic writes | Calls it out | Calls it out | Confirmed: naive read/overwrite; no atomic rename/locks |
| “Attached domain” referenced but not codified in runtime | Calls it out | Calls it out | Confirmed: rules use attached(...), trigger ignores it |
| Observability lacks correlation IDs | Calls it out | Calls it out | Confirmed: counts/durations only; no correlation threading |
| Orchestrator postrun imports missing DecisionScoringTool | Not mentioned | Called out (addendum) | Confirmed: class not present in score.py |
| Cycle detection in planning | Says “appears incomplete; test fails” | Says “exists; logic passes” | A correct, B incorrect: current impl mismatches keys; test will fail |
| CI not defined; tests rely on missing arx | Says CI not defined | Original same; addendum fixes it | A incorrect (and B corrected): CI exists and installs arx |

Key code evidence (paths/lines)
```34:76:/workspace/tools/orchestrator/trigger_next.py
def run_shell(cmd: list, dry_run: bool) -> None:
    if dry_run:
        print("DRY_RUN:", " ".join(cmd))
        return
    subprocess.check_call(cmd, cwd=str(ROOT))
...
dtype = res.get("decision", {}).get("type")
if dtype in {"NEXT_STEP", "OPTION_SET"} and res.get("candidates"):
    cmd_id = res["candidates"][0]["id"]
    if cmd_id not in mapping:
        print(f"No registry mapping for id: {cmd_id}")
        return
    run_shell(mapping[cmd_id], args.dry_run)
```

```1:152:/workspace/.cursor/commands/registry.yaml
cat > .cursor/commands/registry.yaml <<'YAML'
...
  - id: planning → audit
...
      shell: ["python3","tools/run_role.py","auditor_ai","--inputs","memory-bank/plan/Action_Plan.md"]
```

```32:40:/workspace/tools/decision_scoring/advanced_score.py
def _collect_scores(c: Dict[str, Any]) -> Dict[str, float]:
    s_in = c.get("scores", {})
...
```

```33:40:/workspace/tools/decision_scoring/score.py
def score_candidate(c, W):
    m = c.get("metrics", {})
    sI = clamp01(m.get("intent", 0))
```

```24:26:/workspace/tools/orchestrator/state.py
def save_state(data: Dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
```

```14:18:/workspace/tools/runner/io_utils.py
def append_event(evt: Dict[str, Any]) -> None:
    ensure_parent(EVENTS)
    content = (EVENTS.read_text() if EVENTS.exists() else "") + json.dumps(evt) + "\n"
    EVENTS.write_text(content, encoding="utf-8")
```

```14:18:/workspace/.github/workflows/rag-check.yml
- name: Install deps + package (creates `arx` console script)
  run: |
    python -m pip install -U pip setuptools wheel
    python -m pip install -r requirements.txt
    python -m pip install -e .
```

```122:124:/workspace/pyproject.toml
[project.scripts]
arx = "cli.main:main"
advancedrules = "cli.main:main"
```

```31:33:/workspace/.cursor/rules/orchestrator/scenario_router.mdc
and([
  not(attached("domain_python")),
  not(attached("domain_node"))
])
```

```21:24:/workspace/tools/orchestrator_postrun.py
# Add decision_scoring to path
sys.path.append(str(Path(__file__).parent / "decision_scoring"))
from score import DecisionScoringTool
```

```77:98:/workspace/tests/test_planning_pipeline.py
def test_cycle_detection(self):
...
    task = Task(
        id="test_task",
...
        steps=[
            TaskStep("step1", "Step 1", dependencies=["step3"]),
            TaskStep("step2", "Step 2", dependencies=["step1"]),
            TaskStep("step3", "Step 3", dependencies=["step2"]),
        ]
    )
    is_valid, issues = decomposer.validate_task_graph(task)
    assert not is_valid
```

```25:41:/workspace/tools/observability/aggregate.py
def aggregate(items):
    counts = defaultdict(int)
    durations = defaultdict(list)
    for e in items:
        t = e.get("type", "unknown")
        counts[t] += 1
        if t == "role_duration":
            mod = e.get("module", "unknown")
            durations[mod].append(float(e.get("seconds", 0)))
```

Findings grouped

1) Confirmed by code
- Missing runtime gate enforcement in trigger path
- Divergent scoring schemas (metrics vs scores)
- Invalid registry file; brittle regex loader; non‑ASCII IDs
- Execution safety defaults to run; no allowlist/sandbox/signing
- No file locks or atomic writes for state/events
- Domain attachments unused by runtime trigger
- Observability lacks correlation IDs
- Orchestrator postrun imports nonexistent DecisionScoringTool

2) Exaggerated/incorrect claims
- “CI not defined; arx missing” → Incorrect. CI exists and installs arx, via editable install.
- “Cycle detection logic passes” → Incorrect. With current dependency keying, the cycle test will fail.

3) Blind spots (neither report mentioned)
- Workflow state schema mismatch: `state.py` writes state/prev_state/history, while postrun reads status/current_goal → stale/misleading context in postrun.
- Non‑deterministic trigger: `explore=True` in `trigger_next.py` flips candidates near ties on minute buckets, undermining deterministic tie‑breaks.
- Postrun evidence scan mismatch: looks for `reports/*.json`/`test_glob/*.json`; repo primarily uses `.md` in `reports/`.

4) Recommendations implementable now (clear loci of change)
- Enforce gates/contexts before triggers (gate evaluator + preflight in `tools/orchestrator/trigger_next.py`; consume `.mdc` and `must_exist`)
- Standardize on `advanced_score.py` with adapter for legacy `metrics` → `scores`
- Fix registry: remove heredoc, load with `yaml.safe_load`, normalize IDs to ASCII kebab, add schema validation
- Harden execution: default dry‑run via env (ALLOW_RUN=1 to enable), command allowlist, optional sandbox, registry checksum/signature
- Add correlation IDs and extend observability aggregation to include decisions/gate-failure reasons
- Stabilize tests/CI: CI already installs `arx`; optionally stub/skip where missing; ensure deps
- Improve state integrity: file locks and atomic writes (temp→fsync→rename) for state/events
- Postrun fixes: implement DecisionScoringTool wrapper or update import; align workflow state schema; adjust evidence scanning
- .mdc hygiene/runtime parity: add linter, generate machine‑readable index and compare against gate evaluator

Bottom line
- Report A: largely accurate but wrong about CI.
- Report B: largely accurate; overstates cycle detection as “passes”; correctly calls out postrun import issue.
- Codebase confirms the key gaps; recommended fixes are directly actionable with clear change points.