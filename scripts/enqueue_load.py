#!/usr/bin/env python3
import argparse, sys
sys.path.insert(0, '.')
from exec_queue.tasks import execute_step

p = argparse.ArgumentParser()
p.add_argument('--coder', type=int, default=30)
p.add_argument('--auditor', type=int, default=10)
p.add_argument('--flow', type=str, default='flow_demo')
p.add_argument('--branch', type=str, default='feature/queue-demo')
args = p.parse_args()

def enq(n, persona):
    for i in range(n):
        execute_step.apply_async(kwargs=dict(
            flow_id=args.flow,
            task_id=f"T-{persona[:2]}-{i:04d}",
            step_id=f"step_{i:03d}",
            persona=persona,
            exec_mode="dry_run",
            branch=args.branch,
            model="local-13b",
            payload={"i": i}
        ))

enq(args.coder, "CODER_AI")
enq(args.auditor, "AUDITOR_AI")
print(f"✅ Enqueued {args.coder}+{args.auditor} tasks")
