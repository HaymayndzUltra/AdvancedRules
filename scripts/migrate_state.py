#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'workflow_state.json'
REPORT = ROOT / 'reports/migration_report.json'
SCHEMA_VERSION = '1.0.0'


def load_state():
	try:
		return json.loads(STATE.read_text(encoding='utf-8'))
	except Exception:
		return {}


def migrate(data: dict) -> dict:
	changed = False
	if 'schema_version' not in data:
		data['schema_version'] = SCHEMA_VERSION
		changed = True
	if 'history' in data:
		for h in data['history']:
			if 'correlation_id' not in h:
				h['correlation_id'] = None
				changed = True
	# last_updated always refreshed
	data['last_updated'] = datetime.utcnow().isoformat()
	return data, changed


def main() -> int:
	data = load_state()
	new_data, changed = migrate(data)
	if changed:
		STATE.write_text(json.dumps(new_data, indent=2), encoding='utf-8')
	report = {
		"changed": changed,
		"schema_version": new_data.get('schema_version'),
		"last_updated": new_data.get('last_updated'),
		"history_items": len(new_data.get('history', []))
	}
	reports_dir = REPORT.parent
	reports_dir.mkdir(parents=True, exist_ok=True)
	REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
	print(json.dumps(report, indent=2))
	return 0


if __name__ == '__main__':
	exit(main())