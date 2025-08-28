#!/usr/bin/env python3
import hashlib
import json
import time
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "memory-bank/artifacts_index.json"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def record(path: Path, role: str) -> Dict:
    entry = {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
        "created_at": time.time(),
        "source_role": role,
    }
    idx = []
    if INDEX.exists():
        try:
            idx = json.loads(INDEX.read_text() or "[]")
        except Exception:
            idx = []
    idx.append(entry)
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(idx, indent=2), encoding="utf-8")
    return entry

if __name__ == "__main__":
    p = ROOT / "memory-bank/plan/Final_Implementation_Plan.md"
    if p.exists() and p.stat().st_size:
        rec = record(p, "principal_engineer_ai")
        print(json.dumps(rec, indent=2))

