import pytest
import json
from typing import List, Dict
from app.services.session_store import InMemorySessionStore
from app.services.orchestrator import ConversationOrchestrator
from app.services.llm_provider import LLMProvider
from app.domain.state import PersonalWishesState
from app.domain.llm import LLMExtractionResult

class DynamicMockProvider(LLMProvider):
    def __init__(self):
        self.next_response = "{}"
        
    async def extract_state_changes(
        self, conversation: List[Dict[str, str]], current_state: PersonalWishesState
    ) -> LLMExtractionResult:
        return self.parse_raw_response(self.next_response, "mock-v2")

@pytest.fixture
def setup_orchestrator():
    store = InMemorySessionStore()
    provider = DynamicMockProvider()
    orchestrator = ConversationOrchestrator(store, provider)
    session = store.create_session()
    return orchestrator, provider, session

@pytest.mark.asyncio
async def test_happy_path_single_field(setup_orchestrator):
    orchestrator, provider, session = setup_orchestrator
    
    # User says "My name is Jane Smith"
    provider.next_response = json.dumps({
        "changes": [{"field": "full_name", "proposed_value": "Jane Smith", "status": "CONFIRMED"}],
        "needs_clarification": False
    })
    
    response = await orchestrator.process_message(session.session_id, "My name is Jane Smith")
    
    # Should update state
    assert response.state.full_name.value == "Jane Smith"
    # Should ask for home_address (next in line)
    assert "home address" in response.reply.lower()

@pytest.mark.asyncio
async def test_multiple_fields_in_one_answer(setup_orchestrator):
    orchestrator, provider, session = setup_orchestrator
    
    provider.next_response = json.dumps({
        "changes": [
            {"field": "full_name", "proposed_value": "Jane Smith", "status": "CONFIRMED"},
            {"field": "home_address", "proposed_value": "123 Main St", "status": "CONFIRMED"}
        ]
    })
    
    response = await orchestrator.process_message(session.session_id, "I'm Jane Smith at 123 Main St.")
    
    assert response.state.full_name.value == "Jane Smith"
    assert response.state.home_address.value == "123 Main St"
    # Next should be covers_worldwide_assets
    assert "worldwide assets" in response.reply.lower()

@pytest.mark.asyncio
async def test_missing_information(setup_orchestrator):
    # Field left blank explicitly handled by missing info priority
    orchestrator, provider, session = setup_orchestrator
    
    # LLM extracts nothing new
    provider.next_response = json.dumps({"changes": []})
    
    response = await orchestrator.process_message(session.session_id, "Hello")
    assert "full name" in response.reply.lower()

@pytest.mark.asyncio
async def test_uncertainty(setup_orchestrator):
    orchestrator, provider, session = setup_orchestrator
    
    provider.next_response = json.dumps({
        "changes": [{"field": "full_name", "proposed_value": "Jane", "status": "PROPOSED", "confidence": 0.5}]
    })
    
    response = await orchestrator.process_message(session.session_id, "I think my name is Jane.")
    
    # Should ask for confirmation, not the next field
    assert "should your full_name be recorded as 'Jane'" in response.reply

@pytest.mark.asyncio
async def test_correction(setup_orchestrator):
    orchestrator, provider, session = setup_orchestrator
    
    # Pre-populate state
    session.state.full_name.value = "Jane"
    session.state.full_name.status = "CONFIRMED"
    orchestrator.store.save_session(session)
    
    provider.next_response = json.dumps({
        "changes": [{"field": "full_name", "proposed_value": "Jane Smith", "status": "CORRECTED"}]
    })
    
    response = await orchestrator.process_message(session.session_id, "Actually, it's Jane Smith.")
    assert response.state.full_name.value == "Jane Smith"

@pytest.mark.asyncio
async def test_contradiction(setup_orchestrator):
    orchestrator, provider, session = setup_orchestrator
    
    session.state.full_name.value = "Jane"
    session.state.full_name.status = "CONFIRMED"
    orchestrator.store.save_session(session)
    
    # Silent contradiction without CORRECTED tag
    provider.next_response = json.dumps({
        "changes": [{"field": "full_name", "proposed_value": "John", "status": "CONFIRMED"}]
    })
    
    response = await orchestrator.process_message(session.session_id, "John")
    # Should reject the change and ask for clarification
    assert response.state.full_name.value == "Jane" # Still Jane
    assert "conflict" in response.reply.lower()

@pytest.mark.asyncio
async def test_malformed_llm_response(setup_orchestrator):
    orchestrator, provider, session = setup_orchestrator
    provider.next_response = "not json"
    
    response = await orchestrator.process_message(session.session_id, "Hello")
    assert "trouble processing that" in response.reply
    assert "Malformed JSON" in response.reply

@pytest.mark.asyncio
async def test_repeated_answer(setup_orchestrator):
    orchestrator, provider, session = setup_orchestrator
    
    session.state.full_name.value = "Jane"
    session.state.full_name.status = "CONFIRMED"
    orchestrator.store.save_session(session)
    
    # LLM extracts the same info
    provider.next_response = json.dumps({
        "changes": [{"field": "full_name", "proposed_value": "Jane", "status": "CONFIRMED"}]
    })
    
    response = await orchestrator.process_message(session.session_id, "Jane")
    
    # Ignores duplicate, asks the next required question (home address)
    assert response.state.full_name.value == "Jane"
    assert "home address" in response.reply.lower()
