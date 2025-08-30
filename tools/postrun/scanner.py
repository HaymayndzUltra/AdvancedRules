#!/usr/bin/env python3
"""Postrun consistency scanner - validates execution against registry and schemas."""
import json
import yaml
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".cursor/commands/registry.yaml"
EVENTS_LOG = ROOT / "logs/events.jsonl"
DECISION_TRACES = ROOT / "logs/decision_traces.jsonl"
ARTIFACTS_INDEX = ROOT / "memory-bank/artifacts_index.json"
WORKFLOW_STATE = ROOT / "workflow_state.json"
POSTRUN_REPORT = ROOT / "memory-bank/postrun_consistency.json"


@dataclass
class ConsistencyIssue:
    """Represents a consistency issue found during postrun scan."""
    category: str  # "registry", "schema", "emits", "evidence"
    severity: str  # "error", "warning", "info"
    expected: Any
    actual: Any
    message: str
    correlation_id: Optional[str] = None


@dataclass
class PostrunReport:
    """Complete postrun consistency report."""
    scan_timestamp: float
    total_executions: int
    issues: List[ConsistencyIssue]
    registry_mismatches: List[Dict]
    schema_violations: List[Dict]
    missing_emits: List[Dict]
    orphaned_artifacts: List[str]
    consistency_score: float
    passed: bool


def load_registry() -> Dict[str, Any]:
    """Load and parse the registry YAML."""
    try:
        with open(REGISTRY, 'r') as f:
            data = yaml.safe_load(f)
        
        # Normalize command IDs
        commands = {}
        for cmd in data.get('commands', []):
            cmd_id = cmd.get('id', '')
            # Normalize ID (remove special chars, lowercase)
            normalized_id = cmd_id.replace('-', '_').replace(' ', '_').lower()
            commands[normalized_id] = cmd
            commands[cmd_id] = cmd  # Keep original too
        
        return commands
    except Exception as e:
        print(f"Error loading registry: {e}")
        return {}


def load_events() -> List[Dict]:
    """Load execution events from the event log."""
    events = []
    if EVENTS_LOG.exists():
        with open(EVENTS_LOG, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return events


def load_decision_traces() -> List[Dict]:
    """Load decision traces."""
    traces = []
    if DECISION_TRACES.exists():
        with open(DECISION_TRACES, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        traces.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return traces


def load_artifacts_index() -> List[Dict]:
    """Load the artifacts index."""
    if ARTIFACTS_INDEX.exists():
        try:
            with open(ARTIFACTS_INDEX, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def load_workflow_state() -> Dict:
    """Load current workflow state."""
    if WORKFLOW_STATE.exists():
        try:
            with open(WORKFLOW_STATE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def validate_canonical_schema(candidate: Dict) -> Tuple[bool, Optional[str]]:
    """Validate a candidate against the canonical schema."""
    # Required fields for canonical schema (from Phase 2)
    required_fields = {
        'id': str,
        'action_type': str,
        'scores': dict,  # Canonical uses 'scores' not 'metrics'
    }
    
    # Check required fields
    for field, expected_type in required_fields.items():
        if field not in candidate:
            return False, f"Missing required field: {field}"
        if not isinstance(candidate[field], expected_type):
            return False, f"Field {field} has wrong type: expected {expected_type.__name__}"
    
    # Check scores structure
    scores = candidate.get('scores', {})
    score_fields = ['intent', 'state', 'evidence', 'recency', 'preference']
    for field in score_fields:
        if field not in scores:
            return False, f"Missing score field: {field}"
        if not isinstance(scores[field], (int, float)):
            return False, f"Score field {field} must be numeric"
        if not 0 <= scores[field] <= 1:
            return False, f"Score field {field} must be between 0 and 1"
    
    return True, None


def check_registry_alignment(executions: List[Dict], registry: Dict) -> List[ConsistencyIssue]:
    """Check if executed commands exist in registry."""
    issues = []
    
    for execution in executions:
        command_id = execution.get('command_id', execution.get('id', ''))
        if not command_id:
            continue
        
        # Normalize the ID
        normalized_id = command_id.replace('-', '_').replace(' ', '_').lower()
        
        # Check if command exists in registry
        if normalized_id not in registry and command_id not in registry:
            issues.append(ConsistencyIssue(
                category="registry",
                severity="error",
                expected=f"Command '{command_id}' in registry",
                actual="Command not found",
                message=f"Executed command '{command_id}' not found in registry",
                correlation_id=execution.get('correlation_id')
            ))
        else:
            # Command exists, check if trigger matches
            reg_cmd = registry.get(normalized_id) or registry.get(command_id)
            if 'trigger' in execution and 'trigger' in reg_cmd:
                if execution['trigger'] != reg_cmd['trigger']:
                    issues.append(ConsistencyIssue(
                        category="registry",
                        severity="warning",
                        expected=reg_cmd['trigger'],
                        actual=execution['trigger'],
                        message=f"Trigger mismatch for command '{command_id}'",
                        correlation_id=execution.get('correlation_id')
                    ))
    
    return issues


def check_schema_compliance(decisions: List[Dict]) -> List[ConsistencyIssue]:
    """Check if decision candidates match canonical schema."""
    issues = []
    
    for decision in decisions:
        candidates = decision.get('candidates', [])
        for candidate in candidates:
            # Check if using legacy 'metrics' instead of canonical 'scores'
            if 'metrics' in candidate and 'scores' not in candidate:
                issues.append(ConsistencyIssue(
                    category="schema",
                    severity="warning",
                    expected="'scores' field",
                    actual="'metrics' field",
                    message=f"Candidate '{candidate.get('id', 'unknown')}' uses legacy 'metrics' instead of 'scores'",
                    correlation_id=decision.get('correlation_id')
                ))
                
                # Try to validate with adapted schema
                adapted = candidate.copy()
                adapted['scores'] = adapted.pop('metrics', {})
                valid, error = validate_canonical_schema(adapted)
            else:
                valid, error = validate_canonical_schema(candidate)
            
            if not valid:
                issues.append(ConsistencyIssue(
                    category="schema",
                    severity="error",
                    expected="Valid canonical schema",
                    actual=str(candidate),
                    message=f"Schema violation in candidate '{candidate.get('id', 'unknown')}': {error}",
                    correlation_id=decision.get('correlation_id')
                ))
    
    return issues


def check_emits_created(executions: List[Dict], registry: Dict, state: Dict, artifacts: List[Dict]) -> List[ConsistencyIssue]:
    """Check if declared emits were actually created."""
    issues = []
    
    for execution in executions:
        command_id = execution.get('command_id', execution.get('id', ''))
        if not command_id:
            continue
        
        # Get registry entry
        normalized_id = command_id.replace('-', '_').replace(' ', '_').lower()
        reg_cmd = registry.get(normalized_id) or registry.get(command_id, {})
        
        if not reg_cmd:
            continue
        
        emits = reg_cmd.get('emits', {})
        
        # Check state transitions
        if 'sets_state' in emits:
            expected_state = emits['sets_state']
            current_state = state.get('state')
            
            # Check if state was set (may have changed since)
            history = state.get('history', [])
            state_was_set = any(h.get('to') == expected_state for h in history)
            
            if not state_was_set and current_state != expected_state:
                issues.append(ConsistencyIssue(
                    category="emits",
                    severity="warning",
                    expected=f"State: {expected_state}",
                    actual=f"State: {current_state}",
                    message=f"Command '{command_id}' declared state '{expected_state}' but it was never set",
                    correlation_id=execution.get('correlation_id')
                ))
        
        # Check completed steps
        if 'add_completed_step' in emits:
            expected_step = emits['add_completed_step']
            completed_steps = state.get('completed_steps', [])
            
            if expected_step not in completed_steps:
                issues.append(ConsistencyIssue(
                    category="emits",
                    severity="warning",
                    expected=f"Completed step: {expected_step}",
                    actual="Step not in completed_steps",
                    message=f"Command '{command_id}' declared step '{expected_step}' but it's not in completed_steps",
                    correlation_id=execution.get('correlation_id')
                ))
        
        # Check artifact creation
        if 'creates_artifact' in emits:
            expected_artifact = emits['creates_artifact']
            artifact_paths = [a.get('path', '') for a in artifacts]
            
            if not any(expected_artifact in path for path in artifact_paths):
                issues.append(ConsistencyIssue(
                    category="emits",
                    severity="error",
                    expected=f"Artifact: {expected_artifact}",
                    actual="Artifact not found",
                    message=f"Command '{command_id}' declared artifact '{expected_artifact}' but it wasn't created",
                    correlation_id=execution.get('correlation_id')
                ))
    
    return issues


def check_evidence_linkage(decisions: List[Dict], artifacts: List[Dict]) -> List[ConsistencyIssue]:
    """Check if evidence paths in decisions actually exist."""
    issues = []
    
    for decision in decisions:
        evidence_paths = decision.get('context', {}).get('evidence_paths', [])
        
        for path in evidence_paths:
            if path.startswith('file://'):
                file_path = path.replace('file://', '')
                
                # Check if it's a memory-bank artifact
                if 'memory-bank' in file_path:
                    artifact_exists = any(
                        file_path in a.get('path', '') 
                        for a in artifacts
                    )
                    
                    if not artifact_exists:
                        # Check if file physically exists
                        full_path = ROOT / file_path
                        if not full_path.exists():
                            issues.append(ConsistencyIssue(
                                category="evidence",
                                severity="warning",
                                expected=f"Evidence file: {file_path}",
                                actual="File not found",
                                message=f"Evidence path '{file_path}' referenced but not found",
                                correlation_id=decision.get('correlation_id')
                            ))
    
    return issues


def find_orphaned_artifacts(artifacts: List[Dict], events: List[Dict]) -> List[str]:
    """Find artifacts that have no correlation ID or event linkage."""
    orphaned = []
    
    # Get all correlation IDs from events
    event_correlations = set()
    for event in events:
        if 'correlation_id' in event and event['correlation_id']:
            event_correlations.add(event['correlation_id'])
    
    # Check artifacts
    for artifact in artifacts:
        correlation_id = artifact.get('correlation_id')
        
        # Artifact is orphaned if it has no correlation ID or 
        # its correlation ID doesn't appear in any events
        if not correlation_id or correlation_id not in event_correlations:
            orphaned.append(artifact.get('path', 'unknown'))
    
    return orphaned


def scan_postrun_consistency() -> PostrunReport:
    """Main function to scan postrun consistency."""
    # Load all data
    registry = load_registry()
    events = load_events()
    decisions = load_decision_traces()
    artifacts = load_artifacts_index()
    state = load_workflow_state()
    
    # Extract executions from events
    executions = [e for e in events if e.get('type') in ['command_executed', 'decision_made']]
    
    # Run all checks
    all_issues = []
    
    # 1. Registry alignment
    registry_issues = check_registry_alignment(executions, registry)
    all_issues.extend(registry_issues)
    
    # 2. Schema compliance
    schema_issues = check_schema_compliance(decisions)
    all_issues.extend(schema_issues)
    
    # 3. Emits verification
    emit_issues = check_emits_created(executions, registry, state, artifacts)
    all_issues.extend(emit_issues)
    
    # 4. Evidence linkage
    evidence_issues = check_evidence_linkage(decisions, artifacts)
    all_issues.extend(evidence_issues)
    
    # 5. Find orphaned artifacts
    orphaned = find_orphaned_artifacts(artifacts, events)
    
    # Calculate consistency score
    total_checks = len(executions) * 4  # 4 types of checks per execution
    total_issues = len([i for i in all_issues if i.severity == 'error'])
    consistency_score = 1.0 - (total_issues / max(total_checks, 1))
    
    # Build report
    report = PostrunReport(
        scan_timestamp=time.time(),
        total_executions=len(executions),
        issues=all_issues,
        registry_mismatches=[asdict(i) for i in all_issues if i.category == 'registry'],
        schema_violations=[asdict(i) for i in all_issues if i.category == 'schema'],
        missing_emits=[asdict(i) for i in all_issues if i.category == 'emits'],
        orphaned_artifacts=orphaned,
        consistency_score=consistency_score,
        passed=len([i for i in all_issues if i.severity == 'error']) == 0
    )
    
    return report


def save_report(report: PostrunReport) -> None:
    """Save postrun consistency report."""
    from tools.io.fs import atomic_write_text
    
    POSTRUN_REPORT.parent.mkdir(parents=True, exist_ok=True)
    report_dict = asdict(report)
    atomic_write_text(POSTRUN_REPORT, json.dumps(report_dict, indent=2))


def main():
    """Run postrun consistency scan and generate report."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Postrun consistency scanner")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--strict", action="store_true", help="Exit with error on issues")
    parser.add_argument("--correlation-id", help="Filter by correlation ID")
    
    args = parser.parse_args()
    
    # Run scan
    report = scan_postrun_consistency()
    
    # Filter by correlation ID if specified
    if args.correlation_id:
        report.issues = [
            i for i in report.issues 
            if i.correlation_id == args.correlation_id
        ]
    
    # Save report
    save_report(report)
    
    # Output
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"Postrun Consistency Scan")
        print(f"========================")
        print(f"Total executions: {report.total_executions}")
        print(f"Consistency score: {report.consistency_score:.1%}")
        print(f"Status: {'✅ PASSED' if report.passed else '❌ FAILED'}")
        
        if report.issues:
            print(f"\nIssues found: {len(report.issues)}")
            
            errors = [i for i in report.issues if i.severity == 'error']
            warnings = [i for i in report.issues if i.severity == 'warning']
            
            if errors:
                print(f"\n❌ Errors ({len(errors)}):")
                for issue in errors[:5]:
                    print(f"  - {issue.message}")
            
            if warnings:
                print(f"\n⚠️  Warnings ({len(warnings)}):")
                for issue in warnings[:5]:
                    print(f"  - {issue.message}")
        
        if report.orphaned_artifacts:
            print(f"\n🔍 Orphaned artifacts: {len(report.orphaned_artifacts)}")
            for artifact in report.orphaned_artifacts[:5]:
                print(f"  - {artifact}")
        
        print(f"\nReport saved to: {POSTRUN_REPORT.relative_to(ROOT)}")
    
    # Exit code
    if args.strict and not report.passed:
        exit(1)


if __name__ == "__main__":
    main()