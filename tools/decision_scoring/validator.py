#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/candidates.schema.json"


def validate_candidates_payload(payload: Dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))
    if errors:
        msgs = [f"/{'/'.join(map(str, e.path))}: {e.message}" for e in errors]
        raise ValueError("Candidates payload failed validation:\n" + "\n".join(msgs))


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: validator.py <candidates.json|yaml>")
        raise SystemExit(2)
    p = Path(sys.argv[1])
    if not p.exists():
        raise SystemExit(f"Missing: {p}")
    if p.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    else:
        data = json.loads(p.read_text(encoding="utf-8"))
    validate_candidates_payload(data)
    print("OK: candidates payload is valid")

