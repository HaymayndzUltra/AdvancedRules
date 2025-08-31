#!/usr/bin/env python3
from pathlib import Path


def test_codegen_plugin_writes_artifacts(tmp_path, monkeypatch):
    import tools.plugins.codegen as codegen
    import tools.runner.io_utils as io_utils
    monkeypatch.setattr(codegen, 'ROOT', tmp_path)
    monkeypatch.setattr(codegen, 'MB', tmp_path / 'memory-bank' / 'codegen')
    monkeypatch.setattr(io_utils, 'ROOT', tmp_path)
    monkeypatch.setattr(io_utils, 'MB', tmp_path / 'memory-bank')

    res = codegen.run({"mode": "SCAFFOLD", "items": ["README.md"]})
    assert res["status"] == "ok"
    mf = tmp_path / 'memory-bank' / 'codegen' / 'scaffold_manifest.json'
    notes = tmp_path / 'memory-bank' / 'codegen' / 'scaffold_notes.md'
    assert mf.exists() and notes.exists()

