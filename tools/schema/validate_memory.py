#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Tuple

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas" / "memory"


def _detect_schema_for(path: Path) -> Path | None:
    """Map memory-bank files to schema files.

    Rules (initial minimal mapping):
    - memory-bank/business/client_score.json -> client_score.schema.json
    - memory-bank/business/estimate_brief.md -> estimate_brief.schema.json (markdown, len>0)
    - memory-bank/business/capacity_report.md -> capacity_report.schema.json (markdown, len>0)
    - memory-bank/plan/proposal.md -> proposal.schema.json (markdown, len>0)
    - *.json default -> generic_json.schema.json
    - *.md default -> generic_markdown.schema.json
    """
    rel = str(path).replace(str(ROOT) + "/", "")
    # Explicit mappings
    if rel.endswith("memory-bank/business/client_score.json"):
        return SCHEMAS / "client_score.schema.json"
    name = path.name
    if name.endswith(".json"):
        return SCHEMAS / "generic_json.schema.json"
    if name.endswith(".md"):
        return SCHEMAS / "generic_markdown.schema.json"
    return None


def validate_memory_artifact(path: Path, content: str) -> Tuple[bool, str | None]:
    """Validate memory content against schema based on file path.

    Returns (ok, error_message).
    """
    schema_path = _detect_schema_for(path)
    if not schema_path or not schema_path.exists():
        return True, None  # no schema -> allow
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        kind = schema.get("kind")
        if kind == "json":
            data = json.loads(content or "null")
            # minimal required fields
            required = schema.get("required", [])
            if isinstance(data, dict):
                missing = [k for k in required if k not in data]
                if missing:
                    return False, f"missing fields: {missing}"
            return True, None
        if kind == "markdown":
            min_len = int(schema.get("min_length", 1))
            if len(content.strip()) < min_len:
                return False, f"markdown too short (<{min_len})"
            return True, None
    except Exception as e:
        return False, f"schema/validation error: {e}"
    return True, None


if __name__ == "__main__":
    import sys
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not p:
        print("usage: validate_memory.py <path>")
        raise SystemExit(2)
    ok, err = validate_memory_artifact(p, p.read_text(encoding="utf-8") if p.exists() else "")
    print(json.dumps({"ok": ok, "error": err}))

