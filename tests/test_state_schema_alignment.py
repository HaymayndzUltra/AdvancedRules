import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def test_workflow_state_matches_schema():
	# Ensure migration has been applied if needed
	from scripts.migrate_state import main as migrate_main
	migrate_main()
	schema = json.loads((ROOT / 'schemas/workflow_state.schema.json').read_text(encoding='utf-8'))
	state = json.loads((ROOT / 'workflow_state.json').read_text(encoding='utf-8'))
	jsonschema.validate(instance=state, schema=schema)


def test_migration_upgrades_legacy(tmp_path, monkeypatch):
	# prepare a legacy state without schema_version
	legacy = {
		"state": "PLANNING_DONE",
		"history": [{"ts": 1, "from": None, "to": "PLANNING_DONE"}]
	}
	state_file = ROOT / 'workflow_state.json'
	backup = state_file.read_text(encoding='utf-8')
	try:
		state_file.write_text(json.dumps(legacy, indent=2), encoding='utf-8')
		# run migration
		from scripts.migrate_state import main as migrate_main
		migrate_main()
		new_state = json.loads(state_file.read_text(encoding='utf-8'))
		assert 'schema_version' in new_state and 'last_updated' in new_state
	finally:
		state_file.write_text(backup, encoding='utf-8')