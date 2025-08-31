#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[2]
MB = ROOT / "memory-bank" / "codegen"


def run(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Codegen plugin: produce scaffold manifest and boilerplate notes.

    Writes artifacts under memory-bank/codegen using shared IO wrappers
    (append event, hashing, correlation) via tools.runner.io_utils.
    """
    from tools.runner.io_utils import write_text, touch_json

    payload = payload or {}
    mode = str(payload.get("mode", "SCAFFOLD")).upper()

    MB.mkdir(parents=True, exist_ok=True)
    manifest_path = MB / "scaffold_manifest.json"
    notes_path = MB / "scaffold_notes.md"

    manifest = {
        "schema_version": "1.0.0",
        "mode": mode,
        "items": payload.get("items", []),
    }
    touch_json(manifest_path, manifest, role="codegen")

    notes = """# Codegen Scaffold

This file documents the scaffold/boilerplate generation.

- Mode: {mode}
- Items: {items}
""".format(mode=mode, items=json.dumps(manifest.get("items", [])))
    write_text(notes_path, notes, role="codegen")

    return {"status": "ok", "mode": mode, "artifacts": [
        str(manifest_path.relative_to(ROOT)),
        str(notes_path.relative_to(ROOT)),
    ]}

