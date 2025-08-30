#!/usr/bin/env python3
import argparse
import json
import re
import yaml
import json
import subprocess
import sys
import os
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / ".cursor/commands/registry.yaml"
REG_SHA = ROOT / ".cursor/commands/registry.sha256"


def _normalize_id(raw_id: str) -> str:
    ascii_id = (
        raw_id.replace("→", "-")
        .replace(" ", "-")
        .replace("_", "-")
        .lower()
    )
    ascii_id = re.sub(r"[^a-z0-9-]", "", ascii_id)
    ascii_id = re.sub(r"-+", "-", ascii_id).strip("-")
    return ascii_id


def load_registry_commands() -> dict:
    mapping = {}
    if not REG.exists():
        return mapping
    content = REG.read_text(encoding="utf-8")
    # Strip heredoc preface if present
    if content.startswith("cat >"):
        lines = content.splitlines()
        start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("version:"):
                start = i
                break
        content = "\n".join(lines[start:])
    data = yaml.safe_load(content) or {}
    commands = data.get("commands", [])
    for cmd in commands:
        raw_id = str(cmd.get("id", "")).strip()
        norm_id = _normalize_id(raw_id)
        shell = cmd.get("run", {}).get("shell", [])
        if isinstance(shell, list) and norm_id:
            mapping[norm_id] = shell
    return mapping


def run_shell(cmd: list, dry_run: bool) -> None:
    if dry_run:
        print("DRY_RUN:", " ".join(cmd))
        return
    subprocess.check_call(cmd, cwd=str(ROOT))


def should_dry_run(cli_dry_run: bool) -> bool:
    return os.getenv("ALLOW_RUN", "0") != "1" or bool(cli_dry_run)


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_registry_checksum() -> (bool, str):
    if not REG.exists():
        return False, "registry.yaml missing"
    if not REG_SHA.exists():
        return False, "registry.sha256 missing (run scripts/update_registry_checksum.py)"
    try:
        expected = REG_SHA.read_text(encoding="utf-8").strip().split()[0]
    except Exception:
        return False, "invalid registry.sha256 format"
    actual = compute_file_sha256(REG)
    return (actual == expected, f"checksum {'ok' if actual == expected else 'mismatch'}")


ALLOWED_COMMANDS = {
    "arx": "any",
    "python3:tools/run_role.py": "only",
}


def is_command_allowed(cmd: list) -> (bool, str):
    if not cmd:
        return False, "empty command"
    program = cmd[0]
    if program == "arx":
        return True, "ok"
    if program == "python3" and len(cmd) >= 2 and str(cmd[1]).startswith("tools/"):
        # Restrict to run_role.py by default
        if str(cmd[1]).endswith("run_role.py"):
            return True, "ok"
        return False, f"python3 allowed only for tools/run_role.py (got {cmd[1]})"
    return False, f"program '{program}' not in allowlist"


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Trigger orchestrator: scores candidates, enforces gates, and maps to registry commands.\n"
            "Default behavior: gates enforced; DRY-RUN unless ALLOW_RUN=1."
        ),
        epilog=(
            "Execution policy:\n"
            "- Dry-run by default. To execute, export ALLOW_RUN=1 or pass --dry-run to force dry-run.\n"
            "- Allowlist: only 'arx' and 'python3 tools/run_role.py' are permitted by default.\n"
            "- Gates: must_exist/states/domains evaluated before any execution."
        )
    )
    ap.add_argument("--candidates", default=str(ROOT / "tools/decision_scoring/examples/trigger_candidates.json"), help="Path to candidates JSON (list or {candidates:[...]})")
    ap.add_argument("--dry-run", action="store_true", help="Force dry-run (also default unless ALLOW_RUN=1)")
    ap.add_argument("--sandbox", action="store_true", help="Enable sandbox mode (no-op placeholder)")
    ap.add_argument("--print-allowlist", action="store_true", help="Print the current command allowlist and exit")
    ap.add_argument("--enqueue", action="store_true", help="Enqueue the chosen command instead of executing immediately")
    args = ap.parse_args()
    if args.print_allowlist:
        print(json.dumps({"allowlist": list(ALLOWED_COMMANDS.keys())}, indent=2))
        return

    mapping = load_registry_commands()
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from tools.decision_scoring.advanced_score import score_candidates
        from tools.gates.gate_evaluator import evaluate_gates
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
    decision = res.get("decision", {})
    top = res.get("candidates", [{}])[0].get("id")
    # Emit decision trace with correlation id and trace id
    try:
        from tools.runner.io_utils import append_event, append_decision_trace
        import uuid as _uuid
        corr_id = str(_uuid.uuid4())
        trace_id = str(_uuid.uuid4())
        # Set in environment for child processes
        os.environ['CORRELATION_ID'] = corr_id
        os.environ['TRACE_ID'] = trace_id
        trace = {"type":"decision","top": top, "decision": decision, "correlation_id": corr_id, "trace_id": trace_id}
        append_decision_trace(trace)
        append_event({"type":"decision_made","top": top, "correlation_id": corr_id, "trace_id": trace_id})
    except Exception:
        pass
    print(json.dumps({"decision": decision, "top": top}, indent=2))

    dtype = res.get("decision", {}).get("type")
    if dtype in {"NEXT_STEP", "OPTION_SET"} and res.get("candidates"):
        cmd_id = _normalize_id(res["candidates"][0]["id"])
        if cmd_id not in mapping:
            print(f"No registry mapping for id: {cmd_id}")
            return
        # Gate enforcement
        gates = evaluate_gates()
        gate_entry = next((r for r in gates.get("results", []) if _normalize_id(r.get("command_id","")) == cmd_id), None)
        if gate_entry and not gate_entry.get("passed", False):
            print("Refusing execution: gate checks failed for", cmd_id)
            print(json.dumps(gate_entry, indent=2))
            return
        # Verify registry checksum
        ok, msg = verify_registry_checksum()
        if not ok:
            print("Refusing execution: registry checksum verification failed -", msg)
            return
        # Allowlist enforcement
        allowed, reason = is_command_allowed(mapping[cmd_id])
        if not allowed:
            print("Refusing execution: command not allowed -", reason)
            return
        # Enqueue path
        if args.enqueue:
            try:
                from tools.queue.exec_queue import enqueue_task
                # Reuse a correlation id; if none from earlier, generate
                import uuid as _uuid
                corr_id = str(_uuid.uuid4())
                qres = enqueue_task(cmd_id, corr_id, {"shell": mapping[cmd_id]})
                print(json.dumps({"enqueued": qres}, indent=2))
            except Exception as e:
                print("Failed to enqueue:", e)
            return

        # Dry-run default policy
        eff_dry = should_dry_run(args.dry_run)
        if eff_dry and os.getenv("ALLOW_RUN", "0") != "1":
            print("Dry-run enforced by default. Set ALLOW_RUN=1 to execute.")
        if args.sandbox and not eff_dry:
            # Placeholder sandbox note
            print("SANDBOX MODE enabled: executing within sandbox profile (placeholder)")
        run_shell(mapping[cmd_id], eff_dry)
    else:
        print("No trigger —", dtype)


if __name__ == "__main__":
    main()

