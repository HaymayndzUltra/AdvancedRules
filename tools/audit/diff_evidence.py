#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def collect_paths(plan_md: Path):
    txt = plan_md.read_text(encoding="utf-8")
    # naive path extraction: code-style or markdown links
    paths = set()
    for m in re.finditer(r"(?:`|\()([^`\)\s]+\.(?:py|md|json|yaml|yml|toml))", txt):
        paths.add(m.group(1))
    return sorted(paths)

def cite_existing(paths):
    cites = []
    for rel in paths:
        p = ROOT / rel
        if p.exists():
            cites.append({"path": rel, "exists": True, "size": p.stat().st_size})
        else:
            cites.append({"path": rel, "exists": False})
    return cites

if __name__ == "__main__":
    plan = ROOT / "memory-bank/plan/Action_Plan.md"
    if not plan.exists():
        print(json.dumps({"error":"missing Action_Plan.md"}))
    else:
        paths = collect_paths(plan)
        print(json.dumps({"cites": cite_existing(paths)}, indent=2))

