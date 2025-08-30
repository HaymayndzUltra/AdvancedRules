import json
import os
from pathlib import Path

from tools.runner.io_utils import touch_json


def test_memory_validation_rejects_bad_acceptance_criteria(tmp_path, monkeypatch):
    # Create invalid acceptance_criteria (missing required keys)
    target = Path("memory-bank/plan/acceptance_criteria.json")
    full = tmp_path / target
    full.parent.mkdir(parents=True, exist_ok=True)
    # Write invalid first, then attempt to validate via touch_json (should rewrite valid JSON)
    full.write_text("{}", encoding="utf-8")
    # Now attempt to write via IO utils; invalid schema should raise
    try:
        touch_json(full, {"wrong": []}, role="tests")
    except Exception:
        # Ensure file is still a valid JSON (atomic write protects from partials)
        json.loads(full.read_text())
    else:
        # If no error, ensure validator allows shape only when correct
        data = json.loads(full.read_text())
        assert "items" in data

