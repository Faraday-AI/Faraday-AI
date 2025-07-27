"""
Tests for the compatibility API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, AsyncMock, patch

from app.dashboard.api.v1.endpoints.compatibility import router
from app.dashboard.services.compatibility_service import CompatibilityService
from app.dashboard.models.gpt_models import GPTDefinition, GPTCategory, GPTType
from app.db.session import get_db

# Setup test client
app = FastAPI()
app.include_router(router, prefix="/api/v1/compatibility")

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_compatibility_service():
    with patch("app.dashboard.api.v1.endpoints.compatibility.CompatibilityService") as mock_class:
        service_instance = Mock()
        # Mock all the async methods
        service_instance.check_compatibility = AsyncMock(return_value={
            "status": "success",
            "compatibility_score": 0.95,
            "checks": {
                "dependencies": {"status": "passed", "satisfied_dependencies": ["numpy", "pandas"], "compatibility_issues": []},
                "version": {"status": "passed", "is_compatible": True, "issues": []},
                "integrations": {"status": "passed", "available_integrations": ["lms", "analytics"], "integration_issues": []},
                "resources": {"status": "passed", "satisfied_resources": ["memory", "cpu"], "resource_issues": []}
            },
            "recommendations": [
                "Consider updating dependencies",
                "Monitor resource usage"
            ]
        })
        service_instance.get_compatibility_details = AsyncMock(return_value={
            "dependencies": {"status": "passed", "details": "All dependencies satisfied"},
            "version": {"status": "passed", "details": "Version is compatible"},
            "integrations": {"status": "passed", "details": "Integrations are compatible"},
            "resources": {"status": "passed", "details": "Resource requirements met"}
        })
        service_instance.analyze_compatibility_impact = AsyncMock(return_value={
            "performance_impact": "minimal",
            "security_impact": "none",
            "cost_impact": "low",
            "deployment_impact": "minimal"
        })
        service_instance.get_compatibility_recommendations = AsyncMock(return_value=[
            "Consider updating dependencies",
            "Monitor resource usage"
        ])
        service_instance.get_compatible_gpts = AsyncMock(return_value={
            "status": "success",
            "compatible_gpts": {
                "gpt-2": {
                    "name": "Science Teacher",
                    "compatibility_score": 0.9,
                    "compatibility_details": {
                        "version": "compatible",
                        "resources": "compatible",
                        "integrations": "compatible"
                    }
                }
            },
            "total_compatible": 1,
            "compatibility_summary": {
                "high_compatibility": 1,
                "medium_compatibility": 0,
                "low_compatibility": 0
            }
        })
        service_instance.get_compatibility_metrics = AsyncMock(return_value={
            "overall_score": 0.95,
            "category_score": 0.9,
            "trend": "improving"
        })
        service_instance.get_compatibility_rankings = AsyncMock(return_value=[
            {"gpt_id": "gpt-2", "score": 0.9, "rank": 1},
            {"gpt_id": "gpt-3", "score": 0.85, "rank": 2}
        ])
        service_instance.get_compatibility_improvements = AsyncMock(return_value=[
            "Update numpy to latest version",
            "Increase memory allocation"
        ])
        service_instance.validate_integration_requirements = AsyncMock(return_value={
            "status": "success",
            "integration_type": "lms",
            "validation_results": {
                "requirements_met": True,
                "compatibility_score": 0.95,
                "missing_requirements": [],
                "integration_issues": []
            },
            "recommendations": [
                "Integration is fully compatible",
                "No additional configuration needed"
            ]
        })
        service_instance.get_integration_requirements = AsyncMock(return_value={
            "required_dependencies": ["lms_api"],
            "required_permissions": ["read", "write"],
            "required_configuration": {"api_key": True, "endpoint": True}
        })
        service_instance.get_integration_validation = AsyncMock(return_value={
            "is_compatible": True,
            "compatibility_score": 0.95,
            "issues": []
        })
        service_instance.get_integration_recommendations = AsyncMock(return_value=[
            "Integration is fully compatible",
            "No additional configuration needed"
        ])
        service_instance.get_compatibility_dashboard = AsyncMock(return_value={
            "status": "success",
            "dashboard_data": {
                "overall_stats": {
                    "total_gpts": 10,
                    "compatible_gpts": 8,
                    "average_compatibility_score": 0.85
                },
                "compatibility_by_category": {
                    "TEACHER": {"total": 5, "compatible": 4, "average_score": 0.9},
                    "STUDENT": {"total": 5, "compatible": 4, "average_score": 0.8}
                },
                "compatibility_trends": {
                    "daily": [{"date": "2024-03-20", "average_score": 0.85}]
                },
                "recent_compatibility_checks": [
                    {"gpt_id": "gpt-1", "compatibility_score": 0.95, "timestamp": "2024-03-20T10:00:00Z"}
                ]
            }
        })
        service_instance.get_gpt_compatibility_trends = AsyncMock(return_value={
            "daily": [{"date": "2024-03-20", "score": 0.85}],
            "weekly": [{"week": "2024-W12", "score": 0.87}],
            "monthly": [{"month": "2024-03", "score": 0.86}]
        })
        service_instance.get_gpt_compatibility_issues = AsyncMock(return_value=[
            {"type": "dependency", "severity": "medium", "description": "Dependency conflict"},
            {"type": "resource", "severity": "low", "description": "Resource constraint"}
        ])
        service_instance.get_gpt_compatibility_recommendations = AsyncMock(return_value=[
            {"type": "system", "priority": "high", "description": "Update system dependencies"},
            {"type": "monitoring", "priority": "medium", "description": "Implement compatibility monitoring"}
        ])
        service_instance.get_overall_compatibility_trends = AsyncMock(return_value={
            "daily": [{"date": "2024-03-20", "average_score": 0.85}],
            "weekly": [{"week": "2024-W12", "average_score": 0.87}],
            "monthly": [{"month": "2024-03", "average_score": 0.86}]
        })
        mock_class.return_value = service_instance
        yield service_instance

@pytest.fixture
def client(mock_db):
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

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
async def test_check_compatibility(client, mock_compatibility_service, sample_gpt, sample_target_environment):
    """Test the check compatibility endpoint."""
    response = client.get("/api/v1/compatibility/check/gpt-1")
    assert response.status_code == 200
    data = response.json()
    assert "is_compatible" in data
    assert "compatibility_score" in data
    assert data["compatibility_score"] == 0.95

@pytest.mark.asyncio
async def test_get_compatible_gpts(client, mock_compatibility_service, sample_gpt):
    """Test the get compatible GPTs endpoint."""
    response = client.get("/api/v1/compatibility/compatible/gpt-1")
    assert response.status_code == 200
    data = response.json()
    assert "compatible_gpts" in data
    assert isinstance(data["compatible_gpts"], list)
    assert len(data["compatible_gpts"]) > 0

@pytest.mark.asyncio
async def test_validate_integration_requirements(client, mock_compatibility_service, sample_gpt):
    """Test the validate integration requirements endpoint."""
    response = client.get("/api/v1/compatibility/validate-integration/gpt-1?integration_type=lms")
    assert response.status_code == 200
    data = response.json()
    assert "is_valid" in data
    assert "validation_score" in data
    assert data["validation_score"] == 0.95

@pytest.mark.asyncio
async def test_get_compatibility_dashboard(client, mock_compatibility_service, mock_db):
    """Test getting compatibility dashboard."""
    # Mock the database query to return a list of Mock GPT objects
    mock_gpt1 = Mock()
    mock_gpt1.id = "gpt-1"
    mock_gpt1.name = "Math Teacher"
    mock_gpt1.category = Mock()
    mock_gpt1.category.value = "TEACHER"
    mock_gpt1.type = Mock()
    mock_gpt1.type.value = "MATH_TEACHER"
    
    mock_gpt2 = Mock()
    mock_gpt2.id = "gpt-2"
    mock_gpt2.name = "Science Teacher"
    mock_gpt2.category = Mock()
    mock_gpt2.category.value = "TEACHER"
    mock_gpt2.type = Mock()
    mock_gpt2.type.value = "SCIENCE_TEACHER"
    
    mock_query = Mock()
    mock_query.all.return_value = [mock_gpt1, mock_gpt2]
    mock_query.filter.return_value = mock_query
    
    mock_db.query.return_value = mock_query
    
    response = client.get("/api/v1/compatibility/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "overall_stats" in data
    assert "gpt_metrics" in data
    assert "compatibility_issues" in data
    assert "recommendations" in data

@pytest.mark.asyncio
async def test_input_validation(client):
    """Test input validation for compatibility endpoints."""
    # Test invalid GPT ID - service throws HTTPException which becomes 500
    response = client.get("/api/v1/compatibility/check/invalid-id")
    assert response.status_code == 500  # Service error for invalid GPT ID
    
    # Test invalid integration type - service throws HTTPException which becomes 500
    response = client.get("/api/v1/compatibility/validate-integration/gpt-1?integration_type=")
    assert response.status_code == 500  # Service error for empty integration type 