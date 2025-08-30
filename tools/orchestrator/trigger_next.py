#!/usr/bin/env python3
import argparse
import json
import re
import yaml
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / ".cursor/commands/registry.yaml"


def load_registry_commands() -> dict:
    mapping = {}
    if not REG.exists():
        return mapping
    # Load YAML directly (already normalized/validated in preprocessing)
    data = yaml.safe_load(REG.read_text(encoding="utf-8")) or {}
    for cmd in data.get("commands", []):
        cmd_id = cmd.get("id")
        shell = ((cmd.get("run") or {}).get("shell") or [])
        if cmd_id and isinstance(shell, list) and all(isinstance(s, str) for s in shell):
            mapping[cmd_id] = shell
            # Also map aliases for backward compatibility
            for al in cmd.get("aliases", []) or []:
                mapping.setdefault(al, shell)
    return mapping


def run_shell(cmd: list, dry_run: bool) -> None:
    if dry_run:
        print("DRY_RUN:", " ".join(cmd))
        return
    subprocess.check_call(cmd, cwd=str(ROOT))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default=str(ROOT / "tools/decision_scoring/examples/trigger_candidates.json"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--enforce-gates", action="store_true", help="Validate gates/contexts before execution")
    ap.add_argument("--print-gates", action="store_true", help="Print gate evaluation results")
    args = ap.parse_args()

    mapping = load_registry_commands()
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from tools.decision_scoring.advanced_score import score_candidates
    except Exception as e:
        raise SystemExit(f"Cannot import scorer: {e}")

    cfile = Path(args.candidates)
    if cfile.exists():
        data = json.loads(cfile.read_text())
        candidates = data.get("candidates", data)
    else:
        # fallback sample
        candidates = [
            {"id":"planning_from_backlog","action_type":"COMMAND_TRIGGER","risk":"LOW","scores":{"intent":0.9,"state":0.8,"evidence":0.7,"recency":0.6,"pref":0.5,"cost":0.1,"risk_penalty":0.0}},
            {"id":"ask_for_details","action_type":"NATURAL_STEP","risk":"LOW","scores":{"intent":0.6,"state":0.6,"evidence":0.6,"recency":0.6,"pref":0.6,"cost":0.0,"risk_penalty":0.0}}
        ]

    res = score_candidates(candidates, explore=True, shadow=False)
    print(json.dumps({"decision": res.get("decision"), "top": res.get("candidates", [{}])[0].get("id")}, indent=2))

    dtype = res.get("decision", {}).get("type")
    if dtype in {"NEXT_STEP", "OPTION_SET"} and res.get("candidates"):
        cmd_id = res["candidates"][0]["id"]
        if cmd_id not in mapping:
            print(f"No registry mapping for id: {cmd_id}")
            return
        # Gate enforcement
        if args.enforce_gates:
            sys.path.insert(0, str(ROOT))
            try:
                from tools.gates.gate_evaluator import evaluate_for_command
                gr = evaluate_for_command(cmd_id)
            except Exception as e:
                print(f"Gate evaluator error: {e}")
                return
            if args.print_gates:
                print(json.dumps({"gate_check": {"id": gr.id, "passed": gr.passed, "reasons": gr.reasons}}, indent=2))
            if not gr.passed:
                print("Refusing execution due to failing gates/contexts:")
                for r in gr.reasons:
                    print(" -", r)
                return
        run_shell(mapping[cmd_id], args.dry_run)
    else:
        print("No trigger —", dtype)


if __name__ == "__main__":
    main()

