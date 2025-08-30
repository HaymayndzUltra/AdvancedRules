import subprocess
import sys


def run_cli(args):
	return subprocess.run([sys.executable, "tools/orchestrator/trigger_next.py", *args], capture_output=True, text=True)


def test_trigger_help_shows_policy():
	res = run_cli(["-h"])
	out = res.stdout + res.stderr
	assert "DRY-RUN" in out.upper()
	assert "GATES" in out.upper()
	assert "ALLOWLIST" in out.upper()


def test_trigger_print_allowlist():
	res = run_cli(["--print-allowlist"]) 
	assert res.returncode == 0
	assert 'allowlist' in (res.stdout or '')