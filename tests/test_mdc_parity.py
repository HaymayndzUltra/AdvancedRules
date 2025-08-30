#!/usr/bin/env python3
"""Tests for MDC rule linting, indexing, and runtime parity."""
import json
import yaml
from pathlib import Path
import pytest
from unittest.mock import patch


def test_mdc_linter_detects_missing_frontmatter(tmp_path):
    """Test that linter detects missing frontmatter."""
    # Create test .mdc file without frontmatter
    mdc_file = tmp_path / "test.mdc"
    mdc_file.write_text("# Test Rule\nSome content here")
    
    from tools.rules.mdc_linter import lint_mdc_file
    
    issues, metadata = lint_mdc_file(mdc_file)
    
    assert len(issues) > 0
    assert any(i.category == "frontmatter" for i in issues)
    assert any("Missing or invalid YAML frontmatter" in i.message for i in issues)


def test_mdc_linter_detects_invalid_globs(tmp_path):
    """Test that linter detects invalid glob patterns."""
    # Create test .mdc file with invalid glob
    mdc_file = tmp_path / "test.mdc"
    content = """---
description: Test rule
globs:
  - "/**/**/"
  - "../outside"
alwaysApply: false
---
# Test Content
"""
    mdc_file.write_text(content)
    
    from tools.rules.mdc_linter import lint_mdc_file
    
    issues, metadata = lint_mdc_file(mdc_file)
    
    assert len(issues) >= 2
    assert any(i.category == "glob" for i in issues)
    assert any("Double wildcards" in i.message for i in issues)


def test_mdc_linter_extracts_metadata(tmp_path):
    """Test that linter correctly extracts rule metadata."""
    # Create test .mdc file with complete structure
    mdc_file = tmp_path / "test.mdc"
    content = """---
description: Test rule with complete metadata
globs:
  - "**/*.py"
  - "tests/**"
alwaysApply: true
---
# Test Rule

<rule>
name: test_gate
description: Test gate description
actions:
  - type: attach_rules
    rules:
      - "other_rule.mdc"
  - type: validate
gates: ["gate1", "gate2"]
</rule>

Required artifacts:
- memory-bank/test/artifact1.json
- memory-bank/test/artifact2.md
"""
    mdc_file.write_text(content)
    
    from tools.rules.mdc_linter import lint_mdc_file
    
    issues, metadata = lint_mdc_file(mdc_file)
    
    assert metadata is not None
    assert metadata.description == "Test rule with complete metadata"
    assert len(metadata.globs) == 2
    assert metadata.always_apply is True
    assert len(metadata.required_artifacts) >= 2
    assert len(metadata.gates) >= 2


def test_rules_index_generation(tmp_path, monkeypatch):
    """Test generation of rules index."""
    # Setup test rules directory
    rules_dir = tmp_path / ".cursor/rules"
    rules_dir.mkdir(parents=True)
    
    # Create test rules
    rule1 = rules_dir / "rule1.mdc"
    rule1.write_text("""---
description: Rule 1
globs: ["**/*.py"]
alwaysApply: false
---
# Rule 1
gates: ["gate1"]
Required: memory-bank/artifact1.json
""")
    
    rule2 = rules_dir / "rule2.mdc"
    rule2.write_text("""---
description: Rule 2
globs: ["tests/**"]
alwaysApply: true
---
# Rule 2
gates: ["gate2"]
Required: memory-bank/artifact2.json
""")
    
    # Mock paths
    import tools.rules.index_generator as idx_gen
    monkeypatch.setattr(idx_gen, 'ROOT', tmp_path)
    monkeypatch.setattr(idx_gen, 'RULES_DIR', rules_dir)
    
    from tools.rules.index_generator import build_rules_index
    
    index = build_rules_index()
    
    assert "rules" in index
    assert len(index["rules"]) == 2
    assert "rule1" in index["rules"]
    assert "rule2" in index["rules"]
    
    # Check always-apply tracking
    assert "rule2" in index["always_apply"]
    assert "rule1" not in index["always_apply"]
    
    # Check gate mappings
    assert "gate1" in index["gates"]
    assert "gate2" in index["gates"]
    
    # Check statistics
    assert index["statistics"]["total_rules"] == 2
    assert index["statistics"]["always_apply_count"] == 1


def test_gate_evaluator_consumes_rules_index(tmp_path, monkeypatch):
    """Test that gate evaluator uses rules index for validation."""
    # Setup
    mb = tmp_path / "memory-bank"
    mb.mkdir(parents=True)
    
    # Create rules index
    rules_index = {
        "rules": {
            "test_rule": {
                "gates": ["test_gate"],
                "required_artifacts": ["memory-bank/required.json"]
            }
        },
        "gates": {
            "test_gate": ["test_rule"]
        }
    }
    
    index_file = mb / "rules_index.json"
    index_file.write_text(json.dumps(rules_index))
    
    # Create registry with command requiring the gate
    registry_dir = tmp_path / ".cursor/commands"
    registry_dir.mkdir(parents=True)
    registry = {
        "version": "1.0",
        "commands": [{
            "id": "test-command",
            "requires": {
                "gates_passed_all_of": ["test_gate"]
            },
            "contexts": {}
        }]
    }
    registry_file = registry_dir / "registry.yaml"
    registry_file.write_text(yaml.dump(registry))
    
    # Mock paths
    import tools.gates.gate_evaluator as gate_eval
    monkeypatch.setattr(gate_eval, 'ROOT', tmp_path)
    monkeypatch.setattr(gate_eval, 'REG_PATH', registry_file)
    monkeypatch.setattr(gate_eval, 'STATE_PATH', tmp_path / "workflow_state.json")
    monkeypatch.setattr(gate_eval, 'ATTACH_LOG', tmp_path / "rule_attach_log.json")
    monkeypatch.setattr(gate_eval, 'OUT_PATH', mb / "gate_results.json")
    monkeypatch.setattr(gate_eval, 'RULES_INDEX', index_file)
    
    # Create empty state
    (tmp_path / "workflow_state.json").write_text('{"state": "ready"}')
    
    from tools.gates.gate_evaluator import evaluate_gates
    
    result = evaluate_gates()
    
    assert "results" in result
    assert len(result["results"]) == 1
    
    cmd_result = result["results"][0]
    assert cmd_result["command_id"] == "test-command"
    assert not cmd_result["passed"]  # Should fail due to missing artifact
    assert "memory-bank/required.json" in cmd_result["missing_files"]
    assert "test_gate" in cmd_result["missing_gates"]


def test_runtime_parity_check(tmp_path, monkeypatch):
    """Test runtime parity checking between docs and registry."""
    # Setup
    registry_dir = tmp_path / ".cursor/commands"
    registry_dir.mkdir(parents=True)
    
    # Create registry with runtime requirements
    registry = {
        "version": "1.0",
        "commands": [{
            "id": "cmd1",
            "contexts": {
                "must_exist": ["runtime/artifact1.json"],
                "gates": ["runtime_gate"]
            }
        }]
    }
    registry_file = registry_dir / "registry.yaml"
    registry_file.write_text(yaml.dump(registry))
    
    # Create rules index with documented requirements
    rules_index = {
        "rules": {
            "doc_rule": {
                "required_artifacts": ["docs/artifact1.json", "runtime/artifact1.json"],
                "gates": ["doc_gate", "runtime_gate"]
            }
        },
        "gates": {
            "doc_gate": ["doc_rule"],
            "runtime_gate": ["doc_rule"]
        },
        "artifacts": {}
    }
    
    # Mock paths
    import tools.rules.index_generator as idx_gen
    monkeypatch.setattr(idx_gen, 'ROOT', tmp_path)
    
    from tools.rules.index_generator import check_runtime_parity
    
    parity = check_runtime_parity(rules_index)
    
    assert "matches" in parity
    assert "missing_in_runtime" in parity
    assert "missing_in_docs" in parity
    
    # Check matches
    assert "runtime/artifact1.json" in parity["matches"]["artifacts"]
    assert "runtime_gate" in parity["matches"]["gates"]
    
    # Check mismatches
    assert "docs/artifact1.json" in parity["missing_in_runtime"]["artifacts"]
    assert "doc_gate" in parity["missing_in_runtime"]["gates"]
    
    # Check parity score
    assert "parity_score" in parity
    assert 0 <= parity["parity_score"] <= 1


def test_attachment_consumption(tmp_path, monkeypatch):
    """Test that rule attachments are properly consumed."""
    # Setup
    rules_dir = tmp_path / ".cursor/rules"
    rules_dir.mkdir(parents=True)
    
    # Create main rule with attachment
    main_rule = rules_dir / "main.mdc"
    main_rule.write_text("""---
description: Main rule
globs: ["**"]
---
<rule>
name: main_rule
actions:
  - type: attach_rules
    rules:
      - "attached.mdc"
</rule>
""")
    
    # Create attached rule
    attached_rule = rules_dir / "attached.mdc"
    attached_rule.write_text("""---
description: Attached rule
globs: ["**/*.py"]
---
Required: memory-bank/attached_artifact.json
""")
    
    # Mock paths
    import tools.rules.index_generator as idx_gen
    monkeypatch.setattr(idx_gen, 'ROOT', tmp_path)
    monkeypatch.setattr(idx_gen, 'RULES_DIR', rules_dir)
    
    from tools.rules.index_generator import build_rules_index
    
    index = build_rules_index()
    
    assert "main" in index["rules"]
    assert "attached" in index["rules"]
    
    # Check attachment tracking
    assert "main" in index.get("attachments", {})
    assert "attached.mdc" in index["attachments"]["main"]
    
    # Check that attached rule's artifacts are indexed
    attached_artifacts = index["rules"]["attached"]["required_artifacts"]
    assert "memory-bank/attached_artifact.json" in attached_artifacts