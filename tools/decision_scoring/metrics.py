#!/usr/bin/env python3
import json
import time
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[2]
METRICS = ROOT / "logs/decision_metrics.json"

def load() -> Dict[str, Any]:
    if METRICS.exists():
        try:
            return json.loads(METRICS.read_text() or "{}")
        except Exception:
            return {}
    return {}

def save(data: Dict[str, Any]) -> None:
    METRICS.parent.mkdir(parents=True, exist_ok=True)
    METRICS.write_text(json.dumps(data, indent=2), encoding="utf-8")

def record(event_type: str, payload: Dict[str, Any]) -> None:
    data = load()
    bucket = time.strftime("%Y-%m-%d")
    day = data.setdefault(bucket, {"counts":{}, "events": []})
    cnt = day["counts"].get(event_type, 0)
    day["counts"][event_type] = cnt + 1
    payload = dict(payload)
    payload["ts"] = time.time()
    day["events"].append({"type": event_type, **payload})
    save(data)

if __name__ == "__main__":
    record("decision", {"decision":"NEXT_STEP", "top":0.82})
    print(METRICS)

