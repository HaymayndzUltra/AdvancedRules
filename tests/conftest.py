"""Test configuration and fixtures for AdvancedRules tests"""
import os
import sys
import pytest
import shutil
import subprocess
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def arx_available():
    """Check if arx CLI is available"""
    try:
        # Check if arx is installed and callable
        result = subprocess.run(
            ["python3", "-m", "cli.main", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# Pytest marker for tests that require arx
requires_arx = pytest.mark.skipif(
    not arx_available(),
    reason="arx CLI not available - install package with 'pip install -e .'"
)


@pytest.fixture
def arx_command():
    """Fixture that provides the arx command as a list"""
    # Try to use the installed arx command first
    if shutil.which("arx"):
        return ["arx"]
    # Fallback to Python module invocation
    return ["python3", "-m", "cli.main"]


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace for tests"""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    
    # Create basic structure
    (workspace / "memory-bank").mkdir()
    (workspace / "logs").mkdir()
    (workspace / "config").mkdir()
    
    # Create a minimal config file
    config_file = workspace / "config" / "advanced_rules.yaml"
    config_file.write_text("""
rag:
  enabled: false
  embedding_model: BAAI/bge-m3
  persist_dir: ./memory-bank/chromadb
  
personas:
  CODER_AI:
    namespaces: [coder]
  DOCS_AI:
    namespaces: [docs]
""")
    
    return workspace


@pytest.fixture
def mock_arx_env(monkeypatch):
    """Set up environment variables for testing"""
    monkeypatch.setenv("AR_ENABLE_RAG", "1")
    monkeypatch.setenv("AR_EMBED_MODEL", "BAAI/bge-m3")
    return monkeypatch


# Provide a stub implementation for arx if needed
class ArxStub:
    """Stub implementation of arx CLI for testing when real CLI is not available"""
    
    @staticmethod
    def run(args, **kwargs):
        """Stub run method that simulates arx CLI responses"""
        cmd = args[1] if len(args) > 1 else ""
        subcmd = args[2] if len(args) > 2 else ""
        
        if cmd == "memory":
            if subcmd == "stats":
                return subprocess.CompletedProcess(
                    args, 0, 
                    stdout="RAG disabled. Set AR_ENABLE_RAG=1 to enable.\n",
                    stderr=""
                )
            elif subcmd == "query":
                return subprocess.CompletedProcess(
                    args, 0,
                    stdout="No results found.\n",
                    stderr=""
                )
            elif subcmd == "index":
                return subprocess.CompletedProcess(
                    args, 0,
                    stdout="Indexing complete.\n",
                    stderr=""
                )
        
        return subprocess.CompletedProcess(
            args, 0,
            stdout="arx stub response\n",
            stderr=""
        )


@pytest.fixture
def arx_stub(monkeypatch):
    """Monkey-patch subprocess.run to use ArxStub for arx commands"""
    original_run = subprocess.run
    original_check_call = subprocess.check_call
    
    def mock_run(args, **kwargs):
        if args and args[0] == "arx":
            return ArxStub.run(args, **kwargs)
        return original_run(args, **kwargs)
    
    def mock_check_call(args, **kwargs):
        if args and args[0] == "arx":
            result = ArxStub.run(args, **kwargs)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, args)
            return result.returncode
        return original_check_call(args, **kwargs)
    
    monkeypatch.setattr(subprocess, "run", mock_run)
    monkeypatch.setattr(subprocess, "check_call", mock_check_call)
    
    return ArxStub