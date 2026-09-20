from typing import List, Dict, Any
from app.domain.state import PersonalWishesState, StateField, FieldStatus
from app.domain.engine import FieldChange, StateUpdateResult, AuditDecision, ActionTaken
from pydantic import ValidationError

def process_changes(current_state: PersonalWishesState, changes: List[FieldChange]) -> StateUpdateResult:
    """
    The Trust-Aware State Engine.
    Evaluates proposed changes against the current state, enforcing rules and detecting conflicts.
    Does NOT mutate the input state. Returns a safe cloned state and a detailed audit log.
    """
    new_state = current_state.model_copy(deep=True)
    audit_log: List[AuditDecision] = []
    
    # Store original fields to allow rollback if cross-field business validation fails
    original_fields: Dict[str, StateField] = {}
    
    for change in changes:
        field_name = change.field
        # Protect against hallucinated fields
        if not hasattr(new_state, field_name):
            audit_log.append(AuditDecision(
                field=field_name, 
                action=ActionTaken.REJECTED_VALIDATION, 
                reason="Field does not exist in schema", 
                proposed_value=change.proposed_value
            ))
            continue
            
        current_field: StateField = getattr(new_state, field_name)
        original_fields[field_name] = current_field.model_copy(deep=True)
        
        # 1. Unknowns explicitly submitted
        if change.status == FieldStatus.UNKNOWN:
            if current_field.status == FieldStatus.UNKNOWN:
                audit_log.append(AuditDecision(field=field_name, action=ActionTaken.IGNORED_DUPLICATE, reason="Already UNKNOWN", proposed_value=change.proposed_value))
            elif change.status == FieldStatus.CORRECTED:
                 # Explicitly resetting a field to unknown
                 setattr(new_state, field_name, StateField(value=None, status=FieldStatus.UNKNOWN, source=change.source_message_id))
                 audit_log.append(AuditDecision(field=field_name, action=ActionTaken.ACCEPTED, reason="Corrected back to UNKNOWN", proposed_value=change.proposed_value))
            else:
                audit_log.append(AuditDecision(field=field_name, action=ActionTaken.REJECTED_CONFLICT, reason="Attempted to overwrite known value with UNKNOWN without explicit CORRECTION status", proposed_value=change.proposed_value))
            continue
            
        # 2. Duplicate Information
        if current_field.status == FieldStatus.CONFIRMED and current_field.value == change.proposed_value:
            audit_log.append(AuditDecision(field=field_name, action=ActionTaken.IGNORED_DUPLICATE, reason="Value already confirmed", proposed_value=change.proposed_value))
            continue
            
        # 3. Explicit Corrections
        if change.status == FieldStatus.CORRECTED:
            setattr(new_state, field_name, StateField(value=change.proposed_value, status=FieldStatus.CONFIRMED, confidence=change.confidence, source=change.source_message_id))
            audit_log.append(AuditDecision(field=field_name, action=ActionTaken.ACCEPTED, reason="User correction", proposed_value=change.proposed_value, previous_value=current_field.value))
            continue
            
        # 4. Conflicting Information
        if current_field.status == FieldStatus.CONFIRMED and current_field.value != change.proposed_value:
            audit_log.append(AuditDecision(field=field_name, action=ActionTaken.REJECTED_CONFLICT, reason="Conflict detected", proposed_value=change.proposed_value, previous_value=current_field.value))
            continue
            
        # 5. Uncertain/Probabilistic Information
        # If the LLM isn't sure (<0.8) OR it explicitly proposes it tentatively
        if change.confidence < 0.8 or change.status in [FieldStatus.PROPOSED, FieldStatus.NEEDS_CONFIRMATION]:
            setattr(new_state, field_name, StateField(value=change.proposed_value, status=FieldStatus.NEEDS_CONFIRMATION, confidence=change.confidence, source=change.source_message_id))
            audit_log.append(AuditDecision(field=field_name, action=ActionTaken.NEEDS_CONFIRMATION, reason="Low confidence or proposed status requires user confirmation", proposed_value=change.proposed_value))
            continue
            
        # 6. Standard Accept (New information)
        setattr(new_state, field_name, StateField(value=change.proposed_value, status=FieldStatus.CONFIRMED, confidence=change.confidence, source=change.source_message_id))
        audit_log.append(AuditDecision(field=field_name, action=ActionTaken.ACCEPTED, reason="Accepted new info", proposed_value=change.proposed_value))

    # --- CROSS-FIELD CONSISTENCY VALIDATION ---
    try:
        # Re-validate the entire model to enforce strict Pydantic type checking
        new_state = PersonalWishesState.model_validate(new_state.model_dump())
        # Apply cross field business logic rules
        new_state.enforce_business_rules()
    except ValidationError as e:
        # If applying these changes broke domain rules (e.g., adding children_names when has_children=False)
        # We roll back the changes to maintain state integrity and mark them as conflicts.
        for k, v in original_fields.items():
            setattr(new_state, k, v)
            
        # Retroactively update the audit log for any change that was "Accepted" but caused a rollback
        for decision in audit_log:
            if decision.action in [ActionTaken.ACCEPTED, ActionTaken.NEEDS_CONFIRMATION]:
                decision.action = ActionTaken.REJECTED_CONFLICT
                decision.reason = f"Cross-field validation failed: {str(e)}"

    except ValueError as e:
        for k, v in original_fields.items():
            setattr(new_state, k, v)
        for decision in audit_log:
            if decision.action in [ActionTaken.ACCEPTED, ActionTaken.NEEDS_CONFIRMATION]:
                decision.action = ActionTaken.REJECTED_CONFLICT
                decision.reason = f"Cross-field validation failed: {str(e)}"
                
    # Group the results for the response
    accepted = [d for d in audit_log if d.action == ActionTaken.ACCEPTED]
    rejected = [d for d in audit_log if d.action == ActionTaken.REJECTED_VALIDATION]
    conflicts = [d for d in audit_log if d.action == ActionTaken.REJECTED_CONFLICT]
    needs_conf = [d for d in audit_log if d.action == ActionTaken.NEEDS_CONFIRMATION]

    return StateUpdateResult(
        accepted_changes=accepted,
        rejected_changes=rejected,
        confirmation_required=needs_conf,
        conflicts=conflicts,
        audit_log=audit_log,
        new_state=new_state
    )
