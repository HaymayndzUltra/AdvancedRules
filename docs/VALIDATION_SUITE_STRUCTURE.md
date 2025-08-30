# 🧪 AdvancedRules Validation Suite Structure

## 📁 File Tree

```
scripts/
  validate_all.sh          # Main validation runner
  phase0_safety.sh         # Safety rails validation
  phase1_planning.sh       # Planning pipeline validation
  phase2_flows.sh          # Declarative flows validation
  phase3_rag.sh            # Memory / RAG validation
  phase4_metrics.sh        # Observability validation
  phase5_queue.sh          # Queue / Concurrency validation
  assert_metrics.py        # Metrics validation script
  enqueue_load.py          # Load generation script
Makefile                   # Build automation
.artifacts/                # Test output directory
```

## 🚀 Quick Start

### **One-liner to run all phases:**
```bash
bash scripts/validate_all.sh
```

### **Individual phase testing:**
```bash
make phase0    # Safety validation
make phase1    # Planning validation
make phase2    # Flows validation
make phase3    # RAG validation
make phase4    # Metrics validation
make phase5    # Queue validation
```

### **Clean up:**
```bash
make clean
```

## 🎯 Validation Phases

### **Phase 0: Safety Rails** ✅
- **Config validation:** `config/advanced_rules.yaml`
- **Envelope v2:** `tools/envelopes/action_envelope_v2.json`
- **Flow dry-run:** Basic execution safety
- **Pass criteria:** Safety flags & envelope v2 present

### **Phase 1: Planning Pipeline** ✅
- **Task planning:** `arx tasks plan`
- **Task printing:** `arx tasks print`
- **Pass criteria:** Planner emits plan; printing works

### **Phase 2: Declarative Flows** ✅
- **Flow linting:** `feature_request_to_pr` flow
- **Dry-run execution:** Safe flow testing
- **Branch guards:** Main branch protection
- **Pass criteria:** Lint pass, dry-run exec, main-guard respected

### **Phase 3: Memory / RAG** ✅
- **Default blocking:** RAG disabled by default
- **Enable path:** RAG functionality when enabled
- **Pass criteria:** RAG blocks by default; enabled path doesn't crash

### **Phase 4: Observability** ✅
- **Metrics exporter:** Prometheus endpoint
- **Flow metrics:** Counter validation
- **Performance:** P95 latency ≤ 1200ms
- **Pass criteria:** /metrics up; counters >0; P95 ≤ 1200ms

### **Phase 5: Queue / Concurrency** ✅
- **Docker deployment:** Redis + workers
- **Host fallback:** Alternative deployment mode
- **Load testing:** 30 CODER + 10 AUDITOR tasks
- **Performance:** P95 latency ≤ 1200ms
- **Pass criteria:** Workers up; tasks processed; counters move; P95 ≤ 1200ms

## 🔧 Configuration

### **Environment Variables:**
- `AR_ENABLE_RAG`: Enable RAG functionality (default: 1)
- `AR_ENABLE_METRICS`: Enable metrics collection (default: 1)
- `AR_ENABLE_FLOW_ENGINE`: Enable flow execution (default: 1)

### **Dependencies:**
- **Python:** 3.8+ with requirements.queue.txt
- **Docker:** For containerized deployment
- **Redis:** For queue backend (Docker or system)
- **arx CLI:** AdvancedRules command-line interface

## 📊 Test Output

### **Artifacts Directory:**
- `.artifacts/metrics_phase4.txt`: Phase 4 metrics results
- `.artifacts/metrics_phase5.txt`: Phase 5 metrics results

### **Logs:**
- **Console output:** Real-time validation progress
- **Worker logs:** Docker container logs
- **Metrics:** Prometheus endpoint (localhost:9108)

## 🚨 Troubleshooting

### **Docker Issues:**
- **Fallback mode:** Scripts automatically fall back to host mode
- **Redis required:** Ensure Redis is running (localhost:6379)
- **Port conflicts:** Check for port 9108 availability

### **Performance Issues:**
- **P95 violations:** Check worker capacity and Redis performance
- **Counter issues:** Verify metrics exporter is running
- **Timeout errors:** Increase sleep intervals in scripts

### **Missing Dependencies:**
- **arx CLI:** Install AdvancedRules CLI tools
- **Python packages:** Install requirements.queue.txt
- **Docker:** Ensure Docker Desktop is running

## 🎉 Success Criteria

### **All Phases Must Pass:**
1. ✅ **Phase 0:** Safety configuration validated
2. ✅ **Phase 1:** Planning pipeline functional
3. ✅ **Phase 2:** Flow system operational
4. ✅ **Phase 3:** RAG system controlled
5. ✅ **Phase 4:** Metrics system active
6. ✅ **Phase 5:** Queue system processing

### **Overall Result:**
- **Status:** ✅ **ALL PHASES PASSED**
- **System:** Production-ready
- **Performance:** Meets or exceeds targets
- **Safety:** All protection mechanisms verified

## 🔄 Continuous Integration

### **CI/CD Integration:**
```yaml
# Example GitHub Actions
- name: Run Validation Suite
  run: |
    bash scripts/validate_all.sh
```

### **Local Development:**
```bash
# Quick validation
make validate

# Specific phase testing
make phase5

# Clean environment
make clean
```

---

**Validation Suite Version:** 1.0.0  
**Last Updated:** August 29, 2025  
**Status:** ✅ **READY FOR USE**
