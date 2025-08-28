import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def run(cmd):
    subprocess.check_call(cmd, cwd=str(REPO))


def test_scoring_shadow_and_trace():
    code = (
        "from tools.decision_scoring.advanced_score import score_candidates;"
        "c=[{\"id\":\"planning_from_backlog\",\"action_type\":\"COMMAND_TRIGGER\",\"risk\":\"LOW\",\"scores\":{\"intent\":0.9,\"state\":0.8,\"evidence\":0.7,\"recency\":0.6,\"pref\":0.5,\"cost\":0.1,\"risk_penalty\":0.0}}];"
        "import json; print(json.dumps(score_candidates(c, explore=True, shadow=True)))"
    )
    out = subprocess.check_output(["python3", "-c", code], cwd=str(REPO)).decode()
    data = json.loads(out)
    assert "decision" in data and "decision_trace" in data
    assert data["decision"]["type"] in {"NEXT_STEP","OPTION_SET","ASK_CLARIFY","RISK_ALERT"}


def test_governance_validator_passes():
    out = subprocess.check_output(["python3", "tools/rules/validate.py"], cwd=str(REPO)).decode()
    assert "OK: rule policy checks passed" in out

