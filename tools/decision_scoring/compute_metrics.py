#!/usr/bin/env python3
"""
Stub: computes per-candidate metrics in [0,1].
Replace similarity/evidence/recency with real logic (embeddings, ripgrep hits, timestamps).
"""
import json, sys, os, time


def nz(x):
    return max(0.0, min(1.0, float(x)))


def main():
    data = json.load(sys.stdin)
    # Example dummy logic:
    for c in data["candidates"]:
        m = c.setdefault("metrics", {})
        m.setdefault("intent", 0.8)
        m.setdefault(
            "state",
            0.7 if all("exists:" not in p for p in c.get("preconds", [])) else 0.9,
        )
        m.setdefault("evidence", 0.5)
        m.setdefault("recency", 0.6)
        m.setdefault("pref", 0.6 if c.get("action_type") == "NATURAL_STEP" else 0.55)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
