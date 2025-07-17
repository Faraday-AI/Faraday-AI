"""
Tests for the analytics API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from ..api.v1.endpoints.analytics import router
from ..models.gpt_models import GPTCategory, GPTDefinition, GPTType
from ..core import get_db

# Setup test client
app = TestClient(router)

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_analytics_service():
    with patch("app.dashboard.services.analytics_service.AnalyticsService") as mock:
        yield mock

def test_get_performance_trends(mock_db, mock_analytics_service):
    """Test getting performance trends endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "trends": {
            "response_time": {
                "current_value": 0.5,
                "trend": "improving",
                "stability_score": 0.85
            }
        },
        "performance_score": 0.75,
        "recommendations": []
    }
    mock_analytics_service.return_value.get_performance_trends.return_value = mock_response

    # Test endpoint
    response = app.get("/performance/gpt-1/trends?time_range=24h")
    assert response.status_code == 200
    
    data = response.json()
    assert data == mock_response
    
    # Test invalid time range
    response = app.get("/performance/gpt-1/trends?time_range=invalid")
    assert response.status_code == 422

def test_predict_resource_usage(mock_db, mock_analytics_service):
    """Test resource usage prediction endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "predictions": {
            "peak_hours": [9, 14, 16],
            "growth_trend": 0.05,
            "predicted_peak_usage": 0.75
        },
        "confidence_score": 0.8,
        "potential_bottlenecks": []
    }
    mock_analytics_service.return_value.predict_resource_usage.return_value = mock_response

    # Test endpoint
    response = app.get("/performance/gpt-1/resource-prediction?prediction_window=24h")
    assert response.status_code == 200
    
    data = response.json()
    assert data == mock_response
    
    # Test invalid prediction window
    response = app.get("/performance/gpt-1/resource-prediction?prediction_window=invalid")
    assert response.status_code == 422

def test_get_comparative_analysis(mock_db, mock_analytics_service):
    """Test comparative analysis endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "rankings": {
            "accuracy": {
                "value": 0.9,
                "percentile": 0.85,
                "rank": 2,
                "total": 10
            }
        },
        "comparative_metrics": {
            "gpt-1": {"accuracy": 0.9},
            "gpt-2": {"accuracy": 0.95}
        },
        "improvement_opportunities": []
    }
    mock_analytics_service.return_value.get_comparative_analysis.return_value = mock_response

    # Test endpoint
    response = app.get("/performance/gpt-1/comparative")
    assert response.status_code == 200
    
    data = response.json()
    assert data == mock_response
    
    # Test with category filter
    response = app.get("/performance/gpt-1/comparative?category=TEACHER")
    assert response.status_code == 200
    
    # Test invalid category
    response = app.get("/performance/gpt-1/comparative?category=INVALID")
    assert response.status_code == 422

def test_get_analytics_dashboard(mock_db, mock_analytics_service):
    """Test analytics dashboard endpoint."""
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

    # Mock performance trends
    mock_trends = {
        "status": "success",
        "trends": {
            "response_time": {"trend": "stable"},
            "accuracy": {"trend": "improving"}
        },
        "performance_score": 0.85,
        "recommendations": []
    }
    mock_analytics_service.return_value.get_performance_trends.return_value = mock_trends

    # Test endpoint
    response = app.get("/performance/dashboard?time_range=24h")
    assert response.status_code == 200
    
    data = response.json()
    assert "overall_stats" in data
    assert "gpt_metrics" in data
    assert "trending_issues" in data
    assert "optimization_opportunities" in data
    
    # Verify overall stats
    assert data["overall_stats"]["total_gpts"] == len(mock_gpts)
    
    # Test with category filter
    response = app.get("/performance/dashboard?time_range=24h&category=TEACHER")
    assert response.status_code == 200
    
    # Test invalid time range
    response = app.get("/performance/dashboard?time_range=invalid")
    assert response.status_code == 422

def test_error_handling(mock_db, mock_analytics_service):
    """Test error handling in endpoints."""
    # Mock service error
    mock_analytics_service.return_value.get_performance_trends.side_effect = Exception(
        "Service error"
    )

    # Test endpoint error handling
    response = app.get("/performance/gpt-1/trends")
    assert response.status_code == 500
    
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"].lower()

@pytest.mark.parametrize("endpoint,params", [
    ("/performance/{gpt_id}/trends", {"time_range": "24h"}),
    ("/performance/{gpt_id}/resource-prediction", {"prediction_window": "24h"}),
    ("/performance/{gpt_id}/comparative", {"category": "TEACHER"}),
    ("/performance/dashboard", {"time_range": "24h", "category": "TEACHER"})
])
def test_endpoint_validation(endpoint, params, mock_db, mock_analytics_service):
    """Test input validation for all endpoints."""
    # Test with valid GPT ID
    gpt_id = "gpt-1"
    url = endpoint.format(gpt_id=gpt_id)
    query_params = "&".join(f"{k}={v}" for k, v in params.items())
    
    response = app.get(f"{url}?{query_params}")
    assert response.status_code in [200, 404]  # 404 is acceptable if GPT not found
    
    # Test with invalid GPT ID
    invalid_gpt_id = "invalid-id"
    url = endpoint.format(gpt_id=invalid_gpt_id)
    
    response = app.get(f"{url}?{query_params}")
    assert response.status_code in [404, 422]  # Either not found or validation error

@pytest.mark.parametrize("time_range", ["24h", "7d", "30d"])
def test_time_range_handling(time_range, mock_db, mock_analytics_service):
    """Test handling of different time ranges."""
    # Mock service response
    mock_response = {
        "status": "success",
        "trends": {},
        "performance_score": 0.75
    }
    mock_analytics_service.return_value.get_performance_trends.return_value = mock_response

    # Test endpoint with different time ranges
    response = app.get(f"/performance/gpt-1/trends?time_range={time_range}")
    assert response.status_code == 200
    
    # Verify service was called with correct time range
    mock_analytics_service.return_value.get_performance_trends.assert_called_with(
        gpt_id="gpt-1",
        time_range=time_range,
        metrics=None
    ) 