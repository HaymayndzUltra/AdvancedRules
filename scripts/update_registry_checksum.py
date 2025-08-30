#!/usr/bin/env python3
"""Generate, update, or verify registry checksum for integrity verification."""

import hashlib
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / ".cursor/commands/registry.yaml"
CHECKSUM_FILE = ROOT / ".cursor/commands/registry.sha256"


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_checksum() -> str:
    """Generate checksum for the registry file."""
    if not REGISTRY.exists():
        print(f"❌ Registry file not found: {REGISTRY}")
        sys.exit(1)
    
    checksum = compute_sha256(REGISTRY)
    return checksum


def save_checksum(checksum: str) -> None:
    """Save checksum to file."""
    CHECKSUM_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKSUM_FILE.write_text(f"{checksum}  registry.yaml\n")
    print(f"✅ Checksum saved to {CHECKSUM_FILE}")
    print(f"   SHA-256: {checksum}")


def verify_checksum() -> bool:
    """Verify the registry checksum."""
    if not REGISTRY.exists():
        print(f"❌ Registry file not found: {REGISTRY}")
        return False
    
    if not CHECKSUM_FILE.exists():
        print(f"❌ Checksum file not found: {CHECKSUM_FILE}")
        print(f"   Run: python {__file__} --update")
        return False
    
    # Read expected checksum
    try:
        expected = CHECKSUM_FILE.read_text().strip().split()[0]
    except Exception as e:
        print(f"❌ Error reading checksum file: {e}")
        return False
    
    # Compute actual checksum
    actual = compute_sha256(REGISTRY)
    
    if actual == expected:
        print(f"✅ Registry checksum valid")
        print(f"   SHA-256: {actual}")
        return True
    else:
        print(f"❌ Registry checksum mismatch!")
        print(f"   Expected: {expected}")
        print(f"   Actual:   {actual}")
        print(f"   The registry may have been modified.")
        print(f"   To update checksum: python {__file__} --update")
        return False


def main():
    parser = argparse.ArgumentParser(description="Registry checksum management")
    parser.add_argument("--update", action="store_true", 
                       help="Generate and save new checksum")
    parser.add_argument("--verify", action="store_true",
                       help="Verify existing checksum")
    parser.add_argument("--show", action="store_true",
                       help="Show current checksum without verification")
    
    args = parser.parse_args()
    
    if args.update:
        checksum = generate_checksum()
        save_checksum(checksum)
        sys.exit(0)
    
    elif args.verify:
        if verify_checksum():
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.show:
        if CHECKSUM_FILE.exists():
            checksum = CHECKSUM_FILE.read_text().strip().split()[0]
            print(f"Current checksum: {checksum}")
        else:
            print("No checksum file found")
        sys.exit(0)
    
    else:
        # Default: update checksum
        checksum = generate_checksum()
        save_checksum(checksum)
        sys.exit(0)


if __name__ == "__main__":
    main()