#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

def run(cmd):
    print("$", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))

if __name__ == "__main__":
    try:
        run(["python3", "tools/prestart/ensure_readiness.py"])  # create defaults if missing
        # optional override using adapter values
        # run(["python3", "tools/upwork/adapter.py", "--contract", "fixed", "--escrow", "true", "--diary", "true", "--cap", "10"])
        run(["python3", "tools/run_role.py", "readiness"])  # print preflight status
        print("Prestart composite completed.")
    except subprocess.CalledProcessError as e:
        print("Prestart composite failed:", e, file=sys.stderr)
        sys.exit(e.returncode)

