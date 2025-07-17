"""
Tests for the resource optimization API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from ..api.v1.endpoints.resource_optimization import router
from ..models.gpt_models import GPTCategory, GPTDefinition, GPTType
from ..core import get_db

# Setup test client
app = TestClient(router)

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_optimization_service():
    with patch("app.dashboard.services.resource_optimization_service.ResourceOptimizationService") as mock:
        yield mock

def test_optimize_resources(mock_db, mock_optimization_service):
    """Test resource optimization endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "optimization_plan": {
            "recommended_allocation": 1.0,
            "buffer_strategy": "moderate",
            "scaling_threshold": 0.8,
            "growth_adjusted_allocation": 1.1
        },
        "scaling_recommendations": [],
        "estimated_improvements": {
            "estimated_performance_score": 0.85,
            "response_time_improvement": 0.1,
            "reliability_improvement": 0.05
        }
    }
    mock_optimization_service.return_value.optimize_resources.return_value = mock_response

    # Test endpoint with different optimization targets
    for target in ["balanced", "performance", "efficiency"]:
        response = app.get(f"/optimize/gpt-1?optimization_target={target}")
        assert response.status_code == 200
        
        data = response.json()
        assert data == mock_response
    
    # Test invalid optimization target
    response = app.get("/optimize/gpt-1?optimization_target=invalid")
    assert response.status_code == 422

def test_get_resource_allocation_plan(mock_db, mock_optimization_service):
    """Test resource allocation plan endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "allocations": {
            "gpt-1": {
                "base_allocation": 0.8,
                "recommended_allocation": 1.0,
                "proportion": 0.6,
                "scaling_limits": {
                    "min": 0.6,
                    "max": 1.2
                }
            }
        },
        "total_resources": 1.0,
        "optimization_opportunities": []
    }
    mock_optimization_service.return_value.get_resource_allocation_plan.return_value = mock_response

    # Test endpoint
    response = app.get("/allocation-plan")
    assert response.status_code == 200
    
    data = response.json()
    assert data == mock_response
    
    # Test with category filter
    response = app.get("/allocation-plan?category=TEACHER")
    assert response.status_code == 200
    
    # Test with time window
    response = app.get("/allocation-plan?time_window=7d")
    assert response.status_code == 200
    
    # Test invalid time window
    response = app.get("/allocation-plan?time_window=invalid")
    assert response.status_code == 422

def test_get_scaling_recommendations(mock_db, mock_optimization_service):
    """Test scaling recommendations endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "current_utilization": 0.75,
        "scaling_recommendations": [
            {
                "type": "vertical_scaling",
                "urgency": "high",
                "scale_factor": 1.5,
                "reason": "High utilization"
            }
        ],
        "trigger_points": [
            {
                "metric": "utilization",
                "threshold": 0.8,
                "action": "scale_up"
            }
        ],
        "cost_impact": {
            "total_cost_impact": 50.0,
            "breakdown": []
        }
    }
    mock_optimization_service.return_value.get_scaling_recommendations.return_value = mock_response

    # Test endpoint
    response = app.get("/scaling/gpt-1")
    assert response.status_code == 200
    
    data = response.json()
    assert data == mock_response
    
    # Test with forecast window
    response = app.get("/scaling/gpt-1?forecast_window=30d")
    assert response.status_code == 200
    
    # Test invalid forecast window
    response = app.get("/scaling/gpt-1?forecast_window=invalid")
    assert response.status_code == 422

def test_get_optimization_dashboard(mock_db, mock_optimization_service):
    """Test optimization dashboard endpoint."""
    # Mock GPT data
    mock_gpts = [
        GPTDefinition(
            id="gpt-1",
            name="Math Teacher",
            category=GPTCategory.TEACHER,
            type=GPTType.MATH_TEACHER
        ),
        GPTDefinition(
            id="gpt-2",
            name="Science Teacher",
            category=GPTCategory.TEACHER,
            type=GPTType.SCIENCE_TEACHER
        )
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_gpts

    # Mock optimization response
    mock_optimization = {
        "status": "success",
        "optimization_plan": {
            "buffer_strategy": "moderate",
            "recommended_allocation": 1.0
        },
        "estimated_improvements": {
            "estimated_performance_score": 0.85
        },
        "scaling_recommendations": []
    }
    mock_optimization_service.return_value.optimize_resources.return_value = mock_optimization

    # Mock allocation plan
    mock_allocation_plan = {
        "status": "success",
        "total_resources": 2.0,
        "optimization_opportunities": []
    }
    mock_optimization_service.return_value.get_resource_allocation_plan.return_value = mock_allocation_plan

    # Test endpoint
    response = app.get("/dashboard")
    assert response.status_code == 200
    
    data = response.json()
    assert "overall_stats" in data
    assert "gpt_metrics" in data
    assert "optimization_opportunities" in data
    assert "scaling_recommendations" in data
    
    # Verify overall stats
    assert data["overall_stats"]["total_gpts"] == len(mock_gpts)
    
    # Test with category filter
    response = app.get("/dashboard?category=TEACHER")
    assert response.status_code == 200
    
    # Test with time window
    response = app.get("/dashboard?time_window=7d")
    assert response.status_code == 200
    
    # Test invalid time window
    response = app.get("/dashboard?time_window=invalid")
    assert response.status_code == 422

def test_error_handling(mock_db, mock_optimization_service):
    """Test error handling in endpoints."""
    # Mock service error
    mock_optimization_service.return_value.optimize_resources.side_effect = Exception(
        "Service error"
    )

    # Test endpoint error handling
    response = app.get("/optimize/gpt-1")
    assert response.status_code == 500
    
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"].lower()

@pytest.mark.parametrize("endpoint,params", [
    ("/optimize/{gpt_id}", {"optimization_target": "balanced"}),
    ("/scaling/{gpt_id}", {"forecast_window": "7d"}),
    ("/allocation-plan", {"time_window": "24h", "category": "TEACHER"}),
    ("/dashboard", {"time_window": "24h", "category": "TEACHER"})
])
def test_endpoint_validation(endpoint, params, mock_db, mock_optimization_service):
    """Test input validation for all endpoints."""
    # Test with valid GPT ID
    gpt_id = "gpt-1"
    url = endpoint.format(gpt_id=gpt_id)
    query_params = "&".join(f"{k}={v}" for k, v in params.items())
    
    response = app.get(f"{url}?{query_params}")
    assert response.status_code in [200, 404]  # 404 is acceptable if GPT not found
    
    # Test with invalid GPT ID
    if "{gpt_id}" in endpoint:
        invalid_gpt_id = "invalid-id"
        url = endpoint.format(gpt_id=invalid_gpt_id)
        
        response = app.get(f"{url}?{query_params}")
        assert response.status_code in [404, 422]  # Either not found or validation error

@pytest.mark.parametrize("time_window", ["24h", "7d"])
def test_time_window_handling(time_window, mock_db, mock_optimization_service):
    """Test handling of different time windows."""
    # Mock service response
    mock_response = {
        "status": "success",
        "allocations": {},
        "total_resources": 0
    }
    mock_optimization_service.return_value.get_resource_allocation_plan.return_value = mock_response

    # Test endpoint with different time windows
    response = app.get(f"/allocation-plan?time_window={time_window}")
    assert response.status_code == 200
    
    # Verify service was called with correct time window
    mock_optimization_service.return_value.get_resource_allocation_plan.assert_called_with(
        category=None,
        time_window=time_window
    ) 