# tests/

- Purpose: Automated validation for the end-to-end pipeline and critical invariants.

## Suites
- e2e/: golden-path pipeline test (plan → audit → peer_review → synthesis)
- smoke/: scorer v3 and governance validator smoke tests

## How to run
```bash
# If pytest is on PATH
pytest -q

# Or install to user-local bin and run
python3 -m pip install --break-system-packages pytest -q
/home/ubuntu/.local/bin/pytest -q
```