
# Repository README and Inventory Policy

This repository uses an automated process to ensure important folders contain up-to-date README.md files and to compile a comprehensive system inventory.

## Tooling
- Script: `scripts/docs_readme_sync.py`
- Marker: `<!-- AUTO-GENERATED: docs_readme_sync v1 -->`
- Manual notes section marker: `<!-- MANUAL-NOTES -->`

## Process
1. Identify target folders (default set is defined in the script).
2. For each folder:
   - Generate/update `README.md` with a directory listing.
   - Preserve any content below `<!-- MANUAL-NOTES -->`.
3. Compile `docs/SYSTEM_INVENTORY.md` summarizing all target folders.

## Usage
- Update READMEs and inventory:
```bash
python3 scripts/docs_readme_sync.py --inventory docs/SYSTEM_INVENTORY.md
```
- Check mode (CI): exit non‑zero if any README is missing/outdated:
```bash
python3 scripts/docs_readme_sync.py --check --inventory docs/SYSTEM_INVENTORY.md
```
- Specific directories only:
```bash
python3 scripts/docs_readme_sync.py --dirs tools cli schemas
```

## CI Integration (optional)
Add a job step:
```yaml
- name: Verify READMEs current
  run: |
    python3 scripts/docs_readme_sync.py --check --inventory docs/SYSTEM_INVENTORY.md
```

## Conventions
- Do not edit above the `<!-- MANUAL-NOTES -->` marker in auto‑generated READMEs.
- Add human‑written notes below the marker; they are preserved across syncs.
- If you add new important folders, either pass them via `--dirs` or extend `IMPORTANT_DIRS` in the script.
