# Instrumentation Policy (Deprecated - See OBSERVABILITY_AND_INSTRUMENTATION.md)

> This policy has been consolidated. For the canonical reference, see `docs/OBSERVABILITY_AND_INSTRUMENTATION.md`.

## Overview

This document defines the instrumentation, tracing, and data sanitization policies for the AdvancedRules system. These policies ensure comprehensive observability while protecting sensitive information in logs and reports.

## Trace Identification

### Correlation ID
- **Purpose**: Links all events, state changes, and artifacts within a single execution flow
- **Generation**: UUID v4, created at the start of each orchestration
- **Propagation**: Via environment variable `CORRELATION_ID`
- **Required in**: All events, decision traces, state transitions, and artifact records

### Trace ID
- **Purpose**: Groups related correlation IDs across distributed operations
- **Generation**: UUID v4, defaults to correlation_id if not explicitly set
- **Propagation**: Via environment variable `TRACE_ID`
- **Use case**: Multi-step workflows, parent-child relationships, distributed tracing

### Implementation
```python
# Environment variables set by orchestrator
os.environ['CORRELATION_ID'] = str(uuid.uuid4())
os.environ['TRACE_ID'] = str(uuid.uuid4())

# Automatic injection in events
event = {
    "type": "decision_made",
    "correlation_id": os.environ.get('CORRELATION_ID'),
    "trace_id": os.environ.get('TRACE_ID'),
    "timestamp": time.time()
}
```

## Data Redaction

### Sensitive Data Categories

#### Authentication & Secrets
- API keys (api_key, apikey)
- Passwords (password, passwd, pwd)
- Tokens (token, bearer, auth)
- Secrets (secret, private_key)
- Credentials (credential, cred)

#### Personal Information (PII)
- Email addresses
- Phone numbers
- Social Security Numbers (SSN)
- Credit card numbers
- Home directory paths (/home/username, /Users/username)

#### Infrastructure
- JWT tokens
- IP addresses (configurable)

### Redaction Rules

1. **String Patterns**: Detected via regex and replaced with `[REDACTED]`
2. **Field Names**: Dictionary keys matching sensitive field names are automatically redacted
3. **Nested Structures**: Deep redaction traverses dictionaries and lists recursively
4. **Preservation**: Structural fields (type, timestamp, correlation_id, trace_id, role) are never redacted

### Configuration

#### Environment Variables
- `ENABLE_REDACTION`: Set to `true` (default) or `false`
- Controls redaction in:
  - Event logging (`events.jsonl`)
  - Decision traces (`decision_traces.jsonl`)
  - Aggregate reports (`summary.json`)
  - CLI outputs

#### Programmatic Control
```python
from tools.runner.io_utils import append_event

# Disable redaction for specific event
append_event(event, redact=False)

# Global redaction control
os.environ['ENABLE_REDACTION'] = 'false'
```

## Event Instrumentation

### Required Fields
Every event MUST include:
- `type`: Event type identifier
- `timestamp`: Unix timestamp (auto-added if missing)
- `correlation_id`: Execution correlation ID (auto-added from env)
- `trace_id`: Trace group ID (auto-added from env)

### Event Types
Standard event types include:
- `decision_made`: Scoring decision completed
- `state_transition`: Workflow state changed
- `artifact_emitted`: File or memory artifact created
- `gate_evaluated`: Gate check performed
- `command_executed`: Registry command run
- `error_occurred`: Error or exception

### Event Flow
```
User Request
    ↓
Orchestrator (generates correlation_id, trace_id)
    ↓
Decision Scoring → append_decision_trace()
    ↓
Gate Evaluation → append_event()
    ↓
Command Execution → append_event()
    ↓
State Transition → append_event()
    ↓
Artifacts Created → append_event() + index_record()
```

## Observability Reports

### Aggregation Levels
1. **Global Summary**: Event counts, role durations
2. **By Correlation**: Groups all events/traces by correlation_id
3. **By Trace**: Groups multiple correlations by trace_id
4. **Artifact Audit**: Hash verification, tamper detection

### Redaction in Reports
- Applied before writing to disk
- Statistics tracked and included in report
- Original data never persisted when redaction enabled

### Report Structure
```json
{
  "counts": {...},
  "durations": {...},
  "by_correlation": {...},
  "artifact_audit": {...},
  "redaction_stats": {
    "total": 15,
    "by_type": {
      "password": 3,
      "api_key": 2,
      "email": 5,
      "token": 5
    }
  }
}
```

## Security Considerations

### Log Rotation
- Implement log rotation to prevent unbounded growth
- Archive old logs with encryption if needed
- Consider retention policies for compliance

### Access Control
- Restrict access to unredacted logs
- Use file permissions: 600 for sensitive logs
- Consider separate storage for redacted vs unredacted

### Audit Trail
- Redaction operations are logged
- Statistics track what was redacted
- Original correlation/trace IDs preserved for forensics

## Testing Requirements

### Unit Tests
- Redaction patterns for all sensitive data types
- Trace ID injection and propagation
- Event structure validation
- Statistics tracking

### Integration Tests
- End-to-end trace following
- Cross-component correlation
- Report generation with redaction
- CLI output sanitization

### Test Coverage
Required coverage areas:
- `tools/instrumentation/redactor.py`: 90%+
- Event injection points: 100%
- Report generation: 85%+

## Compliance Notes

### GDPR Considerations
- PII redaction helps with "privacy by design"
- Correlation IDs enable "right to erasure" tracking
- Audit logs support accountability requirements

### Industry Standards
- Follows OpenTelemetry trace/span concepts
- Compatible with distributed tracing systems
- JSON structured logging for analysis tools

## Operational Guidelines

### Enabling Full Instrumentation
```bash
export ENABLE_REDACTION=true
export CORRELATION_ID=$(uuidgen)
export TRACE_ID=$(uuidgen)
```

### Debugging Without Redaction
```bash
# Temporarily disable for debugging
export ENABLE_REDACTION=false
./tools/orchestrator/trigger_next.py --dry-run
```

### Analyzing Traces
```bash
# Generate aggregate report
python tools/observability/aggregate.py

# View specific correlation
grep "correlation_id.*uuid-123" logs/events.jsonl | jq .
```

## Monitoring Metrics

Key metrics to monitor:
- Events per second
- Redaction rate (redacted fields / total fields)
- Trace completion rate
- Correlation chain length
- Error event frequency

## Future Enhancements

Planned improvements:
1. Configurable redaction patterns via config file
2. Sampling strategies for high-volume events  
3. Trace context propagation via headers
4. Integration with APM tools (Datadog, New Relic)
5. Machine learning for anomaly detection
6. Real-time streaming to observability platforms

## References

- [OpenTelemetry Specification](https://opentelemetry.io/docs/reference/specification/)
- [GDPR Technical Measures](https://gdpr-info.eu/art-32-gdpr/)
- [OWASP Logging Guide](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)