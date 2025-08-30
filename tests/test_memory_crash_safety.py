import json
import subprocess
from pathlib import Path

from tools.io.fs import atomic_write_text, recover_file
from tools.io.safe_read import safe_read_json, safe_read_text
from tools.runner.io_utils import write_text, touch_json


def test_invalid_memory_write_rejected(tmp_path):
	mb = tmp_path / 'memory-bank' / 'business'
	mb.mkdir(parents=True, exist_ok=True)
	# client_score requires fields; write invalid JSON content via touch_json
	p = mb / 'client_score.json'
	try:
		# Missing required fields should raise
		touch_json(p, {"foo": "bar"})
		assert False, "Expected validation error"
	except ValueError as e:
		assert 'validation' in str(e).lower()
	assert not p.exists()


def test_crash_safe_write_and_recovery(tmp_path):
	# Simulate crash: .tmp exists but final file missing
	file_path = tmp_path / 'memory-bank' / 'plan' / 'proposal.md'
	file_path.parent.mkdir(parents=True, exist_ok=True)
	# Create a temp file as if write crashed before rename
	tmp = Path(str(file_path) + '.tmp')
	tmp.write_text('Hello world', encoding='utf-8')
	# Now recover
	recovered = recover_file(file_path)
	assert recovered is True
	assert file_path.exists()
	assert file_path.read_text(encoding='utf-8') == 'Hello world'


def test_backup_restore_on_corrupt_json(tmp_path):
	# Create a valid JSON, then backup via write, then corrupt and recover
	p = tmp_path / 'memory-bank' / 'business' / 'client_score.json'
	p.parent.mkdir(parents=True, exist_ok=True)
	# First write valid JSON
	atomic_write_text(p, json.dumps({"fit_score": 90, "project_risk": "LOW", "complexity": "M"}))
	# Second write to create backup
	atomic_write_text(p, json.dumps({"fit_score": 80, "project_risk": "LOW", "complexity": "M"}))
	# Corrupt file
	p.write_text('{invalid json', encoding='utf-8')
	# Attempt recovery
	recovered = recover_file(p)
	assert recovered is True
	# File should be valid JSON after recovery
	data = json.loads(p.read_text(encoding='utf-8'))
	assert 'fit_score' in data


def test_safe_read_with_auto_recovery(tmp_path):
	# Test safe_read_json auto-recovers from corruption
	p = tmp_path / 'test.json'
	# Write valid, then backup, then corrupt
	atomic_write_text(p, '{"valid": true}')
	atomic_write_text(p, '{"valid": "still true"}')
	p.write_text('corrupted{', encoding='utf-8')
	
	# Safe read should auto-recover
	data = safe_read_json(p)
	assert data is not None
	assert 'valid' in data
	
	# Test safe_read_text on empty file with backup
	t = tmp_path / 'test.txt'
	atomic_write_text(t, 'Hello world')  # First write
	atomic_write_text(t, 'Hello again')  # Second write (backs up 'Hello world')
	t.write_text('', encoding='utf-8')  # Empty it
	
	content = safe_read_text(t)
	# The newest backup contains 'Hello world' (created when writing 'Hello again')
	assert content == 'Hello world'  # Should recover from backup


def test_full_schema_validation(tmp_path):
	# Test that full JSON schema validation works with jsonschema
	mb = tmp_path / 'memory-bank' / 'business'
	mb.mkdir(parents=True, exist_ok=True)
	
	# Valid client score
	valid_score = {
		"fit_score": 85,
		"project_risk": "MEDIUM",
		"complexity": "L",
		"must_ask": ["Timeline?", "Budget?"],
		"decline_reasons": []
	}
	p = mb / 'client_score.json'
	
	# Should accept valid data
	touch_json(p, valid_score)
	assert p.exists()
	
	# Invalid enum value should be rejected if jsonschema is available
	invalid_score = valid_score.copy()
	invalid_score["project_risk"] = "UNKNOWN"  # Not in enum
	p2 = mb / 'client_score2.json'
	
	try:
		import jsonschema
		# With jsonschema, this should fail
		try:
			touch_json(p2, invalid_score)
			assert False, "Should have rejected invalid enum"
		except ValueError as e:
			assert 'validation' in str(e).lower()
	except ImportError:
		# Without jsonschema, simple validation passes (only checks required fields)
		touch_json(p2, invalid_score)
		assert p2.exists()

