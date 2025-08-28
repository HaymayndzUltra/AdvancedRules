#!/usr/bin/env python3
from tools.runner.io_utils import write_md_with_frontmatter, MB

def run(mode: str) -> None:
    m = mode.upper()
    if m == "PEER_REVIEW":
        if not (MB / "plan/Summary_Report.md").exists():
            raise SystemExit("Summary_Report.md missing")
        write_md_with_frontmatter(
            MB / "plan/Validation_Report.md",
            {"title":"Validation Report","version":1,"findings":[]},
            "# Validation Report\n- CONFIRM: stub\n",
            role="principal_engineer_ai",
        )
    elif m == "SYNTHESIS":
        for req in ("Action_Plan.md", "Summary_Report.md", "Validation_Report.md"):
            if not (MB / f"plan/{req}").exists():
                raise SystemExit(f"{req} missing")
        write_md_with_frontmatter(
            MB / "plan/Final_Implementation_Plan.md",
            {"title":"Final Implementation Plan","version":1,"tasks":[]},
            "# Final Implementation Plan\n",
            role="principal_engineer_ai",
        )
    else:
        raise SystemExit(f"Unknown mode: {mode}")

