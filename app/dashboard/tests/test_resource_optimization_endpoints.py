"""
Tests for the resource optimization API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.dashboard.api.v1.endpoints.resource_optimization import router
from app.dashboard.models.gpt_models import GPTCategory, GPTDefinition, GPTType
from app.db.session import get_db
from app.dashboard.dependencies import get_current_user

# Setup test client
app = FastAPI()
app.include_router(router, prefix="/api/v1/dashboard/resource-optimization")

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_optimization_service():
    with patch("app.dashboard.services.resource_optimization_service.ResourceOptimizationService") as mock:
        yield mock

@pytest.fixture
def client(mock_db):
    def override_get_db():
        return mock_db
    
    def override_get_current_user():
        return {"id": "user-1"}
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

def test_optimize_resources(client, mock_db, mock_optimization_service):
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
    
    # Mock the service instantiation and method
    with patch("app.dashboard.api.v1.endpoints.resource_optimization.ResourceOptimizationService") as mock_service_class:
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        mock_service_instance.optimize_resources = AsyncMock(return_value=mock_response)

        # Test endpoint with different optimization targets
        for target in ["balanced", "performance", "efficiency"]:
            response = client.get(f"/api/v1/dashboard/resource-optimization/optimize/gpt-1?optimization_target={target}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            assert response.status_code == 200
            
            data = response.json()
            assert data == mock_response
        
        # Test invalid optimization target
        response = client.get("/api/v1/dashboard/resource-optimization/optimize/gpt-1?optimization_target=invalid")
        assert response.status_code == 422

def test_get_resource_allocation_plan(client, mock_db, mock_optimization_service):
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
    
    # Mock the service instantiation and method
    with patch("app.dashboard.api.v1.endpoints.resource_optimization.ResourceOptimizationService") as mock_service_class:
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        mock_service_instance.get_resource_allocation_plan = AsyncMock(return_value=mock_response)

        # Test endpoint
        response = client.get("/api/v1/dashboard/resource-optimization/allocation-plan")
        assert response.status_code == 200
        
        data = response.json()
        assert data == mock_response
        
        # Test with category filter
        response = client.get("/api/v1/dashboard/resource-optimization/allocation-plan?category=TEACHER")
        assert response.status_code == 200
        
        # Test with time window
        response = client.get("/api/v1/dashboard/resource-optimization/allocation-plan?time_window=7d")
        assert response.status_code == 200
        
        # Test invalid time window
        response = client.get("/api/v1/dashboard/resource-optimization/allocation-plan?time_window=invalid")
        assert response.status_code == 422

def test_get_scaling_recommendations(client, mock_db, mock_optimization_service):
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
    
    # Mock the service instantiation and method
    with patch("app.dashboard.api.v1.endpoints.resource_optimization.ResourceOptimizationService") as mock_service_class:
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        mock_service_instance.get_scaling_recommendations = AsyncMock(return_value=mock_response)

        # Test endpoint
        response = client.get("/api/v1/dashboard/resource-optimization/scaling/gpt-1")
        assert response.status_code == 200
        
        data = response.json()
        assert data == mock_response
        
        # Test with forecast window
        response = client.get("/api/v1/dashboard/resource-optimization/scaling/gpt-1?forecast_window=30d")
        assert response.status_code == 200
        
        # Test invalid forecast window
        response = client.get("/api/v1/dashboard/resource-optimization/scaling/gpt-1?forecast_window=invalid")
        assert response.status_code == 422

def test_get_optimization_dashboard(client, mock_db, mock_optimization_service):
    """Test optimization dashboard endpoint."""
    # Mock service response
    mock_response = {
        "status": "success",
        "total_gpts": 2,
        "optimization_summary": {
            "high_priority": 1,
            "medium_priority": 1,
            "low_priority": 0
        },
        "resource_utilization": {
            "average_cpu": 0.75,
            "average_memory": 0.65,
            "peak_usage": 0.85
        },
        "cost_analysis": {
            "total_cost": 1000.0,
            "potential_savings": 150.0,
            "optimization_opportunities": 5
        },
        "performance_metrics": {
            "average_response_time": 1.2,
            "success_rate": 0.95,
            "error_rate": 0.05
        }
    }
    
    # Mock the service instantiation and method
    with patch("app.dashboard.api.v1.endpoints.resource_optimization.ResourceOptimizationService") as mock_service_class:
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        mock_service_instance.get_optimization_dashboard = AsyncMock(return_value=mock_response)

        # Test endpoint
        response = client.get("/api/v1/dashboard/resource-optimization/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data == mock_response
        
        # Test with category filter
        response = client.get("/api/v1/dashboard/resource-optimization/dashboard?category=TEACHER")
        assert response.status_code == 200
        
        # Test with time window
        response = client.get("/api/v1/dashboard/resource-optimization/dashboard?time_window=7d")
        assert response.status_code == 200
        
        # Test invalid time window
        response = client.get("/api/v1/dashboard/resource-optimization/dashboard?time_window=invalid")
        assert response.status_code == 422

def test_error_handling(client, mock_db, mock_optimization_service):
    """Test error handling in endpoints."""
    # Mock the service instantiation and method
    with patch("app.dashboard.api.v1.endpoints.resource_optimization.ResourceOptimizationService") as mock_service_class:
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        mock_service_instance.optimize_resources = AsyncMock(side_effect=Exception("Service error"))

        # Test endpoint error handling
        response = client.get("/api/v1/dashboard/resource-optimization/optimize/gpt-1")
        assert response.status_code == 500
        
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"].lower()

@pytest.mark.parametrize("endpoint,params", [
    ("/api/v1/dashboard/resource-optimization/optimize/{gpt_id}", {"optimization_target": "balanced"}),
    ("/api/v1/dashboard/resource-optimization/scaling/{gpt_id}", {"forecast_window": "7d"}),
    ("/api/v1/dashboard/resource-optimization/allocation-plan", {"time_window": "24h", "category": "TEACHER"}),
    ("/api/v1/dashboard/resource-optimization/dashboard", {"time_window": "24h", "category": "TEACHER"})
])
def test_endpoint_validation(client, endpoint, params, mock_db, mock_optimization_service):
    """Test input validation for all endpoints."""
    # Mock service responses
    mock_response = {"status": "success"}
    
    # Mock the service instantiation and methods
    with patch("app.dashboard.api.v1.endpoints.resource_optimization.ResourceOptimizationService") as mock_service_class:
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        
        if "/optimize/" in endpoint:
            # Mock service to return success for valid GPT ID and 404 for invalid
            def mock_optimize_resources(gpt_id, optimization_target):
                if gpt_id == "gpt-1":
                    return mock_response
                else:
                    raise HTTPException(status_code=404, detail="GPT not found")
            
            mock_service_instance.optimize_resources = AsyncMock(side_effect=mock_optimize_resources)
            
            # Test with valid GPT ID
            gpt_id = "gpt-1"
            url = endpoint.format(gpt_id=gpt_id)
            query_params = "&".join(f"{k}={v}" for k, v in params.items())
            
            response = client.get(f"{url}?{query_params}")
            assert response.status_code == 200
            
            # Test with invalid GPT ID
            invalid_gpt_id = "invalid-id"
            url = endpoint.format(gpt_id=invalid_gpt_id)
            
            response = client.get(f"{url}?{query_params}")
            assert response.status_code in [404, 422]  # Either not found or validation error
        
        elif "/scaling/" in endpoint:
            # Mock service to return success for valid GPT ID and 404 for invalid
            def mock_get_scaling_recommendations(gpt_id, forecast_window):
                if gpt_id == "gpt-1":
                    return mock_response
                else:
                    raise HTTPException(status_code=404, detail="GPT not found")
            
            mock_service_instance.get_scaling_recommendations = AsyncMock(side_effect=mock_get_scaling_recommendations)
            
            # Test with valid GPT ID
            gpt_id = "gpt-1"
            url = endpoint.format(gpt_id=gpt_id)
            query_params = "&".join(f"{k}={v}" for k, v in params.items())
            
            response = client.get(f"{url}?{query_params}")
            assert response.status_code == 200
            
            # Test with invalid GPT ID
            invalid_gpt_id = "invalid-id"
            url = endpoint.format(gpt_id=invalid_gpt_id)
            
            response = client.get(f"{url}?{query_params}")
            assert response.status_code in [404, 422]  # Either not found or validation error
        
        elif "/allocation-plan" in endpoint:
            mock_service_instance.get_resource_allocation_plan = AsyncMock(return_value=mock_response)
            query_params = "&".join(f"{k}={v}" for k, v in params.items())
            
            response = client.get(f"{endpoint}?{query_params}")
            assert response.status_code == 200
        
        elif "/dashboard" in endpoint:
            mock_service_instance.get_optimization_dashboard = AsyncMock(return_value=mock_response)
            query_params = "&".join(f"{k}={v}" for k, v in params.items())
            
            response = client.get(f"{endpoint}?{query_params}")
            assert response.status_code == 200

@pytest.mark.parametrize("time_window", ["24h", "7d"])
def test_time_window_handling(client, time_window, mock_db, mock_optimization_service):
    """Test handling of different time windows."""
    # Mock service response
    mock_response = {
        "status": "success",
        "allocations": {},
        "total_resources": 0
    }
    
    # Mock the service instantiation and method
    with patch("app.dashboard.api.v1.endpoints.resource_optimization.ResourceOptimizationService") as mock_service_class:
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        mock_service_instance.get_resource_allocation_plan = AsyncMock(return_value=mock_response)

        # Test endpoint with different time windows
        response = client.get(f"/api/v1/dashboard/resource-optimization/allocation-plan?time_window={time_window}")
        assert response.status_code == 200 