#!/usr/bin/env python3
"""
Orchestrator Post-Run Tool

This tool activates after each agent completes to:
1. Summarize context (state, gates, latest outputs)
2. Build candidate list (mix of NATURAL_STEP and COMMAND_TRIGGER)
3. Call local scorer tool
4. Emit decision result and rationale
5. Log outputs to logs/decisions/
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add decision_scoring to path
sys.path.append(str(Path(__file__).parent / "decision_scoring"))
from score import DecisionScoringTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorPostRun:
    """Orchestrator that suggests next steps after agent completion."""
    
    def __init__(self, base_path: str = "."):
        """Initialize the orchestrator."""
        self.base_path = Path(base_path)
        self.scorer = DecisionScoringTool(str(self.base_path / "decision_scoring" / "weights.json"))
        self.logs_dir = self.base_path / "logs" / "decisions"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_workflow_state(self) -> Dict[str, Any]:
        """Load workflow state from workflow_state.json."""
        state_file = self.base_path / "workflow_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load workflow state: {e}")
        return {"status": "unknown", "current_goal": "unknown"}
    
    def _load_gate_results(self) -> Dict[str, Any]:
        """Load gate results from gate_results.json."""
        gate_file = self.base_path / "gate_results.json"
        if gate_file.exists():
            try:
                with open(gate_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load gate results: {e}")
        return {"gates": [], "results": {}}
    
    def _load_handoff_log(self) -> Dict[str, Any]:
        """Load handoff log from handoff_log.json."""
        handoff_file = self.base_path / "handoff_log.json"
        if handoff_file.exists():
            try:
                with open(handoff_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load handoff log: {e}")
        return {"handoffs": [], "last_agent": "unknown"}
    
    def _scan_recent_outputs(self) -> List[str]:
        """Scan for recent outputs in memory-bank, reports, and test logs."""
        evidence_paths = []
        
        # Scan memory-bank
        memory_bank = self.base_path / "memory-bank"
        if memory_bank.exists():
            for file_path in memory_bank.glob("*.md"):
                evidence_paths.append(f"file://{file_path}")
        
        # Scan reports
        reports_dir = self.base_path / "reports"
        if reports_dir.exists():
            for file_path in reports_dir.glob("*.json"):
                evidence_paths.append(f"file://{file_path}")
        
        # Scan test logs
        test_logs = self.base_path / "test_glob"
        if test_logs.exists():
            for file_path in test_logs.glob("*.json"):
                evidence_paths.append(f"file://{file_path}")
        
        return evidence_paths
    
    def _build_candidates(self, workflow_state: Dict, gate_results: Dict, handoff_log: Dict) -> List[Dict[str, Any]]:
        """Build candidate list with NATURAL_STEP and COMMAND_TRIGGER actions."""
        candidates = []
        
        # Analyze current state to determine appropriate candidates
        current_status = workflow_state.get("status", "unknown")
        current_goal = workflow_state.get("current_goal", "unknown")
        
        # NATURAL_STEP candidates based on workflow state
        if current_status == "planning":
            candidates.append({
                "id": "continue_planning",
                "intent": 0.8,
                "state": 0.9,
                "evidence": 0.7,
                "recency": 0.8,
                "pref": 0.8,
                "action_type": "NATURAL_STEP",
                "explanation": "Continue planning phase based on current workflow state"
            })
            candidates.append({
                "id": "validate_plan",
                "intent": 0.7,
                "state": 0.8,
                "evidence": 0.6,
                "recency": 0.7,
                "pref": 0.7,
                "action_type": "NATURAL_STEP",
                "explanation": "Validate current plan before proceeding to implementation"
            })
        
        elif current_status == "implementation":
            candidates.append({
                "id": "continue_implementation",
                "intent": 0.9,
                "state": 0.8,
                "evidence": 0.8,
                "recency": 0.9,
                "pref": 0.9,
                "action_type": "NATURAL_STEP",
                "explanation": "Continue implementation based on current progress"
            })
            candidates.append({
                "id": "run_tests",
                "intent": 0.8,
                "state": 0.7,
                "evidence": 0.8,
                "recency": 0.8,
                "pref": 0.8,
                "action_type": "COMMAND_TRIGGER",
                "explanation": "Run tests to validate current implementation"
            })
        
        elif current_status == "testing":
            candidates.append({
                "id": "fix_issues",
                "intent": 0.9,
                "state": 0.9,
                "evidence": 0.8,
                "recency": 0.9,
                "pref": 0.9,
                "action_type": "NATURAL_STEP",
                "explanation": "Fix any issues found during testing"
            })
            candidates.append({
                "id": "deploy_solution",
                "intent": 0.8,
                "state": 0.7,
                "evidence": 0.7,
                "recency": 0.8,
                "pref": 0.8,
                "action_type": "COMMAND_TRIGGER",
                "explanation": "Deploy solution after successful testing"
            })
        
        # COMMAND_TRIGGER candidates for common actions
        candidates.append({
            "id": "generate_report",
            "intent": 0.6,
            "state": 0.5,
            "evidence": 0.7,
            "recency": 0.6,
            "pref": 0.6,
            "action_type": "COMMAND_TRIGGER",
            "explanation": "Generate progress report for current workflow"
        })
        
        candidates.append({
            "id": "update_documentation",
            "intent": 0.5,
            "state": 0.4,
            "evidence": 0.6,
            "recency": 0.5,
            "pref": 0.5,
            "action_type": "NATURAL_STEP",
            "explanation": "Update documentation with latest changes"
        })
        
        return candidates
    
    def _generate_context_summary(self, workflow_state: Dict, gate_results: Dict, handoff_log: Dict) -> str:
        """Generate context summary from available state information."""
        current_status = workflow_state.get("status", "unknown")
        current_goal = workflow_state.get("current_goal", "unknown")
        last_agent = handoff_log.get("last_agent", "unknown")
        
        summary = f"Workflow status: {current_status}, Goal: {current_goal}, Last agent: {last_agent}"
        
        if gate_results.get("gates"):
            summary += f", Active gates: {len(gate_results['gates'])}"
        
        return summary
    
    def run_post_run_analysis(self) -> Dict[str, Any]:
        """Run the complete post-run analysis and suggestion process."""
        try:
            # Load all required inputs
            workflow_state = self._load_workflow_state()
            gate_results = self._load_gate_results()
            handoff_log = self._load_handoff_log()
            evidence_paths = self._scan_recent_outputs()
            
            # Generate context summary
            context_summary = self._generate_context_summary(workflow_state, gate_results, handoff_log)
            
            # Build candidates
            candidates = self._build_candidates(workflow_state, gate_results, handoff_log)
            
            # Evaluate candidates using scorer
            result = self.scorer.evaluate_candidates(context_summary, candidates, evidence_paths)
            
            # Add metadata
            result["metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "workflow_state": workflow_state,
                "gate_results": gate_results,
                "handoff_log": handoff_log
            }
            
            # Log the result
            self._log_decision(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in post-run analysis: {e}")
            error_result = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "chosen": {"id": "error", "action_type": "ERROR", "final_score": 0.0},
                "rationale": f"Error occurred during post-run analysis: {e}",
                "evidence_paths": []
            }
            self._log_decision(error_result)
            return error_result
    
    def _log_decision(self, result: Dict[str, Any]) -> None:
        """Log decision result to logs/decisions/ with timestamp filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.json"
        log_file = self.logs_dir / filename
        
        try:
            with open(log_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Decision logged to {log_file}")
        except Exception as e:
            logger.error(f"Failed to log decision: {e}")

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Orchestrator Post-Run Tool")
    parser.add_argument("--base-path", type=str, default=".", help="Base path for the project")
    parser.add_argument("--output", type=str, help="Output file for results (optional)")
    
    args = parser.parse_args()
    
    orchestrator = OrchestratorPostRun(args.base_path)
    result = orchestrator.run_post_run_analysis()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
