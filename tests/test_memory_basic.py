import os, subprocess, json

def test_flag_blocks_by_default():
    """Test that memory operations are blocked when RAG is disabled by default"""
    out = subprocess.run(["arx","memory","stats"], capture_output=True, text=True).stdout +\
          subprocess.run(["arx","memory","query","--persona","CODER_AI","--query","x","--k","1"], capture_output=True, text=True).stdout
    assert "disabled" in out or "Set AR_ENABLE_RAG" in out

def test_unique_ids_on_reindex(monkeypatch):
    """Test that reindexing doesn't crash despite duplicate IDs"""
    env = dict(os.environ, AR_ENABLE_RAG="1")
    # First reindex - should work
    subprocess.check_call(["arx","memory","index","--src",".","--namespaces","coder","--reindex"], env=env)
    # Second reindex - should not crash even with duplicate IDs
    subprocess.check_call(["arx","memory","index","--src",".","--namespaces","coder","--reindex"], env=env)  # no crash

def test_persona_isolation():
    """Test that personas cannot access unauthorized namespaces"""
    env = dict(os.environ, AR_ENABLE_RAG="1")
    # CODER_AI should not be able to access docs namespace
    result = subprocess.run(["arx","memory","query","--persona","CODER_AI","--query","README","--k","3"],
                          capture_output=True, text=True, env=env)
    # Should not find docs content (though may show some coder content)
    output = result.stdout.lower()
    # If docs content appears, it would indicate a security breach
    assert "docs" not in output or "no results" in output

def test_model_id_validation():
    """Test that model ID format is valid"""
    import yaml
    with open('config/advanced_rules.yaml', 'r') as f:
        config = yaml.safe_load(f)
    model = config.get('rag', {}).get('embedding_model', 'BAAI/bge-m3')
    assert model.startswith(('BAAI/', 'sentence-transformers/')), f'Invalid model ID: {model}'
