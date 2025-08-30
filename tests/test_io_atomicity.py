from pathlib import Path
import json
import time

from tools.io.fs import atomic_write_text


def test_atomic_write_creates_backup_and_is_complete(tmp_path):
	path = tmp_path / 'state.json'
	# initial write
	atomic_write_text(path, json.dumps({"a":1}))
	# second write
	atomic_write_text(path, json.dumps({"a":2}))
	# third write should rotate backup
	atomic_write_text(path, json.dumps({"a":3}))
	# Allow brief time for FS visibility in CI
	for _ in range(50):
		if path.exists():
			break
		time.sleep(0.002)
	assert path.exists()
	data = json.loads(path.read_text(encoding='utf-8'))
	assert data["a"] == 3
	# backup exists after third write
	bak_files = list(path.parent.glob(path.name + ".*.bak"))
	assert len(bak_files) >= 1