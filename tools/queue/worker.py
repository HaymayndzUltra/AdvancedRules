#!/usr/bin/env python3
from __future__ import annotations
import json
import time
from pathlib import Path

from tools.queue.exec_queue import load_queue, processed_ids, mark_processed
from tools.orchestrator.trigger_next import is_command_allowed, should_dry_run, verify_registry_checksum, load_registry_commands, _normalize_id, load_registry_full
from tools.gates.gate_evaluator import evaluate_gates
from tools.orchestrator.trigger_next import run_shell

ROOT = Path(__file__).resolve().parents[2]


def process_once() -> int:
	mapping = load_registry_commands()
	registry_full = load_registry_full()
	ok, msg = verify_registry_checksum()
	if not ok:
		print("Registry checksum invalid:", msg)
		return 0
	gates = evaluate_gates()
	gate_results = { _normalize_id(r.get('command_id','')): r for r in gates.get('results', []) }
	seen = processed_ids()
	count = 0
	for rec in load_queue():
		cid = str(rec.get('correlation_id'))
		if cid in seen:
			continue
		cmd_id = str(rec.get('cmd_id'))
		if cmd_id not in mapping:
			mark_processed(cid, {"status":"skipped","reason":"no registry mapping"})
			continue
		GR = gate_results.get(cmd_id)
		if GR and not GR.get('passed', False):
			mark_processed(cid, {"status":"skipped","reason":"gates failed","detail":GR})
			continue
		allowed, reason = is_command_allowed(mapping[cmd_id])
		if not allowed:
			mark_processed(cid, {"status":"skipped","reason":f"not allowed: {reason}"})
			continue
		eff_dry = should_dry_run(False)
		if eff_dry:
			mark_processed(cid, {"status":"dry_run","shell": mapping[cmd_id]})
			count += 1
			continue
		try:
			run_shell(mapping[cmd_id], False)
			# Persist completed step after successful execution
			try:
				from tools.orchestrator.state import load_state, save_state
				cmd_def = registry_full.get(cmd_id, {})
				step = (cmd_def.get("emits", {}) or {}).get("add_completed_step")
				if step:
					st = load_state() or {}
					arr = list(st.get("completed_steps", []))
					if step not in arr:
						arr.append(step)
						st["completed_steps"] = arr
						save_state(st)
			except Exception:
				pass
			mark_processed(cid, {"status":"executed"})
			count += 1
		except Exception as e:
			mark_processed(cid, {"status":"error","error": str(e)})
	return count


def main() -> None:
	processed = process_once()
	print(json.dumps({"processed": processed}, indent=2))


if __name__ == '__main__':
	main()