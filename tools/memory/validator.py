#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]

SCHEMAS = {
    "memory-bank/plan/acceptance_criteria.json": ROOT / "schemas/memory/acceptance_criteria.schema.json",
}


def validate_memory_file(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    schema_path = SCHEMAS.get(rel)
    if not schema_path or not schema_path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8") or "{}")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(data))
    if errors:
        msgs = [f"/{'/'.join(map(str,e.path))}: {e.message}" for e in errors]
        raise ValueError(f"Memory file validation failed: {rel}\n" + "\n".join(msgs))


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: validator.py <memory-file>")
        raise SystemExit(2)
    p = Path(sys.argv[1])
    validate_memory_file(p)
    print("OK")

