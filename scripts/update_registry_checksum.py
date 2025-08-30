#!/usr/bin/env python3
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / '.cursor/commands/registry.yaml'
OUT = ROOT / '.cursor/commands/registry.sha256'


def compute_sha256(path: Path) -> str:
	sha = hashlib.sha256()
	with path.open('rb') as f:
		for chunk in iter(lambda: f.read(8192), b''):
			sha.update(chunk)
	return sha.hexdigest()


def main() -> int:
	if not REG.exists():
		print('Registry not found:', REG)
		return 1
	digest = compute_sha256(REG)
	OUT.write_text(f"{digest}  registry.yaml\n", encoding='utf-8')
	print('Wrote checksum to', OUT)
	return 0


if __name__ == '__main__':
	exit(main())