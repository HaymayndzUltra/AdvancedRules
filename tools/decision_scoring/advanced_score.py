#!/usr/bin/env python3
from __future__ import annotations
import json, math, time
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
CONF = ROOT / "tools/decision_scoring"

DEFAULT_WEIGHTS = {"intent":0.30, "state":0.25, "evidence":0.20, "recency":0.15, "pref":0.10, "cost":-0.10, "risk_penalty":-0.20}
DEFAULT_THRESH  = {"conf_high":0.75, "conf_mid":0.55, "eps_gap":0.05}
DEFAULT_CALIB   = {"alpha":1.0, "beta":0.0}

def _clamp01(x: float) -> float: return 0.0 if x < 0 else 1.0 if x > 1 else x
def _sigmoid(z: float) -> float: return 1.0/(1.0+math.exp(-z))

def _load_json(path: Path, fallback: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return {**fallback, **json.loads(path.read_text() or "{}")}
    except Exception:
        return fallback

def load_config() -> Tuple[Dict[str, float], Dict[str, float], Dict[str, float]]:
    W = _load_json(CONF / "weights.json", DEFAULT_WEIGHTS)
    T = _load_json(CONF / "thresholds.json", DEFAULT_THRESH)
    C = _load_json(CONF / "calibration.json", DEFAULT_CALIB)
    # normalize weights by sum of abs values (keep sign)
    s = sum(abs(float(v)) for v in W.values()) or 1.0
    W = {k: float(v)/s for k, v in W.items()}
    return W, T, C

def _collect_scores(c: Dict[str, Any]) -> Dict[str, float]:
    s_in = c.get("scores", {})
    out: Dict[str, float] = {}
    for k in DEFAULT_WEIGHTS:
        try:
            out[k] = _clamp01(float(s_in.get(k, 0.0)))
        except Exception:
            out[k] = 0.0
    return out

def score_candidates(candidates: List[Dict[str, Any]],
                     explore: bool = False,
                     eps: float = 0.05,
                     shadow: bool = False) -> Dict[str, Any]:
    W, T, C = load_config()
    alpha, beta = float(C["alpha"]), float(C["beta"])
    conf_high, conf_mid, eps_gap = float(T["conf_high"]), float(T["conf_mid"]), float(T["eps_gap"])

    scored: List[Tuple[float, Dict[str, Any], Dict[str, float], float]] = []
    for c in candidates:
        comps = _collect_scores(c)
        raw = sum(comps.get(k, 0.0) * W.get(k, 0.0) for k in W)
        final = _sigmoid(alpha*(raw - beta))
        risk = str(c.get("risk", "LOW")).upper()
        action_type = str(c.get("action_type", "NATURAL_STEP")).upper()
        evidence_ok = comps.get("evidence", 0.0) >= 0.3
        if action_type == "COMMAND_TRIGGER" and risk in {"MEDIUM","HIGH","CRITICAL"} and not evidence_ok:
            final = min(final, 0.49)
        enriched = {
            "id": c.get("id",""),
            "action_type": action_type,
            "risk": risk,
            "scores": {**comps, "final_raw": round(raw,6), "final": round(final,6)},
            "explanation": c.get("explanation",""),
        }
        scored.append((final, enriched, comps, raw))

    scored.sort(key=lambda t: t[0], reverse=True)
    result: Dict[str, Any] = {"context_summary":"", "candidates":[x[1] for x in scored], "decision":{"type":"ASK_CLARIFY","reason":"no candidates"}}
    if not scored:
        return result

    top, top_c, top_comps, top_raw = scored[0]
    top2_gap = (top - scored[1][0]) if len(scored) > 1 else top
    high_risk = any(c[1]["risk"] in {"MEDIUM","HIGH","CRITICAL"} for c in scored)

    decision_trace = {"mode":"base", "top": top, "gap": top2_gap}
    if top >= conf_high:
        result["decision"] = {"type":"NEXT_STEP","reason":f"top≥{conf_high:.2f}"}
    elif top >= conf_mid and top2_gap <= eps_gap:
        k = min(3, len(scored))
        result["candidates"] = [scored[i][1] for i in range(k)]
        result["decision"] = {"type":"OPTION_SET","reason":f"{conf_mid:.2f}≤top<{conf_high:.2f} & gap≤{eps_gap}"}
    else:
        result["decision"] = {"type":"RISK_ALERT" if high_risk else "ASK_CLARIFY","reason":"low confidence" + (" + elevated risk" if high_risk else "")}

    # exploration (only when not in shadow)
    if explore and not shadow and result["decision"]["type"] == "OPTION_SET" and len(result["candidates"]) > 1:
        # reproducible exploration based on timestamp bucket
        bucket = int(time.time() // 60)  # minute bucket
        if (bucket % int(1/eps if eps > 0 else 999999)) == 0:
            result["candidates"] = list(reversed(result["candidates"]))
            result["decision"]["reason"] += " | explore_eps"
            decision_trace["mode"] = "explore"

    # shadow mode (compute shadow but do not change decision)
    if shadow:
        shadow_candidates = list(reversed([x[1] for x in scored])) if result["decision"]["type"] == "OPTION_SET" else [scored[0][1]]
        result["shadow"] = {"candidates": shadow_candidates, "note": "shadow mode; not applied"}
        decision_trace["mode"] = "shadow"

    result["decision_trace"] = decision_trace
    return result

if __name__ == "__main__":
    demo = [
        {"id":"plan","action_type":"COMMAND_TRIGGER","risk":"LOW","scores":{"intent":0.9,"state":0.7,"evidence":0.6,"recency":0.4,"pref":0.5,"cost":0.2,"risk_penalty":0.1}},
        {"id":"ask","action_type":"NATURAL_STEP","risk":"LOW","scores":{"intent":0.78,"state":0.7,"evidence":0.6,"recency":0.5,"pref":0.4,"cost":0.0,"risk_penalty":0.0}}
    ]
    print(json.dumps(score_candidates(demo, explore=True, eps=0.05, shadow=True), indent=2))

