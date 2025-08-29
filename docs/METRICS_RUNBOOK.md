# ARX Metrics System Runbook

## Overview

The ARX Metrics System provides comprehensive observability for flow execution using Prometheus metrics. It captures flow lifecycle events, step timing, retries, and token usage with strict PII-free labels.

## Quick Start

### 1. Enable Metrics

```bash
# Enable metrics collection
export AR_ENABLE_METRICS=1
```

### 2. Start Metrics Server

```bash
# Start Prometheus metrics endpoint (default port 9108)
arx obs serve --port 9108

# Or use Python directly
python -m observability.exporters.prometheus --port 9108
```

### 3. Run a Flow

```bash
# Run any flow (dry-run is fine for testing)
export AR_ENABLE_FLOW_ENGINE=1
arx flow run --flow=feature_request_to_pr --task-id=T-0099 --dry-run
```

### 4. Check Metrics

```bash
# View raw metrics
curl -s http://localhost:9108/metrics | grep -E "ar_flow_|ar_step_|ar_tokens_"

# Or open in browser
open http://localhost:9108/metrics
```

## Available Metrics

### Flow-Level Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `ar_flow_started_total` | Counter | `flow_id`, `persona`, `exec_mode`, `branch` | Number of flows started |
| `ar_flow_success_total` | Counter | `flow_id`, `persona`, `exec_mode`, `branch` | Number of flows completed successfully |
| `ar_flow_fail_total` | Counter | `flow_id`, `persona`, `exec_mode`, `branch`, `reason` | Number of flows that failed |

### Step-Level Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `ar_step_latency_ms` | Histogram | `flow_id`, `step_id`, `persona`, `model`, `exec_mode` | Step execution latency in milliseconds |
| `ar_step_retries_total` | Counter | `flow_id`, `step_id`, `persona` | Number of step retries |
| `ar_inflight_steps` | Gauge | `flow_id` | Number of currently running steps |

### Resource Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `ar_tokens_total` | Counter | `direction`, `model`, `persona` | Token usage (`direction` = `in`\|`out`) |

## Labels Reference

All labels are sanitized to be PII-free:
- **flow_id**: Flow identifier (e.g., `feature_request_to_pr`)
- **persona**: AI persona name (e.g., `CODER_AI`)
- **exec_mode**: Execution mode (`dry_run` or `live`)
- **branch**: Git branch name
- **step_id**: Step/node identifier within flow
- **model**: Model name (e.g., `gpt-4`, `claude-3`)
- **direction**: Token direction (`in` for input, `out` for output)
- **reason**: Failure reason (exception class name)

## Grafana Integration

### Import Dashboard

1. Copy `observability/dashboards/flows_overview.json`
2. In Grafana: **Dashboards** → **Import** → Upload JSON
3. Configure Prometheus datasource
4. Set refresh interval to 30s

### Available Panels

- **Flow Success Rate**: Real-time success percentage (5m window)
- **Step P95 Latency**: 95th percentile step execution times
- **Retries per Step**: Retry counts by step (1h window)
- **Tokens by Model**: Token usage breakdown

### Key Queries

```promql
# Flow success rate (5m)
100 * (sum(rate(ar_flow_success_total[5m])) / clamp_min(sum(rate(ar_flow_started_total[5m])), 1e-9))

# Step P95 latency
histogram_quantile(0.95, sum by (le, flow_id, step_id) (rate(ar_step_latency_ms_bucket[5m])))

# Token usage by model
sum by (model, persona) (increase(ar_tokens_total{direction="out"}[1h]))
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AR_ENABLE_METRICS` | `""` | Set to `"1"` to enable metrics |
| `AR_METRICS_PORT` | `9108` | Metrics server port |
| `AR_METRICS_ADDR` | `0.0.0.0` | Metrics server bind address |

### Features Toggle

```python
# Alternative to environment variable
# In config file (if implemented):
features:
  metrics_v2: true
```

## Usage Examples

### Basic Flow Instrumentation

```python
from tools.instrumentation import instr

# Start flow
instr.flow_start("my_flow", "CODER_AI", "dry_run", "main")

try:
    # Time a step
    with instr.step("my_flow", "step_1", "CODER_AI", "gpt-4"):
        # Your step logic here
        pass
    
    # Record token usage
    instr.tokens_in("gpt-4", "CODER_AI", 1500)
    instr.tokens_out("gpt-4", "CODER_AI", 800)
    
    # Complete successfully
    instr.flow_end("my_flow", "CODER_AI", "dry_run", "main", success=True)
    
except Exception as e:
    # Record failure
    instr.flow_end("my_flow", "CODER_AI", "dry_run", "main", 
                  success=False, reason=type(e).__name__)
```

### Custom Metrics Collection

```python
from observability.collector import add_tokens, step_timer

# Direct API usage
with step_timer("flow_1", "custom_step", "CODER_AI", "claude-3"):
    # Custom step logic
    pass

add_tokens("out", "claude-3", "CODER_AI", 1200)
```

## Expected Output

After running a flow, `/metrics` should contain:

```
ar_flow_started_total{branch="feature_x",exec_mode="dry_run",flow_id="feature_request_to_pr",persona="CODER_AI"} 1
ar_flow_success_total{branch="feature_x",exec_mode="dry_run",flow_id="feature_request_to_pr",persona="CODER_AI"} 1
ar_step_latency_ms_bucket{flow_id="feature_request_to_pr",step_id="step_001",persona="CODER_AI",model="gpt-4",exec_mode="dry_run",le="800"} 1
ar_step_retries_total{flow_id="feature_request_to_pr",step_id="step_003",persona="CODER_AI"} 2
ar_tokens_total{direction="out",model="gpt-4",persona="CODER_AI"} 312
```

## Troubleshooting

### Metrics Not Appearing

1. **Check environment**: `echo $AR_ENABLE_METRICS`
2. **Verify imports**: Run test script with `python test_metrics_integration.py`
3. **Check logs**: Look for import errors or configuration issues

### Server Not Starting

1. **Port conflicts**: Try different port with `--port 9109`
2. **Firewall**: Ensure port is accessible
3. **Dependencies**: Install `pip install prometheus_client`

### Grafana Issues

1. **Datasource**: Ensure Prometheus points to `http://localhost:9108`
2. **Queries**: Test PromQL queries in Prometheus web UI first
3. **Time range**: Adjust dashboard time range (metrics need activity)

## Performance Notes

- **Overhead**: Near-zero when `AR_ENABLE_METRICS!=1`
- **Labels**: Auto-sanitized and truncated to 64 chars
- **Memory**: Uses Prometheus client default registry (efficient)
- **Network**: Single HTTP endpoint, no external dependencies

## Security

- **PII-Free**: All labels sanitized to remove user content
- **Local Only**: Metrics server binds to localhost by default
- **No Auth**: Metrics endpoint has no authentication (standard Prometheus pattern)

## Development

### Adding New Metrics

1. **Define metric** in `observability/collector.py`
2. **Add helper** in `tools/instrumentation.py`
3. **Update tests** in `test_metrics_integration.py`
4. **Document** in this runbook

### Testing

```bash
# Run integration tests
python test_metrics_integration.py

# Manual testing
export AR_ENABLE_METRICS=1
arx obs serve &
arx flow run --flow=test_flow --dry-run
curl -s http://localhost:9108/metrics | grep ar_
```

## Support

For issues or questions:
1. Check this runbook
2. Run `python test_metrics_integration.py`
3. Review logs with debug enabled
4. File issue with metrics output sample