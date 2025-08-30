import json
from pathlib import Path

from tools.io.fs import atomic_write_text, recover_file
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

