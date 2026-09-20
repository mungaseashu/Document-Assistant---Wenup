import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_session_lifecycle():
    # 1. Create Session
    response = client.post("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    session_id = data["session_id"]
    
    # 2. Get State
    response = client.get(f"/api/sessions/{session_id}/state")
    assert response.status_code == 200
    state_data = response.json()
    assert "full_name" in state_data
    
    # 3. Get Document
    response = client.get(f"/api/sessions/{session_id}/document")
    assert response.status_code == 200
    doc_data = response.json()
    assert "document" in doc_data
    assert "FICTIONAL" in doc_data["document"]
    
    # 4. Patch State Directly
    response = client.patch(
        f"/api/sessions/{session_id}/state", 
        json={
            "changes": [
                {"field": "full_name", "proposed_value": "API User", "status": "CONFIRMED"}
            ]
        }
    )
    assert response.status_code == 200
    patch_data = response.json()
    assert patch_data["state"]["full_name"]["value"] == "API User"
    assert len(patch_data["recent_audit"]) == 1
    assert patch_data["recent_audit"][0]["field"] == "full_name"

def test_api_invalid_session():
    response = client.get("/api/sessions/invalid-id/state")
    assert response.status_code == 404

