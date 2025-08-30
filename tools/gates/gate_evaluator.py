#!/usr/bin/env python3
from __future__ import annotations
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
	import yaml
except Exception:
	yaml = None

ROOT = Path(__file__).resolve().parents[2]
REG_PATH = ROOT / ".cursor/commands/registry.yaml"
STATE_PATH = ROOT / "workflow_state.json"
ATTACH_LOG = ROOT / "rule_attach_log.json"
OUT_PATH = ROOT / "memory-bank/gate_results.json"

@dataclass
class GateResult:
	command_id: str
	passed: bool
	missing_files: List[str]
	missing_states: List[str]
	missing_steps: List[str]
	missing_gates: List[str]
	missing_domains: List[str]
	reasons: List[str]


def _normalize_id(raw_id: str) -> str:
	return (
		raw_id.replace("→", "-").replace(" ", "-").replace("_", "-").lower()
	)


def _load_yaml(path: Path) -> Dict[str, Any]:
	content = path.read_text(encoding="utf-8")
	if content.startswith("cat >"):
		lines = content.splitlines()
		for i, line in enumerate(lines):
			if line.strip().startswith("version:"):
				content = "\n".join(lines[i:])
				break
	return yaml.safe_load(content)


def _load_registry() -> List[Dict[str, Any]]:
	data = _load_yaml(REG_PATH)
	return data.get("commands", [])


def _load_state() -> Dict[str, Any]:
	try:
		return json.loads(STATE_PATH.read_text(encoding="utf-8"))
	except Exception:
		return {"state": None, "history": [], "completed_steps": []}


def _load_attachments() -> List[Dict[str, Any]]:
	recs: List[Dict[str, Any]] = []
	if not ATTACH_LOG.exists():
		return recs
	with ATTACH_LOG.open("r", encoding="utf-8") as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			try:
				recs.append(json.loads(line))
			except Exception:
				continue
	return recs


def _domains_attached(rec_list: List[Dict[str, Any]]) -> List[str]:
	out: List[str] = []
	for r in rec_list:
		mr = str(r.get("matched_rule", ""))
		if "/domains/" in mr:
			# derive domain key like domains/python, domains/node
			parts = mr.split("/domains/")[-1].split("/")
			if parts:
				key = parts[0]
				if key not in out:
					out.append(key)
	return out


def _exists(path: str) -> bool:
	p = (ROOT / path).resolve()
	return p.exists() and p.is_file()


def evaluate_gates() -> Dict[str, Any]:
	commands = _load_registry()
	state = _load_state()
	attach = _load_attachments()
	attached_domains = _domains_attached(attach)
	results: List[Dict[str, Any]] = []

	for cmd in commands:
		cid = str(cmd.get("id", ""))
		req = cmd.get("requires", {})
		ctx = cmd.get("contexts", {})
		gates = req.get("gates_passed_all_of", []) or []
		states_any = req.get("states_any_of", []) or []
		steps_all = req.get("completed_steps_all_of", []) or []
		must_exist = ctx.get("must_exist", []) or []
		domains_all = (ctx.get("domains_attached_all_of", []) or [])

		missing_files = [p for p in must_exist if not _exists(p)]
		missing_states = [] if (not states_any or state.get("state") in states_any) else states_any
		# completed_steps not tracked in sample state; leave as not enforced for now
		missing_steps: List[str] = []
		missing_gates: List[str] = []  # named gate evaluation is placeholder
		missing_domains = [d for d in domains_all if d not in attached_domains]

		passed = not (missing_files or missing_states or missing_steps or missing_gates or missing_domains)
		reasons: List[str] = []
		if missing_files:
			reasons.append(f"missing files: {', '.join(missing_files)}")
		if missing_states:
			reasons.append(f"state not in: {', '.join(states_any)} (current={state.get('state')})")
		if missing_domains:
			reasons.append(f"domains not attached: {', '.join(missing_domains)}")

		results.append(asdict(GateResult(
			command_id=cid,
			passed=passed,
			missing_files=missing_files,
			missing_states=missing_states,
			missing_steps=missing_steps,
			missing_gates=missing_gates,
			missing_domains=missing_domains,
			reasons=reasons,
		)))

	out = {"attached_domains": attached_domains, "results": results}
	OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
	OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
	return out


if __name__ == "__main__":
	res = evaluate_gates()
	print(json.dumps({"summary": {"total": len(res.get("results", [])), "passing": sum(1 for r in res.get("results", []) if r.get("passed"))}}, indent=2))