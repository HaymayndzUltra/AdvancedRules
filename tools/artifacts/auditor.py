#!/usr/bin/env python3
"""Artifact auditor for tamper detection and provenance verification."""
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "memory-bank/artifacts_index.json"
AUDIT_REPORT = ROOT / "memory-bank/artifact_audit_report.json"


@dataclass
class AuditFinding:
    """Represents an audit finding for an artifact."""
    path: str
    finding_type: str  # "missing", "tampered", "valid", "registry_mismatch"
    expected_hash: Optional[str]
    actual_hash: Optional[str]
    correlation_id: Optional[str]
    details: str


def compute_hash(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_registry_checksum() -> Tuple[bool, Optional[str]]:
    """Verify registry checksum matches stored value."""
    registry_path = ROOT / ".cursor/commands/registry.yaml"
    checksum_path = ROOT / ".cursor/commands/registry.sha256"
    
    if not registry_path.exists():
        return False, "Registry file not found"
    
    if not checksum_path.exists():
        return False, "Checksum file not found"
    
    try:
        expected_hash = checksum_path.read_text().strip().split()[0]
        actual_hash = compute_hash(registry_path)
        
        if expected_hash != actual_hash:
            return False, f"Hash mismatch: expected {expected_hash}, got {actual_hash}"
        
        return True, None
    except Exception as e:
        return False, f"Error verifying checksum: {e}"


def load_artifact_index() -> List[Dict]:
    """Load the artifact index."""
    if not INDEX.exists():
        return []
    
    try:
        from tools.io.safe_read import safe_read_json
        data = safe_read_json(INDEX)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def audit_artifacts(check_registry: bool = True) -> Dict:
    """Audit all artifacts against the hash index."""
    findings: List[AuditFinding] = []
    stats = {
        "total_indexed": 0,
        "valid": 0,
        "tampered": 0,
        "missing": 0,
        "registry_valid": False,
        "correlation_ids": set()
    }
    
    # Check registry first if requested
    if check_registry:
        registry_valid, registry_error = verify_registry_checksum()
        stats["registry_valid"] = registry_valid
        
        if not registry_valid:
            findings.append(AuditFinding(
                path=".cursor/commands/registry.yaml",
                finding_type="registry_mismatch",
                expected_hash=None,
                actual_hash=None,
                correlation_id=None,
                details=registry_error or "Registry checksum verification failed"
            ))
    
    # Load and audit artifacts
    index = load_artifact_index()
    stats["total_indexed"] = len(index)
    
    for entry in index:
        path_str = entry.get("path", "")
        expected_hash = entry.get("sha256")
        correlation_id = entry.get("correlation_id")
        
        if correlation_id:
            stats["correlation_ids"].add(correlation_id)
        
        # Resolve path
        if path_str.startswith("/"):
            artifact_path = Path(path_str)
        else:
            artifact_path = ROOT / path_str
        
        # Check if file exists
        if not artifact_path.exists():
            findings.append(AuditFinding(
                path=path_str,
                finding_type="missing",
                expected_hash=expected_hash,
                actual_hash=None,
                correlation_id=correlation_id,
                details="Artifact file not found"
            ))
            stats["missing"] += 1
            continue
        
        # Verify hash
        try:
            actual_hash = compute_hash(artifact_path)
            
            if actual_hash == expected_hash:
                findings.append(AuditFinding(
                    path=path_str,
                    finding_type="valid",
                    expected_hash=expected_hash,
                    actual_hash=actual_hash,
                    correlation_id=correlation_id,
                    details="Hash matches"
                ))
                stats["valid"] += 1
            else:
                findings.append(AuditFinding(
                    path=path_str,
                    finding_type="tampered",
                    expected_hash=expected_hash,
                    actual_hash=actual_hash,
                    correlation_id=correlation_id,
                    details="Hash mismatch - possible tampering"
                ))
                stats["tampered"] += 1
                
        except Exception as e:
            findings.append(AuditFinding(
                path=path_str,
                finding_type="error",
                expected_hash=expected_hash,
                actual_hash=None,
                correlation_id=correlation_id,
                details=f"Error computing hash: {e}"
            ))
    
    # Convert set to list for JSON serialization
    stats["correlation_ids"] = list(stats["correlation_ids"])
    
    # Generate report
    report = {
        "audit_timestamp": time.time(),
        "summary": {
            "total_artifacts": stats["total_indexed"],
            "valid": stats["valid"],
            "tampered": stats["tampered"],
            "missing": stats["missing"],
            "registry_valid": stats["registry_valid"],
            "unique_correlations": len(stats["correlation_ids"])
        },
        "correlation_ids": stats["correlation_ids"],
        "findings": [asdict(f) for f in findings],
        "tamper_detected": stats["tampered"] > 0 or stats["missing"] > 0 or (check_registry and not stats["registry_valid"])
    }
    
    return report


def save_audit_report(report: Dict) -> None:
    """Save audit report to file."""
    from tools.io.fs import atomic_write_text
    AUDIT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(AUDIT_REPORT, json.dumps(report, indent=2))


def get_artifacts_by_correlation(correlation_id: str) -> List[Dict]:
    """Get all artifacts associated with a correlation ID."""
    index = load_artifact_index()
    return [
        entry for entry in index 
        if entry.get("correlation_id") == correlation_id
    ]


def main():
    """Run artifact audit and save report."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Audit artifacts for tampering")
    parser.add_argument("--correlation-id", help="Filter by correlation ID")
    parser.add_argument("--skip-registry", action="store_true", help="Skip registry check")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    if args.correlation_id:
        # Show artifacts for specific correlation
        artifacts = get_artifacts_by_correlation(args.correlation_id)
        if args.json:
            print(json.dumps(artifacts, indent=2))
        else:
            print(f"Found {len(artifacts)} artifacts for correlation {args.correlation_id}:")
            for a in artifacts:
                print(f"  - {a['path']} ({a['sha256'][:8]}...)")
    else:
        # Run full audit
        report = audit_artifacts(check_registry=not args.skip_registry)
        save_audit_report(report)
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Artifact Audit Report")
            print(f"====================")
            print(f"Total artifacts: {report['summary']['total_artifacts']}")
            print(f"Valid: {report['summary']['valid']}")
            print(f"Tampered: {report['summary']['tampered']}")
            print(f"Missing: {report['summary']['missing']}")
            print(f"Registry valid: {report['summary']['registry_valid']}")
            print(f"Unique correlations: {report['summary']['unique_correlations']}")
            
            if report['tamper_detected']:
                print("\n⚠️  TAMPER DETECTED!")
                for f in report['findings']:
                    if f['finding_type'] in ['tampered', 'registry_mismatch']:
                        print(f"  - {f['path']}: {f['details']}")
            else:
                print("\n✅ No tampering detected")
            
            print(f"\nReport saved to: {AUDIT_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()