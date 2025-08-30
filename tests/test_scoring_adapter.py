import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.decision_scoring.adapter import adapt_candidates
from tools.decision_scoring.advanced_score import score_candidates


def test_adapter_converts_metrics_to_scores_and_preserves_ranking():
    legacy = [
        {"id": "a", "action_type": "COMMAND_TRIGGER", "risk": "LOW", "metrics": {"intent": 0.9, "state": 0.8, "evidence": 0.7, "recency": 0.6, "pref": 0.5}},
        {"id": "b", "action_type": "NATURAL_STEP",   "risk": "LOW", "metrics": {"intent": 0.7, "state": 0.7, "evidence": 0.6, "recency": 0.6, "pref": 0.6}},
    ]
    adapted = adapt_candidates(legacy)
    assert all("scores" in c for c in adapted)
    res = score_candidates(adapted, explore=False, shadow=False)
    ids = [c["id"] for c in res["candidates"]]
    assert ids[0] == "a"


def test_adapter_handles_canonical_scores_input():
    canonical = [
        {"id": "x", "action_type": "NATURAL_STEP", "risk": "LOW", "scores": {"intent": 0.1, "state": 0.1, "evidence": 0.1, "recency": 0.1, "pref": 0.1, "cost": 0.0, "risk_penalty": 0.0}},
        {"id": "y", "action_type": "NATURAL_STEP", "risk": "LOW", "scores": {"intent": 0.9, "state": 0.9, "evidence": 0.9, "recency": 0.9, "pref": 0.9, "cost": 0.0, "risk_penalty": 0.0}},
    ]
    adapted = adapt_candidates(canonical)
    res = score_candidates(adapted, explore=False, shadow=False)
    ids = [c["id"] for c in res["candidates"]]
    assert ids[0] == "y"

