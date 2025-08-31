#!/usr/bin/env python3
"""Test plugins for demonstrating timeout, idempotency, and rollback."""
import time
from pathlib import Path
from tools.runner.io_utils import write_text, touch_json

ROOT = Path(__file__).resolve().parents[2]
MB = ROOT / "memory-bank"


def slow_plugin(duration: int = 10):
    """Plugin that takes a long time to run."""
    test_dir = MB / "test"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Write initial file
    write_text(test_dir / "slow_start.txt", f"Started at {time.time()}", role="test")
    
    # Simulate long-running work
    time.sleep(duration)
    
    # Write completion file (won't happen if timeout)
    write_text(test_dir / "slow_complete.txt", f"Completed at {time.time()}", role="test")
    
    return {"status": "completed", "duration": duration}


def failing_plugin():
    """Plugin that creates files then fails."""
    test_dir = MB / "test"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create some files
    write_text(test_dir / "file1.txt", "Content 1", role="test")
    touch_json(test_dir / "data1.json", {"value": 1}, role="test")
    write_text(test_dir / "file2.txt", "Content 2", role="test")
    
    # Simulate failure
    raise RuntimeError("Simulated plugin failure")


def idempotent_plugin(value: int = 42):
    """Plugin that should only run once per value."""
    test_dir = MB / "test"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Read counter file
    counter_file = test_dir / "counter.json"
    if counter_file.exists():
        import json
        data = json.loads(counter_file.read_text())
        count = data.get("count", 0) + 1
    else:
        count = 1
    
    # Write updated counter
    touch_json(counter_file, {"count": count, "value": value}, role="test")
    
    # Write result file
    write_text(test_dir / f"result_{value}.txt", f"Execution {count} with value {value}", role="test")
    
    return {"count": count, "value": value}


def partial_success_plugin(steps: int = 3):
    """Plugin that partially succeeds before failing."""
    test_dir = MB / "test"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(steps):
        write_text(test_dir / f"step_{i}.txt", f"Step {i} completed", role="test")
        time.sleep(0.5)
        
        if i == 1:
            # Fail after second step
            raise RuntimeError(f"Failed at step {i+1}")
    
    return {"completed_steps": steps}