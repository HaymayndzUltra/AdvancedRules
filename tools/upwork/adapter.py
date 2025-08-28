#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

_FILE = Path(__file__).resolve()
# /workspace/AdvancedRules/tools/upwork/adapter.py → parents[2] == repo root
REPO_ROOT = _FILE.parents[2]
MB = REPO_ROOT / "memory-bank"

def write_offer(contract_type: str, escrow_funded: bool, work_diary_ready: bool, weekly_cap_hours: int) -> Path:
    payload = {
        "contract_type": contract_type.lower(),
        "escrow_funded": bool(escrow_funded),
        "work_diary_ready": bool(work_diary_ready),
        "weekly_cap_hours": int(weekly_cap_hours),
    }
    out = MB / "upwork/offer_status.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--contract", default="fixed", choices=["fixed","hourly"]) 
    p.add_argument("--escrow", default="true")
    p.add_argument("--diary", default="true")
    p.add_argument("--cap", default="10")
    a = p.parse_args()
    out = write_offer(
        a.contract,
        a.escrow.lower() in {"1","true","yes","y"},
        a.diary.lower() in {"1","true","yes","y"},
        int(a.cap)
    )
    print(out)

