import json
import os
import time
from pathlib import Path
import pytest

from tools.plugins.wrapper import PluginWrapper, TimeoutError, IdempotencyError
from tools.plugins.test_plugins import (
    slow_plugin, failing_plugin, idempotent_plugin, partial_success_plugin
)


def test_plugin_timeout(tmp_path, monkeypatch):
    """Test that plugins timeout and rollback changes."""
    # Setup test environment
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    
    # Mock paths
    import tools.plugins.wrapper as wrapper_mod
    import tools.plugins.test_plugins as test_mod
    import tools.runner.io_utils as io_utils
    
    monkeypatch.setattr(wrapper_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(wrapper_mod, 'PLUGIN_STATE', tmp_path / "memory-bank" / ".plugin_state")
    monkeypatch.setattr(test_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(test_mod, 'MB', mb)
    monkeypatch.setattr(io_utils, 'ROOT', tmp_path)
    monkeypatch.setattr(io_utils, 'MB', mb)
    
    wrapper_mod.PLUGIN_STATE.mkdir(parents=True, exist_ok=True)
    
    # Create wrapper with short timeout
    wrapper = PluginWrapper("slow_plugin", timeout_seconds=2)
    
    # Run plugin that takes longer than timeout
    with pytest.raises(TimeoutError):
        wrapper.run(slow_plugin, duration=5)
    
    # Check that partial writes were rolled back
    test_dir = mb / "test"
    assert not (test_dir / "slow_complete.txt").exists()
    
    # Check state was recorded
    state = wrapper._load_state()
    assert len(state) == 1
    run = list(state.values())[0]
    assert run.status == "timeout"
    assert run.rollback_performed is True


def test_plugin_idempotency(tmp_path, monkeypatch):
    """Test that plugins with same key only run once."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    
    import tools.plugins.wrapper as wrapper_mod
    import tools.plugins.test_plugins as test_mod
    import tools.runner.io_utils as io_utils
    
    monkeypatch.setattr(wrapper_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(wrapper_mod, 'PLUGIN_STATE', tmp_path / "memory-bank" / ".plugin_state")
    monkeypatch.setattr(test_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(test_mod, 'MB', mb)
    monkeypatch.setattr(io_utils, 'ROOT', tmp_path)
    monkeypatch.setattr(io_utils, 'MB', mb)
    
    wrapper_mod.PLUGIN_STATE.mkdir(parents=True, exist_ok=True)
    
    wrapper = PluginWrapper("idempotent_plugin")
    
    # First run
    result1 = wrapper.run(idempotent_plugin, value=42)
    assert result1["count"] == 1
    
    # Second run with same arguments - should be skipped
    result2 = wrapper.run(idempotent_plugin, value=42)
    assert result2["status"] == "skipped"
    assert result2["reason"] == "idempotent"
    
    # Counter should still be 1
    counter_file = mb / "test" / "counter.json"
    data = json.loads(counter_file.read_text())
    assert data["count"] == 1
    
    # Different arguments should run
    result3 = wrapper.run(idempotent_plugin, value=99)
    assert result3["count"] == 2


def test_plugin_rollback_on_failure(tmp_path, monkeypatch):
    """Test that failed plugins rollback all side effects."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    
    import tools.plugins.wrapper as wrapper_mod
    import tools.runner.io_utils as io_utils
    
    monkeypatch.setattr(wrapper_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(wrapper_mod, 'PLUGIN_STATE', tmp_path / "memory-bank" / ".plugin_state")
    monkeypatch.setattr(io_utils, 'ROOT', tmp_path)
    monkeypatch.setattr(io_utils, 'MB', mb)
    
    wrapper_mod.PLUGIN_STATE.mkdir(parents=True, exist_ok=True)
    
    # Create a local failing plugin that uses the functions directly
    def local_failing_plugin():
        from tools.runner.io_utils import write_text, touch_json
        test_dir = mb / "test"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create some files
        write_text(test_dir / "file1.txt", "Content 1", role="test")
        touch_json(test_dir / "data1.json", {"value": 1}, role="test")
        write_text(test_dir / "file2.txt", "Content 2", role="test")
        
        # Simulate failure
        raise RuntimeError("Simulated plugin failure")
    
    wrapper = PluginWrapper("failing_plugin")
    
    # Run failing plugin
    with pytest.raises(RuntimeError, match="Simulated plugin failure"):
        wrapper.run(local_failing_plugin)
    
    # Check that all files were rolled back
    test_dir = mb / "test"
    assert not (test_dir / "file1.txt").exists()
    assert not (test_dir / "data1.json").exists()
    assert not (test_dir / "file2.txt").exists()
    
    # Check state
    state = wrapper._load_state()
    run = list(state.values())[0]
    assert run.status == "failed"
    assert run.rollback_performed is True
    assert "Simulated plugin failure" in run.error


def test_plugin_partial_rollback(tmp_path, monkeypatch):
    """Test rollback of partially completed plugin."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    
    import tools.plugins.wrapper as wrapper_mod
    import tools.runner.io_utils as io_utils
    
    monkeypatch.setattr(wrapper_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(wrapper_mod, 'PLUGIN_STATE', tmp_path / "memory-bank" / ".plugin_state")
    monkeypatch.setattr(io_utils, 'ROOT', tmp_path)
    monkeypatch.setattr(io_utils, 'MB', mb)
    
    wrapper_mod.PLUGIN_STATE.mkdir(parents=True, exist_ok=True)
    
    # Create local partial plugin
    def local_partial_plugin(steps: int = 3):
        from tools.runner.io_utils import write_text
        test_dir = mb / "test"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(steps):
            write_text(test_dir / f"step_{i}.txt", f"Step {i} completed", role="test")
            time.sleep(0.1)
            
            if i == 1:
                # Fail after second step
                raise RuntimeError(f"Failed at step {i+1}")
        
        return {"completed_steps": steps}
    
    wrapper = PluginWrapper("partial_plugin")
    
    # Run plugin that partially succeeds
    with pytest.raises(RuntimeError, match="Failed at step 2"):
        wrapper.run(local_partial_plugin, steps=3)
    
    # Check that all partial writes were rolled back
    test_dir = mb / "test"
    assert not (test_dir / "step_0.txt").exists()
    assert not (test_dir / "step_1.txt").exists()
    assert not (test_dir / "step_2.txt").exists()


def test_plugin_stale_lock_detection(tmp_path, monkeypatch):
    """Test detection and recovery from stale locks."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    
    import tools.plugins.wrapper as wrapper_mod
    import tools.plugins.test_plugins as test_mod
    
    monkeypatch.setattr(wrapper_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(wrapper_mod, 'PLUGIN_STATE', tmp_path / "memory-bank" / ".plugin_state")
    monkeypatch.setattr(test_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(test_mod, 'MB', mb)
    
    wrapper_mod.PLUGIN_STATE.mkdir(parents=True, exist_ok=True)
    
    wrapper = PluginWrapper("test_plugin", timeout_seconds=5)
    
    # Manually create a stale lock
    from tools.plugins.wrapper import PluginRun
    stale_run = PluginRun(
        plugin_id="test_plugin",
        idempotency_key="test_key",
        start_time=time.time() - 1000,  # Old timestamp
        end_time=None,
        status="running",
        side_effects=[],
        error=None
    )
    
    state = {"test_key": stale_run}
    wrapper._save_state(state)
    
    # Should detect stale lock and allow retry
    def dummy_func():
        return {"status": "ok"}
    
    result = wrapper.run(dummy_func, idempotency_key="test_key")
    assert result["status"] == "ok"
    
    # Check state was updated
    state = wrapper._load_state()
    # Should have two entries - stale one marked as timeout, new one as completed
    assert len(state) == 2
    assert any(r.status == "timeout" and "Stale lock" in (r.error or "") for r in state.values())
    assert any(r.status == "completed" for r in state.values())


def test_plugin_with_custom_idempotency_key(tmp_path, monkeypatch):
    """Test using custom idempotency keys."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    
    import tools.plugins.wrapper as wrapper_mod
    monkeypatch.setattr(wrapper_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(wrapper_mod, 'PLUGIN_STATE', tmp_path / "memory-bank" / ".plugin_state")
    
    wrapper_mod.PLUGIN_STATE.mkdir(parents=True, exist_ok=True)
    
    wrapper = PluginWrapper("test_plugin")
    
    def dummy_func(value):
        return {"value": value}
    
    # Run with custom key
    result1 = wrapper.run(dummy_func, 42, idempotency_key="custom_key_1")
    assert result1["value"] == 42
    
    # Same custom key - should skip
    result2 = wrapper.run(dummy_func, 99, idempotency_key="custom_key_1")
    assert result2["status"] == "skipped"
    
    # Different custom key - should run
    result3 = wrapper.run(dummy_func, 99, idempotency_key="custom_key_2")
    assert result3["value"] == 99