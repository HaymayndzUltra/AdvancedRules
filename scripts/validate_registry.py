#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

try:
	import yaml
	from jsonschema import Draft202012Validator
except Exception as e:
	print(f"Missing dependencies: {e}. Install with: pip install --break-system-packages pyyaml jsonschema")
	sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / ".cursor/commands/registry.yaml"
SCHEMA_PATH = ROOT / "schemas/registry.schema.json"
REPORT_PATH = ROOT / "reports/registry_report.json"


def normalize_id(raw_id: str) -> str:
	"""Normalize IDs to ASCII kebab-case (letters, digits, hyphen)."""
	# Replace unicode arrows and spaces with hyphen
	ascii_id = (
		raw_id.replace("→", "-")
		.replace("→", "-")
		.replace(" ", "-")
		.replace("_", "-")
	)
	# Lowercase and keep only allowed chars
	ascii_id = ascii_id.lower()
	ascii_id = re.sub(r"[^a-z0-9-]", "", ascii_id)
	# Collapse multiple hyphens
	ascii_id = re.sub(r"-+", "-", ascii_id).strip("-")
	return ascii_id


def load_yaml(path: Path) -> dict:
	if not path.exists():
		raise FileNotFoundError(f"Registry file not found: {path}")
	with path.open("r", encoding="utf-8") as f:
		content = f.read()
		# Strip heredoc preface if someone reintroduces it
		if content.startswith("cat >"):
			lines = content.splitlines()
			start_index = 0
			for i, line in enumerate(lines):
				if line.strip().startswith("version:"):
					start_index = i
					break
			content = "\n".join(lines[start_index:])
		return yaml.safe_load(content)


def validate_registry(registry: dict, schema: dict) -> dict:
	validator = Draft202012Validator(schema)
	errors = []
	for error in sorted(validator.iter_errors(registry), key=str):
		errors.append({
			"path": "/" + "/".join(map(str, error.path)),
			"message": error.message,
			"validator": error.validator,
		})
	return {"valid": len(errors) == 0, "errors": errors}


def build_report(registry: dict, validation: dict) -> dict:
	commands = registry.get("commands", [])
	id_set = set()
	entries = []
	for cmd in commands:
		raw_id = str(cmd.get("id", ""))
		norm = normalize_id(raw_id)
		dup = norm in id_set
		id_set.add(norm)
		entries.append({
			"raw_id": raw_id,
			"normalized_id": norm,
			"duplicate": dup,
			"trigger": cmd.get("trigger"),
			"shell": cmd.get("run", {}).get("shell", []),
		})

	return {
		"summary": {
			"valid": validation["valid"],
			"error_count": len(validation["errors"]),
			"unique_ids": len(id_set),
			"total_commands": len(commands),
		},
		"validation_errors": validation["errors"],
		"commands": entries,
	}


def main() -> int:
	try:
		registry = load_yaml(REG_PATH)
		schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
		validation = validate_registry(registry, schema)
		report = build_report(registry, validation)
		REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
		REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
		print(json.dumps(report["summary"], indent=2))
		return 0 if report["summary"]["valid"] else 1
	except Exception as e:
		print(f"Registry validation failed: {e}")
		return 2


if __name__ == "__main__":
	sys.exit(main())