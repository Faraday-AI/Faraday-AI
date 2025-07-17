"""
Tests for the compatibility API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from ..api.v1.endpoints.compatibility import router
from ..services.compatibility_service import CompatibilityService
from ..models.gpt_models import GPTDefinition, GPTCategory, GPTType

# Setup test client
@pytest.fixture
def client():
    return TestClient(router)

@pytest.fixture
def mock_compatibility_service():
    return Mock(spec=CompatibilityService)

@pytest.fixture
def sample_gpt():
    return {
        "id": "gpt-1",
        "name": "Math Teacher",
        "category": GPTCategory.TEACHER,
        "type": GPTType.MATH_TEACHER,
        "version": "1.0.0",
        "requirements": {
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
    }

@pytest.fixture
def sample_target_environment():
    return {
        "numpy": "1.21.0",
        "pandas": "1.3.2",
        "memory": 4.0,
        "cpu": 2.0
    }

@pytest.mark.asyncio
async def test_check_compatibility(
    client,
    mock_compatibility_service,
    sample_gpt,
    sample_target_environment
):
    """Test the check compatibility endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "compatibility_score": 0.95,
        "checks": {
            "dependencies": {
                "status": "passed",
                "satisfied_dependencies": ["numpy", "pandas"],
                "compatibility_issues": []
            },
            "version": {
                "status": "passed",
                "is_compatible": True,
                "issues": []
            },
            "integrations": {
                "status": "passed",
                "available_integrations": ["lms", "analytics"],
                "integration_issues": []
            },
            "resources": {
                "status": "passed",
                "satisfied_resources": ["memory", "cpu"],
                "resource_issues": []
            }
        },
        "recommendations": []
    }
    mock_compatibility_service.check_compatibility.return_value = mock_response

    # Make request
    response = client.post(
        "/compatibility/check",
        json={
            "gpt_id": "gpt-1",
            "target_environment": sample_target_environment
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["compatibility_score"] == 0.95
    assert "checks" in data
    assert "recommendations" in data

    # Test error handling
    mock_compatibility_service.check_compatibility.side_effect = Exception("Test error")
    response = client.post(
        "/compatibility/check",
        json={
            "gpt_id": "gpt-1",
            "target_environment": sample_target_environment
        }
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"

@pytest.mark.asyncio
async def test_get_compatible_gpts(client, mock_compatibility_service, sample_gpt):
    """Test the get compatible GPTs endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "compatible_gpts": {
            "gpt-2": {
                "name": "Science Teacher",
                "category": "TEACHER",
                "type": "SCIENCE_TEACHER",
                "compatibility_score": 0.85
            }
        },
        "total_compatible": 1,
        "compatibility_summary": {
            "average_compatibility_score": 0.85,
            "compatibility_by_category": {"TEACHER": 1},
            "compatibility_by_type": {"SCIENCE_TEACHER": 1},
            "high_compatibility_count": 1
        }
    }
    mock_compatibility_service.get_compatible_gpts.return_value = mock_response

    # Make request
    response = client.get("/compatibility/compatible-gpts/gpt-1")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "compatible_gpts" in data
    assert "compatibility_summary" in data
    assert data["total_compatible"] == 1

    # Test with category filter
    response = client.get(
        "/compatibility/compatible-gpts/gpt-1",
        params={"category": "TEACHER"}
    )
    assert response.status_code == 200

    # Test error handling
    mock_compatibility_service.get_compatible_gpts.side_effect = Exception("Test error")
    response = client.get("/compatibility/compatible-gpts/gpt-1")
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"

@pytest.mark.asyncio
async def test_validate_integration_requirements(
    client,
    mock_compatibility_service,
    sample_gpt
):
    """Test the validate integration requirements endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "is_valid": True,
        "validation_results": {
            "integration_type": "lms",
            "total_checks": 4,
            "passed_checks": 4,
            "checks": [
                {
                    "check": "config_api_key",
                    "status": "passed",
                    "message": "API key configuration is valid"
                },
                {
                    "check": "config_max_students",
                    "status": "passed",
                    "message": "Max students configuration is valid"
                },
                {
                    "check": "permission_read",
                    "status": "passed",
                    "message": "Read permission is granted"
                },
                {
                    "check": "permission_write",
                    "status": "passed",
                    "message": "Write permission is granted"
                }
            ]
        },
        "recommendations": []
    }
    mock_compatibility_service.validate_integration_requirements.return_value = mock_response

    # Make request
    response = client.post(
        "/compatibility/validate-integration",
        json={
            "gpt_id": "gpt-1",
            "integration_type": "lms"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["is_valid"]
    assert "validation_results" in data
    assert "recommendations" in data

    # Test with invalid integration type
    response = client.post(
        "/compatibility/validate-integration",
        json={
            "gpt_id": "gpt-1",
            "integration_type": "invalid"
        }
    )
    assert response.status_code == 422

    # Test error handling
    mock_compatibility_service.validate_integration_requirements.side_effect = Exception("Test error")
    response = client.post(
        "/compatibility/validate-integration",
        json={
            "gpt_id": "gpt-1",
            "integration_type": "lms"
        }
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"

@pytest.mark.asyncio
async def test_get_compatibility_dashboard(client, mock_compatibility_service):
    """Test the get compatibility dashboard endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "dashboard_data": {
            "overall_stats": {
                "total_gpts": 10,
                "compatible_gpts": 8,
                "average_compatibility_score": 0.85
            },
            "compatibility_by_category": {
                "TEACHER": {
                    "total": 5,
                    "compatible": 4,
                    "average_score": 0.9
                },
                "STUDENT": {
                    "total": 5,
                    "compatible": 4,
                    "average_score": 0.8
                }
            },
            "recent_compatibility_checks": [
                {
                    "gpt_id": "gpt-1",
                    "timestamp": "2024-03-20T10:00:00Z",
                    "compatibility_score": 0.95
                }
            ],
            "compatibility_trends": {
                "daily": [
                    {
                        "date": "2024-03-20",
                        "average_score": 0.85
                    }
                ]
            }
        }
    }
    mock_compatibility_service.get_compatibility_dashboard.return_value = mock_response

    # Make request
    response = client.get("/compatibility/dashboard")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "dashboard_data" in data
    assert "overall_stats" in data["dashboard_data"]
    assert "compatibility_by_category" in data["dashboard_data"]
    assert "recent_compatibility_checks" in data["dashboard_data"]
    assert "compatibility_trends" in data["dashboard_data"]

    # Test with category filter
    response = client.get(
        "/compatibility/dashboard",
        params={"category": "TEACHER"}
    )
    assert response.status_code == 200

    # Test error handling
    mock_compatibility_service.get_compatibility_dashboard.side_effect = Exception("Test error")
    response = client.get("/compatibility/dashboard")
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"

@pytest.mark.asyncio
async def test_input_validation():
    """Test input validation for all endpoints."""
    client = TestClient(router)

    # Test invalid GPT ID
    response = client.post(
        "/compatibility/check",
        json={
            "gpt_id": "",  # Empty GPT ID
            "target_environment": {}
        }
    )
    assert response.status_code == 422

    # Test invalid target environment
    response = client.post(
        "/compatibility/check",
        json={
            "gpt_id": "gpt-1",
            "target_environment": None  # Invalid environment
        }
    )
    assert response.status_code == 422

    # Test invalid integration type
    response = client.post(
        "/compatibility/validate-integration",
        json={
            "gpt_id": "gpt-1",
            "integration_type": ""  # Empty integration type
        }
    )
    assert response.status_code == 422

    # Test invalid category filter
    response = client.get(
        "/compatibility/dashboard",
        params={"category": "INVALID"}  # Invalid category
    )
    assert response.status_code == 422 