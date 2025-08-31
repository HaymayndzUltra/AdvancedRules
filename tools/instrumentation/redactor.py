#!/usr/bin/env python3
"""
Redaction and sanitization module for sensitive data in logs and reports.
Provides filters for PII, secrets, and other sensitive information.
"""
from __future__ import annotations
import re
import json
from typing import Any, Dict, List, Pattern, Union
from pathlib import Path

# Patterns for sensitive data detection
PATTERNS: Dict[str, Pattern] = {
    # Authentication & Secrets
    'api_key': re.compile(r'(?i)(api[_\-]?key|apikey)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9\-_]+)["\']?'),
    'password': re.compile(r'(?i)(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s"\',]+)["\']?'),
    'token': re.compile(r'(?i)(token|bearer|auth)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9\-_.]{6,})["\']?'),
    'secret': re.compile(r'(?i)(secret|private[_\-]?key)["\']?\s*[:=]\s*["\']?([^\s"\',]+)["\']?'),
    'credential': re.compile(r'(?i)(credential|cred)["\']?\s*[:=]\s*["\']?([^\s"\',]+)["\']?'),
    
    # Personal Information
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
    'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
    
    # Network & Infrastructure
    'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    'jwt': re.compile(r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'),
    
    # File paths with user info
    'home_path': re.compile(r'/home/[a-zA-Z0-9_-]+/'),
    'users_path': re.compile(r'/Users/[a-zA-Z0-9_-]+/'),
}

# Fields that should always be redacted in JSON/dict structures
SENSITIVE_FIELDS = {
    'password', 'passwd', 'pwd', 'secret', 'token', 'api_key', 'apikey',
    'private_key', 'privatekey', 'credential', 'cred', 'auth', 'authorization',
    'ssn', 'social_security', 'credit_card', 'card_number', 'cvv',
    'email', 'phone', 'phone_number', 'address', 'home_address'
}

class Redactor:
    """Handles redaction of sensitive information from various data types."""
    
    def __init__(self, patterns: Dict[str, Pattern] = None, sensitive_fields: set = None):
        self.patterns = patterns or PATTERNS
        self.sensitive_fields = sensitive_fields or SENSITIVE_FIELDS
        self.redaction_stats = {'total': 0, 'by_type': {}}
    
    def redact_string(self, text: str, placeholder: str = "[REDACTED]") -> str:
        """Redact sensitive patterns from a string."""
        if not text:
            return text
        
        redacted = text
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(redacted)
            if matches:
                # For patterns with groups, replace the sensitive part
                if pattern_name in ['api_key', 'password', 'token', 'secret', 'credential']:
                    # These patterns capture the key and value separately
                    for match in pattern.finditer(redacted):
                        if match.groups():
                            # Replace the value part, keep the key visible
                            full_match = match.group(0)
                            key_part = match.group(1) if len(match.groups()) > 0 else ""
                            redacted = redacted.replace(full_match, f"{key_part}={placeholder}")
                else:
                    # For other patterns, replace the entire match
                    redacted = pattern.sub(placeholder, redacted)
                
                self.redaction_stats['total'] += len(matches)
                self.redaction_stats['by_type'][pattern_name] = \
                    self.redaction_stats['by_type'].get(pattern_name, 0) + len(matches)
        
        return redacted
    
    def redact_dict(self, data: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
        """Redact sensitive fields from a dictionary."""
        if not data:
            return data
        
        redacted = {}
        for key, value in data.items():
            # Check if the key itself is sensitive
            if any(s in key.lower() for s in self.sensitive_fields):
                redacted[key] = "[REDACTED]"
                self.redaction_stats['total'] += 1
                self.redaction_stats['by_type']['field'] = \
                    self.redaction_stats['by_type'].get('field', 0) + 1
            elif isinstance(value, str):
                redacted[key] = self.redact_string(value)
            elif isinstance(value, dict) and deep:
                redacted[key] = self.redact_dict(value, deep=True)
            elif isinstance(value, list) and deep:
                redacted[key] = self.redact_list(value, deep=True)
            else:
                redacted[key] = value
        
        return redacted
    
    def redact_list(self, data: List[Any], deep: bool = True) -> List[Any]:
        """Redact sensitive information from a list."""
        if not data:
            return data
        
        redacted = []
        for item in data:
            if isinstance(item, str):
                redacted.append(self.redact_string(item))
            elif isinstance(item, dict) and deep:
                redacted.append(self.redact_dict(item, deep=True))
            elif isinstance(item, list) and deep:
                redacted.append(self.redact_list(item, deep=True))
            else:
                redacted.append(item)
        
        return redacted
    
    def redact_json(self, json_str: str) -> str:
        """Redact sensitive information from a JSON string."""
        try:
            data = json.loads(json_str)
            if isinstance(data, dict):
                redacted_data = self.redact_dict(data)
            elif isinstance(data, list):
                redacted_data = self.redact_list(data)
            else:
                redacted_data = data
            return json.dumps(redacted_data)
        except json.JSONDecodeError:
            # If not valid JSON, treat as string
            return self.redact_string(json_str)
    
    def redact_file(self, file_path: Path, output_path: Path = None) -> Path:
        """Redact sensitive information from a file."""
        content = file_path.read_text(encoding='utf-8')
        
        # Determine file type and apply appropriate redaction
        if file_path.suffix in ['.json', '.jsonl']:
            if file_path.suffix == '.jsonl':
                # Handle JSONL files line by line
                lines = content.strip().split('\n')
                redacted_lines = [self.redact_json(line) for line in lines if line]
                redacted_content = '\n'.join(redacted_lines)
            else:
                redacted_content = self.redact_json(content)
        else:
            # Treat as plain text
            redacted_content = self.redact_string(content)
        
        # Write to output
        if output_path is None:
            output_path = file_path.with_suffix(file_path.suffix + '.redacted')
        
        output_path.write_text(redacted_content, encoding='utf-8')
        return output_path
    
    def get_stats(self) -> Dict[str, Any]:
        """Get redaction statistics."""
        return self.redaction_stats.copy()
    
    def reset_stats(self) -> None:
        """Reset redaction statistics."""
        self.redaction_stats = {'total': 0, 'by_type': {}}


# Global redactor instance
_global_redactor = Redactor()

def redact(data: Union[str, dict, list]) -> Union[str, dict, list]:
    """Convenience function to redact any supported data type."""
    if isinstance(data, str):
        return _global_redactor.redact_string(data)
    elif isinstance(data, dict):
        return _global_redactor.redact_dict(data)
    elif isinstance(data, list):
        return _global_redactor.redact_list(data)
    else:
        return data

def redact_dict(data: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
    """Convenience function to redact a dictionary."""
    return _global_redactor.redact_dict(data, deep=deep)

def redact_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive information from an event dictionary while preserving structure."""
    # Preserve important fields that should not be redacted
    preserved_fields = {'type', 'timestamp', 'correlation_id', 'trace_id', 'role', 'command_id'}
    
    redacted = {}
    for key, value in event.items():
        if key in preserved_fields:
            redacted[key] = value
        elif any(s in key.lower() for s in SENSITIVE_FIELDS):
            # Key itself is sensitive
            redacted[key] = "[REDACTED]"
        else:
            if isinstance(value, (dict, list, str)):
                redacted[key] = redact(value)
            else:
                redacted[key] = value
    
    return redacted

def get_redaction_stats() -> Dict[str, Any]:
    """Get global redaction statistics."""
    return _global_redactor.get_stats()

def reset_redaction_stats() -> None:
    """Reset global redaction statistics."""
    _global_redactor.reset_stats()