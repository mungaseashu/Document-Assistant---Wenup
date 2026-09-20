from enum import Enum
from typing import Generic, TypeVar, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

T = TypeVar('T')

class FieldStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    PROPOSED = "PROPOSED"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    CORRECTED = "CORRECTED"

class StateField(BaseModel, Generic[T]):
    """
    Metadata wrapper for any piece of structured state.
    Provides reliability tracking and auditability.
    """
    value: Optional[T] = None
    status: FieldStatus = FieldStatus.UNKNOWN
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Optional[str] = None
    last_updated: Optional[datetime] = None
    evidence: Optional[str] = None

    @model_validator(mode='after')
    def validate_unknown_has_no_value(self):
        # UNKNOWN fields cannot silently hold fabricated values
        if self.status == FieldStatus.UNKNOWN and self.value is not None:
            # If a value is somehow provided but marked unknown, clear it or raise.
            # We raise to enforce strict correctness.
            raise ValueError("UNKNOWN fields must have a None value")
        return self

class PersonalWishesState(BaseModel):
    """
    The Single Source of Truth for the Document Intake process.
    """
    full_name: StateField[str] = Field(default_factory=lambda: StateField[str]())
    home_address: StateField[str] = Field(default_factory=lambda: StateField[str]())
    covers_worldwide_assets: StateField[bool] = Field(default_factory=lambda: StateField[bool]())
    has_children: StateField[bool] = Field(default_factory=lambda: StateField[bool]())
    children_names: StateField[List[str]] = Field(default_factory=lambda: StateField[List[str]]())
    
    executor_name: StateField[str] = Field(default_factory=lambda: StateField[str]())
    executor_relationship: StateField[str] = Field(default_factory=lambda: StateField[str]())
    
    specific_gifts: StateField[List[str]] = Field(default_factory=lambda: StateField[List[str]]())
    additional_wishes: StateField[List[str]] = Field(default_factory=lambda: StateField[List[str]]())

    @model_validator(mode='after')
    def enforce_business_rules(self):
        # Rule 1: children_names only meaningful if has_children is True
        if self.has_children.value is not True:
            # If they provided children_names but has_children is False or UNKNOWN
            if self.children_names.value is not None and len(self.children_names.value) > 0:
                raise ValueError("children_names cannot be populated unless has_children is explicitly True")

        # Rule 2: executor_relationship should not exist without an executor
        if not self.executor_name.value:
            if self.executor_relationship.value is not None:
                raise ValueError("executor_relationship cannot exist without an executor_name")

        # Rule 3: Contradiction checking for executor relationship
        if self.has_children.value is False and self.executor_relationship.value is not None:
            rel = self.executor_relationship.value.lower()
            if "son" in rel or "daughter" in rel or "child" in rel:
                raise ValueError(f"You stated you have no children, but named your '{self.executor_relationship.value}' as executor.")

        return self
