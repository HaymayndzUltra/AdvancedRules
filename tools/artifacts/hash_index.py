#!/usr/bin/env python3
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "memory-bank/artifacts_index.json"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def get_current_correlation_id() -> Optional[str]:
    """Get correlation ID from environment or generate one."""
    return os.environ.get('CORRELATION_ID')

def record(path: Path, role: str, correlation_id: Optional[str] = None) -> Dict:
    """Record artifact with hash and optional correlation ID."""
    if not correlation_id:
        correlation_id = get_current_correlation_id()
    
    entry = {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
        "created_at": time.time(),
        "source_role": role,
        "correlation_id": correlation_id,
    }
    
    # Use atomic write for index
    from tools.io.fs import atomic_write_text, read_text
    
    idx = []
    if INDEX.exists():
        try:
            content = read_text(INDEX)
            idx = json.loads(content or "[]")
        except Exception:
            idx = []
    
    idx.append(entry)
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(INDEX, json.dumps(idx, indent=2))
    return entry

if __name__ == "__main__":
    p = ROOT / "memory-bank/plan/Final_Implementation_Plan.md"
    if p.exists() and p.stat().st_size:
        rec = record(p, "principal_engineer_ai")
        print(json.dumps(rec, indent=2))

