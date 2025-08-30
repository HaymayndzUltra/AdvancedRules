import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_trigger_help_mentions_safety_and_gates():
    out = subprocess.check_output([sys.executable, str(ROOT / "tools/orchestrator/trigger_next.py"), "--help"], cwd=str(ROOT)).decode()
    assert "Dry-run" in out and "Allowlist" in out and "Gates" in out


def test_aggregate_help_mentions_correlation():
    out = subprocess.check_output([sys.executable, str(ROOT / "tools/observability/aggregate.py"), "--help"], cwd=str(ROOT)).decode()
    assert "correlation" in out.lower()

