import json
from pathlib import Path

from tools.orchestrator.state import load_state, save_state, transition


def test_round_trip_and_version_bump(tmp_path, monkeypatch):
    # Point state to a temp file by monkeypatching module globals
    import tools.orchestrator.state as st
    st.STATE_FILE = tmp_path / "workflow_state.json"

    # Start with legacy state missing schema_version
    st.STATE_FILE.write_text(json.dumps({"state": "PLANNING_DONE", "history": []}, indent=2), encoding="utf-8")
    data = load_state()
    assert data.get("schema_version") is not None

    # Save and reload
    save_state(data)
    data2 = load_state()
    assert data2.get("schema_version") == data.get("schema_version")

    # Transition should append history and preserve version
    out = transition("AUDIT_DONE")
    assert out["new"] == "AUDIT_DONE"
    data3 = load_state()
    assert data3.get("schema_version") == data.get("schema_version")
    assert any(h.get("to") == "AUDIT_DONE" for h in data3.get("history", []))


def test_migration_script_creates_report(tmp_path, monkeypatch):
    # Use a temp root by adjusting paths in migrate module
    import tools.migrate.state_migrate as mig
    mig.ROOT = tmp_path
    mig.STATE = tmp_path / "workflow_state.json"
    mig.REPORT = tmp_path / "migration_report.json"

    mig.STATE.write_text(json.dumps({"state": "X", "history": []}, indent=2), encoding="utf-8")
    rc = mig.main()
    assert rc == 0
    rep = json.loads(mig.REPORT.read_text())
    assert "state" in rep
    assert rep["state"]["message"] in {"schema_version set", "no change"}
