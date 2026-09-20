import pytest
from app.domain.state import PersonalWishesState, FieldStatus, StateField
from app.domain.engine import FieldChange, ActionTaken
from app.services.state_engine import process_changes

def test_normal_extraction():
    state = PersonalWishesState()
    changes = [
        FieldChange(field="executor_name", proposed_value="Rahul", status=FieldStatus.CONFIRMED, confidence=0.9)
    ]
    result = process_changes(state, changes)
    assert len(result.accepted_changes) == 1
    assert result.new_state.executor_name.value == "Rahul"
    assert result.new_state.executor_name.status == FieldStatus.CONFIRMED

def test_uncertain_statement():
    # "My brother Rahul will probably be my executor."
    state = PersonalWishesState()
    changes = [
        FieldChange(field="executor_name", proposed_value="Rahul", status=FieldStatus.PROPOSED, confidence=0.6),
        FieldChange(field="executor_relationship", proposed_value="brother", status=FieldStatus.PROPOSED, confidence=0.6)
    ]
    result = process_changes(state, changes)
    assert len(result.confirmation_required) == 2
    assert result.new_state.executor_name.value == "Rahul"
    assert result.new_state.executor_name.status == FieldStatus.NEEDS_CONFIRMATION
    assert result.new_state.executor_relationship.value == "brother"

def test_corrections():
    # "Actually, my executor should be Rohit."
    state = PersonalWishesState(
        executor_name=StateField[str](value="Rahul", status=FieldStatus.CONFIRMED)
    )
    changes = [
        FieldChange(field="executor_name", proposed_value="Rohit", status=FieldStatus.CORRECTED)
    ]
    result = process_changes(state, changes)
    assert len(result.accepted_changes) == 1
    assert result.new_state.executor_name.value == "Rohit"
    assert result.new_state.executor_name.status == FieldStatus.CONFIRMED

def test_contradictions():
    # "My executor is Rohit." (without explicit CORRECTION status)
    state = PersonalWishesState(
        executor_name=StateField[str](value="Rahul", status=FieldStatus.CONFIRMED)
    )
    changes = [
        FieldChange(field="executor_name", proposed_value="Rohit", status=FieldStatus.CONFIRMED)
    ]
    result = process_changes(state, changes)
    assert len(result.conflicts) == 1
    # State should remain Rahul
    assert result.new_state.executor_name.value == "Rahul"

def test_cross_field_contradiction_rolls_back():
    # Earlier: has_children = false. Later: "My daughter Sarah..."
    state = PersonalWishesState(
        has_children=StateField[bool](value=False, status=FieldStatus.CONFIRMED)
    )
    changes = [
        FieldChange(field="children_names", proposed_value=["Sarah"], status=FieldStatus.CONFIRMED)
    ]
    result = process_changes(state, changes)
    assert len(result.conflicts) == 1
    # State should be completely unmodified (rollback)
    assert result.new_state.children_names.value is None
    assert result.new_state.has_children.value is False

def test_duplicate_information():
    # Repeatedly saying the same executor
    state = PersonalWishesState(
        executor_name=StateField[str](value="Rahul", status=FieldStatus.CONFIRMED)
    )
    changes = [
        FieldChange(field="executor_name", proposed_value="Rahul", status=FieldStatus.CONFIRMED)
    ]
    result = process_changes(state, changes)
    # Should be tracked in audit log as IGNORED_DUPLICATE
    assert result.audit_log[0].action == ActionTaken.IGNORED_DUPLICATE
    assert len(result.accepted_changes) == 0

def test_unknown_values():
    # "I don't know who my executor will be"
    state = PersonalWishesState()
    changes = [
        FieldChange(field="executor_name", proposed_value=None, status=FieldStatus.UNKNOWN)
    ]
    result = process_changes(state, changes)
    # Already unknown, so it gets ignored
    assert result.audit_log[0].action == ActionTaken.IGNORED_DUPLICATE
    assert result.new_state.executor_name.status == FieldStatus.UNKNOWN

def test_invalid_field_rejection():
    # Hallucinated field
    state = PersonalWishesState()
    changes = [
        FieldChange(field="fake_field", proposed_value="fake", status=FieldStatus.CONFIRMED)
    ]
    result = process_changes(state, changes)
    assert result.audit_log[0].action == ActionTaken.REJECTED_VALIDATION

def test_multi_field_changes():
    # Provide multiple fields correctly
    state = PersonalWishesState()
    changes = [
        FieldChange(field="has_children", proposed_value=True, status=FieldStatus.CONFIRMED),
        FieldChange(field="children_names", proposed_value=["Sarah", "John"], status=FieldStatus.CONFIRMED)
    ]
    result = process_changes(state, changes)
    assert len(result.accepted_changes) == 2
    assert result.new_state.has_children.value is True
    assert result.new_state.children_names.value == ["Sarah", "John"]
