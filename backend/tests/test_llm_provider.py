import pytest
from app.services.mock_provider import MockLLMProvider
from app.domain.state import PersonalWishesState, FieldStatus

@pytest.mark.asyncio
async def test_valid_response():
    provider = MockLLMProvider("valid")
    result = await provider.extract_state_changes([], PersonalWishesState())
    assert result.success is True
    assert result.data is not None
    assert len(result.data.changes) == 1
    assert result.data.changes[0].field == "executor_name"
    assert result.data.changes[0].proposed_value == "James"
    assert result.prompt_version == "mock-v1.0"

@pytest.mark.asyncio
async def test_ambiguous_response():
    provider = MockLLMProvider("ambiguous")
    result = await provider.extract_state_changes([], PersonalWishesState())
    assert result.success is True
    assert result.data.needs_clarification is True
    assert result.data.changes[0].status == FieldStatus.PROPOSED
    assert len(result.data.uncertainties) > 0

@pytest.mark.asyncio
async def test_malformed_json_response():
    provider = MockLLMProvider("malformed")
    result = await provider.extract_state_changes([], PersonalWishesState())
    assert result.success is False
    assert result.data is None
    assert "Malformed JSON" in result.error

@pytest.mark.asyncio
async def test_missing_field_response():
    provider = MockLLMProvider("missing_field")
    result = await provider.extract_state_changes([], PersonalWishesState())
    assert result.success is False
    assert result.data is None
    assert "Schema Validation Error" in result.error

@pytest.mark.asyncio
async def test_contradictory_response():
    # LLM spots contradiction, reports it
    provider = MockLLMProvider("contradictory")
    result = await provider.extract_state_changes([], PersonalWishesState())
    assert result.success is True
    assert len(result.data.potential_conflicts) == 1
    assert result.data.changes[0].field == "executor_name"

@pytest.mark.asyncio
async def test_multi_field_response():
    provider = MockLLMProvider("multi_field")
    result = await provider.extract_state_changes([], PersonalWishesState())
    assert result.success is True
    assert len(result.data.changes) == 2
    assert result.data.changes[0].field == "has_children"
    assert result.data.changes[1].field == "children_names"

@pytest.mark.asyncio
async def test_timeout_response():
    provider = MockLLMProvider("timeout")
    result = await provider.extract_state_changes([], PersonalWishesState())
    assert result.success is False
    assert "timed out" in result.error
