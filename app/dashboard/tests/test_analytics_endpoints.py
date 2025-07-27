"""
Tests for the analytics API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from fastapi import FastAPI

from app.dashboard.api.v1.endpoints.analytics import router
from app.dashboard.models.gpt_models import GPTCategory, GPTDefinition, GPTType
from app.db.session import get_db

# Setup test app and client
app = FastAPI()
app.include_router(router, prefix="/api/v1/dashboard/analytics")
client = TestClient(app)

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_analytics_service():
    with patch("app.dashboard.services.analytics_service.AnalyticsService") as mock:
        yield mock

# Override the get_db dependency for testing
def override_get_db():
    mock_db = Mock()
    # Mock the query chain
    mock_query = Mock()
    mock_join = Mock()
    mock_filter = Mock()
    mock_all = Mock()
    
    # Set up the chain
    mock_db.query.return_value = mock_query
    mock_query.join.return_value = mock_join
    mock_join.filter.return_value = mock_filter
    mock_filter.all.return_value = []
    
    return mock_db

app.dependency_overrides[get_db] = override_get_db

def test_get_performance_trends(mock_db, mock_analytics_service):
    """Test getting performance trends endpoint."""
    # Mock service response that matches the actual service format
    mock_response = {
        "trends": {
            "response_time": [0.5],
            "accuracy": [0.8],
            "user_satisfaction": [0.9],
            "resource_usage": [0.3]
        },
        "timestamps": [datetime.utcnow()],
        "metrics": {
            "response_time": {"current": 0.5, "trend": 0.1},
            "accuracy": {"current": 0.8, "trend": 0.05},
            "user_satisfaction": {"current": 0.9, "trend": 0.02},
            "resource_usage": {"current": 0.3, "trend": -0.1}
        }
    }
    
    # Patch the AnalyticsService instantiation in the endpoint
    with patch("app.dashboard.api.v1.endpoints.analytics.AnalyticsService") as mock_service_class:
        mock_service_instance = Mock()
        # Make the method return an awaitable
        async def async_get_performance_trends(*args, **kwargs):
            return mock_response
        mock_service_instance.get_performance_trends = async_get_performance_trends
        mock_service_class.return_value = mock_service_instance

        # Test endpoint
        response = client.get("/api/v1/dashboard/analytics/performance/gpt-1/trends?time_range=24h")
        assert response.status_code == 200
        
        data = response.json()
        # Check that required fields are present
        assert "trends" in data
        assert "timestamps" in data
        assert "metrics" in data
        assert data["trends"]["response_time"] == [0.5]
        assert data["trends"]["accuracy"] == [0.8]
        assert data["trends"]["user_satisfaction"] == [0.9]
        assert data["trends"]["resource_usage"] == [0.3]
    
    # Test invalid time range
    response = client.get("/api/v1/dashboard/analytics/performance/gpt-1/trends?time_range=invalid")
    assert response.status_code == 422

def test_predict_resource_usage(mock_db, mock_analytics_service):
    """Test resource usage prediction endpoint."""
    # Mock service response
    mock_response = {
        "predictions": {
            "cpu_usage": [0.75, 0.80, 0.70],
            "memory_usage": [0.65, 0.70, 0.60],
            "network_usage": [0.45, 0.50, 0.40]
        },
        "timestamps": [datetime.utcnow().isoformat()],
        "confidence": {
            "overall_confidence": 0.8,
            "data_quality": 0.9,
            "model_accuracy": 0.85,
            "trend_stability": 0.75
        },
        "impact": {
            "performance_impact": {"value": 0.15, "trend": 0.02},
            "cost_impact": {"value": 0.25, "trend": 0.05},
            "scalability_impact": {"value": 0.10, "trend": 0.01},
            "user_experience_impact": {"value": 0.20, "trend": 0.03}
        },
        "optimization": {
            "recommendations": [
                "Consider horizontal scaling for peak hours",
                "Implement auto-scaling policies"
            ],
            "optimization_score": ["0.75", "0.65"]
        },
        "risk": {
            "risk_level": {"value": 0.3, "trend": 0.05},
            "risk_factors": {"value": 0.25, "trend": 0.02},
            "mitigation_strategies": {"value": 0.8, "trend": 0.01}
        },
        "mitigation": {
            "strategies": [
                "Auto-scaling: Automatically scale resources based on demand",
                "Load balancing: Distribute load across multiple instances"
            ]
        }
    }
    
    # Patch the AnalyticsService instantiation in the endpoint
    with patch("app.dashboard.api.v1.endpoints.analytics.AnalyticsService") as mock_service_class:
        mock_service_instance = Mock()
        # Make the method return an awaitable
        async def async_predict_resource_usage(*args, **kwargs):
            return mock_response
        mock_service_instance.predict_resource_usage = async_predict_resource_usage
        mock_service_class.return_value = mock_service_instance

        # Test endpoint
        response = client.get("/api/v1/dashboard/analytics/performance/gpt-1/resource-prediction?prediction_window=24h")
        assert response.status_code == 200
        
        data = response.json()
        assert data == mock_response
    
    # Test invalid prediction window
    response = client.get("/api/v1/dashboard/analytics/performance/gpt-1/resource-prediction?prediction_window=invalid")
    assert response.status_code == 422

def test_get_comparative_analysis(mock_db, mock_analytics_service):
    """Test comparative analysis endpoint."""
    # Mock service response
    mock_response = {
        "metrics": {
            "gpt-1": {"accuracy": 0.9},
            "gpt-2": {"accuracy": 0.95}
        },
        "rankings": {
            "accuracy": 2
        },
        "improvements": {
            "accuracy": ["Improve accuracy", "Optimize response time"]
        }
    }

    # Patch the AnalyticsService instantiation in the endpoint
    with patch("app.dashboard.api.v1.endpoints.analytics.AnalyticsService") as mock_service_class:
        mock_service_instance = Mock()
        
        # Make the methods return awaitables
        async def async_get_comparative_analysis(*args, **kwargs):
            return mock_response
        
        async def async_get_industry_benchmarks(*args, **kwargs):
            return {"accuracy": {"benchmark": 0.85}, "response_time": {"benchmark": 0.5}}
        
        async def async_get_comparative_rankings(*args, **kwargs):
            return {"accuracy": 2}
        
        async def async_get_improvement_recommendations(*args, **kwargs):
            return {"accuracy": ["Improve accuracy", "Optimize response time"]}
        
        async def async_get_comparative_insights(*args, **kwargs):
            return {"performance": "Above average", "trends": "Improving"}
        
        async def async_get_improvement_opportunities(*args, **kwargs):
            return {"accuracy": ["Accuracy optimization", "Response time reduction"]}
        
        mock_service_instance.get_comparative_analysis = async_get_comparative_analysis
        mock_service_instance.get_industry_benchmarks = async_get_industry_benchmarks
        mock_service_instance.get_comparative_rankings = async_get_comparative_rankings
        mock_service_instance.get_improvement_recommendations = async_get_improvement_recommendations
        mock_service_instance.get_comparative_insights = async_get_comparative_insights
        mock_service_instance.get_improvement_opportunities = async_get_improvement_opportunities
        
        mock_service_class.return_value = mock_service_instance

        # Test endpoint
        response = client.get("/api/v1/dashboard/analytics/performance/gpt-1/comparative")
        assert response.status_code == 200
        
        data = response.json()
        assert "metrics" in data
        assert "rankings" in data
        assert "improvements" in data
        assert "benchmarks" in data
        assert "insights" in data
        assert "opportunities" in data
        
        # Test invalid category
        response = client.get("/api/v1/dashboard/analytics/performance/gpt-1/comparative?category=INVALID")
        assert response.status_code == 422

def test_get_analytics_dashboard(mock_db, mock_analytics_service):
    """Test analytics dashboard endpoint."""
    # Mock GPT data
    mock_gpts = [
        Mock(
            id="gpt-1",
            name="Math Teacher",
            category=GPTCategory.TEACHER,
            type=GPTType.MATH_TEACHER
        ),
        Mock(
            id="gpt-2",
            name="Science Teacher",
            category=GPTCategory.TEACHER,
            type=GPTType.SCIENCE_TEACHER
        )
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_gpts

    # Mock dashboard response
    mock_dashboard_response = {
        "summary": {
            "total_gpts": {"count": 2.0},
            "active_gpts": {"count": 2.0},
            "total_usage": {"count": 200.0},
            "average_performance": {"score": 0.85}
        }
    }

    # Patch the AnalyticsService instantiation in the endpoint
    with patch("app.dashboard.api.v1.endpoints.analytics.AnalyticsService") as mock_service_class:
        mock_service_instance = Mock()
        
        # Make the methods return awaitables
        async def async_get_analytics_dashboard(*args, **kwargs):
            return mock_dashboard_response
        
        async def async_get_dashboard_trends(*args, **kwargs):
            return {"response_time": [0.5, 0.48, 0.52]}
        
        async def async_get_dashboard_alerts(*args, **kwargs):
            return {"alert-1": {"type": "performance", "severity": "medium", "message": "Test alert"}}
        
        async def async_get_dashboard_optimization(*args, **kwargs):
            return {"high_priority": ["Optimize performance"]}
        
        async def async_get_dashboard_insights(*args, **kwargs):
            return {"performance": "Performance is stable"}
        
        async def async_get_dashboard_forecast(*args, **kwargs):
            return {"response_time": [0.48, 0.47, 0.49]}
        
        mock_service_instance.get_analytics_dashboard = async_get_analytics_dashboard
        mock_service_instance.get_dashboard_trends = async_get_dashboard_trends
        mock_service_instance.get_dashboard_alerts = async_get_dashboard_alerts
        mock_service_instance.get_dashboard_optimization = async_get_dashboard_optimization
        mock_service_instance.get_dashboard_insights = async_get_dashboard_insights
        mock_service_instance.get_dashboard_forecast = async_get_dashboard_forecast
        
        mock_service_class.return_value = mock_service_instance

        # Test endpoint
        response = client.get("/api/v1/dashboard/analytics/performance/dashboard?time_range=24h")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert "total_gpts" in data["summary"]
        assert "active_gpts" in data["summary"]
        assert "total_usage" in data["summary"]
        assert "average_performance" in data["summary"]
        
        # Verify summary stats
        assert data["summary"]["total_gpts"]["count"] == 2.0
        
        # Test with category filter
        response = client.get("/api/v1/dashboard/analytics/performance/dashboard?time_range=24h")
        assert response.status_code == 200
        
        # Test invalid time range
        response = client.get("/api/v1/dashboard/analytics/performance/dashboard?time_range=invalid")
        assert response.status_code == 422

def test_error_handling(mock_db, mock_analytics_service):
    """Test error handling in endpoints."""
    # Patch the AnalyticsService instantiation in the endpoint to throw an error
    with patch("app.dashboard.api.v1.endpoints.analytics.AnalyticsService") as mock_service_class:
        mock_service_instance = Mock()
        
        # Make the method throw an exception
        async def async_get_performance_trends(*args, **kwargs):
            raise Exception("Service error")
        
        mock_service_instance.get_performance_trends = async_get_performance_trends
        mock_service_class.return_value = mock_service_instance

        # Test endpoint error handling
        response = client.get("/api/v1/dashboard/analytics/performance/gpt-1/trends")
        assert response.status_code == 500
        
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"].lower()

@pytest.mark.parametrize("endpoint,params", [
    ("/performance/{gpt_id}/trends", {"time_range": "24h"}),
    ("/performance/{gpt_id}/resource-prediction", {"prediction_window": "24h"}),
    ("/performance/{gpt_id}/comparative", {}),
    ("/performance/dashboard", {"time_range": "24h"})
])
def test_endpoint_validation(endpoint, params, mock_db, mock_analytics_service):
    """Test input validation for all endpoints."""
    # Patch the AnalyticsService instantiation in the endpoint
    with patch("app.dashboard.api.v1.endpoints.analytics.AnalyticsService") as mock_service_class:
        mock_service_instance = Mock()
        
        # Make the methods return awaitables
        async def async_get_performance_trends(*args, **kwargs):
            return {"trends": {}, "timestamps": [], "metrics": {}}
        
        async def async_predict_resource_usage(*args, **kwargs):
            return {"predictions": {"cpu": [0.5, 0.6, 0.7], "memory": [0.4, 0.5, 0.6]}, "timestamps": [datetime.utcnow()]}
        
        async def async_get_comparative_analysis(*args, **kwargs):
            return {"metrics": {"gpt-1": {"accuracy": 0.9}}, "rankings": {"accuracy": 1}, "improvements": {"accuracy": ["Improve accuracy"]}}
        
        async def async_get_analytics_dashboard(*args, **kwargs):
            return {"summary": {"total_gpts": {"count": 1.0}, "active_gpts": {"count": 1.0}, "total_usage": {"count": 100.0}, "average_performance": {"score": 0.8}}}
        
        mock_service_instance.get_performance_trends = async_get_performance_trends
        mock_service_instance.predict_resource_usage = async_predict_resource_usage
        mock_service_instance.get_comparative_analysis = async_get_comparative_analysis
        mock_service_instance.get_analytics_dashboard = async_get_analytics_dashboard
        mock_service_instance.get_industry_benchmarks = AsyncMock(return_value={})
        mock_service_instance.get_comparative_rankings = AsyncMock(return_value={})
        mock_service_instance.get_improvement_recommendations = AsyncMock(return_value={"accuracy": ["Improve accuracy"]})
        mock_service_instance.get_comparative_insights = AsyncMock(return_value={"performance": "Above average"})
        mock_service_instance.get_improvement_opportunities = AsyncMock(return_value={"accuracy": ["Optimize accuracy"]})
        mock_service_instance.get_dashboard_trends = AsyncMock(return_value={})
        mock_service_instance.get_dashboard_alerts = AsyncMock(return_value={})
        mock_service_instance.get_dashboard_optimization = AsyncMock(return_value={})
        mock_service_instance.get_dashboard_insights = AsyncMock(return_value={})
        mock_service_instance.get_dashboard_forecast = AsyncMock(return_value={})
        
        mock_service_class.return_value = mock_service_instance

        # Test with valid GPT ID
        gpt_id = "gpt-1"
        url = endpoint.format(gpt_id=gpt_id)
        query_params = "&".join(f"{k}={v}" for k, v in params.items())
        
        response = client.get(f"/api/v1/dashboard/analytics{url}?{query_params}")
        assert response.status_code == 200  # Should work with mocked service
        
        # Test with invalid GPT ID - should still work with mocked service
        invalid_gpt_id = "invalid-id"
        url = endpoint.format(gpt_id=invalid_gpt_id)
        
        response = client.get(f"/api/v1/dashboard/analytics{url}?{query_params}")
        assert response.status_code == 200  # Should work with mocked service

@pytest.mark.parametrize("time_range", ["24h", "7d", "30d"])
def test_time_range_handling(time_range, mock_db, mock_analytics_service):
    """Test handling of different time ranges."""
    # Mock service response
    mock_response = {
        "trends": {
            "response_time": [0.5, 0.48, 0.52],
            "accuracy": [0.9, 0.92, 0.88],
            "user_satisfaction": [0.85, 0.87, 0.83],
            "resource_usage": [0.7, 0.72, 0.68]
        },
        "timestamps": [datetime.utcnow()],
        "metrics": {
            "response_time": {"current": 0.52, "trend": 0.02},
            "accuracy": {"current": 0.88, "trend": -0.02},
            "user_satisfaction": {"current": 0.83, "trend": -0.02},
            "resource_usage": {"current": 0.68, "trend": -0.02}
        }
    }

    # Patch the AnalyticsService instantiation in the endpoint
    with patch("app.dashboard.api.v1.endpoints.analytics.AnalyticsService") as mock_service_class:
        mock_service_instance = Mock()
        
        # Track calls to verify parameters
        call_args = []
        
        async def async_get_performance_trends(*args, **kwargs):
            call_args.append((args, kwargs))
            return mock_response
        
        mock_service_instance.get_performance_trends = async_get_performance_trends
        mock_service_class.return_value = mock_service_instance

        # Test endpoint with different time ranges
        response = client.get(f"/api/v1/dashboard/analytics/performance/gpt-1/trends?time_range={time_range}")
        assert response.status_code == 200
        
        # Verify service was called with correct time range
        assert len(call_args) == 1
        args, kwargs = call_args[0]
        assert kwargs["gpt_id"] == "gpt-1"
        assert kwargs["time_range"] == time_range
        assert kwargs["metrics"] is None 