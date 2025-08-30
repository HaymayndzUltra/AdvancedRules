#!/usr/bin/env python3
import json
import time
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = REPO_ROOT / "workflow_state.json"

from tools.io.fs import atomic_write_json
from jsonschema import Draft202012Validator

SCHEMA = json.loads((REPO_ROOT / "schemas/workflow_state.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)
CURRENT_SCHEMA_VERSION = "1.0"


def _now() -> float:
    return time.time()


def _validate(data: Dict[str, Any]) -> None:
    errors = list(VALIDATOR.iter_errors(data))
    if errors:
        msgs = [f"/{'/'.join(map(str,e.path))}: {e.message}" for e in errors]
        raise ValueError("workflow_state.json failed validation:\n" + "\n".join(msgs))


def load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text() or "{}")
            # If missing schema_version, set for compatibility and validate
            if "schema_version" not in data:
                data["schema_version"] = CURRENT_SCHEMA_VERSION
            _validate(data)
            return data
        except Exception:
            return {}
    return {}


def save_state(data: Dict[str, Any]) -> None:
    data.setdefault("schema_version", CURRENT_SCHEMA_VERSION)
    _validate(data)
    atomic_write_json(STATE_FILE, data)


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

