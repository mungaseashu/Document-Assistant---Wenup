from pydantic import BaseModel, Field
from typing import Any, List, Optional
from enum import Enum
from app.domain.state import FieldStatus, PersonalWishesState

class FieldChange(BaseModel):
    """
    Represents a single proposed change to the state extracted by the LLM.
    """
    field: str
    proposed_value: Any
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    status: FieldStatus = FieldStatus.PROPOSED
    reason: Optional[str] = None
    source_message_id: Optional[str] = None

class ActionTaken(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_CONFLICT = "REJECTED_CONFLICT"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
    IGNORED_DUPLICATE = "IGNORED_DUPLICATE"
    REJECTED_VALIDATION = "REJECTED_VALIDATION"

from datetime import datetime

class AuditDecision(BaseModel):
    """
    Internal decision/audit representation for transparency.
    """
    field: str
    action: ActionTaken
    reason: str
    proposed_value: Any = None
    previous_value: Any = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StateUpdateResult(BaseModel):
    """
    The result of processing a batch of proposed changes.
    """
    accepted_changes: List[AuditDecision]
    rejected_changes: List[AuditDecision]
    confirmation_required: List[AuditDecision]
    conflicts: List[AuditDecision]
    audit_log: List[AuditDecision]
    new_state: PersonalWishesState
