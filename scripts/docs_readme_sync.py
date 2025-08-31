#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

IMPORTANT_DIRS = [
    'cli', 'tools', 'tools/io', 'tools/orchestrator', 'tools/runner', 'tools/observability',
    'tools/decision_scoring', 'tools/gates', 'tools/plugins', 'tools/artifacts', 'schemas',
    'schemas/memory', 'tests', 'docs', '.github/workflows', 'scripts', 'memory-bank'
]

README_HEADER = '<!-- AUTO-GENERATED: docs_readme_sync v1 -->\n'


def find_targets(root: Path, explicit: List[str]) -> List[Path]:
    dirs = []
    if explicit:
        for rel in explicit:
            p = (root / rel).resolve()
            if p.exists() and p.is_dir():
                dirs.append(p)
    else:
        for rel in IMPORTANT_DIRS:
            p = (root / rel)
            if p.exists() and p.is_dir():
                dirs.append(p)
    # de-duplicate
    uniq = []
    seen = set()
    for d in dirs:
        if d not in seen:
            uniq.append(d)
            seen.add(d)
    return uniq


def dir_summary(d: Path) -> Dict:
    files = []
    for path in sorted(d.iterdir(), key=lambda p: (p.is_dir(), p.name)):
        if path.name.startswith('.') and path.name not in {'.github'}:
            continue
        if path.name in {'__pycache__'}:
            continue
        files.append({
            'name': path.name,
            'type': 'dir' if path.is_dir() else 'file',
            'size': path.stat().st_size,
        })
    return {
        'path': str(d.relative_to(Path.cwd())),
        'count': len(files),
        'entries': files,
    }


def render_readme(summary: Dict, existing: str | None) -> str:
    title = summary['path']
    rows = []
    for e in summary['entries']:
        emoji = '📁' if e['type']=='dir' else '📄'
        rows.append(f"- {emoji} **{e['name']}**")
    body = '\n'.join(rows) if rows else '(empty)'
    manual = ''
    if existing and README_HEADER in existing:
        # preserve any manual section after the marker <!-- MANUAL-NOTES -->
        marker = '<!-- MANUAL-NOTES -->'
        idx = existing.find(marker)
        if idx != -1:
            manual = '\n' + existing[idx:]
    md = f"""{README_HEADER}# {title}

This README is auto-synced. Edit below the MANUAL-NOTES marker to add notes.

## Contents
{body}

<!-- MANUAL-NOTES -->
<!-- Add additional notes below. They will be preserved on sync. -->{manual}
"""
    return md


def write_readme(d: Path, check: bool) -> Tuple[str, bool]:
    readme = d/'README.md'
    existing = readme.read_text(encoding='utf-8') if readme.exists() else None
    summary = dir_summary(d)
    content = render_readme(summary, existing)
    if check:
        return (summary['path'], existing == content if existing else False)
    readme.write_text(content, encoding='utf-8')
    return (summary['path'], True)


def compile_inventory(dirs: List[Path], out: Path, check: bool) -> None:
    items = []
    for d in dirs:
        s = dir_summary(d)
        items.append(s)
    data = {'generated_by':'docs_readme_sync','roots':[str(p.relative_to(Path.cwd())) for p in dirs], 'items':items}
    # render markdown
    lines = ['# System Inventory', '', f"Roots: {', '.join(data['roots'])}", '']
    for s in items:
        lines.append(f"## {s['path']}")
        for e in s['entries']:
            emoji = '📁' if e['type']=='dir' else '📄'
            lines.append(f"- {emoji} {e['name']}")
        lines.append('')
    if not check:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text('\n'.join(lines), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description='Sync folder README.md and compile inventory')
    ap.add_argument('--dirs', nargs='*', default=[], help='Specific directories (relative) to process')
    ap.add_argument('--check', action='store_true', help='Check mode: nonzero exit if any README missing/outdated')
    ap.add_argument('--inventory', default='docs/SYSTEM_INVENTORY.md', help='Output inventory markdown')
    args = ap.parse_args()

    root = Path.cwd()
    dirs = find_targets(root, args.dirs)
    missing_or_outdated = []
    for d in dirs:
        path, ok = write_readme(d, check=args.check)
        if args.check:
            if not ok:
                missing_or_outdated.append(path)
    compile_inventory(dirs, root/args.inventory, check=args.check)
    if args.check and missing_or_outdated:
        print(json.dumps({'missing_or_outdated': missing_or_outdated}, indent=2))
        raise SystemExit(2)


if __name__ == '__main__':
    main()
