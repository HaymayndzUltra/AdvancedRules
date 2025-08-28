#!/usr/bin/env python3
import json
import time
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = REPO_ROOT / "workflow_state.json"


def _now() -> float:
    return time.time()


def load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text() or "{}")
        except Exception:
            return {}
    return {}


def save_state(data: Dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def transition(new_state: str) -> Dict[str, Any]:
    """Idempotent transition. Writes only when the state changes."""
    data = load_state()
    cur = data.get("state")
    ts = _now()
    if cur != new_state:
        data["prev_state"] = cur
        data["state"] = new_state
        data.setdefault("history", []).append({
            "ts": ts,
            "from": cur,
            "to": new_state
        })
        save_state(data)
    return {"prev": cur, "new": data.get("state"), "ts": ts}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="set_state", default="", help="set state")
    ap.add_argument("--resume", action="store_true", help="print current state")
    args = ap.parse_args()
    if args.set_state:
        out = transition(args.set_state)
        print(json.dumps(out, indent=2))
    elif args.resume:
        print(json.dumps(load_state(), indent=2))
    else:
        print(json.dumps({"usage": "--set <STATE> | --resume"}, indent=2))

