from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import uuid
from app.domain.state import PersonalWishesState

class SessionData(BaseModel):
    session_id: str
    history: List[Dict[str, str]] = Field(default_factory=list)
    state: PersonalWishesState = Field(default_factory=PersonalWishesState)
    activity_log: List[Any] = Field(default_factory=list)

class SessionStore(ABC):
    @abstractmethod
    def create_session(self) -> SessionData:
        pass
        
    @abstractmethod
    def get_session(self, session_id: str) -> Optional[SessionData]:
        pass

    @abstractmethod
    def save_session(self, session: SessionData):
        pass

class InMemorySessionStore(SessionStore):
    def __init__(self):
        self._store: Dict[str, SessionData] = {}

    def create_session(self) -> SessionData:
        session_id = str(uuid.uuid4())
        session = SessionData(session_id=session_id)
        self._store[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        return self._store.get(session_id)

    def save_session(self, session: SessionData):
        self._store[session.session_id] = session
