#!/usr/bin/env python3
"""
Tests for instrumentation, trace IDs, and redaction functionality.
"""
import json
import os
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.instrumentation.redactor import (
    Redactor, redact, redact_event, 
    get_redaction_stats, reset_redaction_stats
)


class TestRedactor:
    """Test the redaction module."""
    
    def test_redact_api_keys(self):
        """Test API key redaction."""
        redactor = Redactor()
        
        # Various API key formats
        test_cases = [
            ('api_key="sk-1234567890abcdef"', 'api_key=[REDACTED]'),
            ('API_KEY: sk_test_4242424242424242', 'API_KEY=[REDACTED]'),
            ('apikey=AKIAIOSFODNN7EXAMPLE', 'apikey=[REDACTED]'),
        ]
        
        for input_text, expected in test_cases:
            result = redactor.redact_string(input_text)
            assert '[REDACTED]' in result
            assert 'sk-1234' not in result
            assert 'AKIA' not in result
    
    def test_redact_passwords(self):
        """Test password redaction."""
        redactor = Redactor()
        
        test_cases = [
            ('password: "my_secret_pass123"', 'password=[REDACTED]'),
            ('pwd=SuperSecret!', 'pwd=[REDACTED]'),
            ('PASSWD: hunter2', 'PASSWD=[REDACTED]'),
        ]
        
        for input_text, expected in test_cases:
            result = redactor.redact_string(input_text)
            assert '[REDACTED]' in result
            assert 'my_secret' not in result
            assert 'SuperSecret' not in result
            assert 'hunter2' not in result
    
    def test_redact_personal_info(self):
        """Test PII redaction."""
        redactor = Redactor()
        
        # Email
        text = "Contact me at john.doe@example.com for details"
        result = redactor.redact_string(text)
        assert '[REDACTED]' in result
        assert 'john.doe' not in result
        
        # Phone
        text = "Call me at 555-123-4567 or (555) 987-6543"
        result = redactor.redact_string(text)
        assert '[REDACTED]' in result
        assert '555-123' not in result
        
        # SSN
        text = "SSN: 123-45-6789"
        result = redactor.redact_string(text)
        assert '[REDACTED]' in result
        assert '123-45' not in result
    
    def test_redact_dict(self):
        """Test dictionary redaction."""
        redactor = Redactor()
        
        data = {
            "username": "john_doe",
            "password": "secret123",
            "api_key": "sk-abcdef123456",
            "email": "john@example.com",
            "metadata": {
                "token": "Bearer eyJhbGciOiJIUzI1NiIs",
                "safe_field": "this is ok"
            }
        }
        
        result = redactor.redact_dict(data)
        
        assert result["username"] == "john_doe"  # Not sensitive by default
        assert result["password"] == "[REDACTED]"
        assert result["api_key"] == "[REDACTED]"
        assert "[REDACTED]" in result["email"]
        assert result["metadata"]["token"] == "[REDACTED]"
        assert result["metadata"]["safe_field"] == "this is ok"
    
    def test_redact_list(self):
        """Test list redaction."""
        redactor = Redactor()
        
        data = [
            "normal text",
            "password=secret",
            {"api_key": "sk-123456"},
            ["nested", "email@example.com"]
        ]
        
        result = redactor.redact_list(data)
        
        assert result[0] == "normal text"
        assert "[REDACTED]" in result[1]
        assert result[2]["api_key"] == "[REDACTED]"
        assert "[REDACTED]" in result[3][1]
    
    def test_redact_json(self):
        """Test JSON string redaction."""
        redactor = Redactor()
        
        json_str = json.dumps({
            "user": "admin",
            "password": "admin123",
            "config": {
                "api_key": "sk-prod-key-12345"
            }
        })
        
        result = redactor.redact_json(json_str)
        parsed = json.loads(result)
        
        assert parsed["user"] == "admin"
        assert parsed["password"] == "[REDACTED]"
        assert parsed["config"]["api_key"] == "[REDACTED]"
    
    def test_redaction_stats(self):
        """Test redaction statistics tracking."""
        reset_redaction_stats()
        
        text = "password=secret api_key=sk-123 email@test.com"
        redact(text)
        
        stats = get_redaction_stats()
        assert stats['total'] > 0
        assert 'password' in stats['by_type']
        assert 'api_key' in stats['by_type']
        assert 'email' in stats['by_type']


class TestEventRedaction:
    """Test event-specific redaction."""
    
    def test_redact_event_preserves_structure(self):
        """Test that event redaction preserves important fields."""
        event = {
            "type": "artifact_emitted",
            "timestamp": 1234567890,
            "correlation_id": "uuid-123",
            "trace_id": "trace-456",
            "role": "runner",
            "password": "secret123",
            "data": {
                "api_key": "sk-test-key"
            }
        }
        
        result = redact_event(event)
        
        # Preserved fields
        assert result["type"] == "artifact_emitted"
        assert result["timestamp"] == 1234567890
        assert result["correlation_id"] == "uuid-123"
        assert result["trace_id"] == "trace-456"
        assert result["role"] == "runner"
        
        # Redacted fields
        assert result["password"] == "[REDACTED]"
        assert result["data"]["api_key"] == "[REDACTED]"


class TestTraceInjection:
    """Test trace ID and correlation ID injection."""
    
    @patch('tools.io.fs.append_line_atomic')
    def test_event_trace_injection(self, mock_append):
        """Test that events get trace_id and correlation_id."""
        from tools.runner.io_utils import append_event
        
        # Set environment variables
        os.environ['CORRELATION_ID'] = 'test-corr-123'
        os.environ['TRACE_ID'] = 'test-trace-456'
        os.environ['ENABLE_REDACTION'] = 'false'  # Disable for this test
        
        try:
            append_event({"type": "test_event", "data": "test"})
            
            # Check the call
            assert mock_append.called
            call_args = mock_append.call_args[0]
            event_json = call_args[1]
            event = json.loads(event_json)
            
            assert event["correlation_id"] == "test-corr-123"
            assert event["trace_id"] == "test-trace-456"
            assert "timestamp" in event
            assert event["type"] == "test_event"
        finally:
            # Cleanup
            os.environ.pop('CORRELATION_ID', None)
            os.environ.pop('TRACE_ID', None)
            os.environ.pop('ENABLE_REDACTION', None)
    
    @patch('tools.io.fs.append_line_atomic')
    def test_decision_trace_injection(self, mock_append):
        """Test that decision traces get trace_id and correlation_id."""
        from tools.runner.io_utils import append_decision_trace
        
        os.environ['CORRELATION_ID'] = 'test-corr-789'
        os.environ['TRACE_ID'] = 'test-trace-012'
        os.environ['ENABLE_REDACTION'] = 'false'
        
        try:
            append_decision_trace({"type": "decision", "choice": "option_a"})
            
            assert mock_append.called
            call_args = mock_append.call_args[0]
            trace_json = call_args[1]
            trace = json.loads(trace_json)
            
            assert trace["correlation_id"] == "test-corr-789"
            assert trace["trace_id"] == "test-trace-012"
            assert "timestamp" in trace
        finally:
            os.environ.pop('CORRELATION_ID', None)
            os.environ.pop('TRACE_ID', None)
            os.environ.pop('ENABLE_REDACTION', None)
    
    @patch('tools.io.fs.append_line_atomic')
    def test_auto_generated_ids(self, mock_append):
        """Test that IDs are auto-generated if not in environment."""
        from tools.runner.io_utils import append_event
        
        # Ensure no IDs in environment
        os.environ.pop('CORRELATION_ID', None)
        os.environ.pop('TRACE_ID', None)
        os.environ['ENABLE_REDACTION'] = 'false'
        
        try:
            append_event({"type": "test"})
            
            call_args = mock_append.call_args[0]
            event = json.loads(call_args[1])
            
            # Should have auto-generated IDs
            assert "correlation_id" in event
            assert "trace_id" in event
            assert len(event["correlation_id"]) > 0
            assert len(event["trace_id"]) > 0
            # trace_id defaults to correlation_id when not set
            assert event["trace_id"] == event["correlation_id"]
        finally:
            os.environ.pop('ENABLE_REDACTION', None)


class TestRedactionIntegration:
    """Test redaction in integrated scenarios."""
    
    @patch('tools.io.fs.append_line_atomic')
    def test_event_with_redaction_enabled(self, mock_append):
        """Test that events are redacted when redaction is enabled."""
        from tools.runner.io_utils import append_event
        
        os.environ['ENABLE_REDACTION'] = 'true'
        
        try:
            event = {
                "type": "test",
                "password": "secret123",
                "api_key": "sk-test-key-123456"
            }
            
            append_event(event)
            
            call_args = mock_append.call_args[0]
            saved_event = json.loads(call_args[1])
            
            # Check redaction occurred
            assert saved_event["password"] == "[REDACTED]"
            assert saved_event["api_key"] == "[REDACTED]"
            assert saved_event["type"] == "test"  # Preserved
        finally:
            os.environ.pop('ENABLE_REDACTION', None)
    
    @patch('tools.io.fs.append_line_atomic')
    def test_event_without_redaction(self, mock_append):
        """Test that events are not redacted when disabled."""
        from tools.runner.io_utils import append_event
        
        os.environ['ENABLE_REDACTION'] = 'false'
        
        try:
            event = {
                "type": "test",
                "password": "secret123"
            }
            
            append_event(event, redact=False)
            
            call_args = mock_append.call_args[0]
            saved_event = json.loads(call_args[1])
            
            # Should not be redacted
            assert saved_event["password"] == "secret123"
        finally:
            os.environ.pop('ENABLE_REDACTION', None)
    
    def test_file_redaction(self, tmp_path):
        """Test file redaction functionality."""
        redactor = Redactor()
        
        # Create a test file with sensitive data
        test_file = tmp_path / "test.json"
        test_data = {
            "config": {
                "api_key": "sk-prod-12345",
                "password": "admin123",
                "safe_option": "enabled"
            }
        }
        test_file.write_text(json.dumps(test_data))
        
        # Redact the file
        output_file = redactor.redact_file(test_file)
        
        # Check the output
        assert output_file.exists()
        redacted_data = json.loads(output_file.read_text())
        
        assert redacted_data["config"]["api_key"] == "[REDACTED]"
        assert redacted_data["config"]["password"] == "[REDACTED]"
        assert redacted_data["config"]["safe_option"] == "enabled"
    
    def test_jsonl_file_redaction(self, tmp_path):
        """Test JSONL file redaction."""
        redactor = Redactor()
        
        # Create JSONL file
        jsonl_file = tmp_path / "events.jsonl"
        lines = [
            json.dumps({"type": "event1", "token": "Bearer abc123"}),
            json.dumps({"type": "event2", "email": "user@example.com"}),
            json.dumps({"type": "event3", "safe": "data"})
        ]
        jsonl_file.write_text('\n'.join(lines))
        
        # Redact
        output = redactor.redact_file(jsonl_file)
        
        # Check each line
        redacted_lines = output.read_text().strip().split('\n')
        assert len(redacted_lines) == 3
        
        line1 = json.loads(redacted_lines[0])
        assert line1["token"] == "[REDACTED]"
        
        line2 = json.loads(redacted_lines[1])
        assert "[REDACTED]" in line2["email"]
        
        line3 = json.loads(redacted_lines[2])
        assert line3["safe"] == "data"


class TestObservabilityRedaction:
    """Test redaction in observability reports."""
    
    @patch('tools.observability.aggregate.OUT_DIR')
    def test_aggregate_report_redaction(self, mock_out_dir, tmp_path):
        """Test that aggregate reports are redacted."""
        from tools.observability.aggregate import write_reports
        
        mock_out_dir.return_value = tmp_path
        os.environ['ENABLE_REDACTION'] = 'true'
        
        try:
            summary = {
                "counts": {"events": 10},
                "durations": {"module1": {"count": 5, "total_sec": 10, "avg_sec": 2}},
                "sensitive_data": {
                    "password": "secret123",
                    "api_key": "sk-test-key"
                }
            }
            
            # Patch OUT_DIR to use tmp_path
            import tools.observability.aggregate as agg
            original_out_dir = agg.OUT_DIR
            agg.OUT_DIR = tmp_path
            
            write_reports(summary)
            
            # Check the written file
            report_file = tmp_path / "summary.json"
            assert report_file.exists()
            
            report = json.loads(report_file.read_text())
            
            # Check redaction
            assert report["sensitive_data"]["password"] == "[REDACTED]"
            assert report["sensitive_data"]["api_key"] == "[REDACTED]"
            
            # Check stats included
            assert "redaction_stats" in report
            assert report["redaction_stats"]["total"] > 0
            
            # Restore
            agg.OUT_DIR = original_out_dir
        finally:
            os.environ.pop('ENABLE_REDACTION', None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])