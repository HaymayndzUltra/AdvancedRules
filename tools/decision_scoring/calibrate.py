#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONF = ROOT / "tools/decision_scoring"
METRICS = ROOT / "logs/decision_metrics.json"


def load_json(p: Path, default):
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text() or json.dumps(default))
    except Exception:
        return default


def save_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main():
    # Load configs
    weights = load_json(CONF / "weights.json", {})
    thresholds = load_json(CONF / "thresholds.json", {"conf_high": 0.75, "conf_mid": 0.55, "eps_gap": 0.05})
    calib = load_json(CONF / "calibration.json", {"alpha": 1.0, "beta": 0.0})

    # Load metrics
    data = load_json(METRICS, {})
    # Aggregate last day (if any)
    if not data:
        print("No metrics to calibrate; keeping configs as-is")
        return
    last_day = sorted(data.keys())[-1]
    counts = data[last_day].get("counts", {})

    # Heuristics: if OPTION_SET dominates, lower conf_mid slightly; if ASK_CLARIFY dominates, reduce alpha to compress scores
    total_decisions = sum(counts.get(k, 0) for k in ["decision"])
    # Fallback to counts by decision types in events if present
    events = data[last_day].get("events", [])
    type_counts = {"NEXT_STEP": 0, "OPTION_SET": 0, "ASK_CLARIFY": 0, "RISK_ALERT": 0}
    for e in events:
        if e.get("type") == "decision":
            dt = e.get("decision") or e.get("payload", {}).get("decision")
            if isinstance(dt, str) and dt in type_counts:
                type_counts[dt] += 1

    total = sum(type_counts.values()) or 1
    opt_ratio = type_counts["OPTION_SET"] / total
    ask_ratio = type_counts["ASK_CLARIFY"] / total

    new_thresholds = dict(thresholds)
    new_calib = dict(calib)

    # Adjust conf_mid gently
    if opt_ratio > 0.6:
        new_thresholds["conf_mid"] = max(0.50, thresholds["conf_mid"] - 0.02)
    elif opt_ratio < 0.2 and type_counts["NEXT_STEP"] > 0:
        new_thresholds["conf_mid"] = min(0.60, thresholds["conf_mid"] + 0.02)

    # Adjust alpha if too many ASK_CLARIFY
    if ask_ratio > 0.5:
        new_calib["alpha"] = max(0.8, calib["alpha"] - 0.05)
    elif ask_ratio < 0.2:
        new_calib["alpha"] = min(1.5, calib["alpha"] + 0.05)

    save_json(CONF / "thresholds.json", new_thresholds)
    save_json(CONF / "calibration.json", new_calib)
    print(json.dumps({"updated_thresholds": new_thresholds, "updated_calibration": new_calib}, indent=2))


if __name__ == "__main__":
    main()

