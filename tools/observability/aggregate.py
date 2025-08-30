#!/usr/bin/env python3
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVENTS = ROOT / "logs/events.jsonl"
OUT_DIR = ROOT / "logs/observability"


def load_events(events_path: Path):
    items = []
    if not events_path.exists():
        return items
    for line in events_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            pass
    return items


def aggregate(items):
    counts = defaultdict(int)
    durations = defaultdict(list)
    by_corr = defaultdict(lambda: {"events": 0, "artifacts": 0, "last_decision": None, "candidates": []})
    for e in items:
        t = e.get("type", "unknown")
        counts[t] += 1
        cid = e.get("correlation_id", "unknown")
        by_corr[cid]["events"] += 1
        if t == "role_duration":
            mod = e.get("module", "unknown")
            durations[mod].append(float(e.get("seconds", 0)))
        if t == "artifact_emitted":
            by_corr[cid]["artifacts"] += 1
        if t == "decision_trace":
            by_corr[cid]["last_decision"] = e.get("decision")
            by_corr[cid]["candidates"] = e.get("candidates", [])
    duration_stats = {
        mod: {
            "count": len(vals),
            "total_sec": round(sum(vals), 6),
            "avg_sec": round(statistics.mean(vals), 6)
        } for mod, vals in durations.items()
    }
    return {"counts": dict(counts), "durations": duration_stats, "by_correlation": by_corr}


def write_reports(summary):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # minimal markdown
    lines = ["# Observability Summary\n"]
    lines.append("## Event Counts\n")
    for k, v in summary["counts"].items():
        lines.append(f"- {k}: {v}")
    lines.append("\n## Role Durations\n")
    for mod, stats in summary["durations"].items():
        lines.append(f"- {mod}: count={stats['count']}, total={stats['total_sec']}s, avg={stats['avg_sec']}s")
    (OUT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description=(
            "Aggregate events.jsonl into summary reports.\n"
            "Includes correlation_id metrics and decision trace summaries."
        )
    )
    ap.add_argument("--events", default=str(DEFAULT_EVENTS), help="Path to events.jsonl (correlation-aware)")
    args = ap.parse_args()
    events_path = Path(args.events)
    items = load_events(events_path)
    summary = aggregate(items)
    write_reports(summary)
    print(json.dumps({"events": len(items)}, indent=2))

