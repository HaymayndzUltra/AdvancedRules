#!/usr/bin/env python3
from tools.runner.io_utils import write_text, MB

def run() -> None:
    if not (MB / "plan/product_backlog.yaml").exists():
        raise SystemExit("product_backlog.yaml missing")
    if not (MB / "plan/acceptance_criteria.json").exists():
        raise SystemExit("acceptance_criteria.json missing")
    write_text(MB / "plan/Action_Plan.md", "# Action Plan\n", role="planning_ai")
    write_text(MB / "plan/technical_plan.md", "# Technical Plan\n", role="planning_ai")
    write_text(MB / "plan/task_breakdown.yaml", "# tasks\n", role="planning_ai")

