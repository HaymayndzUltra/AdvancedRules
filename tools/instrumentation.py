#!/usr/bin/env python3
"""
Drop-in helpers for instrumenting runner/personas
Provides a convenient interface to the metrics collector
"""

from observability import collector as obs


class instr:
    """
    Instrumentation helpers for quick metrics integration
    
    Usage:
        # Flow lifecycle
        instr.flow_start(flow_id, persona, exec_mode, branch)
        instr.flow_end(flow_id, persona, exec_mode, branch, success=True)
        
        # Step timing
        with instr.step(flow_id, step_id, persona, model="gpt-4"):
            # execute step logic
            pass
        
        # Retry tracking
        instr.retry(flow_id, step_id, persona)
        
        # Token tracking
        instr.tokens_in(model="gpt-4", persona="CODER_AI", n=1500)
        instr.tokens_out(model="gpt-4", persona="CODER_AI", n=800)
    """
    
    @staticmethod
    def flow_start(flow_id, persona, exec_mode, branch):
        """Mark the start of a flow execution"""
        obs.flow_start(flow_id, persona, exec_mode, branch)
    
    @staticmethod
    def flow_end(flow_id, persona, exec_mode, branch, success: bool, reason="ok"):
        """Mark the end of a flow execution"""
        obs.flow_end(flow_id, persona, exec_mode, branch, success, reason)
    
    @staticmethod
    def step(flow_id, step_id, persona, model="unknown", exec_mode="dry_run"):
        """
        Context manager for timing step execution
        
        Usage:
            with instr.step(flow_id, step_id, persona, model="gpt-4"):
                # step execution code here
                pass
        """
        return obs.step_timer(flow_id, step_id, persona, model, exec_mode)
    
    @staticmethod
    def retry(flow_id, step_id, persona):
        """Record a retry event for a step"""
        obs.add_retry(flow_id, step_id, persona)
    
    @staticmethod
    def tokens_in(model, persona, n):
        """Record input tokens consumed"""
        obs.add_tokens("in", model, persona, n)
    
    @staticmethod
    def tokens_out(model, persona, n):
        """Record output tokens generated"""
        obs.add_tokens("out", model, persona, n)


# Convenience aliases
flow_start = instr.flow_start
flow_end = instr.flow_end
step = instr.step
retry = instr.retry
tokens_in = instr.tokens_in
tokens_out = instr.tokens_out


# Example integration patterns
def example_flow_integration():
    """
    Example showing how to instrument a flow
    """
    flow_id = "feature_request_to_pr"
    persona = "CODER_AI"
    exec_mode = "dry_run"
    branch = "feature/metrics"
    
    # Start flow
    instr.flow_start(flow_id, persona, exec_mode, branch)
    
    try:
        # Execute steps with timing
        with instr.step(flow_id, "step_001", persona, model="gpt-4", exec_mode=exec_mode):
            # Step logic here
            time.sleep(0.5)  # simulate work
            
        # Record token usage
        instr.tokens_in(model="gpt-4", persona=persona, n=1500)
        instr.tokens_out(model="gpt-4", persona=persona, n=800)
        
        # Simulate retry
        instr.retry(flow_id, "step_002", persona)
        
        # Complete successfully
        instr.flow_end(flow_id, persona, exec_mode, branch, success=True)
        
    except Exception as e:
        # Record failure
        instr.flow_end(flow_id, persona, exec_mode, branch, success=False, reason=type(e).__name__)
        raise


if __name__ == "__main__":
    import time
    print("Running instrumentation example...")
    example_flow_integration()
    print("Example complete")