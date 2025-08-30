#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List

from tools.io.fs import append_jsonl, atomic_write_text, FileLock

ROOT = Path(__file__).resolve().parents[2]
QUEUE_DIR = ROOT / "exec_queue"
QUEUE_FILE = QUEUE_DIR / "exec_queue.jsonl"
PROCESSED_FILE = QUEUE_DIR / "processed.json"


def _now() -> float:
    return time.time()


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    items: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            pass
    return items


def _write_jsonl_atomically(path: Path, items: List[Dict[str, Any]]) -> None:
    content = "\n".join(json.dumps(i) for i in items if i) + ("\n" if items else "")
    atomic_write_text(path, content)


def _load_processed() -> Dict[str, Any]:
    if PROCESSED_FILE.exists():
        try:
            return json.loads(PROCESSED_FILE.read_text(encoding="utf-8") or "{}")
        except Exception:
            return {}
    return {}


def _save_processed(data: Dict[str, Any]) -> None:
    atomic_write_text(PROCESSED_FILE, json.dumps(data, indent=2))


def idempotency_key(correlation_id: str, state: str | None) -> str:
    return f"{correlation_id}:{state or ''}"


def enqueue(correlation_id: str, cmd_id: str, shell: List[str], state: str | None = None) -> Dict[str, Any]:
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    item = {
        "ts": _now(),
        "correlation_id": correlation_id,
        "cmd_id": cmd_id,
        "shell": shell,
        "state": state,
    }
    key = idempotency_key(correlation_id, state)
    with FileLock(QUEUE_FILE):
        processed = _load_processed()
        if processed.get(key):
            return {"status": "noop", "reason": "already processed", "item": item}
        items = _read_jsonl(QUEUE_FILE)
        if any(idempotency_key(i.get("correlation_id", ""), i.get("state")) == key for i in items):
            return {"status": "noop", "reason": "already enqueued", "item": item}
        append_jsonl(QUEUE_FILE, item)
    return {"status": "enqueued", "item": item}


def dequeue() -> Dict[str, Any] | None:
    with FileLock(QUEUE_FILE):
        items = _read_jsonl(QUEUE_FILE)
        if not items:
            return None
        # FIFO
        head, rest = items[0], items[1:]
        _write_jsonl_atomically(QUEUE_FILE, rest)
        return head


def process_item(item: Dict[str, Any], enforce_gates: bool = True, sandbox: bool = False) -> str:
    key = idempotency_key(item.get("correlation_id", ""), item.get("state"))
    processed = _load_processed()
    if processed.get(key):
        return "noop"

    # set correlation id env for downstream writes
    if item.get("correlation_id"):
        os.environ["AR_CORRELATION_ID"] = item["correlation_id"]

    # enforce gates
    if enforce_gates:
        try:
            from tools.gates.gate_evaluator import evaluate_for_command
            gr = evaluate_for_command(item.get("cmd_id", ""))
            if not gr.passed:
                print("Refusing execution due to failing gates/contexts:")
                for r in gr.reasons:
                    print(" -", r)
                return "skipped"
        except Exception as e:
            print(f"Gate evaluator error: {e}")
            return "error"

    # allowlist and dry-run
    cmd = item.get("shell") or []
    from tools.orchestrator.trigger_next import is_command_allowed, run_shell
    allowed, reason = is_command_allowed(cmd)
    if not allowed:
        print(f"Refusing execution: disallowed command — {reason}")
        return "skipped"
    dry_run = os.getenv("ALLOW_RUN") != "1"
    if dry_run:
        print("Execution safety: dry-run enforced by default. Set ALLOW_RUN=1 to execute.")
    if sandbox:
        print("Sandbox mode requested (no-op)")
    run_shell(cmd, dry_run)

    processed[key] = {"at": _now(), "cmd_id": item.get("cmd_id")}
    _save_processed(processed)
    return "ok"


def worker_once(enforce_gates: bool = True, sandbox: bool = False) -> str:
    item = dequeue()
    if not item:
        return "empty"
    return process_item(item, enforce_gates=enforce_gates, sandbox=sandbox)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Exec queue worker — processes exec_queue.jsonl in FIFO order.\n"
            "Idempotency: correlation_id + state. Gates enforced by default."
        )
    )
    ap.add_argument("--once", action="store_true", help="Process a single item then exit")
    ap.add_argument("--no-gates", action="store_true", help="Do not enforce gates (not recommended)")
    ap.add_argument("--sandbox", action="store_true", help="Sandbox mode (placeholder)")
    args = ap.parse_args()
    if args.once:
        status = worker_once(enforce_gates=not args.no_gates, sandbox=args.sandbox)
        print(json.dumps({"status": status}))
        return
    # loop mode
    while True:
        status = worker_once(enforce_gates=not args.no_gates, sandbox=args.sandbox)
        print(json.dumps({"status": status}))
        if status == "empty":
            time.sleep(0.5)


if __name__ == "__main__":
    main()

