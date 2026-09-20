import pytest
from app.domain.state import PersonalWishesState, StateField, FieldStatus
from app.services.document_generator import generate_document

def test_state_changes_update_document():
    # Prove that modifying the structured state propagates directly to the document
    state = PersonalWishesState(
        full_name=StateField[str](value="Alice Walker", status=FieldStatus.CONFIRMED)
    )
    doc = generate_document(state)
    assert "**Full Name:** Alice Walker" in doc
    
    # State change
    state.full_name.value = "Alice Johnson"
    doc2 = generate_document(state)
    assert "**Full Name:** Alice Johnson" in doc2

def test_corrections_update_document():
    # Prove that applying a correction reflects immediately
    state = PersonalWishesState(
        home_address=StateField[str](value="123 Old St", status=FieldStatus.CONFIRMED)
    )
    doc = generate_document(state)
    assert "**Home Address:** 123 Old St" in doc
    
    # Correction applied
    state.home_address.value = "456 New Ave"
    state.home_address.status = FieldStatus.CONFIRMED # In our architecture, corrections become CONFIRMED state
    doc2 = generate_document(state)
    assert "**Home Address:** 456 New Ave" in doc2

def test_unknown_values_represented_safely():
    # Pure empty state (everything is UNKNOWN)
    state = PersonalWishesState()
    doc = generate_document(state)
    
    # Verify the safe placeholder is used
    assert "**Full Name:** *[Not specified]*" in doc
    assert "**Home Address:** *[Not specified]*" in doc

def test_unconfirmed_values_not_presented_as_confirmed():
    state = PersonalWishesState(
        executor_name=StateField[str](value="Rahul", status=FieldStatus.NEEDS_CONFIRMATION)
    )
    doc = generate_document(state)
    
    # It must NOT present "Rahul" as a confirmed fact
    assert "Rahul" not in doc
    assert "**Executor Name:** *[Information requires confirmation]*" in doc

def test_disclaimer_always_present():
    state = PersonalWishesState()
    doc = generate_document(state)
    
    assert "FICTIONAL – NOT LEGAL ADVICE" in doc

def test_no_external_information_appears():
    # Only fields explicitly in state map to the document.
    state = PersonalWishesState(
        full_name=StateField[str](value="Bob", status=FieldStatus.CONFIRMED)
    )
    doc = generate_document(state)
    
    # Check strict structure. Nothing else should exist.
    assert "Bob" in doc
    # We shouldn't see random AI hallucinations here because it's deterministically built
    # Just check that it has exactly the expected structure headers and no weird appended data
    assert doc.count("##") == 4 # 4 main sections
    
def test_conditional_rendering():
    # Prove children names aren't rendered if has_children is False
    state = PersonalWishesState(
        has_children=StateField[bool](value=False, status=FieldStatus.CONFIRMED)
    )
    doc = generate_document(state)
    assert "**Has Children:** No" in doc
    assert "**Children Names:**" not in doc

    # Prove they appear if has_children is True
    state_true = PersonalWishesState(
        has_children=StateField[bool](value=True, status=FieldStatus.CONFIRMED),
        children_names=StateField[list[str]](value=["Sarah", "Tim"], status=FieldStatus.CONFIRMED)
    )
    doc_true = generate_document(state_true)
    assert "**Children Names:** Sarah, Tim" in doc_true
