#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
import uuid

ROOT = Path(__file__).resolve().parents[2]
MB = ROOT / "memory-bank"
EVENTS = ROOT / "logs/events.jsonl"
TRACES = ROOT / "logs/decision_traces.jsonl"

def ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

def append_event(evt: Dict[str, Any]) -> None:
    from tools.io.fs import append_line_atomic
    ensure_parent(EVENTS)
    if "correlation_id" not in evt:
        evt["correlation_id"] = str(uuid.uuid4())
    append_line_atomic(EVENTS, json.dumps(evt))


def append_decision_trace(trace: Dict[str, Any]) -> None:
    from tools.io.fs import append_line_atomic
    ensure_parent(TRACES)
    if "correlation_id" not in trace:
        trace["correlation_id"] = str(uuid.uuid4())
    append_line_atomic(TRACES, json.dumps(trace))

def write_text(path: Path, content: str, role: str | None = None) -> None:
    from tools.artifacts.hash_index import record as index_record  # local import to avoid cycles
    from tools.io.fs import atomic_write_text
    ensure_parent(path)
    atomic_write_text(path, content)
    append_event({"type":"artifact_emitted","role":role or "runner","path":str(path.relative_to(ROOT))})
    try:
        if str(path).startswith(str(MB)) and path.exists() and path.stat().st_size:
            index_record(path, role=role or "runner")
    except Exception:
        pass

def touch_json(path: Path, payload: Dict[str, Any], role: str | None = None) -> None:
    from tools.artifacts.hash_index import record as index_record
    from tools.io.fs import atomic_write_text
    ensure_parent(path)
    atomic_write_text(path, json.dumps(payload, indent=2))
    append_event({"type":"artifact_emitted","role":role or "runner","path":str(path.relative_to(ROOT))})
    try:
        if str(path).startswith(str(MB)) and path.exists() and path.stat().st_size:
            index_record(path, role=role or "runner")
    except Exception:
        pass

def write_md_with_frontmatter(path: Path, frontmatter: Dict[str, Any], body: str, role: str | None = None) -> None:
    fm = "---\n" + json.dumps(frontmatter, ensure_ascii=False) + "\n---\n"
    write_text(path, fm + body, role=role)

