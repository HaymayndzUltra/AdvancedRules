#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[2]
MB = ROOT / "memory-bank"
EVENTS = ROOT / "logs/events.jsonl"

def ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

def append_event(evt: Dict[str, Any]) -> None:
    ensure_parent(EVENTS)
    content = (EVENTS.read_text() if EVENTS.exists() else "") + json.dumps(evt) + "\n"
    EVENTS.write_text(content, encoding="utf-8")

def write_text(path: Path, content: str, role: str | None = None) -> None:
    from tools.artifacts.hash_index import record as index_record  # local import to avoid cycles
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")
    append_event({"type":"artifact_emitted","role":role or "runner","path":str(path.relative_to(ROOT))})
    try:
        if str(path).startswith(str(MB)) and path.exists() and path.stat().st_size:
            index_record(path, role=role or "runner")
    except Exception:
        pass

def touch_json(path: Path, payload: Dict[str, Any], role: str | None = None) -> None:
    from tools.artifacts.hash_index import record as index_record
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    append_event({"type":"artifact_emitted","role":role or "runner","path":str(path.relative_to(ROOT))})
    try:
        if str(path).startswith(str(MB)) and path.exists() and path.stat().st_size:
            index_record(path, role=role or "runner")
    except Exception:
        pass

def write_md_with_frontmatter(path: Path, frontmatter: Dict[str, Any], body: str, role: str | None = None) -> None:
    fm = "---\n" + json.dumps(frontmatter, ensure_ascii=False) + "\n---\n"
    write_text(path, fm + body, role=role)

