from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List

from app.domain.state import PersonalWishesState
from app.services.session_store import SessionStore, InMemorySessionStore
from app.services.llm_provider import LLMProvider
from app.services.orchestrator import ConversationOrchestrator
from app.services.document_generator import generate_document
from app.services.state_engine import process_changes
from app.domain.engine import FieldChange
from app.core.config import settings

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Dependency Injection setup
# In a real app this would use a more robust DI container
_global_store = InMemorySessionStore()

def get_session_store() -> SessionStore:
    return _global_store

def get_llm_provider() -> LLMProvider:
    from app.services.universal_provider import UniversalProvider
    return UniversalProvider()

def get_orchestrator(
    store: SessionStore = Depends(get_session_store),
    provider: LLMProvider = Depends(get_llm_provider)
) -> ConversationOrchestrator:
    return ConversationOrchestrator(store, provider)


class CreateSessionResponse(BaseModel):
    session_id: str

class MessageRequest(BaseModel):
    content: str

class OrchestrationAPIResponse(BaseModel):
    reply: str
    document: str
    state: PersonalWishesState
    recent_audit: List[Any] = []
    conflicts: List[Any] = []

class StateUpdateAPIResponse(BaseModel):
    state: PersonalWishesState
    recent_audit: List[Any] = []

class StateUpdateAPIRequest(BaseModel):
    changes: list[FieldChange]


@router.post("", response_model=CreateSessionResponse)
def create_session(store: SessionStore = Depends(get_session_store)):
    session = store.create_session()
    return CreateSessionResponse(session_id=session.session_id)


@router.post("/{session_id}/messages", response_model=OrchestrationAPIResponse)
async def send_message(
    session_id: str,
    request: MessageRequest,
    orchestrator: ConversationOrchestrator = Depends(get_orchestrator)
):
    try:
        response = await orchestrator.process_message(session_id, request.content)
        return OrchestrationAPIResponse(
            reply=response.reply,
            document=response.document,
            state=response.state,
            recent_audit=response.recent_audit,
            conflicts=response.conflicts
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{session_id}")
def get_session(session_id: str, store: SessionStore = Depends(get_session_store)):
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/{session_id}/state", response_model=PersonalWishesState)
def get_state(session_id: str, store: SessionStore = Depends(get_session_store)):
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.state


@router.get("/{session_id}/document")
def get_document(session_id: str, store: SessionStore = Depends(get_session_store)):
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"document": generate_document(session.state)}


@router.patch("/{session_id}/state", response_model=StateUpdateAPIResponse)
def update_state(
    session_id: str,
    request: StateUpdateAPIRequest,
    store: SessionStore = Depends(get_session_store)
):
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    update_result = process_changes(session.state, request.changes)
    session.state = update_result.new_state
    session.activity_log.extend(update_result.audit_log)
    store.save_session(session)
    
    return StateUpdateAPIResponse(state=session.state, recent_audit=update_result.audit_log)
