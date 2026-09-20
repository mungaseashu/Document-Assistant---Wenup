import pytest
from app.domain.state import PersonalWishesState, StateField, FieldStatus
from app.api.schemas import StateResponse

def test_serialization_deserialization():
    state = PersonalWishesState(
        full_name=StateField[str](
            value="Jane Smith",
            status=FieldStatus.CONFIRMED,
            confidence=0.99
        ),
        has_children=StateField[bool](
            value=False,
            status=FieldStatus.PROPOSED,
            source="LLM_Extracted"
        )
    )

    response = StateResponse(session_id="session_123", state=state)
    
    # Serialize to JSON string
    json_data = response.model_dump_json()

    # Deserialize back from JSON
    deserialized_response = StateResponse.model_validate_json(json_data)

    # Assert equality
    assert deserialized_response.session_id == "session_123"
    assert deserialized_response.state.full_name.value == "Jane Smith"
    assert deserialized_response.state.has_children.value is False
    assert deserialized_response.state.has_children.source == "LLM_Extracted"
