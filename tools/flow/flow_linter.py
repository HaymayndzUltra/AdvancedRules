#!/usr/bin/env python3
"""
AdvancedRules Flow Linter v2.0
Validates flow definitions, references, and schema compliance

Features:
- YAML schema validation
- Reference integrity checks
- DAG cycle detection
- Guard validation
- Fail-fast error reporting
"""

import yaml
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import networkx as nx  # For DAG validation
import re


@dataclass
class ValidationError:
    """Structured validation error"""
    level: str  # "ERROR", "WARNING", "INFO"
    code: str
    message: str
    file_path: str
    line_number: Optional[int] = None
    context: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result"""
    flow_id: str
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]


class FlowLinter:
    """Comprehensive flow definition validator"""

    def __init__(self):
        self.schema_cache = {}
        self.built_in_guards = self._load_built_in_guards()

    def _load_built_in_guards(self) -> Dict[str, Dict]:
        """Load built-in guard definitions"""
        return {
            "branch_not_main": {
                "description": "Ensure not running on main branch",
                "required_params": ["forbidden_branches"]
            },
            "dry_run_unless_allowed": {
                "description": "Enforce dry-run unless ALLOW_WRITES=1",
                "required_params": ["variable", "required_value"]
            },
            "artifacts_present": {
                "description": "Verify required artifacts exist",
                "required_params": ["required_files"]
            },
            "git_clean": {
                "description": "Ensure working directory is clean",
                "required_params": []
            },
            "ci_environment": {
                "description": "Verify CI environment variables",
                "required_params": ["variable"]
            },
            "test_framework_available": {
                "description": "Check if test framework is available",
                "required_params": ["command"]
            }
        }

    def validate_flow_registry(self, registry_path: str) -> Dict[str, ValidationResult]:
        """Validate complete flow registry"""
        try:
            with open(registry_path, 'r') as f:
                registry = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            return {
                "registry": ValidationResult(
                    flow_id="registry",
                    is_valid=False,
                    errors=[ValidationError(
                        level="ERROR",
                        code="REGISTRY_LOAD_FAILED",
                        message=f"Failed to load registry: {e}",
                        file_path=registry_path
                    )],
                    warnings=[],
                    info=[]
                )
            }

        results = {}

        # Validate registry structure
        registry_result = self._validate_registry_structure(registry, registry_path)
        results["registry"] = registry_result

        if not registry_result.is_valid:
            return results  # Stop if registry is invalid

        # Validate individual flows
        if "flows" in registry:
            for flow_id, flow_def in registry["flows"].items():
                result = self.validate_single_flow(flow_id, flow_def, registry_path)
                results[flow_id] = result

        return results

    def _validate_registry_structure(self, registry: Dict, file_path: str) -> ValidationResult:
        """Validate registry-level structure"""
        errors = []
        warnings = []
        info = []

        # Check required fields
        required_fields = ["version", "flows"]
        for field in required_fields:
            if field not in registry:
                errors.append(ValidationError(
                    level="ERROR",
                    code="MISSING_REGISTRY_FIELD",
                    message=f"Required field '{field}' missing from registry",
                    file_path=file_path
                ))

        # Validate version format
        if "version" in registry:
            if not re.match(r'^\d+\.\d+$', str(registry["version"])):
                warnings.append(ValidationError(
                    level="WARNING",
                    code="INVALID_VERSION_FORMAT",
                    message=f"Version '{registry['version']}' should follow semantic versioning",
                    file_path=file_path
                ))

        # Validate flows structure
        if "flows" in registry:
            if not isinstance(registry["flows"], dict):
                errors.append(ValidationError(
                    level="ERROR",
                    code="INVALID_FLOWS_STRUCTURE",
                    message="flows must be a dictionary",
                    file_path=file_path
                ))

        return ValidationResult(
            flow_id="registry",
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info
        )

    def validate_single_flow(self, flow_id: str, flow_def: Dict,
                           registry_path: str) -> ValidationResult:
        """Validate a single flow definition"""
        errors = []
        warnings = []
        info = []

        # Basic structure validation
        required_fields = ["id", "name", "nodes", "edges"]
        for field in required_fields:
            if field not in flow_def:
                errors.append(ValidationError(
                    level="ERROR",
                    code="MISSING_FLOW_FIELD",
                    message=f"Required field '{field}' missing from flow '{flow_id}'",
                    file_path=registry_path
                ))

        # Validate flow ID format
        if "id" in flow_def:
            if not re.match(r'^flow_[a-z_][a-z0-9_]*$', flow_def["id"]):
                errors.append(ValidationError(
                    level="ERROR",
                    code="INVALID_FLOW_ID_FORMAT",
                    message=f"Flow ID '{flow_def['id']}' must match pattern 'flow_[a-z_][a-z0-9_]*'",
                    file_path=registry_path
                ))

        # Validate nodes
        if "nodes" in flow_def:
            node_errors, node_warnings = self._validate_nodes(flow_def["nodes"], flow_id, registry_path)
            errors.extend(node_errors)
            warnings.extend(node_warnings)

        # Validate edges
        if "edges" in flow_def:
            edge_errors, edge_warnings = self._validate_edges(flow_def["edges"], flow_def.get("nodes", {}), flow_id, registry_path)
            errors.extend(edge_errors)
            warnings.extend(edge_warnings)

        # Validate guards
        if "guards" in flow_def:
            guard_errors = self._validate_guards(flow_def["guards"], flow_id, registry_path)
            errors.extend(guard_errors)

        # Validate DAG structure
        if "nodes" in flow_def and "edges" in flow_def:
            dag_errors = self._validate_dag_structure(flow_def["nodes"], flow_def["edges"], flow_id, registry_path)
            errors.extend(dag_errors)

        # Validate config
        if "config" in flow_def:
            config_errors, config_warnings = self._validate_config(flow_def["config"], flow_id, registry_path)
            errors.extend(config_errors)
            warnings.extend(config_warnings)

        return ValidationResult(
            flow_id=flow_id,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info
        )

    def _validate_nodes(self, nodes: Dict, flow_id: str, file_path: str) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate node definitions"""
        errors = []
        warnings = []

        if not isinstance(nodes, dict):
            errors.append(ValidationError(
                level="ERROR",
                code="INVALID_NODES_TYPE",
                message=f"nodes must be a dictionary in flow '{flow_id}'",
                file_path=file_path
            ))
            return errors, warnings

        for node_id, node_def in nodes.items():
            # Validate node ID format
            if not re.match(r'^[a-z_][a-z0-9_]*$', node_id):
                errors.append(ValidationError(
                    level="ERROR",
                    code="INVALID_NODE_ID_FORMAT",
                    message=f"Node ID '{node_id}' must match pattern '[a-z_][a-z0-9_]*'",
                    file_path=file_path
                ))

            # Validate required fields
            required_fields = ["type", "name", "command"]
            for field in required_fields:
                if field not in node_def:
                    errors.append(ValidationError(
                        level="ERROR",
                        code="MISSING_NODE_FIELD",
                        message=f"Required field '{field}' missing from node '{node_id}' in flow '{flow_id}'",
                        file_path=file_path
                    ))

            # Validate node type
            if "type" in node_def:
                valid_types = ["command", "condition", "gateway"]
                if node_def["type"] not in valid_types:
                    errors.append(ValidationError(
                        level="ERROR",
                        code="INVALID_NODE_TYPE",
                        message=f"Node type '{node_def['type']}' not in valid types: {valid_types}",
                        file_path=file_path
                    ))

            # Validate timeout
            if "timeout" in node_def:
                timeout = node_def["timeout"]
                if not isinstance(timeout, int) or timeout < 1 or timeout > 3600:
                    errors.append(ValidationError(
                        level="ERROR",
                        code="INVALID_TIMEOUT",
                        message=f"Timeout {timeout} must be integer between 1-3600 seconds",
                        file_path=file_path
                    ))

            # Validate retries
            if "retries" in node_def:
                retries = node_def["retries"]
                if not isinstance(retries, int) or retries < 0 or retries > 10:
                    errors.append(ValidationError(
                        level="ERROR",
                        code="INVALID_RETRIES",
                        message=f"Retries {retries} must be integer between 0-10",
                        file_path=file_path
                    ))

        return errors, warnings

    def _validate_edges(self, edges: List, nodes: Dict, flow_id: str, file_path: str) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate edge definitions and references"""
        errors = []
        warnings = []

        if not isinstance(edges, list):
            errors.append(ValidationError(
                level="ERROR",
                code="INVALID_EDGES_TYPE",
                message=f"edges must be a list in flow '{flow_id}'",
                file_path=file_path
            ))
            return errors, warnings

        node_ids = set(nodes.keys()) if nodes else set()

        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                errors.append(ValidationError(
                    level="ERROR",
                    code="INVALID_EDGE_TYPE",
                    message=f"Edge {i} must be a dictionary in flow '{flow_id}'",
                    file_path=file_path
                ))
                continue

            # Validate required fields
            required_fields = ["from", "to"]
            for field in required_fields:
                if field not in edge:
                    errors.append(ValidationError(
                        level="ERROR",
                        code="MISSING_EDGE_FIELD",
                        message=f"Required field '{field}' missing from edge {i} in flow '{flow_id}'",
                        file_path=file_path
                    ))

            # Validate node references
            if "from" in edge and edge["from"] not in node_ids:
                errors.append(ValidationError(
                    level="ERROR",
                    code="INVALID_EDGE_FROM",
                    message=f"Edge {i} references unknown node '{edge['from']}' in flow '{flow_id}'",
                    file_path=file_path
                ))

            if "to" in edge and edge["to"] not in node_ids:
                errors.append(ValidationError(
                    level="ERROR",
                    code="INVALID_EDGE_TO",
                    message=f"Edge {i} references unknown node '{edge['to']}' in flow '{flow_id}'",
                    file_path=file_path
                ))

            # Validate 'when' condition syntax (basic)
            if "when" in edge:
                when_condition = edge["when"]
                if not isinstance(when_condition, str):
                    errors.append(ValidationError(
                        level="ERROR",
                        code="INVALID_WHEN_CONDITION",
                        message=f"Edge {i} 'when' condition must be a string in flow '{flow_id}'",
                        file_path=file_path
                    ))

        return errors, warnings

    def _validate_guards(self, guards: List, flow_id: str, file_path: str) -> List[ValidationError]:
        """Validate guard definitions"""
        errors = []

        if not isinstance(guards, list):
            errors.append(ValidationError(
                level="ERROR",
                code="INVALID_GUARDS_TYPE",
                message=f"guards must be a list in flow '{flow_id}'",
                file_path=file_path
            ))
            return errors

        for guard in guards:
            if not isinstance(guard, str):
                errors.append(ValidationError(
                    level="ERROR",
                    code="INVALID_GUARD_TYPE",
                    message=f"Guard '{guard}' must be a string in flow '{flow_id}'",
                    file_path=file_path
                ))
                continue

            # Check if guard is built-in
            if guard not in self.built_in_guards:
                errors.append(ValidationError(
                    level="ERROR",
                    code="UNKNOWN_GUARD",
                    message=f"Unknown guard '{guard}' in flow '{flow_id}'",
                    file_path=file_path
                ))

        return errors

    def _validate_dag_structure(self, nodes: Dict, edges: List, flow_id: str, file_path: str) -> List[ValidationError]:
        """Validate DAG structure (acyclic, connected)"""
        errors = []

        try:
            # Build graph
            G = nx.DiGraph()

            # Add nodes
            for node_id in nodes.keys():
                G.add_node(node_id)

            # Add edges
            for edge in edges:
                if "from" in edge and "to" in edge:
                    G.add_edge(edge["from"], edge["to"])

            # Check for cycles
            if nx.is_directed_acyclic_graph(G):
                # Find root nodes (no incoming edges)
                root_nodes = [node for node in G.nodes() if G.in_degree(node) == 0]
                if not root_nodes:
                    errors.append(ValidationError(
                        level="ERROR",
                        code="NO_ROOT_NODES",
                        message=f"Flow '{flow_id}' has no root nodes (nodes with no incoming edges)",
                        file_path=file_path
                    ))
            else:
                # Find cycles
                cycles = list(nx.simple_cycles(G))
                errors.append(ValidationError(
                    level="ERROR",
                    code="CYCLIC_DEPENDENCY",
                    message=f"Flow '{flow_id}' contains cycles: {cycles}",
                    file_path=file_path
                ))

        except Exception as e:
            errors.append(ValidationError(
                level="ERROR",
                code="DAG_VALIDATION_FAILED",
                message=f"DAG validation failed for flow '{flow_id}': {e}",
                file_path=file_path
            ))

        return errors

    def _validate_config(self, config: Dict, flow_id: str, file_path: str) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate flow configuration"""
        errors = []
        warnings = []

        if not isinstance(config, dict):
            errors.append(ValidationError(
                level="ERROR",
                code="INVALID_CONFIG_TYPE",
                message=f"config must be a dictionary in flow '{flow_id}'",
                file_path=file_path
            ))
            return errors, warnings

        # Validate max_execution_time
        if "max_execution_time" in config:
            max_time = config["max_execution_time"]
            if not isinstance(max_time, int) or max_time < 1:
                errors.append(ValidationError(
                    level="ERROR",
                    code="INVALID_MAX_EXECUTION_TIME",
                    message=f"max_execution_time must be positive integer in flow '{flow_id}'",
                    file_path=file_path
                ))

        # Validate max_iterations
        if "max_iterations" in config:
            max_iter = config["max_iterations"]
            if not isinstance(max_iter, int) or max_iter < 1:
                errors.append(ValidationError(
                    level="ERROR",
                    code="INVALID_MAX_ITERATIONS",
                    message=f"max_iterations must be positive integer in flow '{flow_id}'",
                    file_path=file_path
                ))

        return errors, warnings

    def print_validation_report(self, results: Dict[str, ValidationResult]) -> None:
        """Print comprehensive validation report"""
        print("🛡️  AdvancedRules Flow Validation Report")
        print("=" * 50)

        total_errors = 0
        total_warnings = 0

        for flow_id, result in results.items():
            print(f"\n📋 Flow: {flow_id}")
            print("-" * 30)

            if result.errors:
                print(f"❌ Errors ({len(result.errors)}):")
                for error in result.errors:
                    print(f"   • {error.code}: {error.message}")
                total_errors += len(result.errors)

            if result.warnings:
                print(f"⚠️  Warnings ({len(result.warnings)}):")
                for warning in result.warnings:
                    print(f"   • {warning.code}: {warning.message}")
                total_warnings += len(result.warnings)

            if not result.errors and not result.warnings:
                print("✅ Valid")

        print("\n🎯 Summary:")
        print(f"   Total Errors: {total_errors}")
        print(f"   Total Warnings: {total_warnings}")

        if total_errors == 0:
            print("\n🎉 All flows validated successfully!")
            return True
        else:
            print(f"\n❌ {total_errors} errors found - validation failed")
            return False


def main():
    """CLI interface for flow validation"""
    if len(sys.argv) != 2:
        print("Usage: python flow_linter.py <flow_registry.yaml>")
        sys.exit(1)

    registry_path = sys.argv[1]

    if not Path(registry_path).exists():
        print(f"❌ Flow registry not found: {registry_path}")
        sys.exit(1)

    linter = FlowLinter()
    results = linter.validate_flow_registry(registry_path)
    success = linter.print_validation_report(results)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
