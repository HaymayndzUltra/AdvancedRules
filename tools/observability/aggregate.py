#!/usr/bin/env python3
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "logs/events.jsonl"
TRACES = ROOT / "logs/decision_traces.jsonl"
OUT_DIR = ROOT / "logs/observability"

def load_events():
    items = []
    if not EVENTS.exists():
        return items
    for line in EVENTS.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            pass
    return items


def load_traces():
    items = []
    if not TRACES.exists():
        return items
    for line in TRACES.read_text().splitlines():
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
    for e in items:
        t = e.get("type", "unknown")
        counts[t] += 1
        if t == "role_duration":
            mod = e.get("module", "unknown")
            durations[mod].append(float(e.get("seconds", 0)))
    duration_stats = {
        mod: {
            "count": len(vals),
            "total_sec": round(sum(vals), 6),
            "avg_sec": round(statistics.mean(vals), 6)
        } for mod, vals in durations.items()
    }
    return {"counts": dict(counts), "durations": duration_stats}


def aggregate_by_correlation(events, traces):
    by_corr = defaultdict(lambda: {"events": [], "traces": []})
    for e in events:
        cid = e.get("correlation_id")
        if cid:
            by_corr[cid]["events"].append(e)
    for t in traces:
        cid = t.get("correlation_id")
        if cid:
            by_corr[cid]["traces"].append(t)
    # summarize
    summary = {}
    for cid, bucket in by_corr.items():
        summary[cid] = {
            "event_count": len(bucket["events"]),
            "trace_count": len(bucket["traces"]),
            "types": sorted({e.get("type","unknown") for e in bucket["events"]}),
        }
    return {"by_correlation": summary}

def write_reports(summary, redact=True):
    import os
    from tools.instrumentation.redactor import redact_dict, get_redaction_stats
    
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Apply redaction if enabled
    if redact and os.environ.get('ENABLE_REDACTION', 'true').lower() == 'true':
        redacted_summary = redact_dict(summary, deep=True)
        stats = get_redaction_stats()
        redacted_summary['redaction_stats'] = stats
    else:
        redacted_summary = summary
    
    (OUT_DIR / "summary.json").write_text(json.dumps(redacted_summary, indent=2), encoding="utf-8")
    
    # minimal markdown
    lines = ["# Observability Summary\n"]
    lines.append("## Event Counts\n")
    for k, v in redacted_summary["counts"].items():
        lines.append(f"- {k}: {v}")
    lines.append("\n## Role Durations\n")
    for mod, stats in redacted_summary["durations"].items():
        lines.append(f"- {mod}: count={stats['count']}, total={stats['total_sec']}s, avg={stats['avg_sec']}s")
    
    # Add redaction stats if present
    if 'redaction_stats' in redacted_summary:
        lines.append("\n## Redaction Statistics\n")
        stats = redacted_summary['redaction_stats']
        lines.append(f"- Total redactions: {stats.get('total', 0)}")
        if stats.get('by_type'):
            lines.append("- By type:")
            for rtype, count in stats['by_type'].items():
                lines.append(f"  - {rtype}: {count}")
    
    (OUT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    items = load_events()
    traces = load_traces()
    summary = aggregate(items)
    corr = aggregate_by_correlation(items, traces)
    
    # Run artifact audit and include in report
    try:
        from tools.artifacts.auditor import audit_artifacts
        audit_report = audit_artifacts()
        tamper_summary = {
            "tamper_detected": audit_report.get('tamper_detected', False),
            "artifacts_valid": audit_report['summary'].get('valid', 0),
            "artifacts_tampered": audit_report['summary'].get('tampered', 0),
            "artifacts_missing": audit_report['summary'].get('missing', 0),
            "registry_valid": audit_report['summary'].get('registry_valid', False)
        }
    except Exception as e:
        tamper_summary = {"error": str(e)}
    
    out = {**summary, **corr, "artifact_audit": tamper_summary}
    write_reports(out)
    
    print(json.dumps({
        "events": len(items), 
        "traces": len(traces),
        "tamper_detected": tamper_summary.get('tamper_detected', None)
    }, indent=2))

