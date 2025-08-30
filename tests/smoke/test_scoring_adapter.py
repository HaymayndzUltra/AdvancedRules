import json
import pytest

from tools.decision_scoring.adapter import adapt_candidates, validate_canonical
from tools.decision_scoring.advanced_score import score_candidates


def test_adapter_maps_metrics_to_scores():
	legacy = [
		{
			"id": "planning_from_backlog",
			"action_type": "COMMAND_TRIGGER",
			"risk": "LOW",
			"metrics": {"intent": 0.9, "state": 0.8, "evidence": 0.7, "recency": 0.6, "pref": 0.5, "cost": 0.1, "risk_penalty": 0.0},
		},
	]
	canon = adapt_candidates(legacy)
	ok, errors = validate_canonical(canon)
	assert ok, f"Schema errors: {errors}"
	c0 = canon[0]["scores"]
	assert set(["intent","state","evidence","recency","pref","cost","risk_penalty"]) <= set(c0.keys())
	assert 0.0 <= c0["intent"] <= 1.0


def test_scoring_adapter_consistent_ranking():
	legacy = [
		{
			"id": "a",
			"action_type": "COMMAND_TRIGGER",
			"risk": "LOW",
			"metrics": {"intent": 0.9, "state": 0.5, "evidence": 0.5, "recency": 0.4, "pref": 0.5, "cost": 0.1, "risk_penalty": 0.0},
		},
		{
			"id": "b",
			"action_type": "NATURAL_STEP",
			"risk": "LOW",
			"metrics": {"intent": 0.85, "state": 0.6, "evidence": 0.6, "recency": 0.4, "pref": 0.5, "cost": 0.0, "risk_penalty": 0.0},
		},
	]
	canonical = [
		{
			"id": "a",
			"action_type": "COMMAND_TRIGGER",
			"risk": "LOW",
			"scores": {"intent": 0.9, "state": 0.5, "evidence": 0.5, "recency": 0.4, "pref": 0.5, "cost": 0.1, "risk_penalty": 0.0},
		},
		{
			"id": "b",
			"action_type": "NATURAL_STEP",
			"risk": "LOW",
			"scores": {"intent": 0.85, "state": 0.6, "evidence": 0.6, "recency": 0.4, "pref": 0.5, "cost": 0.0, "risk_penalty": 0.0},
		},
	]

	res_legacy = score_candidates(legacy, explore=False, shadow=False)
	res_canon = score_candidates(canonical, explore=False, shadow=False)

	top_legacy = res_legacy.get("candidates", [{}])[0].get("id")
	top_canon = res_canon.get("candidates", [{}])[0].get("id")
	assert top_legacy == top_canon