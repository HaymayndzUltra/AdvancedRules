#!/usr/bin/env python3
from pathlib import Path


def test_qa_plugin_reports(tmp_path, monkeypatch):
    import tools.plugins.qa as qa
    import tools.runner.io_utils as io_utils
    monkeypatch.setattr(qa, 'ROOT', tmp_path)
    monkeypatch.setattr(qa, 'MB', tmp_path / 'memory-bank' / 'qa')
    monkeypatch.setattr(io_utils, 'ROOT', tmp_path)
    monkeypatch.setattr(io_utils, 'MB', tmp_path / 'memory-bank')

    res = qa.run({"mode": "VALIDATE"})
    assert res["status"] == "ok"
    assert (tmp_path / 'memory-bank' / 'qa' / 'lint_report.json').exists()
    assert (tmp_path / 'memory-bank' / 'qa' / 'test_report.json').exists()
    assert (tmp_path / 'memory-bank' / 'qa' / 'coverage_summary.json').exists()

