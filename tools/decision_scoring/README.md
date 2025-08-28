# tools/decision_scoring/

- Purpose: Rank candidate actions and produce a safe, explainable decision.

## v3 Features
- Calibration (calibration.json), thresholds (thresholds.json), weights (weights.json)
- Exploration on OPTION_SET, shadow mode, decision_trace
- Metrics in logs/decision_metrics.json; calibrate.py to adjust values

## Commands
```bash
python3 tools/decision_scoring/advanced_score.py
python3 tools/decision_scoring/calibrate.py
```