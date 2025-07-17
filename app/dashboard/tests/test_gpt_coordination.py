"""
Tests for the GPT coordination service.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from ...models import (
    User,
    GPTDefinition,
    GPTSubscription,
    GPTContext,
    ContextInteraction,
    SharedContext
)
from ...services.gpt_coordination_service import GPTCoordinationService

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def coordination_service(mock_db):
    return GPTCoordinationService(mock_db)

@pytest.fixture
def sample_user():
    return User(
        id="user-1",
        email="test@example.com"
    )

@pytest.fixture
def sample_gpt():
    return GPTDefinition(
        id="gpt-1",
        name="Test GPT",
        category="TEACHER"
    )

@pytest.fixture
def sample_subscription(sample_user, sample_gpt):
    return GPTSubscription(
        id="sub-1",
        user_id=sample_user.id,
        gpt_definition_id=sample_gpt.id,
        gpt_definition=sample_gpt
    )

@pytest.fixture
def sample_context(sample_user, sample_gpt):
    return GPTContext(
        id="ctx-1",
        user_id=sample_user.id,
        primary_gpt_id=sample_gpt.id,
        name="Test Context",
        context_data={"test": "data"},
        is_active=True
    )

async def test_initialize_context(
    coordination_service,
    mock_db,
    sample_user,
    sample_subscription
):
    """Test context initialization."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.return_value = sample_subscription

    result = await coordination_service.initialize_context(
        user_id=sample_user.id,
        primary_gpt_id=sample_subscription.gpt_definition_id,
        context_data={"test": "data"},
        name="Test Context"
    )

    assert result["context_id"].startswith("ctx-")
    assert result["primary_gpt"] == sample_subscription.gpt_definition_id
    assert result["context_data"] == {"test": "data"}
    assert result["name"] == "Test Context"
    assert len(result["active_gpts"]) == 1

async def test_add_gpt_to_context(
    coordination_service,
    mock_db,
    sample_context,
    sample_gpt
):
    """Test adding GPT to context."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        sample_context,  # For context query
        sample_gpt      # For GPT query
    ]

    result = await coordination_service.add_gpt_to_context(
        context_id=sample_context.id,
        gpt_id=sample_gpt.id,
        role="assistant"
    )

    assert result["status"] == "success"
    assert result["context_id"] == sample_context.id
    assert result["added_gpt"] == sample_gpt.id
    assert result["role"] == "assistant"

async def test_share_context(
    coordination_service,
    mock_db,
    sample_context,
    sample_gpt
):
    """Test context sharing between GPTs."""
    # Mock active GPTs
    sample_context.active_gpts = [sample_gpt, Mock(id="gpt-2")]
    
    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.return_value = sample_context

    shared_data = {"key": "value"}
    result = await coordination_service.share_context(
        context_id=sample_context.id,
        source_gpt_id=sample_gpt.id,
        target_gpt_id="gpt-2",
        shared_data=shared_data
    )

    assert result["shared_context_id"].startswith("sh-")
    assert result["context_id"] == sample_context.id
    assert result["source_gpt"] == sample_gpt.id
    assert result["target_gpt"] == "gpt-2"
    assert result["shared_data"] == shared_data

async def test_get_context_history(
    coordination_service,
    mock_db,
    sample_context
):
    """Test retrieving context history."""
    # Mock interactions
    interactions = [
        ContextInteraction(
            id=f"int-{i}",
            context_id=sample_context.id,
            gpt_id="gpt-1",
            interaction_type="test",
            content={"test": f"data-{i}"},
            timestamp=datetime.utcnow()
        ) for i in range(3)
    ]

    # Mock database query
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = interactions

    result = await coordination_service.get_context_history(
        context_id=sample_context.id
    )

    assert len(result) == 3
    assert all(isinstance(item, dict) for item in result)
    assert all("interaction_id" in item for item in result)
    assert all("content" in item for item in result)

async def test_update_context(
    coordination_service,
    mock_db,
    sample_context,
    sample_gpt
):
    """Test context update."""
    # Add GPT to active GPTs
    sample_context.active_gpts = [sample_gpt]
    
    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.return_value = sample_context

    update_data = {"new": "data"}
    result = await coordination_service.update_context(
        context_id=sample_context.id,
        gpt_id=sample_gpt.id,
        update_data=update_data
    )

    assert result["context_id"] == sample_context.id
    assert result["gpt_id"] == sample_gpt.id
    assert "new" in result["update_data"]

async def test_close_context(
    coordination_service,
    mock_db,
    sample_context
):
    """Test context closure."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.return_value = sample_context

    summary = {"summary": "test"}
    result = await coordination_service.close_context(
        context_id=sample_context.id,
        summary=summary
    )

    assert result["context_id"] == sample_context.id
    assert result["summary"] == summary
    assert "closed_at" in result

async def test_get_active_contexts(
    coordination_service,
    mock_db,
    sample_user,
    sample_context
):
    """Test retrieving active contexts."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.all.return_value = [sample_context]

    result = await coordination_service.get_active_contexts(
        user_id=sample_user.id
    )

    assert len(result) == 1
    assert result[0]["context_id"] == sample_context.id
    assert result[0]["is_active"] is True

def test_error_handling(coordination_service, mock_db):
    """Test error handling in coordination service."""
    # Mock database error
    mock_db.query.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc:
        coordination_service.get_context_history("ctx-1")
    assert "Error retrieving context history" in str(exc.value) 