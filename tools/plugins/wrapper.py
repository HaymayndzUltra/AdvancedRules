#!/usr/bin/env python3
"""Plugin wrapper with timeouts, idempotency, and atomic side-effects."""
from __future__ import annotations
import json
import signal
import time
import hashlib
import tempfile
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, asdict

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_STATE = ROOT / "memory-bank" / ".plugin_state"
PLUGIN_STATE.mkdir(parents=True, exist_ok=True)


@dataclass
class PluginRun:
    """Record of a plugin execution."""
    plugin_id: str
    idempotency_key: str
    start_time: float
    end_time: Optional[float]
    status: str  # "running", "completed", "failed", "timeout"
    side_effects: List[str]  # Paths of files created/modified
    error: Optional[str]
    rollback_performed: bool = False


class TimeoutError(Exception):
    """Raised when plugin execution times out."""
    pass


class IdempotencyError(Exception):
    """Raised when attempting duplicate execution with same idempotency key."""
    pass


def _timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutError("Plugin execution timed out")


@contextmanager
def timeout(seconds: int):
    """Context manager for setting execution timeout."""
    if seconds <= 0:
        yield
        return
    
    # Set up signal alarm
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)  # Cancel alarm
        signal.signal(signal.SIGALRM, old_handler)


class PluginWrapper:
    """Wrapper for plugin execution with safety guarantees."""
    
    def __init__(self, plugin_id: str, timeout_seconds: int = 300):
        self.plugin_id = plugin_id
        self.timeout_seconds = timeout_seconds
        self.state_file = PLUGIN_STATE / f"{plugin_id}.json"
        self.temp_dir = None
        self.tracked_files: Set[Path] = set()
        self.original_files: Dict[Path, bytes] = {}
        
    def _load_state(self) -> Dict[str, PluginRun]:
        """Load plugin execution history."""
        if not self.state_file.exists():
            return {}
        try:
            data = json.loads(self.state_file.read_text())
            return {k: PluginRun(**v) for k, v in data.items()}
        except Exception:
            return {}
    
    def _save_state(self, state: Dict[str, PluginRun]) -> None:
        """Save plugin execution history."""
        data = {k: asdict(v) for k, v in state.items()}
        self.state_file.write_text(json.dumps(data, indent=2))
    
    def _generate_idempotency_key(self, *args, **kwargs) -> str:
        """Generate idempotency key from plugin ID and arguments."""
        data = f"{self.plugin_id}:{repr(args)}:{repr(sorted(kwargs.items()))}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _check_idempotency(self, key: str) -> Optional[PluginRun]:
        """Check if this execution was already performed."""
        state = self._load_state()
        if key in state:
            run = state[key]
            if run.status == "completed":
                return run
            elif run.status == "running":
                # Check if still actually running (stale lock detection)
                if time.time() - run.start_time > self.timeout_seconds * 2:
                    # Stale run, mark as timeout but keep in state
                    run.status = "timeout"
                    run.error = "Stale lock detected"
                    run.end_time = time.time()
                    # Use a new key for the stale entry
                    stale_key = f"{key}_stale_{int(run.start_time)}"
                    state[stale_key] = run
                    del state[key]  # Remove from original key
                    self._save_state(state)
                    return None
                else:
                    raise IdempotencyError(f"Plugin {self.plugin_id} already running with key {key}")
        return None
    
    def _track_file(self, path: Path) -> None:
        """Track a file for potential rollback."""
        if path not in self.tracked_files:
            self.tracked_files.add(path)
            if path.exists():
                # Save original content for rollback
                self.original_files[path] = path.read_bytes()
    
    def _rollback_files(self) -> None:
        """Rollback all tracked file changes."""
        for path in self.tracked_files:
            if path in self.original_files:
                # Restore original content
                path.write_bytes(self.original_files[path])
            else:
                # File was created, remove it
                if path.exists():
                    path.unlink()
    
    def _atomic_write(self, path: Path, content: str | bytes) -> None:
        """Atomically write to a file with tracking."""
        from tools.io.fs import atomic_write_text
        
        self._track_file(path)
        
        if isinstance(content, str):
            atomic_write_text(path, content)
        else:
            # Binary write
            temp = Path(str(path) + ".tmp")
            temp.write_bytes(content)
            temp.replace(path)
    
    def run(self, func: Callable, *args, **kwargs) -> Any:
        """Execute plugin with safety guarantees."""
        # Generate idempotency key
        idempotency_key = kwargs.pop('idempotency_key', None)
        if not idempotency_key:
            idempotency_key = self._generate_idempotency_key(*args, **kwargs)
        
        # Check idempotency
        existing_run = self._check_idempotency(idempotency_key)
        if existing_run:
            print(f"Plugin {self.plugin_id} already completed with key {idempotency_key}")
            return {"status": "skipped", "reason": "idempotent", "run": asdict(existing_run)}
        
        # Create run record
        run = PluginRun(
            plugin_id=self.plugin_id,
            idempotency_key=idempotency_key,
            start_time=time.time(),
            end_time=None,
            status="running",
            side_effects=[],
            error=None
        )
        
        # Save initial state
        state = self._load_state()
        state[idempotency_key] = run
        self._save_state(state)
        
        # Create temp directory for atomic operations
        self.temp_dir = Path(tempfile.mkdtemp(prefix=f"plugin_{self.plugin_id}_"))
        
        # Store original functions
        import tools.runner.io_utils as io_utils
        original_write_text = io_utils.write_text
        original_touch_json = io_utils.touch_json
        
        try:
            # Monkey-patch write functions to track side effects
            wrapper_self = self  # Capture self for closure
            run_ref = run  # Capture run for closure
            
            def tracked_write_text(path: Path, content: str, role: str | None = None):
                wrapper_self._track_file(path)
                run_ref.side_effects.append(str(path))
                return original_write_text(path, content, role)
            
            def tracked_touch_json(path: Path, payload: Dict[str, Any], role: str | None = None):
                wrapper_self._track_file(path)
                run_ref.side_effects.append(str(path))
                return original_touch_json(path, payload, role)
            
            # Patch the module
            io_utils.write_text = tracked_write_text
            io_utils.touch_json = tracked_touch_json
            
            # Also patch in sys.modules to affect already-imported references
            import sys
            if 'tools.runner.io_utils' in sys.modules:
                sys.modules['tools.runner.io_utils'].write_text = tracked_write_text
                sys.modules['tools.runner.io_utils'].touch_json = tracked_touch_json
            
            # Execute with timeout
            with timeout(self.timeout_seconds):
                result = func(*args, **kwargs)
            
            # Success - mark as completed
            run.status = "completed"
            run.end_time = time.time()
            
            # Save final state
            state[idempotency_key] = run
            self._save_state(state)
            
            return result
            
        except TimeoutError as e:
            # Timeout - rollback and mark as failed
            run.status = "timeout"
            run.end_time = time.time()
            run.error = str(e)
            
            # Rollback side effects
            self._rollback_files()
            run.rollback_performed = True
            
            # Save state
            state[idempotency_key] = run
            self._save_state(state)
            
            raise
            
        except Exception as e:
            # Other error - rollback and mark as failed
            run.status = "failed"
            run.end_time = time.time()
            run.error = str(e)
            
            # Rollback side effects
            self._rollback_files()
            run.rollback_performed = True
            
            # Save state
            state[idempotency_key] = run
            self._save_state(state)
            
            raise
            
        finally:
            # Restore original functions
            if original_write_text:
                io_utils.write_text = original_write_text
            if original_touch_json:
                io_utils.touch_json = original_touch_json
            
            # Clean up temp directory
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)


def run_plugin_safe(plugin_id: str, func: Callable, *args, 
                    timeout_seconds: int = 300, **kwargs) -> Any:
    """Convenience function to run a plugin with safety guarantees."""
    wrapper = PluginWrapper(plugin_id, timeout_seconds)
    return wrapper.run(func, *args, **kwargs)