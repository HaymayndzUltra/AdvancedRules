#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import re
import subprocess
from glob import iglob
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_ROOT = REPO_ROOT / ".cursor/rules"
LOG_PATH = REPO_ROOT / "rule_attach_log.json"


def get_repo_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT)).decode().strip()
    except Exception:
        return "unknown"


def parse_frontmatter(text: str) -> Tuple[List[str], bool]:
    """Return (globs, always_apply). Handles inline and multi-line lists.
    Only inspects the first frontmatter block delimited by '---'."""
    globs: List[str] = []
    always_apply = False
    blocks = re.split(r"^---\s*$", text, flags=re.M)
    if len(blocks) < 3:
        return globs, always_apply
    fm = blocks[1]
    # alwaysApply
    m = re.search(r"^alwaysApply:\s*(true|false)\s*$", fm, flags=re.M)
    if m:
        always_apply = m.group(1).lower() == "true"
    # globs inline
    m2 = re.search(r"^globs:\s*\[(.*?)\]\s*$", fm, flags=re.M | re.S)
    if m2:
        inside = m2.group(1).strip()
        if inside:
            for part in inside.split(','):
                pat = part.strip().strip('"\'')
                if pat:
                    globs.append(pat)
        return globs, always_apply
    # globs multi-line list
    if re.search(r"^globs:\s*$", fm, flags=re.M):
        # collect subsequent lines beginning with '-'
        lines = fm.splitlines()
        capture = False
        for ln in lines:
            if re.match(r"^globs:\s*$", ln):
                capture = True
                continue
            if capture:
                if re.match(r"^\s*-\s*['\"]?", ln):
                    part = ln.strip()[1:].strip()
                    part = part.strip('"\'')
                    if part:
                        globs.append(part)
                elif re.match(r"^[A-Za-z_]+:\s*", ln):
                    break
    return globs, always_apply


def find_matches(pattern: str) -> List[Path]:
    # Patterns are evaluated relative to repo root, recursive allowed
    abs_pat = str(REPO_ROOT / pattern)
    out: List[Path] = []
    for p in iglob(abs_pat, recursive=True):
        path = Path(p)
        # skip .git and .github noise
        if any(seg in {".git", ".github"} for seg in path.parts):
            continue
        if path.is_file():
            out.append(path)
    return out


def append_log(entry: dict, jsonl_path: Path) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def detect_and_log(log_path: Path, dry_run: bool = False) -> List[dict]:
    repo_sha = get_repo_sha()
    timestamp = dt.datetime.utcnow().isoformat() + "Z"
    results: List[dict] = []

    rule_files = sorted([p for p in RULES_ROOT.rglob("*.mdc") if "/roles/" not in str(p)])
    for rule in rule_files:
        text = rule.read_text(encoding="utf-8")
        globs, always_apply = parse_frontmatter(text)
        rel_rule = str(rule.relative_to(REPO_ROOT))
        nested_scope = str(rule.parent.relative_to(RULES_ROOT))

        if always_apply:
            entry = {
                "timestamp": timestamp,
                "repo_sha": repo_sha,
                "file_path": "",
                "matched_rule": rel_rule,
                "match_reason": "alwaysApply",
                "nested_scope": nested_scope,
                "decision_trace": "alwaysApply:true"
            }
            results.append(entry)
            if not dry_run:
                append_log(entry, log_path)
            continue

        if globs:
            # Deterministic: evaluate patterns in lexical order, file matches in lexical order
            for pat in sorted(set(globs)):
                matches = sorted(find_matches(pat))
                if not matches:
                    continue
                # Log first N matches to keep log compact; N=1 sufficient to prove attach
                first = matches[0]
                entry = {
                    "timestamp": timestamp,
                    "repo_sha": repo_sha,
                    "file_path": str(first.relative_to(REPO_ROOT)),
                    "matched_rule": rel_rule,
                    "match_reason": "glob",
                    "nested_scope": nested_scope,
                    "decision_trace": f"glob:{pat} matched:{first.name}"
                }
                results.append(entry)
                if not dry_run:
                    append_log(entry, log_path)
                # one entry per rule is enough to consider it attached
                break
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=str(LOG_PATH), help="path to append-only JSONL log")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    out = detect_and_log(Path(args.log), dry_run=args.dry_run)
    print(json.dumps({"attached": len(out)}, indent=2))

