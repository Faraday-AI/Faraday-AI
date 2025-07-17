"""
Tests for the GPT manager service and endpoints.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import json

from ..services.gpt_manager_service import GPTManagerService
from ..api.v1.endpoints.gpt_manager import router
from ..models.gpt_models import GPTDefinition, GPTSubscription, GPTCategory, GPTType

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def gpt_manager_service(mock_db):
    return GPTManagerService(mock_db)

@pytest.fixture
def client():
    return TestClient(router)

@pytest.fixture
def sample_gpt():
    return GPTDefinition(
        id="gpt-1",
        name="Math Teacher",
        category=GPTCategory.TEACHER,
        type=GPTType.MATH_TEACHER,
        version="1.0.0",
        requirements={
            "dependencies": {
                "numpy": "^1.20.0",
                "pandas": "^1.3.0"
            },
            "integrations": ["lms", "analytics"],
            "resources": {
                "memory": 2.0,
                "cpu": 1.0
            }
        }
    )

@pytest.fixture
def sample_subscription():
    return GPTSubscription(
        id="sub-1",
        user_id="user-1",
        gpt_definition_id="gpt-1",
        status="active"
    )

# Service Tests
async def test_get_user_tools(gpt_manager_service, mock_db, sample_subscription):
    """Test getting user's available tools."""
    # Mock database query
    mock_db.query.return_value.filter.return_value.all.return_value = [sample_subscription]

    # Test getting tools
    tools = await gpt_manager_service.get_user_tools("user-1")
    assert len(tools) == 1
    assert tools[0] == "gpt-1"

    # Test cache hit
    tools = await gpt_manager_service.get_user_tools("user-1")
    assert len(tools) == 1
    mock_db.query.assert_called_once()  # Should use cached result

async def test_add_tool(gpt_manager_service, mock_db, sample_gpt):
    """Test adding a tool."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.return_value = sample_gpt

    # Test adding tool
    result = await gpt_manager_service.add_tool("user-1", "Math Teacher")
    assert result["status"] == "success"
    assert result["tool_id"] == "gpt-1"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

async def test_remove_tool(gpt_manager_service, mock_db, sample_subscription):
    """Test removing a tool."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        sample_subscription
    ]

    # Test removing tool
    result = await gpt_manager_service.remove_tool("user-1", "Math Teacher")
    assert result["status"] == "success"
    mock_db.commit.assert_called_once()

async def test_get_function_specs(gpt_manager_service, mock_db, sample_gpt):
    """Test getting function specifications."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.all.return_value = [sample_gpt]

    # Test getting specs
    specs = await gpt_manager_service.get_function_specs("user-1")
    assert len(specs) == 1
    assert specs[0]["name"] == "use_math_teacher"
    assert "task" in specs[0]["parameters"]["properties"]

async def test_handle_gpt_command(gpt_manager_service):
    """Test handling GPT commands."""
    with patch("openai.ChatCompletion.create") as mock_create:
        # Mock OpenAI response
        mock_create.return_value.choices = [
            Mock(
                function_call=Mock(
                    name="use_math_teacher",
                    arguments=json.dumps({"task": "solve equation"})
                )
            )
        ]

        # Test command handling
        result = await gpt_manager_service.handle_gpt_command(
            "user-1",
            "Help me solve this equation"
        )
        assert result["status"] == "success"
        assert result["action"] == "use_math_teacher"

# API Endpoint Tests
async def test_get_user_tools_endpoint(client, mock_db):
    """Test the get user tools endpoint."""
    response = client.get("/tools")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_add_tool_endpoint(client, mock_db):
    """Test the add tool endpoint."""
    response = client.post("/tools/add?tool_name=Math%20Teacher")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

async def test_remove_tool_endpoint(client, mock_db):
    """Test the remove tool endpoint."""
    response = client.post("/tools/remove?tool_name=Math%20Teacher")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

async def test_get_function_specs_endpoint(client, mock_db):
    """Test the get function specs endpoint."""
    response = client.get("/tools/specs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_handle_command_endpoint(client, mock_db):
    """Test the handle command endpoint."""
    response = client.post(
        "/command",
        json={"command": "Help me solve this equation"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

# Error Handling Tests
async def test_invalid_tool_name(gpt_manager_service, mock_db):
    """Test handling invalid tool name."""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        await gpt_manager_service.add_tool("user-1", "Invalid Tool")
    assert exc.value.status_code == 404

async def test_database_error(gpt_manager_service, mock_db):
    """Test handling database errors."""
    mock_db.query.side_effect = Exception("Database error")
    
    with pytest.raises(HTTPException) as exc:
        await gpt_manager_service.get_user_tools("user-1")
    assert exc.value.status_code == 500

async def test_openai_error(gpt_manager_service):
    """Test handling OpenAI API errors."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.side_effect = Exception("API error")
        
        with pytest.raises(HTTPException) as exc:
            await gpt_manager_service.handle_gpt_command(
                "user-1",
                "Help me solve this equation"
            )
        assert exc.value.status_code == 500 