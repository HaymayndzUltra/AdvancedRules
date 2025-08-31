from pathlib import Path
import threading

from tools.io.fs import file_lock, append_line_atomic


def test_file_lock_prevents_concurrent_write(tmp_path):
	path = tmp_path / 'events.jsonl'
	# acquire lock in main thread
	with file_lock(path):
		# start a writer that will block until lock is released
		lines_written = []
		def writer():
			append_line_atomic(path, '{"type":"x"}')
			lines_written.append(1)
		th = threading.Thread(target=writer)
		th.start()
		# while locked, file should not exist or be empty
		assert not path.exists() or path.read_text() == ''
	# after release, join and check content
	th.join(timeout=2)
	assert path.exists() and path.read_text().strip() != ''