from pydantic import BaseModel
from typing import Optional
from app.domain.state import PersonalWishesState

class StateResponse(BaseModel):
    """
    Standard response wrapper for the current session state.
    """
    session_id: str
    state: PersonalWishesState

class StateUpdateRequest(BaseModel):
    """
    Request model for partial state updates.
    The client will send a proposed PersonalWishesState to merge.
    """
    session_id: str
    # Making it optional allows the backend to handle the merge 
    # based on the current state engine implementation.
    proposed_state: PersonalWishesState
