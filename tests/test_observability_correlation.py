import json
from pathlib import Path

from tools.runner.io_utils import append_event, append_decision_trace
from tools.observability.aggregate import load_events, load_traces, aggregate_by_correlation

ROOT = Path(__file__).resolve().parents[1]


def test_correlation_propagation(tmp_path):
	cid = "corr-test-123"
	append_decision_trace({"type":"decision","top":"x","decision":{"type":"NEXT_STEP"},"correlation_id":cid})
	append_event({"type":"artifact_emitted","path":"memory-bank/plan/Action_Plan.md","correlation_id":cid})
	events = load_events()
	traces = load_traces()
	corr = aggregate_by_correlation(events, traces)
	assert cid in corr["by_correlation"], corr
	entry = corr["by_correlation"][cid]
	assert entry["event_count"] >= 1 and entry["trace_count"] >= 1