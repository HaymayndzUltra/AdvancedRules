import os
import json
from pathlib import Path
import subprocess

from tools.orchestrator.trigger_next import is_command_allowed, should_dry_run, verify_registry_checksum

ROOT = Path(__file__).resolve().parents[1]


def test_allowlist_blocks_unknown_program():
	ok, reason = is_command_allowed(["bash", "-c", "rm -rf /"])
	assert not ok and 'allowlist' in reason


def test_allowlist_allows_arx():
	ok, reason = is_command_allowed(["arx", "memory", "stats"])
	assert ok


def test_dry_run_default_policy(monkeypatch):
	monkeypatch.delenv("ALLOW_RUN", raising=False)
	assert should_dry_run(False) is True
	monkeypatch.setenv("ALLOW_RUN", "1")
	assert should_dry_run(False) is False


def test_checksum_verification(monkeypatch):
	ok, msg = verify_registry_checksum()
	assert ok, msg
	# Corrupt checksum then test failure
	sha = ROOT / '.cursor/commands/registry.sha256'
	orig = sha.read_text(encoding='utf-8')
	try:
		sha.write_text('deadbeef registry.yaml\n', encoding='utf-8')
		ok2, msg2 = verify_registry_checksum()
		assert not ok2
	finally:
		sha.write_text(orig, encoding='utf-8')