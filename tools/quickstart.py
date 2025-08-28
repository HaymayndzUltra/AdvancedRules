#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(cmd):
    print("$", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(ROOT))

def main():
    # Prestart composite (ensure offer_status + preflight)
    run(["python3", "tools/prestart/prestart_composite.py"])
    # Minimal happy path
    plan = ROOT / "memory-bank/plan"
    plan.mkdir(parents=True, exist_ok=True)
    (plan / "client_brief.md").write_text("Client brief", encoding="utf-8")
    run(["python3", "tools/run_role.py", "product_owner_ai"])
    run(["python3", "tools/run_role.py", "planning_ai"])
    run(["python3", "tools/run_role.py", "auditor_ai"])
    run(["python3", "tools/run_role.py", "principal_engineer_ai", "--mode", "PEER_REVIEW"])
    run(["python3", "tools/run_role.py", "principal_engineer_ai", "--mode", "SYNTHESIS"])
    print("Quickstart complete. Check memory-bank/plan and logs/")

if __name__ == "__main__":
    main()

