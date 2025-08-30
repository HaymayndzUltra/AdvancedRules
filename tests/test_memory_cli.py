import json
import sys
from pathlib import Path

# Test the memory CLI commands
def test_memory_validate_command(tmp_path, monkeypatch):
    """Test arx memory validate command."""
    # Setup test environment
    mb = tmp_path / "memory-bank" / "business"
    mb.mkdir(parents=True, exist_ok=True)
    
    # Monkeypatch ROOT to use tmp_path
    import cli.memory
    monkeypatch.setattr(cli.memory, 'ROOT', tmp_path)
    
    # Create valid and invalid files
    valid_file = mb / "test_valid.json"
    valid_file.write_text('{"test": "data"}')
    
    invalid_file = mb / "client_score.json"
    invalid_file.write_text('{"incomplete": "data"}')  # Missing required fields
    
    # Import and run
    from cli.memory import main
    result = main(['arx', 'memory', 'validate', str(mb)])
    
    # Should return non-zero due to invalid file
    assert result != 0
    
    # Check report was created
    report_path = tmp_path / "memory-bank" / "validation_report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text())
    assert report["invalid"] > 0


def test_memory_repair_command(tmp_path, monkeypatch):
    """Test arx memory repair command."""
    # Setup test environment
    mb = tmp_path / "memory-bank" / "business"
    mb.mkdir(parents=True, exist_ok=True)
    
    # Monkeypatch ROOT to use tmp_path
    import cli.memory
    monkeypatch.setattr(cli.memory, 'ROOT', tmp_path)
    
    # Create a file with orphaned .tmp
    target = mb / "data.json"
    tmp_file = Path(str(target) + ".tmp")
    tmp_file.write_text('{"recovered": true}')
    
    # Run repair
    from cli.memory import main
    result = main(['arx', 'memory', 'repair', str(mb)])
    
    assert result == 0
    assert target.exists()
    assert not tmp_file.exists()
    
    # Check content was recovered
    data = json.loads(target.read_text())
    assert data["recovered"] is True
    
    # Check log was created
    log_path = tmp_path / "memory-bank" / "repair_log.json"
    assert log_path.exists()