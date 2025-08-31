#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[2]
MB = ROOT / "memory-bank" / "deploy"


def run(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Deploy/Handover plugin: package artifacts, run postrun scanner, write bundle manifest."""
    from tools.runner.io_utils import touch_json, write_text
    from tools.postrun.scanner import scan_postrun_consistency, save_report
    from tools.postrun.scanner import POSTRUN_REPORT

    payload = payload or {}
    mode = str(payload.get("mode", "PACKAGE")).upper()

    MB.mkdir(parents=True, exist_ok=True)
    bundle_manifest = MB / "handover_bundle.json"
    postrun_report = ROOT / "memory-bank" / "postrun_consistency.json"

    # Run postrun scanner to ensure consistency
    report = scan_postrun_consistency()
    save_report(report, postrun_report)

    touch_json(bundle_manifest, {
        "schema_version": "1.0.0",
        "mode": mode,
        "postrun_report": str(postrun_report.relative_to(ROOT)),
        "artifacts": [],
        "status": "ready" if report.passed else "needs_attention",
    }, role="deploy")

    # Minimal README for bundle consumers
    readme = MB / "README.md"
    write_text(readme, """# Handover Bundle\n\nContains packaged artifacts and postrun consistency report.\n""", role="deploy")

    return {"status": "ok", "mode": mode, "artifacts": [
        str(bundle_manifest.relative_to(ROOT)),
        str(readme.relative_to(ROOT)),
        str(postrun_report.relative_to(ROOT)),
    ]}

