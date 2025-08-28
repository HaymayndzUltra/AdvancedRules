import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MB = REPO / "memory-bank"


def run(cmd):
    subprocess.check_call(cmd, cwd=str(REPO))


def test_pipeline_golden_path(tmp_path):
    # 0) ensure readiness
    run(["python3", "tools/prestart/ensure_readiness.py"])  # creates offer_status.json if missing

    # 1) client brief
    plan_dir = MB / "plan"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "client_brief.md").write_text("Client brief test", encoding="utf-8")

    # 2) product owner → backlog + acceptance
    run(["python3", "tools/run_role.py", "product_owner_ai"])

    # 3) planning → plans (requires offer_status.json)
    run(["python3", "tools/run_role.py", "planning_ai"])

    # 4) audit
    run(["python3", "tools/run_role.py", "auditor_ai"])

    # 5) principal engineer peer review → validation
    run(["python3", "tools/run_role.py", "principal_engineer_ai", "--mode", "PEER_REVIEW"])

    # 6) principal engineer synthesis → final plan
    run(["python3", "tools/run_role.py", "principal_engineer_ai", "--mode", "SYNTHESIS"])

    # Assertions: artifacts exist
    must_exist = [
        MB / "plan/product_backlog.yaml",
        MB / "plan/acceptance_criteria.json",
        MB / "plan/Action_Plan.md",
        MB / "plan/technical_plan.md",
        MB / "plan/task_breakdown.yaml",
        MB / "plan/Summary_Report.md",
        MB / "plan/Validation_Report.md",
        MB / "plan/Final_Implementation_Plan.md",
    ]
    for p in must_exist:
        assert p.exists() and p.stat().st_size > 0, f"missing: {p}"

    # Provenance index exists and has entries
    idx = REPO / "memory-bank/artifacts_index.json"
    assert idx.exists() and idx.stat().st_size > 0
    data = json.loads(idx.read_text())
    assert isinstance(data, list) and len(data) >= 5

    # Events logged
    events = REPO / "logs/events.jsonl"
    assert events.exists() and events.stat().st_size > 0

