#!/usr/bin/env python3
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / ".cursor/commands/registry.yaml"
STATE = ROOT / "workflow_state.json"
RULE_ATTACH_LOG = ROOT / "rule_attach_log.json"
OUT = ROOT / "gate_results.json"


@dataclass
class GateResult:
    id: str
    passed: bool
    reasons: List[str]


def _load_registry() -> Dict[str, Any]:
    if not REG.exists():
        return {"commands": []}
    return yaml.safe_load(REG.read_text(encoding="utf-8")) or {"commands": []}


def _load_state() -> Dict[str, Any]:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _has_attachment(domain_keyword: str) -> bool:
    # naive domain evidence: check if any log line mentions matched_rule path containing domain_keyword
    if not RULE_ATTACH_LOG.exists():
        return False
    try:
        with RULE_ATTACH_LOG.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                mr = str(rec.get("matched_rule", "")).lower()
                if domain_keyword.lower() in mr:
                    return True
    except Exception:
        return False
    return False


def evaluate_for_command(cmd_id: str) -> GateResult:
    reg = _load_registry()
    state = _load_state()

    cmd = next((c for c in reg.get("commands", []) if c.get("id") == cmd_id or cmd_id in (c.get("aliases") or [])), None)
    if not cmd:
        return GateResult(id=cmd_id, passed=False, reasons=[f"unknown command id: {cmd_id}"]) 

    reasons: List[str] = []
    ok = True

    # Check state requirements
    cur_state = str(state.get("state", ""))
    req = cmd.get("requires") or {}
    allowed_states = req.get("states_any_of") or []
    if allowed_states and cur_state not in allowed_states:
        ok = False
        reasons.append(f"state '{cur_state}' not in states_any_of={allowed_states}")

    # Completed steps (optional: not tracked explicitly; check history titles as hint)
    wanted_steps = set(req.get("completed_steps_all_of") or [])
    if wanted_steps:
        # naive: ensure each wanted step exists in history as a 'to' state or skip if not present
        hist = state.get("history", [])
        have = {str(h.get("to")) for h in hist}
        missing = [s for s in wanted_steps if s not in have]
        if missing:
            ok = False
            reasons.append(f"missing completed_steps_all_of={missing}")

    # Gates (named): use rule attachments as coarse evidence
    gates = set(req.get("gates_passed_all_of") or [])
    for g in gates:
        # heuristic: require attachment evidence containing gate name (lowercased)
        if not _has_attachment(g.lower()):
            ok = False
            reasons.append(f"gate not satisfied: {g}")

    # Contexts: must_exist files
    ctx = cmd.get("contexts") or {}
    for p in ctx.get("must_exist", []) or []:
        if not (ROOT / p).exists():
            ok = False
            reasons.append(f"missing file: {p}")

    res = GateResult(id=cmd_id, passed=ok, reasons=reasons)
    OUT.write_text(json.dumps({"id": res.id, "passed": res.passed, "reasons": res.reasons}, indent=2), encoding="utf-8")
    return res


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: gate_evaluator.py <command_id>")
        raise SystemExit(2)
    r = evaluate_for_command(sys.argv[1])
    print(json.dumps({"id": r.id, "passed": r.passed, "reasons": r.reasons}, indent=2))

