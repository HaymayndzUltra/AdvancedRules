import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.gates.gate_evaluator import evaluate_for_command


def test_gate_evaluator_reports_missing_state():
    # Choose a command that requires PLANNING_DONE while state is SYNTHESIS_DONE → should fail
    res = evaluate_for_command("planning-audit")
    assert not res.passed
    joined = "\n".join(res.reasons).lower()
    assert "state" in joined


def test_trigger_refuses_execution_when_gates_fail(monkeypatch, tmp_path):
    # Prepare a minimal candidates payload that selects flow-lint explicitly as top id
    payload = {
        "candidates": [
            {"id": "planning-audit", "action_type": "COMMAND_TRIGGER", "risk": "LOW", "scores": {"intent": 1, "state": 1, "evidence": 1, "recency": 1, "pref": 1, "cost": 0, "risk_penalty": 0}},
            {"id": "memory-doctor",  "action_type": "COMMAND_TRIGGER", "risk": "LOW", "scores": {"intent": 1, "state": 1, "evidence": 1, "recency": 1, "pref": 1, "cost": 0, "risk_penalty": 0}}
        ]
    }
    cfile = tmp_path / "cands.json"
    cfile.write_text(json.dumps(payload), encoding="utf-8")

    # Run trigger with gate enforcement; expect refusal due to missing files/state
    import subprocess
    out = subprocess.check_output([
        sys.executable,
        str(ROOT / "tools/orchestrator/trigger_next.py"),
        "--candidates", str(cfile),
        "--dry-run",
        "--enforce-gates",
        "--print-gates",
    ], cwd=str(ROOT))
    s = out.decode()
    assert "Refusing execution" in s or "gate_check" in s

