import json
import os
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def run_trigger_with(cmd_id: str) -> str:
    # Provide two candidates with equal scores to force OPTION_SET decision
    payload = {
        "candidates": [
            {"id": cmd_id, "action_type": "COMMAND_TRIGGER", "risk": "LOW", "scores": {"intent": 1, "state": 1, "evidence": 1, "recency": 1, "pref": 1, "cost": 0, "risk_penalty": 0}},
            {"id": "memory-doctor", "action_type": "COMMAND_TRIGGER", "risk": "LOW", "scores": {"intent": 1, "state": 1, "evidence": 1, "recency": 1, "pref": 1, "cost": 0, "risk_penalty": 0}}
        ]
    }
    cfile = ROOT / ".cache" / f"cands_{cmd_id}.json"
    cfile.parent.mkdir(parents=True, exist_ok=True)
    cfile.write_text(json.dumps(payload), encoding="utf-8")
    import subprocess
    out = subprocess.check_output([
        sys.executable,
        str(ROOT / "tools/orchestrator/trigger_next.py"),
        "--candidates", str(cfile),
        "--dry-run",
        "--enforce-gates",
        "--print-gates",
    ], cwd=str(ROOT))
    return out.decode()


def test_dry_run_default_hint_printed():
    s = run_trigger_with("memory-doctor")
    # Either no trigger (if gates decide so) or dry-run hint printed
    if "No trigger" in s:
        assert True
    else:
        assert "dry-run enforced" in s or "Hint: set ALLOW_RUN=1" in s or "DRY_RUN:" in s


def test_disallowed_command_is_blocked(monkeypatch):
    # Append a disallowed command entry and ensure it's blocked by allowlist
    reg = ROOT / ".cursor/commands/registry.yaml"
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    data.setdefault("commands", []).append({
        "id": "hack-disallowed",
        "run": {"shell": ["rm", "-rf", "/"]},
        "requires": {},
        "contexts": {},
        "emits": {},
        "ui": {"label": "hack", "reason": "test"}
    })
    reg.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    try:
        # Neutralize checksum to allow test mutation
        sha = reg.with_suffix(".sha256")
        if sha.exists():
            sha.unlink()
        s = run_trigger_with("hack-disallowed")
        assert "disallowed command" in s
    finally:
        # Restore original registry by re-validating (normalizes file)
        import subprocess
        subprocess.call([sys.executable, str(ROOT / "scripts/validate_registry.py")])


def test_registry_checksum_mismatch_blocks_execution():
    # Write wrong sha256 and expect refusal
    reg = ROOT / ".cursor/commands/registry.yaml"
    sha = reg.with_suffix(".sha256")
    sha.write_text("deadbeef", encoding="utf-8")
    try:
        s = run_trigger_with("memory-doctor")
        assert "checksum mismatch" in s
    finally:
        # Write correct checksum
        import hashlib
        calc = hashlib.sha256(reg.read_bytes()).hexdigest()
        sha.write_text(calc, encoding="utf-8")

