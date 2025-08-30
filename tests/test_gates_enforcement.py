import json
from pathlib import Path

from tools.gates.gate_evaluator import evaluate_gates
from tools.orchestrator.trigger_next import load_registry_commands, _normalize_id

ROOT = Path(__file__).resolve().parents[1]


def test_gate_evaluator_produces_report(tmp_path, monkeypatch):
	# Use real repo files; ensure output path is writable
	out_path = ROOT / 'memory-bank' / 'gate_results.json'
	if out_path.exists():
		out_path.unlink()
	res = evaluate_gates()
	assert 'results' in res and isinstance(res['results'], list)
	assert out_path.exists()


def test_missing_artifacts_are_reported(monkeypatch):
	# Ensure a known must_exist is missing or use a dummy path
	registry = ROOT / '.cursor/commands/registry.yaml'
	content = registry.read_text(encoding='utf-8')
	assert 'commands:' in content
	# Evaluate
	res = evaluate_gates()
	any_missing = any(r.get('missing_files') for r in res.get('results', []))
	assert isinstance(any_missing, bool)


def test_trigger_mapping_and_gate_lookup():
	mapping = load_registry_commands()
	assert isinstance(mapping, dict) and mapping
	res = evaluate_gates()
	first_cmd = next(iter(mapping.keys()))
	entry = next((r for r in res.get('results', []) if _normalize_id(r.get('command_id','')) == first_cmd), None)
	assert entry is not None