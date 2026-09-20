from pydantic import BaseModel, Field
from typing import List, Optional
from app.domain.engine import FieldChange

class LLMExtractionResponse(BaseModel):
    """
    Strict response schema expected from the LLM.
    """
    changes: List[FieldChange] = Field(..., description="List of proposed state updates.")
    uncertainties: List[str] = Field(default_factory=list, description="List of uncertain statements to flag to the user.")
    potential_conflicts: List[str] = Field(default_factory=list, description="List of conflicts the LLM detected.")
    needs_clarification: bool = Field(default=False, description="True if the LLM cannot confidently extract fields and needs to ask the user.")
    suggested_question: Optional[str] = Field(default=None, description="A follow-up question the LLM proposes to ask the user.")

class LLMExtractionResult(BaseModel):
    """
    Wrapper for the LLM output providing graceful degradation metadata.
    """
    success: bool
    data: Optional[LLMExtractionResponse] = None
    error: Optional[str] = None
    prompt_version: str
