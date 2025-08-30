import json
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the modules we're testing
import tools.queue.exec_queue as exec_queue
import tools.queue.worker as worker


def test_enqueue_and_idempotency(tmp_path, monkeypatch):
	"""Test that enqueue works and duplicate correlation_ids are handled."""
	# Mock the queue directory to use tmp_path
	queue_dir = tmp_path / "exec_queue"
	queue_dir.mkdir(parents=True, exist_ok=True)
	
	monkeypatch.setattr(exec_queue, 'QUEUE_DIR', queue_dir)
	monkeypatch.setattr(exec_queue, 'QUEUE_FILE', queue_dir / 'exec_queue.jsonl')
	monkeypatch.setattr(exec_queue, 'PROCESSED_FILE', queue_dir / 'processed.jsonl')
	
	# Test enqueue
	cmd_id = 'test-command'
	cid = 'corr-queue-123'
	
	# Enqueue the same task twice (should be idempotent based on correlation_id)
	result1 = exec_queue.enqueue_task(cmd_id, cid, {"shell": ["echo", "test"]})
	result2 = exec_queue.enqueue_task(cmd_id, cid, {"shell": ["echo", "test"]})
	
	assert result1["status"] == "queued"
	assert result1["correlation_id"] == cid
	assert result2["status"] == "queued"
	assert result2["correlation_id"] == cid
	
	# Load queue and verify both entries exist (idempotency is checked during processing)
	queue_items = exec_queue.load_queue()
	assert len(queue_items) == 2  # Both enqueued
	assert all(item["correlation_id"] == cid for item in queue_items)
	
	# Mark one as processed
	exec_queue.mark_processed(cid, {"status": "completed"})
	
	# Check processed IDs
	processed = exec_queue.processed_ids()
	assert cid in processed


def test_worker_process_once(tmp_path, monkeypatch):
	"""Test that worker.process_once handles queued items correctly."""
	# Mock the queue directory
	queue_dir = tmp_path / "exec_queue"
	queue_dir.mkdir(parents=True, exist_ok=True)
	
	monkeypatch.setattr(exec_queue, 'QUEUE_DIR', queue_dir)
	monkeypatch.setattr(exec_queue, 'QUEUE_FILE', queue_dir / 'exec_queue.jsonl')
	monkeypatch.setattr(exec_queue, 'PROCESSED_FILE', queue_dir / 'processed.jsonl')
	
	# Create mock registry and state files
	registry_dir = tmp_path / ".cursor" / "commands"
	registry_dir.mkdir(parents=True, exist_ok=True)
	registry_file = registry_dir / "registry.yaml"
	registry_file.write_text("""
commands:
  - id: test-command
    ui:
      label: Test Command
    run:
      shell: ["echo", "test"]
    contexts:
      must_exist: []
      states_any_of: []
""")
	
	# Create workflow state
	workflow_state_file = tmp_path / "workflow_state.json"
	workflow_state_file.write_text(json.dumps({
		"state": "ready",
		"history": [],
		"schema_version": "1.0.0",
		"last_updated": "2024-01-01T00:00:00Z"
	}))
	
	# Mock the ROOT path for the worker
	monkeypatch.setattr(worker, 'ROOT', tmp_path)
	
	# Also need to mock the trigger_next module's paths since worker imports from it
	from tools.orchestrator import trigger_next
	monkeypatch.setattr(trigger_next, 'ROOT', tmp_path)
	monkeypatch.setattr(trigger_next, 'REG', tmp_path / ".cursor/commands/registry.yaml")
	monkeypatch.setattr(trigger_next, 'REG_SHA', tmp_path / ".cursor/commands/registry.sha256")
	
	# Mock various functions to avoid actual execution
	with patch.object(worker, 'verify_registry_checksum', return_value=(True, "OK")), \
	     patch.object(worker, 'evaluate_gates', return_value={"results": []}), \
	     patch.object(worker, 'is_command_allowed', return_value=(True, "allowed")), \
	     patch.object(worker, 'should_dry_run', return_value=True), \
	     patch.object(worker, 'run_shell') as mock_run:
		
		# Enqueue a task
		cmd_id = 'test-command'
		cid = 'corr-worker-123'
		exec_queue.enqueue_task(cmd_id, cid, {"shell": ["echo", "test"]})
		
		# Process the queue
		count = worker.process_once()
		
		# Should have processed 1 item in dry-run mode
		assert count == 1
		
		# Check that it was marked as processed
		processed = exec_queue.processed_ids()
		assert cid in processed
		
		# run_shell should not have been called (dry-run mode)
		mock_run.assert_not_called()


def test_worker_respects_allowlist(tmp_path, monkeypatch):
	"""Test that worker respects command allowlist."""
	# Mock the queue directory
	queue_dir = tmp_path / "exec_queue"
	queue_dir.mkdir(parents=True, exist_ok=True)
	
	monkeypatch.setattr(exec_queue, 'QUEUE_DIR', queue_dir)
	monkeypatch.setattr(exec_queue, 'QUEUE_FILE', queue_dir / 'exec_queue.jsonl')
	monkeypatch.setattr(exec_queue, 'PROCESSED_FILE', queue_dir / 'processed.jsonl')
	
	# Mock ROOT
	monkeypatch.setattr(worker, 'ROOT', tmp_path)
	
	# Mock functions
	with patch.object(worker, 'verify_registry_checksum', return_value=(True, "OK")), \
	     patch.object(worker, 'evaluate_gates', return_value={"results": []}), \
	     patch.object(worker, 'is_command_allowed', return_value=(False, "not in allowlist")), \
	     patch.object(worker, 'load_registry_commands', return_value={'blocked-cmd': ['rm', '-rf', '/']}):
		
		# Enqueue a blocked command
		cmd_id = 'blocked-cmd'
		cid = 'corr-blocked-123'
		exec_queue.enqueue_task(cmd_id, cid, {})
		
		# Process the queue
		count = worker.process_once()
		
		# Should have skipped the item (not in allowlist)
		assert count == 0
		
		# Should still be marked as processed (but skipped)
		processed = exec_queue.processed_ids()
		assert cid in processed