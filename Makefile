.PHONY: validate phase0 phase1 phase2 phase3 phase4 phase5 clean

validate: phase0 phase1 phase2 phase3 phase4 phase5

phase0: ; bash scripts/phase0_safety.sh
phase1: ; bash scripts/phase1_planning.sh
phase2: ; bash scripts/phase2_flows.sh
phase3: ; AR_ENABLE_RAG=${AR_ENABLE_RAG} bash scripts/phase3_rag.sh
phase4: ; AR_ENABLE_METRICS=1 bash scripts/phase4_metrics.sh
phase5: ; bash scripts/phase5_queue.sh

clean:
	-pkill -f "observability.exporters.prometheus" || true
	-rm -rf .artifacts/metrics_*.txt
