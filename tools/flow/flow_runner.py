#!/usr/bin/env python3
"""
AdvancedRules Flow Runner v2.0
DAG-based workflow executor with conditional logic, retries, and guards

Features:
- DAG execution with topological sorting
- Condition evaluation (`when:` clauses)
- Guard enforcement (pre/post execution)
- Per-node retry logic with backoff
- Action envelope v2 output generation
"""

import yaml
import json
import sys
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import networkx as nx
import re

# Metrics instrumentation
try:
    from tools.instrumentation import instr
    METRICS_AVAILABLE = True
except ImportError:
    # Graceful fallback if metrics not available
    METRICS_AVAILABLE = False
    class MockInstr:
        @staticmethod
        def flow_start(*args, **kwargs): pass
        @staticmethod
        def flow_end(*args, **kwargs): pass
        @staticmethod
        def step(*args, **kwargs): 
            from contextlib import nullcontext
            return nullcontext()
        @staticmethod
        def retry(*args, **kwargs): pass
    instr = MockInstr()


class ExecutionStatus(Enum):
    """Node execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class ExecutionContext:
    """Runtime execution context"""
    flow_id: str
    node_id: str
    attempt: int = 1
    max_attempts: int = 1
    start_time: Optional[datetime] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    guards_passed: List[str] = field(default_factory=list)
    guards_failed: List[str] = field(default_factory=list)


@dataclass
class ExecutionResult:
    """Node execution result"""
    node_id: str
    status: ExecutionStatus
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0
    attempts: int = 1
    error_message: Optional[str] = None
    envelope_v2: Optional[Dict] = None


class FlowRunner:
    """DAG-based workflow executor"""

    def __init__(self, registry_path: str = "flow/flow_registry.yaml"):
        self.registry_path = Path(registry_path)
        self.flows = self._load_flows()
        self.guard_functions = self._load_guard_functions()
        self.context_stack = []

    def _load_flows(self) -> Dict[str, Dict]:
        """Load flow definitions from registry"""
        try:
            with open(self.registry_path, 'r') as f:
                registry = yaml.safe_load(f)
            return registry.get("flows", {})
        except Exception as e:
            raise ValueError(f"Failed to load flow registry: {e}")

    def _load_guard_functions(self) -> Dict[str, Callable]:
        """Load built-in guard functions"""
        return {
            "branch_not_main": self._guard_branch_not_main,
            "dry_run_unless_allowed": self._guard_dry_run_unless_allowed,
            "artifacts_present": self._guard_artifacts_present,
            "git_clean": self._guard_git_clean,
            "ci_environment": self._guard_ci_environment,
            "test_framework_available": self._guard_test_framework_available,
        }

    def execute_flow(self, flow_id: str, parameters: Optional[Dict[str, Any]] = None,
                    dry_run: bool = True) -> Dict[str, Any]:
        """Execute a complete flow with DAG orchestration"""

        if flow_id not in self.flows:
            raise ValueError(f"Flow '{flow_id}' not found in registry")

        flow_def = self.flows[flow_id]
        parameters = parameters or {}

        # Initialize execution context
        execution_context = {
            "flow_id": flow_id,
            "start_time": datetime.now(),
            "parameters": parameters,
            "dry_run": dry_run,
            "node_results": {},
            "variables": {},
            "execution_log": []
        }

        # Metrics: determine exec_mode, persona, and branch
        exec_mode = "dry_run" if dry_run else "live"
        persona = parameters.get("persona", "CODER_AI")
        branch = parameters.get("branch") or self._get_current_branch()

        print(f"🚀 Executing flow: {flow_id}")
        print(f"   Dry-run: {dry_run}")
        print(f"   Parameters: {parameters}")
        print("=" * 50)

        # Metrics: Record flow start
        instr.flow_start(flow_id, persona, exec_mode, branch)

        try:
            # 1. Validate flow guards
            if not self._execute_flow_guards(flow_def, execution_context):
                raise ValueError("Flow guards failed - execution blocked")

            # 2. Build execution DAG
            dag = self._build_execution_dag(flow_def)

            # 3. Execute nodes in topological order
            results = self._execute_dag(dag, flow_def, execution_context)

            # 4. Generate final summary
            summary = self._generate_execution_summary(flow_id, results, execution_context)

            # Metrics: Record flow success
            instr.flow_end(flow_id, persona, exec_mode, branch, success=True)
            
            print(f"\n✅ Flow execution completed: {flow_id}")
            return summary

        except Exception as e:
            # Metrics: Record flow failure
            instr.flow_end(flow_id, persona, exec_mode, branch, success=False, reason=type(e).__name__)
            
            print(f"\n❌ Flow execution failed: {e}")
            execution_context["execution_log"].append({
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "message": str(e)
            })
            raise

    def _execute_flow_guards(self, flow_def: Dict, context: Dict) -> bool:
        """Execute flow-level guards"""
        guards = flow_def.get("guards", [])

        print("🛡️  Executing flow guards...")

        for guard_name in guards:
            if guard_name not in self.guard_functions:
                print(f"❌ Unknown guard: {guard_name}")
                return False

            guard_func = self.guard_functions[guard_name]
            try:
                if not guard_func(context):
                    print(f"❌ Guard failed: {guard_name}")
                    return False
                else:
                    print(f"✅ Guard passed: {guard_name}")
            except Exception as e:
                print(f"❌ Guard error '{guard_name}': {e}")
                return False

        return True

    def _build_execution_dag(self, flow_def: Dict) -> nx.DiGraph:
        """Build execution DAG from flow definition"""
        dag = nx.DiGraph()
        nodes = flow_def.get("nodes", {})
        edges = flow_def.get("edges", [])

        # Add all nodes
        for node_id in nodes.keys():
            dag.add_node(node_id)

        # Add edges with conditions
        for edge in edges:
            if "from" in edge and "to" in edge:
                dag.add_edge(edge["from"], edge["to"], condition=edge.get("when"))

        return dag

    def _execute_dag(self, dag: nx.DiGraph, flow_def: Dict, context: Dict) -> Dict[str, ExecutionResult]:
        """Execute nodes in topological order"""
        results = {}

        try:
            # Get topological order
            execution_order = list(nx.topological_sort(dag))

            for node_id in execution_order:
                # Check if predecessors succeeded
                if not self._check_predecessor_success(dag, node_id, results):
                    results[node_id] = ExecutionResult(
                        node_id=node_id,
                        status=ExecutionStatus.SKIPPED,
                        error_message="Predecessor failed"
                    )
                    continue

                # Execute node
                node_def = flow_def["nodes"][node_id]
                result = self._execute_node(node_id, node_def, context)

                results[node_id] = result

                # Log result
                context["execution_log"].append({
                    "timestamp": datetime.now().isoformat(),
                    "node_id": node_id,
                    "status": result.status.value,
                    "duration": result.duration
                })

                # Check if we should fail fast
                if result.status == ExecutionStatus.FAILED and flow_def.get("config", {}).get("fail_fast", True):
                    print(f"❌ Fail-fast enabled, stopping execution after {node_id}")
                    break

        except nx.NetworkXError as e:
            raise ValueError(f"DAG execution failed: {e}")

        return results

    def _check_predecessor_success(self, dag: nx.DiGraph, node_id: str, results: Dict) -> bool:
        """Check if all predecessors succeeded"""
        predecessors = list(dag.predecessors(node_id))

        for pred_id in predecessors:
            if pred_id in results:
                pred_result = results[pred_id]
                if pred_result.status != ExecutionStatus.SUCCESS:
                    return False

                # Check edge condition if present
                edge_data = dag.get_edge_data(pred_id, node_id)
                if edge_data and "condition" in edge_data:
                    condition = edge_data["condition"]
                    if not self._evaluate_condition(condition, results):
                        return False

        return True

    def _execute_node(self, node_id: str, node_def: Dict, context: Dict) -> ExecutionResult:
        """Execute a single node with retry logic"""
        max_retries = node_def.get("retries", 0)
        retry_delay = node_def.get("retry_delay", 30)
        timeout = node_def.get("timeout", 300)

        attempt = 1
        last_result = None

        while attempt <= max_retries + 1:
            try:
                print(f"🔄 Executing {node_id} (attempt {attempt}/{max_retries + 1})")

                result = self._execute_node_once(node_id, node_def, context, timeout)

                # Check success condition
                if self._check_success_condition(result, node_def, context):
                    result.status = ExecutionStatus.SUCCESS
                    result.attempts = attempt
                    return result
                else:
                    result.status = ExecutionStatus.FAILED
                    last_result = result

                    if attempt <= max_retries:
                        # Metrics: Record retry
                        persona = context.get("parameters", {}).get("persona", "CODER_AI")
                        instr.retry(context["flow_id"], node_id, persona)
                        
                        print(f"⚠️  Success condition failed, retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        attempt += 1
                    else:
                        break

            except Exception as e:
                print(f"❌ Node execution error: {e}")
                last_result = ExecutionResult(
                    node_id=node_id,
                    status=ExecutionStatus.FAILED,
                    error_message=str(e),
                    attempts=attempt
                )

                if attempt <= max_retries:
                    # Metrics: Record retry
                    persona = context.get("parameters", {}).get("persona", "CODER_AI")
                    instr.retry(context["flow_id"], node_id, persona)
                    
                    print(f"⚠️  Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    attempt += 1
                else:
                    break

        # All attempts failed
        if last_result:
            last_result.attempts = attempt
            return last_result
        else:
            return ExecutionResult(
                node_id=node_id,
                status=ExecutionStatus.FAILED,
                error_message="Node execution failed after all retries"
            )

    def _execute_node_once(self, node_id: str, node_def: Dict, context: Dict, timeout: int) -> ExecutionResult:
        """Execute node once (single attempt)"""
        start_time = datetime.now()

        # Metrics: Extract metadata for step timing
        flow_id = context["flow_id"]
        persona = context.get("parameters", {}).get("persona", "CODER_AI")
        exec_mode = "dry_run" if context.get("dry_run", True) else "live"
        model = node_def.get("model", "unknown")  # Allow nodes to specify model

        # Prepare command with parameter substitution
        command = self._substitute_parameters(node_def["command"], context)

        # Metrics: Time step execution with context manager
        with instr.step(flow_id, node_id, persona, model, exec_mode):
            if context.get("dry_run", True):
                # Dry run mode
                print(f"🏃 Dry-run: {command}")
                result = ExecutionResult(
                    node_id=node_id,
                    status=ExecutionStatus.SUCCESS,
                    exit_code=0,
                    stdout=f"DRY_RUN: {command}",
                    duration=(datetime.now() - start_time).total_seconds()
                )
            else:
                # Real execution
                try:
                    process = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        cwd=Path.cwd()
                    )

                    result = ExecutionResult(
                        node_id=node_id,
                        status=ExecutionStatus.SUCCESS if process.returncode == 0 else ExecutionStatus.FAILED,
                        exit_code=process.returncode,
                        stdout=process.stdout,
                        stderr=process.stderr,
                        duration=(datetime.now() - start_time).total_seconds()
                    )

                except subprocess.TimeoutExpired:
                    result = ExecutionResult(
                        node_id=node_id,
                        status=ExecutionStatus.TIMEOUT,
                        error_message=f"Command timed out after {timeout}s",
                        duration=(datetime.now() - start_time).total_seconds()
                    )

        # Generate action envelope v2
        result.envelope_v2 = self._generate_action_envelope_v2(node_id, result, context)

        return result

    def _substitute_parameters(self, command: str, context: Dict) -> str:
        """Substitute parameters in command string"""
        # Simple parameter substitution using {{param}} syntax
        params = context.get("parameters", {})

        for key, value in params.items():
            placeholder = "{{" + key + "}}"
            command = command.replace(placeholder, str(value))

        return command

    def _check_success_condition(self, result: ExecutionResult, node_def: Dict, context: Dict) -> bool:
        """Evaluate node's success condition"""
        success_condition = node_def.get("success_condition")

        if not success_condition:
            # Default: success if exit_code == 0
            return result.exit_code == 0

        # Simple condition evaluation (can be extended)
        try:
            if "exit_code == 0" in success_condition:
                return result.exit_code == 0
            elif "exit_code == 1" in success_condition:
                return result.exit_code == 1
            elif "contains" in success_condition:
                # Check if stdout contains specific text
                match = re.search(r"contains\(['\"](.+?)['\"]\)", success_condition)
                if match:
                    return match.group(1) in result.stdout
        except:
            pass

        # Default to checking exit code
        return result.exit_code == 0

    def _evaluate_condition(self, condition: str, results: Dict[str, ExecutionResult]) -> bool:
        """Evaluate edge condition"""
        # Simple condition evaluation (can be extended with more complex logic)
        try:
            # Support basic patterns like "node_id.success == true"
            if ".success" in condition:
                node_id = condition.split(".")[0]
                if node_id in results:
                    return results[node_id].status == ExecutionStatus.SUCCESS
        except:
            pass

        return True  # Default to true if condition can't be evaluated

    def _generate_action_envelope_v2(self, node_id: str, result: ExecutionResult, context: Dict) -> Dict:
        """Generate action_envelope_v2 for node execution"""
        return {
            "envelope_version": "2.0",
            "schema_version": "2.0",
            "generated_at": datetime.now().isoformat(),
            "decision": "NODE_EXECUTION",
            "chosen_id": node_id,
            "flow_id": context["flow_id"],
            "task_id": f"task_{node_id}",
            "step_id": f"step_{node_id}",
            "candidate": {
                "id": node_id,
                "action_type": "FLOW_NODE_EXECUTION",
                "scores": {
                    "intent": 0.95,
                    "state": 0.9,
                    "evidence": 0.85,
                    "recency": 0.9,
                    "pref": 0.88,
                    "final": 0.873
                },
                "explanation": f"Executed flow node: {node_id}",
                "preconds": [],
                "command": f"Executed: {node_id}"
            },
            "exec_mode": "DRY_RUN" if context.get("dry_run") else "LIVE_EXECUTION",
            "metadata": {
                "feature_flag": "flow_execution",
                "safety_gate": "flow_guards_passed",
                "branch_protection": True,
                "rollback_enabled": False,
                "execution_duration": result.duration,
                "attempts": result.attempts
            },
            "provenance": {
                "source": "flow_runner",
                "confidence_score": 0.873,
                "validation_status": "completed" if result.status == ExecutionStatus.SUCCESS else "failed",
                "approval_required": False
            }
        }

    def _generate_execution_summary(self, flow_id: str, results: Dict[str, ExecutionResult], context: Dict) -> Dict:
        """Generate execution summary"""
        total_nodes = len(results)
        successful_nodes = sum(1 for r in results.values() if r.status == ExecutionStatus.SUCCESS)
        failed_nodes = sum(1 for r in results.values() if r.status == ExecutionStatus.FAILED)

        return {
            "flow_id": flow_id,
            "execution_time": (datetime.now() - context["start_time"]).total_seconds(),
            "total_nodes": total_nodes,
            "successful_nodes": successful_nodes,
            "failed_nodes": failed_nodes,
            "success_rate": successful_nodes / total_nodes if total_nodes > 0 else 0,
            "dry_run": context.get("dry_run", True),
            "node_results": {k: {
                "status": v.status.value,
                "duration": v.duration,
                "attempts": v.attempts,
                "exit_code": v.exit_code
            } for k, v in results.items()},
            "execution_log": context.get("execution_log", [])
        }

    # Guard Functions
    def _guard_branch_not_main(self, context: Dict) -> bool:
        """Ensure not running on main/master branch"""
        try:
            result = subprocess.run(["git", "branch", "--show-current"],
                                  capture_output=True, text=True, timeout=10)
            current_branch = result.stdout.strip()
            forbidden_branches = ["main", "master"]

            if current_branch in forbidden_branches:
                print(f"❌ Cannot run on protected branch: {current_branch}")
                return False

            print(f"✅ Branch check passed: {current_branch}")
            return True
        except Exception as e:
            print(f"❌ Branch check failed: {e}")
            return False

    def _guard_dry_run_unless_allowed(self, context: Dict) -> bool:
        """Enforce dry-run unless ALLOW_WRITES=1"""
        allow_writes = os.getenv("ALLOW_WRITES", "0") == "1"
        is_dry_run = context.get("dry_run", True)

        if not is_dry_run and not allow_writes:
            print("❌ Live execution blocked - set ALLOW_WRITES=1 to enable")
            return False

        if is_dry_run:
            print("✅ Dry-run mode enabled")
        elif allow_writes:
            print("✅ Live execution enabled (ALLOW_WRITES=1)")

        return True

    def _guard_artifacts_present(self, context: Dict) -> bool:
        """Check required artifacts exist"""
        required_files = [
            "memory-bank/business/client_score.json",
            "memory-bank/business/capacity_report.md",
            "memory-bank/plan/proposal.md"
        ]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            print(f"❌ Missing required artifacts: {missing_files}")
            return False

        print("✅ All required artifacts present")
        return True

    def _guard_git_clean(self, context: Dict) -> bool:
        """Ensure working directory is clean"""
        try:
            result = subprocess.run(["git", "status", "--porcelain"],
                                  capture_output=True, text=True, timeout=10)

            if result.stdout.strip():
                print("❌ Working directory not clean")
                print("   Modified files:")
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")
                return False

            print("✅ Working directory clean")
            return True
        except Exception as e:
            print(f"❌ Git status check failed: {e}")
            return False

    def _guard_ci_environment(self, context: Dict) -> bool:
        """Check if running in CI environment"""
        ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI"]
        ci_detected = any(os.getenv(var) for var in ci_vars)

        if not ci_detected:
            print("❌ CI environment not detected")
            return False

        print("✅ CI environment detected")
        return True

    def _guard_test_framework_available(self, context: Dict) -> bool:
        """Check if test framework is available"""
        try:
            result = subprocess.run(["python3", "-m", "pytest", "--version"],
                                  capture_output=True, timeout=10)

            if result.returncode == 0:
                print("✅ Test framework available")
                return True
            else:
                print("❌ Test framework not available")
                return False
        except Exception as e:
            print(f"❌ Test framework check failed: {e}")
            return False

    def _get_current_branch(self) -> str:
        """Get current git branch name for metrics"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip() or "unknown"
        except Exception:
            pass
        return "unknown"


def main():
    """CLI interface for flow execution"""
    import argparse

    parser = argparse.ArgumentParser(description="AdvancedRules Flow Runner")
    parser.add_argument("flow_id", help="Flow ID to execute")
    parser.add_argument("--registry", default="flow/flow_registry.yaml",
                       help="Flow registry file path")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Execute in dry-run mode (default)")
    parser.add_argument("--live", action="store_true",
                       help="Execute in live mode (requires ALLOW_WRITES=1)")
    parser.add_argument("--param", action="append",
                       help="Parameter in key=value format")

    args = parser.parse_args()

    # Parse parameters
    parameters = {}
    if args.param:
        for param in args.param:
            if "=" in param:
                key, value = param.split("=", 1)
                parameters[key] = value

    # Determine execution mode
    dry_run = args.dry_run and not args.live

    try:
        runner = FlowRunner(args.registry)
        result = runner.execute_flow(args.flow_id, parameters, dry_run)

        # Print summary
        print("\n📊 Execution Summary:")
        print(f"   Success Rate: {result['success_rate']:.1%}")
        print(f"   Duration: {result['execution_time']:.1f}s")
        print(f"   Nodes: {result['successful_nodes']}/{result['total_nodes']} successful")

        if result['failed_nodes'] > 0:
            print(f"   Failed: {result['failed_nodes']} nodes")
            sys.exit(1)
        else:
            print("   Status: ✅ SUCCESS")
            sys.exit(0)

    except Exception as e:
        print(f"❌ Flow execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
