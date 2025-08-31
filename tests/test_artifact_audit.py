#!/usr/bin/env python3
"""Tests for artifact auditing and tamper detection."""
import json
import os
import time
from pathlib import Path
import pytest


def test_artifact_hash_index_with_correlation(tmp_path, monkeypatch):
    """Test that artifacts are indexed with correlation IDs."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    index_file = mb / "artifacts_index.json"
    
    # Mock paths
    import tools.artifacts.hash_index as hash_mod
    import tools.runner.io_utils as io_utils
    
    monkeypatch.setattr(hash_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(hash_mod, 'INDEX', index_file)
    monkeypatch.setattr(io_utils, 'ROOT', tmp_path)
    monkeypatch.setattr(io_utils, 'MB', mb)
    
    # Set correlation ID in environment
    test_corr_id = "test-correlation-123"
    monkeypatch.setenv('CORRELATION_ID', test_corr_id)
    
    # Create and index an artifact
    test_file = mb / "test_artifact.txt"
    test_content = "Test content for hashing"
    
    from tools.runner.io_utils import write_text
    write_text(test_file, test_content, role="test")
    
    # Check index
    assert index_file.exists()
    index_data = json.loads(index_file.read_text())
    assert len(index_data) == 1
    
    entry = index_data[0]
    assert entry['correlation_id'] == test_corr_id
    assert entry['source_role'] == 'test'
    assert 'sha256' in entry
    assert entry['path'] == str(test_file.relative_to(tmp_path))


def test_tamper_detection(tmp_path, monkeypatch):
    """Test detection of tampered artifacts."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    index_file = mb / "artifacts_index.json"
    
    # Mock paths
    import tools.artifacts.hash_index as hash_mod
    import tools.artifacts.auditor as audit_mod
    
    monkeypatch.setattr(hash_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(hash_mod, 'INDEX', index_file)
    monkeypatch.setattr(audit_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(audit_mod, 'INDEX', index_file)
    
    # Create registry files to avoid registry check failures
    registry_dir = tmp_path / ".cursor/commands"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry_file = registry_dir / "registry.yaml"
    registry_file.write_text("test: true\n")
    
    # Create an artifact
    test_file = mb / "important_data.json"
    original_content = '{"value": 42}'
    test_file.write_text(original_content)
    
    # Record in index
    from tools.artifacts.hash_index import record
    record(test_file, "test", correlation_id="test-123")
    
    # Run audit - should be valid
    from tools.artifacts.auditor import audit_artifacts
    report = audit_artifacts(check_registry=False)
    
    assert report['summary']['valid'] == 1
    assert report['summary']['tampered'] == 0
    assert not report['tamper_detected']
    
    # Tamper with the file
    test_file.write_text('{"value": 999, "tampered": true}')
    
    # Run audit again - should detect tampering
    report = audit_artifacts(check_registry=False)
    
    assert report['summary']['valid'] == 0
    assert report['summary']['tampered'] == 1
    assert report['tamper_detected']
    
    # Check finding details
    tampered_finding = next(f for f in report['findings'] if f['finding_type'] == 'tampered')
    assert tampered_finding['path'] == str(test_file.relative_to(tmp_path))
    assert 'Hash mismatch' in tampered_finding['details']


def test_missing_artifact_detection(tmp_path, monkeypatch):
    """Test detection of missing artifacts."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    index_file = mb / "artifacts_index.json"
    
    # Mock paths
    import tools.artifacts.auditor as audit_mod
    monkeypatch.setattr(audit_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(audit_mod, 'INDEX', index_file)
    
    # Create index entry for non-existent file
    index_data = [{
        "path": "memory-bank/missing_file.txt",
        "sha256": "abc123",
        "created_at": time.time(),
        "source_role": "test",
        "correlation_id": "test-456"
    }]
    index_file.write_text(json.dumps(index_data))
    
    # Run audit
    from tools.artifacts.auditor import audit_artifacts
    report = audit_artifacts(check_registry=False)
    
    assert report['summary']['missing'] == 1
    assert report['summary']['valid'] == 0
    assert report['tamper_detected']  # Missing files count as tampering
    
    # Check finding
    missing_finding = report['findings'][0]
    assert missing_finding['finding_type'] == 'missing'
    assert missing_finding['correlation_id'] == 'test-456'


def test_registry_checksum_verification(tmp_path, monkeypatch):
    """Test registry checksum verification."""
    # Setup
    registry_dir = tmp_path / ".cursor/commands"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry_file = registry_dir / "registry.yaml"
    checksum_file = registry_dir / "registry.sha256"
    
    # Mock paths
    import tools.artifacts.auditor as audit_mod
    monkeypatch.setattr(audit_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(audit_mod, 'INDEX', tmp_path / "memory-bank/artifacts_index.json")
    
    # Create registry with known content
    registry_content = "test: registry\nversion: 1.0\n"
    registry_file.write_text(registry_content)
    
    # Compute and save correct checksum
    import hashlib
    h = hashlib.sha256()
    h.update(registry_content.encode())
    correct_hash = h.hexdigest()
    checksum_file.write_text(f"{correct_hash}  registry.yaml\n")
    
    # Run audit - should pass
    from tools.artifacts.auditor import verify_registry_checksum
    valid, error = verify_registry_checksum()
    assert valid
    assert error is None
    
    # Tamper with registry
    registry_file.write_text("tampered: true\n")
    
    # Run audit - should fail
    valid, error = verify_registry_checksum()
    assert not valid
    assert "Hash mismatch" in error


def test_correlation_linkage(tmp_path, monkeypatch):
    """Test that artifacts are properly linked by correlation ID."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    index_file = mb / "artifacts_index.json"
    
    # Mock paths
    import tools.artifacts.hash_index as hash_mod
    import tools.artifacts.auditor as audit_mod
    import tools.runner.io_utils as io_utils
    
    monkeypatch.setattr(hash_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(hash_mod, 'INDEX', index_file)
    monkeypatch.setattr(audit_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(audit_mod, 'INDEX', index_file)
    monkeypatch.setattr(io_utils, 'ROOT', tmp_path)
    monkeypatch.setattr(io_utils, 'MB', mb)
    
    # Create artifacts with same correlation ID
    corr_id = "workflow-789"
    monkeypatch.setenv('CORRELATION_ID', corr_id)
    
    from tools.runner.io_utils import write_text, touch_json
    
    write_text(mb / "step1.txt", "Step 1 output", role="planner")
    touch_json(mb / "config.json", {"step": 1}, role="planner")
    write_text(mb / "step2.txt", "Step 2 output", role="executor")
    
    # Get artifacts by correlation
    from tools.artifacts.auditor import get_artifacts_by_correlation
    artifacts = get_artifacts_by_correlation(corr_id)
    
    assert len(artifacts) == 3
    assert all(a['correlation_id'] == corr_id for a in artifacts)
    
    # Check roles are preserved
    roles = {a['source_role'] for a in artifacts}
    assert 'planner' in roles
    assert 'executor' in roles


def test_audit_report_generation(tmp_path, monkeypatch):
    """Test complete audit report generation."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    index_file = mb / "artifacts_index.json"
    report_file = mb / "artifact_audit_report.json"
    
    # Mock paths
    import tools.artifacts.hash_index as hash_mod
    import tools.artifacts.auditor as audit_mod
    
    monkeypatch.setattr(hash_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(hash_mod, 'INDEX', index_file)
    monkeypatch.setattr(audit_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(audit_mod, 'INDEX', index_file)
    monkeypatch.setattr(audit_mod, 'AUDIT_REPORT', report_file)
    
    # Create mixed artifacts (valid, tampered, missing)
    valid_file = mb / "valid.txt"
    valid_file.write_text("Valid content")
    
    tampered_file = mb / "tampered.txt"
    tampered_file.write_text("Original")
    
    # Record them
    from tools.artifacts.hash_index import record
    record(valid_file, "test", "corr-1")
    record(tampered_file, "test", "corr-2")
    
    # Add missing file to index
    index_data = json.loads(index_file.read_text())
    index_data.append({
        "path": "memory-bank/missing.txt",
        "sha256": "xyz789",
        "created_at": time.time(),
        "source_role": "test",
        "correlation_id": "corr-3"
    })
    index_file.write_text(json.dumps(index_data))
    
    # Tamper with one file
    tampered_file.write_text("Tampered content")
    
    # Run audit and save report
    from tools.artifacts.auditor import audit_artifacts, save_audit_report
    report = audit_artifacts(check_registry=False)
    save_audit_report(report)
    
    # Check report file
    assert report_file.exists()
    saved_report = json.loads(report_file.read_text())
    
    assert saved_report['summary']['total_artifacts'] == 3
    assert saved_report['summary']['valid'] == 1
    assert saved_report['summary']['tampered'] == 1
    assert saved_report['summary']['missing'] == 1
    assert saved_report['tamper_detected'] is True
    
    # Check correlation IDs are tracked
    assert len(saved_report['correlation_ids']) == 3
    assert set(saved_report['correlation_ids']) == {"corr-1", "corr-2", "corr-3"}