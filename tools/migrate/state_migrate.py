#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "workflow_state.json"
REPORT = ROOT / "migration_report.json"

CURRENT_VERSION = "1.0"


def migrate_state(data: Dict[str, Any]) -> Dict[str, Any]:
    changed = False
    if "schema_version" not in data:
        data["schema_version"] = CURRENT_VERSION
        changed = True
    # Future migrations can be handled based on version
    return data, changed


def main() -> int:
    report = {"state": {"changed": False, "message": ""}}
    if STATE.exists():
        try:
            data = json.loads(STATE.read_text() or "{}")
            new_data, changed = migrate_state(data)
            if changed:
                STATE.write_text(json.dumps(new_data, indent=2), encoding="utf-8")
                report["state"]["changed"] = True
                report["state"]["message"] = "schema_version set"
            else:
                report["state"]["message"] = "no change"
        except Exception as e:
            report["state"]["message"] = f"error: {e}"
    else:
        report["state"]["message"] = "missing"
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

