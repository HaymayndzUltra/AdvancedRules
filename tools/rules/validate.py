#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main() -> int:
    errors = []

    # Roles must not auto-attach (non-empty globs) and must not be alwaysApply:true
    for f in (ROOT / ".cursor/rules/roles").glob("*.mdc"):
        txt = f.read_text(encoding="utf-8")
        # Accept exactly: globs: []
        m = re.search(r"^globs:\s*\[(.*?)\]\s*$", txt, re.M)
        if m:
            if m.group(1).strip() != "":
                errors.append(f"{f}: roles must not declare non-empty globs")
        if re.search(r"^alwaysApply:\s*true", txt, re.M):
            errors.append(f"{f}: roles must not be alwaysApply:true")

    # Only orchestrator/gate/policy can be alwaysApply:true
    for f in (ROOT / ".cursor/rules").rglob("*.mdc"):
        txt = f.read_text(encoding="utf-8")
        if re.search(r"^alwaysApply:\s*true", txt, re.M) and "/roles/" in str(f):
            errors.append(f"{f}: roles cannot be alwaysApply:true")

    if errors:
        print("\n".join(errors))
        return 1

    print("OK: rule policy checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())

