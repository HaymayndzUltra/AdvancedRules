#!/usr/bin/env python3
"""Tests for postrun consistency scanner."""
import json
import yaml
import time
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock


def test_registry_alignment_check(tmp_path, monkeypatch):
    """Test that executed commands are validated against registry."""
    # Setup
    registry_file = tmp_path / ".cursor/commands/registry.yaml"
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create registry with test commands
    registry_data = {
        "version": "1.0",
        "commands": [
            {
                "id": "test-command",
                "trigger": "run_test",
                "emits": {
                    "sets_state": "TEST_DONE"
                }
            }
        ]
    }
    registry_file.write_text(yaml.dump(registry_data))
    
    # Create execution events
    events = [
        {"type": "command_executed", "command_id": "test-command", "correlation_id": "corr-1"},
        {"type": "command_executed", "command_id": "unknown-command", "correlation_id": "corr-2"}
    ]
    
    # Mock paths
    import tools.postrun.scanner as scanner
    monkeypatch.setattr(scanner, 'ROOT', tmp_path)
    monkeypatch.setattr(scanner, 'REGISTRY', registry_file)
    
    # Load registry and check alignment
    registry = scanner.load_registry()
    issues = scanner.check_registry_alignment(events, registry)
    
    assert len(issues) == 1
    assert issues[0].category == "registry"
    assert issues[0].severity == "error"
    assert "unknown-command" in issues[0].message


def test_schema_compliance_check(tmp_path, monkeypatch):
    """Test that decision candidates are validated against canonical schema."""
    # Create decisions with mixed schemas
    decisions = [
        {
            "correlation_id": "corr-1",
            "candidates": [
                {
                    "id": "valid_candidate",
                    "action_type": "COMMAND_TRIGGER",
                    "scores": {
                        "intent": 0.9,
                        "state": 0.8,
                        "evidence": 0.7,
                        "recency": 0.6,
                        "preference": 0.5
                    }
                }
            ]
        },
        {
            "correlation_id": "corr-2",
            "candidates": [
                {
                    "id": "legacy_candidate",
                    "action_type": "NATURAL_STEP",
                    "metrics": {  # Using legacy field name
                        "intent": 0.9,
                        "state": 0.8,
                        "evidence": 0.7,
                        "recency": 0.6,
                        "preference": 0.5
                    }
                }
            ]
        },
        {
            "correlation_id": "corr-3",
            "candidates": [
                {
                    "id": "invalid_candidate",
                    "action_type": "COMMAND_TRIGGER"
                    # Missing scores/metrics entirely
                }
            ]
        }
    ]
    
    import tools.postrun.scanner as scanner
    
    issues = scanner.check_schema_compliance(decisions)
    
    # Should have warning for legacy and error for invalid
    assert len(issues) >= 2
    
    # Check for legacy warning
    legacy_issues = [i for i in issues if "legacy" in i.message]
    assert len(legacy_issues) == 1
    assert legacy_issues[0].severity == "warning"
    
    # Check for missing scores error
    invalid_issues = [i for i in issues if "invalid_candidate" in i.message]
    assert len(invalid_issues) == 1
    assert invalid_issues[0].severity == "error"


def test_emits_verification(tmp_path, monkeypatch):
    """Test that declared emits are verified to exist."""
    # Setup
    registry_file = tmp_path / ".cursor/commands/registry.yaml"
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    state_file = tmp_path / "workflow_state.json"
    artifacts_file = tmp_path / "memory-bank/artifacts_index.json"
    artifacts_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create registry with emits
    registry_data = {
        "commands": [
            {
                "id": "test-cmd-1",
                "emits": {
                    "sets_state": "STATE_A",
                    "add_completed_step": "step_1",
                    "creates_artifact": "memory-bank/test.json"
                }
            }
        ]
    }
    registry_file.write_text(yaml.dump(registry_data))
    
    # Create state showing emit was honored
    state_data = {
        "state": "STATE_A",
        "completed_steps": ["step_1"],
        "history": [
            {"from": None, "to": "STATE_A", "timestamp": time.time()}
        ]
    }
    state_file.write_text(json.dumps(state_data))
    
    # Create artifacts index
    artifacts_data = [
        {"path": "memory-bank/test.json", "sha256": "abc123"}
    ]
    artifacts_file.write_text(json.dumps(artifacts_data))
    
    # Create execution event
    executions = [
        {"command_id": "test-cmd-1", "correlation_id": "corr-1"}
    ]
    
    # Mock paths
    import tools.postrun.scanner as scanner
    monkeypatch.setattr(scanner, 'ROOT', tmp_path)
    monkeypatch.setattr(scanner, 'REGISTRY', registry_file)
    monkeypatch.setattr(scanner, 'WORKFLOW_STATE', state_file)
    monkeypatch.setattr(scanner, 'ARTIFACTS_INDEX', artifacts_file)
    
    # Load data and check
    registry = scanner.load_registry()
    state = scanner.load_workflow_state()
    artifacts = scanner.load_artifacts_index()
    
    issues = scanner.check_emits_created(executions, registry, state, artifacts)
    
    # Should have no issues - all emits were created
    assert len(issues) == 0


def test_missing_emits_detection(tmp_path, monkeypatch):
    """Test detection of missing emits."""
    # Setup similar to above but with missing emits
    registry_file = tmp_path / ".cursor/commands/registry.yaml"
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    state_file = tmp_path / "workflow_state.json"
    artifacts_file = tmp_path / "memory-bank/artifacts_index.json"
    artifacts_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Registry declares emits
    registry_data = {
        "commands": [
            {
                "id": "test-cmd-2",
                "emits": {
                    "sets_state": "EXPECTED_STATE",
                    "add_completed_step": "expected_step",
                    "creates_artifact": "memory-bank/expected.json"
                }
            }
        ]
    }
    registry_file.write_text(yaml.dump(registry_data))
    
    # State doesn't have the expected values
    state_data = {
        "state": "DIFFERENT_STATE",
        "completed_steps": ["other_step"],
        "history": []
    }
    state_file.write_text(json.dumps(state_data))
    
    # Artifacts don't include expected file
    artifacts_data = [
        {"path": "memory-bank/other.json", "sha256": "xyz789"}
    ]
    artifacts_file.write_text(json.dumps(artifacts_data))
    
    # Execution event
    executions = [
        {"command_id": "test-cmd-2", "correlation_id": "corr-2"}
    ]
    
    # Mock paths
    import tools.postrun.scanner as scanner
    monkeypatch.setattr(scanner, 'ROOT', tmp_path)
    monkeypatch.setattr(scanner, 'REGISTRY', registry_file)
    monkeypatch.setattr(scanner, 'WORKFLOW_STATE', state_file)
    monkeypatch.setattr(scanner, 'ARTIFACTS_INDEX', artifacts_file)
    
    # Check
    registry = scanner.load_registry()
    state = scanner.load_workflow_state()
    artifacts = scanner.load_artifacts_index()
    
    issues = scanner.check_emits_created(executions, registry, state, artifacts)
    
    # Should have issues for all missing emits
    assert len(issues) >= 2  # At least state and artifact issues
    
    state_issues = [i for i in issues if "EXPECTED_STATE" in str(i.expected)]
    assert len(state_issues) == 1
    
    artifact_issues = [i for i in issues if "expected.json" in str(i.expected)]
    assert len(artifact_issues) == 1


def test_evidence_linkage_check(tmp_path, monkeypatch):
    """Test that evidence paths in decisions are validated."""
    # Create test files
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    
    # Create one evidence file
    (mb / "exists.json").write_text("{}")
    
    # Create artifacts index with the existing file
    artifacts = [
        {"path": "memory-bank/exists.json", "sha256": "abc"}
    ]
    
    # Create decisions with evidence paths
    decisions = [
        {
            "correlation_id": "corr-1",
            "context": {
                "evidence_paths": [
                    "file://memory-bank/exists.json",  # Valid
                    "file://memory-bank/missing.json",  # Invalid
                    "tool://some/tool.py"  # Not a file, should be ignored
                ]
            }
        }
    ]
    
    # Mock paths
    import tools.postrun.scanner as scanner
    monkeypatch.setattr(scanner, 'ROOT', tmp_path)
    
    issues = scanner.check_evidence_linkage(decisions, artifacts)
    
    # Should have one issue for missing file
    assert len(issues) == 1
    assert issues[0].category == "evidence"
    assert "missing.json" in issues[0].message


def test_orphaned_artifacts_detection(tmp_path):
    """Test detection of orphaned artifacts."""
    # Create artifacts with and without correlation IDs
    artifacts = [
        {"path": "artifact1.json", "correlation_id": "corr-1"},
        {"path": "artifact2.json", "correlation_id": "corr-2"},
        {"path": "orphaned1.json", "correlation_id": None},
        {"path": "orphaned2.json", "correlation_id": "corr-999"}  # Not in events
    ]
    
    # Create events with correlation IDs
    events = [
        {"type": "some_event", "correlation_id": "corr-1"},
        {"type": "other_event", "correlation_id": "corr-2"}
    ]
    
    import tools.postrun.scanner as scanner
    
    orphaned = scanner.find_orphaned_artifacts(artifacts, events)
    
    assert len(orphaned) == 2
    assert "orphaned1.json" in orphaned
    assert "orphaned2.json" in orphaned


def test_full_postrun_scan(tmp_path, monkeypatch):
    """Test complete postrun consistency scan."""
    # Setup all required files
    registry_file = tmp_path / ".cursor/commands/registry.yaml"
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    events_file = tmp_path / "logs/events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    traces_file = tmp_path / "logs/decision_traces.jsonl"
    traces_file.parent.mkdir(parents=True, exist_ok=True)
    state_file = tmp_path / "workflow_state.json"
    artifacts_file = tmp_path / "memory-bank/artifacts_index.json"
    artifacts_file.parent.mkdir(parents=True, exist_ok=True)
    report_file = tmp_path / "memory-bank/postrun_consistency.json"
    
    # Create minimal valid data
    registry_data = {
        "commands": [
            {"id": "test-cmd", "emits": {"sets_state": "DONE"}}
        ]
    }
    registry_file.write_text(yaml.dump(registry_data))
    
    events_data = [
        {"type": "command_executed", "command_id": "test-cmd", "correlation_id": "c1"}
    ]
    for event in events_data:
        events_file.write_text(json.dumps(event) + "\n")
    
    traces_data = [
        {
            "correlation_id": "c1",
            "candidates": [{
                "id": "test",
                "action_type": "COMMAND",
                "scores": {
                    "intent": 0.5,
                    "state": 0.5,
                    "evidence": 0.5,
                    "recency": 0.5,
                    "preference": 0.5
                }
            }]
        }
    ]
    for trace in traces_data:
        traces_file.write_text(json.dumps(trace) + "\n")
    
    state_data = {"state": "DONE", "history": [{"to": "DONE"}]}
    state_file.write_text(json.dumps(state_data))
    
    artifacts_file.write_text("[]")
    
    # Mock paths
    import tools.postrun.scanner as scanner
    monkeypatch.setattr(scanner, 'ROOT', tmp_path)
    monkeypatch.setattr(scanner, 'REGISTRY', registry_file)
    monkeypatch.setattr(scanner, 'EVENTS_LOG', events_file)
    monkeypatch.setattr(scanner, 'DECISION_TRACES', traces_file)
    monkeypatch.setattr(scanner, 'WORKFLOW_STATE', state_file)
    monkeypatch.setattr(scanner, 'ARTIFACTS_INDEX', artifacts_file)
    monkeypatch.setattr(scanner, 'POSTRUN_REPORT', report_file)
    
    # Run scan
    report = scanner.scan_postrun_consistency()
    
    assert report.total_executions == 1
    assert report.passed  # Should pass with valid data
    assert report.consistency_score > 0
    
    # Save and verify report file
    scanner.save_report(report)
    assert report_file.exists()
    
    saved_report = json.loads(report_file.read_text())
    assert saved_report['passed'] == True