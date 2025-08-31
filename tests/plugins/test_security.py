#!/usr/bin/env python3
from pathlib import Path


def test_security_plugin_reports(tmp_path, monkeypatch):
    import tools.plugins.security as sec
    import tools.runner.io_utils as io_utils
    monkeypatch.setattr(sec, 'ROOT', tmp_path)
    monkeypatch.setattr(sec, 'MB', tmp_path / 'memory-bank' / 'security')
    monkeypatch.setattr(io_utils, 'ROOT', tmp_path)
    monkeypatch.setattr(io_utils, 'MB', tmp_path / 'memory-bank')

    res = sec.run({"mode": "SAST"})
    assert res["status"] == "ok"
    assert (tmp_path / 'memory-bank' / 'security' / 'sast_summary.json').exists()
    assert (tmp_path / 'memory-bank' / 'security' / 'license_audit.json').exists()
    assert (tmp_path / 'memory-bank' / 'security' / 'redaction_policy_check.json').exists()

