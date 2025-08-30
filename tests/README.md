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

## Notes on optional RAG/arx tests
- Some tests invoke the `arx` CLI for RAG memory. These are conditionally skipped if `arx` is not installed.
- To enable them locally:
  - Install package and deps: `python -m pip install -U pip setuptools wheel && python -m pip install -r requirements.txt && python -m pip install -e .`
  - Enable RAG features for CLI runs: `export AR_ENABLE_RAG=1`
  - Then run: `pytest -q`

Dependencies expected for CI/local:
- pytest, networkx, pyyaml (declared in requirements.txt)
- Heavy ML deps (torch, transformers, sentence-transformers, chromadb) are optional; tests skip when absent.