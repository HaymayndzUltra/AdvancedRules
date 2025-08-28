#!/usr/bin/env python3
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MB = REPO_ROOT / "memory-bank"

def exists_nonempty(p: Path) -> bool:
    return p.exists() and p.stat().st_size > 0

def main() -> None:
    # Ensure offer_status.json exists with sane defaults
    offer = MB / "upwork/offer_status.json"
    if not exists_nonempty(offer):
        offer.parent.mkdir(parents=True, exist_ok=True)
        offer.write_text(json.dumps({
            "contract_type": "fixed",
            "escrow_funded": True,
            "work_diary_ready": True,
            "weekly_cap_hours": 10
        }, indent=2), encoding="utf-8")
        print("created:", offer)
    else:
        print("ok:", offer)

if __name__ == "__main__":
    main()

