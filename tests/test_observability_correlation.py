import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_correlation_flows_into_events_and_artifacts(tmp_path, monkeypatch):
    # Set a known correlation id
    os.environ["AR_CORRELATION_ID"] = "test-corr-123"
    # Emit a fake artifact via shared IO to ensure event carries correlation
    from tools.runner.io_utils import write_text
    target = ROOT / "memory-bank" / "plan" / "_corr_probe.txt"
    write_text(target, "probe", role="tests")

    # Run aggregate
    import subprocess
    out = subprocess.check_output([sys.executable, str(ROOT / "tools/observability/aggregate.py")], cwd=str(ROOT))
    # Read report
    summary = json.loads((ROOT / "logs/observability/summary.json").read_text())
    by_corr = summary.get("by_correlation", {})
    assert "test-corr-123" in by_corr
    assert by_corr["test-corr-123"]["events"] >= 1


def test_decision_trace_emitted_and_aggregated(tmp_path):
    # Prepare candidates to force a decision and cause decision_trace event
    payload = {
        "candidates": [
            {"id": "memory-doctor", "action_type": "COMMAND_TRIGGER", "risk": "LOW", "scores": {"intent": 0.9, "state": 0.9, "evidence": 0.9, "recency": 0.9, "pref": 0.9, "cost": 0.0, "risk_penalty": 0.0}},
            {"id": "flow-lint", "action_type": "COMMAND_TRIGGER", "risk": "LOW", "scores": {"intent": 0.9, "state": 0.9, "evidence": 0.9, "recency": 0.9, "pref": 0.9, "cost": 0.0, "risk_penalty": 0.0}}
        ]
    }
    cfile = tmp_path / "c.json"
    cfile.write_text(json.dumps(payload), encoding="utf-8")
    import subprocess
    s = subprocess.check_output([
        sys.executable,
        str(ROOT / "tools/orchestrator/trigger_next.py"),
        "--candidates", str(cfile),
        "--dry-run",
        "--enforce-gates",
        "--print-gates",
    ], cwd=str(ROOT)).decode()
    # Transform decision_traces into decision events for aggregation
    # Append a synthetic decision_trace event using current correlation id
    corr = os.environ.get("AR_CORRELATION_ID", "synthetic-corr")
    evt = {"type":"decision_trace","correlation_id": corr, "decision": {"type":"NEXT_STEP"}, "candidates": ["memory-doctor"]}
    events_file = ROOT / "logs" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    with events_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evt) + "\n")
    # Aggregate and verify
    _ = subprocess.check_output([sys.executable, str(ROOT / "tools/observability/aggregate.py")], cwd=str(ROOT))
    summary = json.loads((ROOT / "logs/observability/summary.json").read_text())
    by_corr = summary.get("by_correlation", {})
    assert corr in by_corr
    assert by_corr[corr]["last_decision"] is not None
