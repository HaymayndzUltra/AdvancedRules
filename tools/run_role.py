#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
MB = ROOT / "memory-bank"
EVENTS = ROOT / "logs/events.jsonl"

# Ensure repository root is importable (for tools.* modules)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.artifacts.hash_index import record as index_record  # type: ignore
from tools.runner.io_utils import append_event
from importlib import import_module
import time
from tools.orchestrator.state import transition

def ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

def write_text(path: Path, content: str, role: str | None = None) -> None:
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")
    append_event({"type":"artifact_emitted","path":str(path.relative_to(ROOT))})
    # provenance index for memory-bank artifacts
    try:
        if str(path).startswith(str(MB)) and path.exists() and path.stat().st_size:
            index_record(path, role=role or "runner")
    except Exception:
        pass

def touch_json(path: Path, payload: Dict, role: str | None = None) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    append_event({"type":"artifact_emitted","path":str(path.relative_to(ROOT))})
    try:
        if str(path).startswith(str(MB)) and path.exists() and path.stat().st_size:
            index_record(path, role=role or "runner")
    except Exception:
        pass

def write_md_with_frontmatter(path: Path, frontmatter: Dict, body: str, role: str | None = None) -> None:
    fm = "---\n" + json.dumps(frontmatter, ensure_ascii=False) + "\n---\n"
    write_text(path, fm + body, role=role)

def append_event(evt: Dict) -> None:
    ensure_parent(EVENTS)
    EVENTS.write_text((EVENTS.read_text() if EVENTS.exists() else "") + json.dumps(evt) + "\n", encoding="utf-8")

def run_plugin(module: str, func: str = "run", **kwargs):
    """Run plugin with safety wrapper for timeouts and idempotency."""
    start = time.time()
    mod = import_module(module)
    
    # Check if safety mode is enabled
    use_wrapper = os.environ.get('PLUGIN_SAFE_MODE', '1') == '1'
    timeout_seconds = int(os.environ.get('PLUGIN_TIMEOUT', '300'))
    
    if use_wrapper:
        from tools.plugins.wrapper import run_plugin_safe
        try:
            result = run_plugin_safe(
                plugin_id=module.split('.')[-1],
                func=getattr(mod, func),
                timeout_seconds=timeout_seconds,
                **kwargs
            )
            append_event({"type":"plugin_wrapped","module":module,"result":str(result)})
        except Exception as e:
            append_event({"type":"plugin_error","module":module,"error":str(e)})
            raise
    else:
        # Legacy direct execution
        try:
            getattr(mod, func)(**kwargs)
        finally:
            duration = time.time() - start
            append_event({"type":"role_duration","module":module,"seconds":duration})

def role_readiness_check() -> None:
    # Placeholder: a no-op that prints which files exist
    required = [
        MB / "business/client_score.json",
        MB / "business/capacity_report.md",
        MB / "business/pricing.ratecard.yaml",
        MB / "business/estimate_brief.md",
        MB / "plan/proposal.md",
    ]
    status = {str(p.relative_to(ROOT)): p.exists() and p.stat().st_size > 0 for p in required}
    print(json.dumps({"preflight": status}, indent=2))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("role", help="role id or helper name")
    parser.add_argument("--mode", default="", help="role mode (for principal_engineer_ai and plugins)")
    args = parser.parse_args()

    if args.role == "product_owner_ai":
        run_plugin("tools.runner.plugins.product_owner")
        transition("BACKLOG_READY")
    elif args.role == "planning_ai":
        run_plugin("tools.runner.plugins.planning")
        transition("PLANNING_DONE")
    elif args.role == "auditor_ai":
        run_plugin("tools.runner.plugins.auditor")
        transition("AUDIT_DONE")
    elif args.role == "principal_engineer_ai":
        m = (args.mode or "PEER_REVIEW").upper()
        run_plugin("tools.runner.plugins.principal_engineer", mode=m)
        if m == "PEER_REVIEW":
            transition("VALIDATION_DONE")
        elif m == "SYNTHESIS":
            transition("SYNTHESIS_DONE")
    elif args.role == "readiness":
        role_readiness_check()
    elif args.role == "codegen_ai":
        # Route via safe wrapper to tools.plugins.codegen
        run_plugin("tools.plugins.codegen", func="run", payload={"mode": (args.mode or "SCAFFOLD").upper()})
        transition("CODEGEN_DONE")
    elif args.role == "qa_ai":
        run_plugin("tools.plugins.qa", func="run", payload={"mode": (args.mode or "VALIDATE").upper()})
        transition("QA_DONE")
    elif args.role == "security_ai":
        run_plugin("tools.plugins.security", func="run", payload={"mode": (args.mode or "SAST").upper()})
        transition("SECURITY_DONE")
    elif args.role == "deploy_ai":
        run_plugin("tools.plugins.deploy", func="run", payload={"mode": (args.mode or "PACKAGE").upper()})
        transition("DEPLOY_PREPARED")
    else:
        raise SystemExit(f"Unsupported role: {args.role}")

    # After any successful transition above, attempt to trigger next step (non-blocking suggestion or enqueue)
    try:
        import subprocess as _sp
        # Prefer enqueue to avoid blocking; respects dry-run by default
        _sp.call(["python3", "tools/orchestrator/trigger_next.py", "--auto-candidates", "--enqueue"], cwd=str(ROOT))
    except Exception:
        pass

if __name__ == "__main__":
    main()

