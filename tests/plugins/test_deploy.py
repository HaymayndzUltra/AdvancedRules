#!/usr/bin/env python3
from pathlib import Path


def test_deploy_plugin_bundle(tmp_path, monkeypatch):
    import tools.plugins.deploy as dep
    import tools.runner.io_utils as io_utils
    import tools.postrun.scanner as scanner
    monkeypatch.setattr(dep, 'ROOT', tmp_path)
    monkeypatch.setattr(dep, 'MB', tmp_path / 'memory-bank' / 'deploy')
    monkeypatch.setattr(io_utils, 'ROOT', tmp_path)
    monkeypatch.setattr(io_utils, 'MB', tmp_path / 'memory-bank')
    monkeypatch.setattr(scanner, 'ROOT', tmp_path)

    res = dep.run({"mode": "PACKAGE"})
    assert res["status"] == "ok"
    assert (tmp_path / 'memory-bank' / 'deploy' / 'handover_bundle.json').exists()
    assert (tmp_path / 'memory-bank' / 'postrun_consistency.json').exists()

