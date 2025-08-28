#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]

def load_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text() or "{}")

def validate_json(instance: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    # Minimal structural validation (no external lib): check required keys
    req = schema.get("required", [])
    for k in req:
        if k not in instance:
            print(f"Missing required key: {k}")
            return False
    return True

def parse_frontmatter(md_path: Path) -> Dict[str, Any]:
    txt = md_path.read_text(encoding="utf-8")
    parts = re.split(r"^---\s*$", txt, flags=re.M)
    if len(parts) >= 3:
        fm = parts[1]
        try:
            return json.loads(fm)
        except Exception:
            pass
    return {}

if __name__ == "__main__":
    # Validate acceptance criteria JSON
    ac = ROOT / "memory-bank/plan/acceptance_criteria.json"
    ac_schema = ROOT / "schema/acceptance_criteria.schema.json"
    if ac.exists():
        ok = validate_json(load_json(ac), load_json(ac_schema))
        print("acceptance_criteria:", "OK" if ok else "FAIL")

    # Frontmatter validations (only checks for presence of frontmatter if any)
    for name, schema_file in [
        ("Validation_Report.md", ROOT / "schema/validation_report.frontmatter.schema.json"),
        ("Final_Implementation_Plan.md", ROOT / "schema/final_implementation_plan.frontmatter.schema.json"),
    ]:
        p = ROOT / f"memory-bank/plan/{name}"
        if p.exists():
            fm = parse_frontmatter(p)
            if fm:
                ok = validate_json(fm, load_json(schema_file))
                print(f"{name} frontmatter:", "OK" if ok else "FAIL")
            else:
                print(f"{name} frontmatter: MISSING or not JSON")

