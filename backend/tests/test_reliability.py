import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def session_id():
    response = client.post("/api/sessions")
    return response.json()["session_id"]

def get_current_state(sid):
    return client.get(f"/api/sessions/{sid}/state").json()

def test_simulator_malformed_json_preserves_state(session_id):
    initial_state = get_current_state(session_id)
    
    # Enable Simulator
    client.post("/api/dev/simulator/mode", json={"mode": "MALFORMED_JSON"})
    
    res = client.post(f"/api/sessions/{session_id}/messages", json={"content": "Hello"})
    assert res.status_code == 200
    assert "trouble processing" in res.json()["reply"]
    
    final_state = get_current_state(session_id)
    assert initial_state == final_state

def test_simulator_missing_field_preserves_state(session_id):
    initial_state = get_current_state(session_id)
    
    client.post("/api/dev/simulator/mode", json={"mode": "MISSING_FIELD"})
    
    res = client.post(f"/api/sessions/{session_id}/messages", json={"content": "Hello"})
    assert "trouble processing" in res.json()["reply"]
    assert "ValidationError" in res.json()["reply"] or "Schema Validation Error" in res.json()["reply"]
    
    final_state = get_current_state(session_id)
    assert initial_state == final_state

def test_simulator_invalid_type_preserves_state(session_id):
    initial_state = get_current_state(session_id)
    client.post("/api/dev/simulator/mode", json={"mode": "INVALID_TYPE"})
    
    res = client.post(f"/api/sessions/{session_id}/messages", json={"content": "Hello"})
    # It might fail in LLMProvider parsing or engine processing, but state MUST remain identical
    final_state = get_current_state(session_id)
    assert initial_state == final_state

def test_simulator_timeout_preserves_state(session_id):
    initial_state = get_current_state(session_id)
    client.post("/api/dev/simulator/mode", json={"mode": "TIMEOUT"})
    
    res = client.post(f"/api/sessions/{session_id}/messages", json={"content": "Hello"})
    assert "Timeout" in res.json()["reply"]
    
    final_state = get_current_state(session_id)
    assert initial_state == final_state

def test_simulator_empty_response_preserves_state(session_id):
    initial_state = get_current_state(session_id)
    client.post("/api/dev/simulator/mode", json={"mode": "EMPTY_RESPONSE"})
    
    res = client.post(f"/api/sessions/{session_id}/messages", json={"content": "Hello"})
    
    final_state = get_current_state(session_id)
    assert initial_state == final_state

def teardown_module(module):
    # Reset simulator back to normal after tests
    client.post("/api/dev/simulator/mode", json={"mode": "NORMAL"})
