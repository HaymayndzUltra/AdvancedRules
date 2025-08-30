#!/usr/bin/env python3
"""Memory management CLI commands for validation and repair."""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.io.fs import recover_file
from tools.schema.validate_memory import validate_memory_artifact


def validate_command(args: List[str]) -> int:
    """Validate memory artifacts against schemas.
    
    Usage: arx memory validate [path]
    """
    mb = ROOT / "memory-bank"
    target = Path(args[0]) if args else mb
    
    if not target.exists():
        print(f"Error: {target} does not exist")
        return 1
    
    results = []
    files_to_check = []
    
    if target.is_file():
        files_to_check = [target]
    else:
        # Recursively find all JSON and MD files
        files_to_check = list(target.glob("**/*.json")) + list(target.glob("**/*.md"))
    
    for file_path in files_to_check:
        content = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
        ok, error = validate_memory_artifact(file_path, content)
        
        rel_path = str(file_path.relative_to(ROOT))
        results.append({
            "path": rel_path,
            "valid": ok,
            "error": error
        })
        
        if not ok:
            print(f"❌ {rel_path}: {error}")
        else:
            print(f"✅ {rel_path}")
    
    # Summary
    valid_count = sum(1 for r in results if r["valid"])
    invalid_count = len(results) - valid_count
    
    print(f"\nSummary: {valid_count} valid, {invalid_count} invalid")
    
    # Write report
    report_path = ROOT / "memory-bank" / "validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps({
        "total": len(results),
        "valid": valid_count,
        "invalid": invalid_count,
        "results": results
    }, indent=2))
    
    print(f"Report written to {report_path}")
    return 0 if invalid_count == 0 else 1


def repair_command(args: List[str]) -> int:
    """Repair corrupted memory artifacts.
    
    Usage: arx memory repair [path]
    """
    mb = ROOT / "memory-bank"
    target = Path(args[0]) if args else mb
    
    if not target.exists():
        print(f"Error: {target} does not exist")
        return 1
    
    files_to_check = []
    if target.is_file():
        files_to_check = [target]
    else:
        # Check all JSON files and any file with .tmp sibling
        files_to_check = list(target.glob("**/*.json"))
        # Also check for orphaned .tmp files
        for tmp_file in target.glob("**/*.tmp"):
            original = Path(str(tmp_file).replace(".tmp", ""))
            if original not in files_to_check:
                files_to_check.append(original)
    
    repaired = []
    for file_path in files_to_check:
        if recover_file(file_path):
            rel_path = str(file_path.relative_to(ROOT))
            repaired.append(rel_path)
            print(f"🔧 Repaired: {rel_path}")
    
    if repaired:
        print(f"\nRepaired {len(repaired)} file(s)")
        # Write repair log
        log_path = ROOT / "memory-bank" / "repair_log.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(json.dumps({
            "repaired_count": len(repaired),
            "files": repaired
        }, indent=2))
        print(f"Log written to {log_path}")
    else:
        print("No repairs needed")
    
    return 0


def main(argv: List[str]) -> int:
    """Main entry point for memory CLI."""
    # Handle being called as 'arx memory <cmd>' or just 'memory <cmd>'
    if len(argv) > 0 and argv[0] == 'arx':
        argv = argv[1:]  # Strip 'arx'
    if len(argv) > 0 and argv[0] == 'memory':
        argv = argv[1:]  # Strip 'memory'
    
    if len(argv) < 1:
        print("Usage: arx memory <command> [args]")
        print("Commands:")
        print("  validate [path]  - Validate memory artifacts")
        print("  repair [path]    - Repair corrupted artifacts")
        return 1
    
    command = argv[0]
    args = argv[1:] if len(argv) > 1 else []
    
    if command == "validate":
        return validate_command(args)
    elif command == "repair":
        return repair_command(args)
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))