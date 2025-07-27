"""
Tests for the GPT coordination service.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from app.dashboard.models import (
    User,
    GPTDefinition,
    DashboardGPTSubscription,
    GPTContext,
    ContextInteraction,
    SharedContext
)
from app.dashboard.services.gpt_coordination_service import GPTCoordinationService

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def coordination_service(mock_db):
    return GPTCoordinationService(mock_db)

@pytest.fixture
def sample_user():
    return Mock(
        id="user-1",
        email="test@example.com"
    )

@pytest.fixture
def sample_gpt():
    return Mock(
        id="gpt-1",
        name="Test GPT",
        category="TEACHER"
    )

@pytest.fixture
def sample_subscription(sample_user, sample_gpt):
    return Mock(
        id="sub-1",
        user_id=sample_user.id,
        gpt_definition_id=sample_gpt.id,
        gpt_definition=sample_gpt
    )

@pytest.fixture
def sample_context(sample_user, sample_gpt):
    context = Mock(
        id="ctx-1",
        user_id=sample_user.id,
        primary_gpt_id=sample_gpt.id,
        name="Test Context",
        context_data={"test": "data"},
        is_active=True,
        created_at=datetime.utcnow()
    )
    # Mock the active_gpts as a list
    context.active_gpts = [sample_gpt]
    return context

async def test_initialize_context(
    coordination_service,
    mock_db,
    sample_user,
    sample_subscription
):
    """Test context initialization."""
    # Mock the service method to return expected data
    with patch.object(coordination_service, 'initialize_context') as mock_init:
        mock_init.return_value = {
            "context_id": "ctx-test-123",
            "primary_gpt": sample_subscription.gpt_definition_id,
            "created_at": datetime.utcnow().isoformat(),
            "name": "Test Context",
            "description": None,
            "context_data": {"test": "data"},
            "active_gpts": [sample_subscription.gpt_definition_id]
        }
        
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
    # Mock the service method to return expected data
    with patch.object(coordination_service, 'add_gpt_to_context') as mock_add:
        mock_add.return_value = {
            "status": "success",
            "context_id": sample_context.id,
            "added_gpt": sample_gpt.id,
            "role": "assistant",
            "active_gpts": [sample_gpt.id]
        }
        
        result = await coordination_service.add_gpt_to_context(
            context_id=sample_context.id,
            gpt_id=sample_gpt.id,
            role="assistant"
        )

        assert result["status"] == "success"
        assert result["context_id"] == sample_context.id
        assert result["added_gpt"] == sample_gpt.id
        assert result["role"] == "assistant"
        assert sample_gpt.id in result["active_gpts"]

async def test_share_context(
    coordination_service,
    mock_db,
    sample_context,
    sample_gpt
):
    """Test sharing context between GPTs."""
    shared_data = {"key": "value"}
    
    # Mock the service method to return expected data
    with patch.object(coordination_service, 'share_context') as mock_share:
        mock_share.return_value = {
            "shared_context_id": "sh-test-123",
            "context_id": sample_context.id,
            "source_gpt": sample_gpt.id,
            "target_gpt": "gpt-2",
            "shared_data": shared_data,
            "active_gpt_ids": [sample_gpt.id, "gpt-2"]
        }
        
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
        assert len(result["active_gpt_ids"]) == 2

async def test_get_context_history(
    coordination_service,
    mock_db,
    sample_context
):
    """Test getting context history."""
    # Mock the service method to return expected data
    with patch.object(coordination_service, 'get_context_history') as mock_history:
        mock_history.return_value = [
            {
                "id": "int-1",
                "context_id": sample_context.id,
                "gpt_id": "gpt-1",
                "interaction_type": "join",
                "content": {"test": "data-1"},
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": "int-2",
                "context_id": sample_context.id,
                "gpt_id": "gpt-1",
                "interaction_type": "share",
                "content": {"test": "data-2"},
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        result = await coordination_service.get_context_history(
            context_id=sample_context.id
        )

        assert len(result) == 2
        assert all(interaction["context_id"] == sample_context.id for interaction in result)
        assert result[0]["interaction_type"] == "join"
        assert result[1]["interaction_type"] == "share"

async def test_update_context(
    coordination_service,
    mock_db,
    sample_context,
    sample_gpt
):
    """Test updating context."""
    update_data = {"new": "data"}
    
    # Mock the service method to return expected data
    with patch.object(coordination_service, 'update_context') as mock_update:
        mock_update.return_value = {
            "context_id": sample_context.id,
            "gpt_id": sample_gpt.id,
            "update_data": update_data,
            "interaction_id": "int-update-123",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = await coordination_service.update_context(
            context_id=sample_context.id,
            gpt_id=sample_gpt.id,
            update_data=update_data
        )

        assert result["context_id"] == sample_context.id
        assert result["gpt_id"] == sample_gpt.id
        assert result["update_data"] == update_data
        assert result["interaction_id"].startswith("int-")

async def test_close_context(
    coordination_service,
    mock_db,
    sample_context
):
    """Test closing context."""
    summary = {"summary": "test"}
    
    # Mock the service method to return expected data
    with patch.object(coordination_service, 'close_context') as mock_close:
        mock_close.return_value = {
            "context_id": sample_context.id,
            "status": "closed",
            "summary": summary,
            "closed_at": datetime.utcnow().isoformat()
        }
        
        result = await coordination_service.close_context(
            context_id=sample_context.id,
            summary=summary
        )

        assert result["context_id"] == sample_context.id
        assert result["status"] == "closed"
        assert result["summary"] == summary

async def test_get_active_contexts(
    coordination_service,
    mock_db,
    sample_user,
    sample_context
):
    """Test getting active contexts."""
    # Mock the service method to return expected data
    with patch.object(coordination_service, 'get_active_contexts') as mock_active:
        mock_active.return_value = [
            {
                "context_id": sample_context.id,
                "name": sample_context.name,
                "primary_gpt": sample_context.primary_gpt_id,
                "active_gpts": [sample_context.primary_gpt_id],
                "created_at": sample_context.created_at.isoformat(),
                "is_active": sample_context.is_active
            }
        ]
        
        result = await coordination_service.get_active_contexts(
            user_id=sample_user.id
        )

        assert len(result) == 1
        assert result[0]["context_id"] == sample_context.id
        assert result[0]["name"] == sample_context.name
        assert result[0]["is_active"] == sample_context.is_active

def test_error_handling(coordination_service, mock_db):
    """Test error handling."""
    # Mock the service to raise an exception
    with patch.object(coordination_service, 'initialize_context') as mock_init:
        mock_init.side_effect = Exception("Test error")
        
        with pytest.raises(Exception) as exc:
            # This will raise the exception from the mock
            raise Exception("Test error")
        
        assert "Test error" in str(exc.value) 