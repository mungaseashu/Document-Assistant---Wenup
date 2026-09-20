import pytest
from pydantic import ValidationError
from app.domain.state import PersonalWishesState, StateField, FieldStatus

def test_default_initialization():
    state = PersonalWishesState()
    assert state.full_name.status == FieldStatus.UNKNOWN
    assert state.full_name.value is None
    assert state.has_children.status == FieldStatus.UNKNOWN
    assert state.has_children.value is None

def test_unknown_with_value_fails():
    with pytest.raises(ValidationError) as exc:
        StateField[str](value="James", status=FieldStatus.UNKNOWN)
    assert "UNKNOWN fields must have a None value" in str(exc.value)

def test_false_distinguishable_from_unknown():
    # True / False must be explicitly settable and distinguishable from None (UNKNOWN)
    field = StateField[bool](value=False, status=FieldStatus.CONFIRMED)
    assert field.value is False
    assert field.status == FieldStatus.CONFIRMED

    field_unknown = StateField[bool]()
    assert field_unknown.value is None
    assert field_unknown.status == FieldStatus.UNKNOWN

def test_confidence_bounds():
    with pytest.raises(ValidationError):
        StateField[str](value="James", status=FieldStatus.PROPOSED, confidence=1.5)
    
    with pytest.raises(ValidationError):
        StateField[str](value="James", status=FieldStatus.PROPOSED, confidence=-0.1)

    # Valid confidence
    valid = StateField[str](value="James", status=FieldStatus.PROPOSED, confidence=0.8)
    assert valid.confidence == 0.8

def test_invalid_status_rejected():
    with pytest.raises(ValidationError):
        # 'FAKE_STATUS' is not in the Enum
        StateField[str](value="James", status="FAKE_STATUS")

def test_rule_children_names_needs_has_children_true():
    # If has_children is UNKNOWN (None), providing children names should fail
    with pytest.raises(ValidationError) as exc:
        PersonalWishesState(
            children_names=StateField[list[str]](value=["Alice", "Bob"], status=FieldStatus.PROPOSED)
        )
    assert "children_names cannot be populated unless has_children is explicitly True" in str(exc.value)

    # If has_children is False, providing children names should fail
    with pytest.raises(ValidationError) as exc:
        PersonalWishesState(
            has_children=StateField[bool](value=False, status=FieldStatus.CONFIRMED),
            children_names=StateField[list[str]](value=["Alice", "Bob"], status=FieldStatus.PROPOSED)
        )
    assert "children_names cannot be populated unless has_children is explicitly True" in str(exc.value)

    # Success case
    state = PersonalWishesState(
        has_children=StateField[bool](value=True, status=FieldStatus.CONFIRMED),
        children_names=StateField[list[str]](value=["Alice", "Bob"], status=FieldStatus.PROPOSED)
    )
    assert state.children_names.value == ["Alice", "Bob"]

def test_rule_executor_relationship_needs_executor_name():
    with pytest.raises(ValidationError) as exc:
        PersonalWishesState(
            executor_relationship=StateField[str](value="Brother", status=FieldStatus.PROPOSED)
        )
    assert "executor_relationship cannot exist without an executor_name" in str(exc.value)

    # Success case
    state = PersonalWishesState(
        executor_name=StateField[str](value="James", status=FieldStatus.CONFIRMED),
        executor_relationship=StateField[str](value="Brother", status=FieldStatus.PROPOSED)
    )
    assert state.executor_name.value == "James"
    assert state.executor_relationship.value == "Brother"
