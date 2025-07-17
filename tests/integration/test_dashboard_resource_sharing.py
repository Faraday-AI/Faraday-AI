import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from app.dashboard.services.dashboard_service import DashboardService
from app.dashboard.services.resource_sharing_service import ResourceSharingService

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_resource_sharing():
    return AsyncMock(spec=ResourceSharingService)

@pytest.fixture
async def dashboard_service(mock_db, mock_resource_sharing):
    service = DashboardService(mock_db)
    service.resource_sharing = mock_resource_sharing
    return service

@pytest.mark.asyncio
async def test_create_resource_usage_widget(dashboard_service):
    """Test creating a resource usage widget."""
    # Arrange
    user_id = "test_user"
    widget_type = "resource_usage"
    config = {
        "organization_id": "test_org",
        "name": "Resource Usage Widget",
        "description": "Test widget"
    }
    
    # Act
    result = await dashboard_service.create_dashboard_widget(
        user_id=user_id,
        widget_type=widget_type,
        configuration=config
    )
    
    # Assert
    assert result["type"] == widget_type
    assert result["name"] == config["name"]
    assert result["description"] == config["description"]
    assert "created_at" in result
    assert "updated_at" in result

@pytest.mark.asyncio
async def test_get_resource_usage_data(dashboard_service):
    """Test getting resource usage data."""
    # Arrange
    widget = {
        "organization_id": "test_org",
        "time_range": "24h"
    }
    mock_metrics = {
        "cpu_usage": 75.5,
        "memory_usage": 82.3,
        "storage_usage": 60.1
    }
    dashboard_service.resource_sharing.get_sharing_metrics.return_value = mock_metrics
    
    # Act
    result = await dashboard_service._get_resource_usage_data(widget)
    
    # Assert
    assert "metrics" in result
    assert result["metrics"] == mock_metrics
    assert "timestamp" in result
    dashboard_service.resource_sharing.get_sharing_metrics.assert_called_once_with(
        org_id="test_org",
        time_range="24h"
    )

@pytest.mark.asyncio
async def test_get_resource_optimization_data(dashboard_service):
    """Test getting resource optimization data."""
    # Arrange
    widget = {
        "organization_id": "test_org",
        "resource_type": "compute",
        "time_range": "24h"
    }
    mock_optimization = {
        "recommendations": [
            {"type": "scaling", "action": "increase", "resource": "cpu"},
            {"type": "allocation", "action": "optimize", "resource": "memory"}
        ]
    }
    dashboard_service.resource_sharing.optimize_resource_allocation.return_value = mock_optimization
    
    # Act
    result = await dashboard_service._get_resource_optimization_data(widget)
    
    # Assert
    assert "optimization" in result
    assert result["optimization"] == mock_optimization
    assert "timestamp" in result
    dashboard_service.resource_sharing.optimize_resource_allocation.assert_called_once_with(
        org_id="test_org",
        resource_type="compute",
        time_range="24h"
    )

@pytest.mark.asyncio
async def test_get_resource_prediction_data(dashboard_service):
    """Test getting resource prediction data."""
    # Arrange
    widget = {
        "organization_id": "test_org",
        "resource_type": "storage",
        "prediction_window": "7d"
    }
    mock_predictions = {
        "predicted_usage": [
            {"timestamp": "2024-01-01T00:00:00", "value": 85.2},
            {"timestamp": "2024-01-02T00:00:00", "value": 87.5}
        ]
    }
    dashboard_service.resource_sharing.predict_resource_needs.return_value = mock_predictions
    
    # Act
    result = await dashboard_service._get_resource_prediction_data(widget)
    
    # Assert
    assert "predictions" in result
    assert result["predictions"] == mock_predictions
    assert "timestamp" in result
    dashboard_service.resource_sharing.predict_resource_needs.assert_called_once_with(
        org_id="test_org",
        resource_type="storage",
        prediction_window="7d"
    )

@pytest.mark.asyncio
async def test_get_cross_org_patterns_data(dashboard_service):
    """Test getting cross-organization patterns data."""
    # Arrange
    widget = {
        "organization_id": "test_org",
        "time_range": "30d"
    }
    mock_patterns = {
        "sharing_patterns": [
            {"org_pair": ["org1", "org2"], "frequency": "high", "resources": ["compute", "storage"]},
            {"org_pair": ["org1", "org3"], "frequency": "medium", "resources": ["memory"]}
        ]
    }
    dashboard_service.resource_sharing.analyze_cross_org_patterns.return_value = mock_patterns
    
    # Act
    result = await dashboard_service._get_cross_org_patterns_data(widget)
    
    # Assert
    assert "patterns" in result
    assert result["patterns"] == mock_patterns
    assert "timestamp" in result
    dashboard_service.resource_sharing.analyze_cross_org_patterns.assert_called_once_with(
        org_id="test_org",
        time_range="30d"
    )

@pytest.mark.asyncio
async def test_get_security_metrics_data(dashboard_service):
    """Test getting security metrics data."""
    # Arrange
    widget = {
        "organization_id": "test_org",
        "resource_type": "compute"
    }
    mock_security = {
        "security_score": 92.5,
        "vulnerabilities": [],
        "recommendations": [
            {"priority": "low", "action": "update_access_policies"}
        ]
    }
    dashboard_service.resource_sharing.enhance_security_measures.return_value = mock_security
    
    # Act
    result = await dashboard_service._get_security_metrics_data(widget)
    
    # Assert
    assert "security" in result
    assert result["security"] == mock_security
    assert "timestamp" in result
    dashboard_service.resource_sharing.enhance_security_measures.assert_called_once_with(
        org_id="test_org",
        resource_type="compute"
    )

@pytest.mark.asyncio
async def test_missing_organization_id(dashboard_service):
    """Test error handling for missing organization ID."""
    # Arrange
    widget = {
        "time_range": "24h"
    }
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await dashboard_service._get_resource_usage_data(widget)
    assert exc_info.value.status_code == 400
    assert "Organization ID is required" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_invalid_widget_type(dashboard_service):
    """Test error handling for invalid widget type."""
    # Arrange
    user_id = "test_user"
    widget_type = "invalid_type"
    config = {
        "organization_id": "test_org",
        "name": "Invalid Widget"
    }
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await dashboard_service.create_dashboard_widget(
            user_id=user_id,
            widget_type=widget_type,
            configuration=config
        )
    assert exc_info.value.status_code == 400
    assert "Invalid widget type" in str(exc_info.value.detail) 