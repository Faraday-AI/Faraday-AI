import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.dashboard.services.optimization_monitoring_service import OptimizationMonitoringService

# Create test client
client = TestClient(app)

@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def mock_monitoring_service(mock_db):
    return Mock(spec=OptimizationMonitoringService)

@pytest.fixture
def mock_current_user():
    return {"id": "test_user", "role": "admin"}

def test_get_optimization_metrics(mock_monitoring_service, mock_current_user):
    """Test getting optimization metrics endpoint."""
    # Arrange
    mock_metrics = {
        "utilization_rate": 0.75,
        "sharing_efficiency": 0.85,
        "optimization_score": 80.0,
        "anomalies": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "resource_type": "compute",
                "usage_amount": 95.0,
                "severity": "high"
            }
        ],
        "recommendations": [
            {
                "type": "utilization",
                "priority": "high",
                "message": "Resource utilization is high"
            }
        ],
        "timestamp": datetime.utcnow()
    }
    mock_monitoring_service.get_optimization_metrics.return_value = mock_metrics

    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/metrics/test_org",
        params={"time_range": "24h"},
        headers={"Authorization": "Bearer test_token"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "utilization_rate" in data
    assert "sharing_efficiency" in data
    assert "optimization_score" in data
    assert "anomalies" in data
    assert "recommendations" in data
    assert "timestamp" in data
    assert 0 <= data["utilization_rate"] <= 1.0
    assert 0 <= data["sharing_efficiency"] <= 1.0
    assert 0 <= data["optimization_score"] <= 100

def test_get_optimization_insights(mock_monitoring_service, mock_current_user):
    """Test getting optimization insights endpoint."""
    # Arrange
    mock_insights = {
        "patterns": {
            "usage_patterns": {
                "peak_hours": [9, 14, 16],
                "resource_distribution": {"compute": 75, "memory": 25},
                "usage_trend": {"direction": "increasing", "rate": 0.15}
            },
            "sharing_patterns": {
                "frequent_partners": {"org_1": 10, "org_2": 8},
                "resource_preferences": {"compute": 15, "memory": 5},
                "sharing_trend": {"direction": "stable", "rate": 0.05}
            }
        },
        "trends": {
            "usage_trend": {"direction": "increasing", "rate": 0.15},
            "sharing_trend": {"direction": "stable", "rate": 0.05},
            "overall_trend": {
                "score": 75.0,
                "direction": "improving",
                "confidence": 0.85
            }
        },
        "opportunities": [
            {
                "type": "underutilized_resources",
                "priority": "high",
                "message": "Some resources are underutilized"
            }
        ],
        "risks": [
            {
                "type": "overutilization",
                "severity": "medium",
                "message": "Resource usage approaching limits"
            }
        ],
        "timestamp": datetime.utcnow()
    }
    mock_monitoring_service.get_optimization_insights.return_value = mock_insights

    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/insights/test_org",
        params={"time_range": "24h"},
        headers={"Authorization": "Bearer test_token"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "patterns" in data
    assert "trends" in data
    assert "opportunities" in data
    assert "risks" in data
    assert "timestamp" in data

def test_get_optimization_metrics_invalid_time_range(mock_monitoring_service, mock_current_user):
    """Test getting optimization metrics with invalid time range."""
    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/metrics/test_org",
        params={"time_range": "invalid"},
        headers={"Authorization": "Bearer test_token"}
    )

    # Assert
    assert response.status_code == 422

def test_get_optimization_metrics_unauthorized():
    """Test getting optimization metrics without authentication."""
    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/metrics/test_org",
        params={"time_range": "24h"}
    )

    # Assert
    assert response.status_code == 401

def test_get_optimization_metrics_error(mock_monitoring_service, mock_current_user):
    """Test getting optimization metrics with service error."""
    # Arrange
    mock_monitoring_service.get_optimization_metrics.side_effect = Exception("Service error")

    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/metrics/test_org",
        params={"time_range": "24h"},
        headers={"Authorization": "Bearer test_token"}
    )

    # Assert
    assert response.status_code == 500
    assert "error" in response.json()

def test_get_optimization_insights_invalid_time_range(mock_monitoring_service, mock_current_user):
    """Test getting optimization insights with invalid time range."""
    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/insights/test_org",
        params={"time_range": "invalid"},
        headers={"Authorization": "Bearer test_token"}
    )

    # Assert
    assert response.status_code == 422

def test_get_optimization_insights_unauthorized():
    """Test getting optimization insights without authentication."""
    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/insights/test_org",
        params={"time_range": "24h"}
    )

    # Assert
    assert response.status_code == 401

def test_get_optimization_insights_error(mock_monitoring_service, mock_current_user):
    """Test getting optimization insights with service error."""
    # Arrange
    mock_monitoring_service.get_optimization_insights.side_effect = Exception("Service error")

    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/insights/test_org",
        params={"time_range": "24h"},
        headers={"Authorization": "Bearer test_token"}
    )

    # Assert
    assert response.status_code == 500
    assert "error" in response.json()

def test_get_optimization_metrics_filter_options(mock_monitoring_service, mock_current_user):
    """Test getting optimization metrics with filter options."""
    # Arrange
    mock_metrics = {
        "utilization_rate": 0.75,
        "sharing_efficiency": 0.85,
        "optimization_score": 80.0,
        "anomalies": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "resource_type": "compute",
                "usage_amount": 95.0,
                "severity": "high"
            }
        ],
        "recommendations": [
            {
                "type": "utilization",
                "priority": "high",
                "message": "Resource utilization is high"
            }
        ],
        "timestamp": datetime.utcnow()
    }
    mock_monitoring_service.get_optimization_metrics.return_value = mock_metrics

    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/metrics/test_org",
        params={
            "time_range": "24h",
            "include_anomalies": False,
            "include_recommendations": False
        },
        headers={"Authorization": "Bearer test_token"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "utilization_rate" in data
    assert "sharing_efficiency" in data
    assert "optimization_score" in data
    assert "anomalies" not in data
    assert "recommendations" not in data

def test_get_optimization_insights_filter_options(mock_monitoring_service, mock_current_user):
    """Test getting optimization insights with filter options."""
    # Arrange
    mock_insights = {
        "patterns": {
            "usage_patterns": {
                "peak_hours": [9, 14, 16],
                "resource_distribution": {"compute": 75, "memory": 25}
            }
        },
        "trends": {
            "usage_trend": {"direction": "increasing", "rate": 0.15}
        },
        "opportunities": [
            {
                "type": "underutilized_resources",
                "priority": "high",
                "message": "Some resources are underutilized"
            }
        ],
        "risks": [
            {
                "type": "overutilization",
                "severity": "medium",
                "message": "Resource usage approaching limits"
            }
        ],
        "timestamp": datetime.utcnow()
    }
    mock_monitoring_service.get_optimization_insights.return_value = mock_insights

    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/insights/test_org",
        params={
            "time_range": "24h",
            "include_patterns": False,
            "include_trends": False,
            "include_opportunities": False,
            "include_risks": False
        },
        headers={"Authorization": "Bearer test_token"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "patterns" not in data
    assert "trends" not in data
    assert "opportunities" not in data
    assert "risks" not in data
    assert "timestamp" in data 