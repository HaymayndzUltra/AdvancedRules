#!/usr/bin/env python3
from __future__ import annotations
from typing import Any, Dict, List


CANON_KEYS = ["intent", "state", "evidence", "recency", "pref", "cost", "risk_penalty"]


def to_canonical_scores(c: Dict[str, Any]) -> Dict[str, float]:
    """Map legacy metrics→scores shape; preserve already-canonical fields.

    - If `scores` present, ensure all canonical keys exist (fill 0).
    - Else if `metrics` present, copy known keys into `scores` and add cost/risk_penalty=0.
    - Else return empty scores (all zeros).
    """
    out: Dict[str, float] = {}
    if isinstance(c.get("scores"), dict):
        s = c.get("scores", {})
        for k in CANON_KEYS:
            try:
                out[k] = float(s.get(k, 0.0))
            except Exception:
                out[k] = 0.0
        return out
    m = c.get("metrics", {})
    if isinstance(m, dict):
        for k in ["intent", "state", "evidence", "recency", "pref"]:
            try:
                out[k] = float(m.get(k, 0.0))
            except Exception:
                out[k] = 0.0
        out.setdefault("cost", 0.0)
        out.setdefault("risk_penalty", 0.0)
        return out
    # fallback: zeros
    for k in CANON_KEYS:
        out[k] = 0.0
    return out


def adapt_candidates(cands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return new list with canonical `scores` populated; does not mutate input."""
    adapted: List[Dict[str, Any]] = []
    for c in cands:
        nc = dict(c)
        nc["scores"] = to_canonical_scores(c)
        adapted.append(nc)
    return adapted

