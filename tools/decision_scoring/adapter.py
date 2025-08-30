#!/usr/bin/env python3
from __future__ import annotations
import json
from typing import Any, Dict, List, Tuple
from pathlib import Path
import re

try:
	from jsonschema import Draft202012Validator
except Exception:
	Draft202012Validator = None  # optional at runtime

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/candidates.schema.json"

_CANON_KEYS = ["intent","state","evidence","recency","pref","cost","risk_penalty"]


def _clamp01(x: float) -> float:
	return 0.0 if x < 0 else 1.0 if x > 1 else x


def _upper_str(val: Any, default: str) -> str:
	try:
		return str(val or default).upper()
	except Exception:
		return default.upper()


def _normalize_action_type(val: Any) -> str:
	v = _upper_str(val, "NATURAL_STEP")
	return v if v in {"NATURAL_STEP","COMMAND_TRIGGER"} else "NATURAL_STEP"


def _normalize_risk(val: Any) -> str:
	v = _upper_str(val, "LOW")
	return v if v in {"LOW","MEDIUM","HIGH","CRITICAL"} else "LOW"


def _metrics_to_scores(metrics: Dict[str, Any]) -> Dict[str, float]:
	scores: Dict[str, float] = {}
	for k in _CANON_KEYS:
		try:
			scores[k] = _clamp01(float(metrics.get(k, 0.0)))
		except Exception:
			scores[k] = 0.0
	return scores


def adapt_candidates(raw: Any) -> List[Dict[str, Any]]:
	"""Adapt input candidates to canonical schema.
	Accepts either {'candidates': [...]} or a list [...].
	Supports legacy 'metrics' by mapping to 'scores'.
	"""
	if isinstance(raw, dict) and "candidates" in raw:
		items = raw.get("candidates", [])
	elif isinstance(raw, list):
		items = raw
	else:
		raise ValueError("Invalid candidates input; expected list or object with 'candidates'.")

	canon: List[Dict[str, Any]] = []
	for c in items:
		cid = str(c.get("id", ""))
		atype = _normalize_action_type(c.get("action_type", "NATURAL_STEP"))
		risk = _normalize_risk(c.get("risk", "LOW"))
		scores = c.get("scores")
		if not isinstance(scores, dict):
			metrics = c.get("metrics", {})
			scores = _metrics_to_scores(metrics)
		# ensure all required keys present
		for k in _CANON_KEYS:
			if k not in scores:
				scores[k] = 0.0
		canon.append({
			"id": cid,
			"action_type": atype,
			"risk": risk,
			"explanation": c.get("explanation", ""),
			"preconds": c.get("preconds", []),
			"scores": scores,
		})
	return canon


def validate_canonical(candidates: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, str]]]:
	"""Validate against JSON schema if jsonschema is available."""
	if Draft202012Validator is None or not SCHEMA_PATH.exists():
		return True, []
	try:
		schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
		validator = Draft202012Validator(schema)
		errors = []
		for err in sorted(validator.iter_errors({"candidates": candidates}), key=str):
			errors.append({"path": "/"+"/".join(map(str, err.path)), "message": err.message})
		return len(errors) == 0, errors
	except Exception as e:
		return False, [{"path": "/", "message": f"Schema validation failed: {e}"}]