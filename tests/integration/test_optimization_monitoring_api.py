import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import Depends
from sqlalchemy.orm import Session
import importlib

from app.main import app
from app.dashboard.services.optimization_monitoring_service import OptimizationMonitoringService

# Create test client factory with proper state clearing
def get_test_client():
    """Get a fresh test client instance with cleared state."""
    # CRITICAL: Ensure app.state.limiter exists for TestClient
    # SlowAPIMiddleware or Limiter may access request.state.limiter
    # If it doesn't exist, we get AttributeError: 'State' object has no attribute 'limiter'
    if not hasattr(app.state, 'limiter'):
        from slowapi import Limiter
        from slowapi.util import get_remote_address
        app.state.limiter = Limiter(key_func=get_remote_address)
    
    # Create a new client for each call to ensure no shared state
    return TestClient(app)

# Default shared client for most tests (authorized tests can share)
client = get_test_client()

# Note: Global autouse fixture in conftest.py handles app state cleanup
# No need for file-specific autouse fixture - it was causing conflicts

@pytest.fixture
def mock_db():
    """Create a properly configured mock database session."""
    db = Mock(spec=Session)
    db.query = Mock()
    db.commit = Mock()
    db.rollback = Mock()
    db.flush = Mock()
    
    # Configure query chain to return empty list immediately to prevent hanging
    # This prevents real database queries from being executed
    query_mock = Mock()
    filter_mock = Mock()
    all_mock = Mock(return_value=[])  # Return empty list immediately
    
    query_mock.filter.return_value = filter_mock
    filter_mock.all.return_value = []
    query_mock.all.return_value = []
    
    db.query.return_value = query_mock
    
    return db

@pytest.fixture
def mock_monitoring_service(mock_db):
    service = Mock(spec=OptimizationMonitoringService)
    service.get_optimization_metrics = AsyncMock()
    service.get_optimization_insights = AsyncMock()
    return service

@pytest.fixture
def mock_current_user():
    return {"id": "test_user", "role": "admin"}

@pytest.fixture
def override_dependencies(mock_db, mock_current_user, mock_monitoring_service):
    """
    Override FastAPI dependencies for testing.
    
    Best practice: Override the exact dependencies that the endpoint uses.
    The endpoint uses: from ....dependencies import get_db, get_current_user
    """
    # CRITICAL: Import from the exact same location as the endpoint
    # The endpoint uses: from ....dependencies import get_db, get_current_user
    # But dependencies/__init__.py imports get_db from app.db.session, so we need to override both
    from app.db.session import get_db as get_db_actual
    from app.dashboard.dependencies import get_db as get_db_dashboard
    from app.dashboard.dependencies import get_current_user as original_get_current_user
    from app.dashboard.api.v1.endpoints import optimization_monitoring
    
    def override_get_db():
        return mock_db
    
    def override_get_current_user():
        return mock_current_user
    
    # Patch the service class to return our mock
    original_service_class = optimization_monitoring.OptimizationMonitoringService
    
    class MockServiceClass:
        """Mock service class that immediately returns mocked data without database queries."""
        def __init__(self, db):
            # Store db reference but don't use it for queries
            self.db = db
        
        async def get_optimization_metrics(self, org_id, time_range):
            # Directly call the mock without any database operations
            return await mock_monitoring_service.get_optimization_metrics(org_id, time_range)
        
        async def get_optimization_insights(self, org_id, time_range):
            # Directly call the mock without any database operations
            return await mock_monitoring_service.get_optimization_insights(org_id, time_range)
    
    # Store references to the overrides we set, so we can remove only them later
    overrides_to_remove = []
    
    try:
        # Override both get_db functions (they're the same object, but FastAPI might cache differently)
        app.dependency_overrides[get_db_actual] = override_get_db
        overrides_to_remove.append(get_db_actual)
        
        # Also override the dashboard version if it's a different reference
        if get_db_dashboard is not get_db_actual:
            app.dependency_overrides[get_db_dashboard] = override_get_db
            overrides_to_remove.append(get_db_dashboard)
        
        app.dependency_overrides[original_get_current_user] = override_get_current_user
        overrides_to_remove.append(original_get_current_user)
        
        # Temporarily replace the service class
        # CRITICAL: Replace before any imports or endpoint calls
        optimization_monitoring.OptimizationMonitoringService = MockServiceClass
        
        # Ensure the module is reloaded to pick up the change
        importlib.reload(optimization_monitoring)
        
        yield
    finally:
        # BEST PRACTICE: Only remove the specific overrides we set
        # This prevents interference with other tests' overrides in the full suite
        for override_key in overrides_to_remove:
            app.dependency_overrides.pop(override_key, None)
        # Restore service class
        optimization_monitoring.OptimizationMonitoringService = original_service_class
        # Reload module to ensure clean state for next test
        importlib.reload(optimization_monitoring)

# Note: Global autouse fixture in conftest.py handles app state cleanup
# No need for file-specific autouse fixture - it was causing conflicts

def test_get_optimization_metrics(db_session, mock_current_user):
    """Test getting optimization metrics endpoint with real database (no mocks needed)."""
    # Override only get_current_user, use real db and service
    from app.dashboard.dependencies import get_current_user as original_get_current_user
    from app.main import app
    
    def override_get_current_user():
        return mock_current_user
    
    try:
        app.dependency_overrides[original_get_current_user] = override_get_current_user
        
        # Act - use real service with real database
        # Service will return empty/default values if no data exists (gracefully handled)
        response = client.get(
            "/api/v1/optimization-monitoring/metrics/test_org",
            params={"time_range": "24h"},
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert - service handles empty data gracefully, returns default structure
        assert response.status_code == 200
        data = response.json()
        assert "utilization_rate" in data
        assert "sharing_efficiency" in data
        assert "optimization_score" in data
        assert "timestamp" in data
        # With no data, these should be 0.0 (service returns defaults for empty data)
        assert 0 <= data["utilization_rate"] <= 1.0
        assert 0 <= data["sharing_efficiency"] <= 1.0
        assert 0 <= data["optimization_score"] <= 100
        # Anomalies and recommendations may be empty arrays if no data
        assert "anomalies" in data or isinstance(data.get("anomalies"), list)
        assert "recommendations" in data or isinstance(data.get("recommendations"), list)
    finally:
        app.dependency_overrides.pop(original_get_current_user, None)

def test_get_optimization_insights(override_dependencies, mock_monitoring_service, mock_current_user):
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

def test_get_optimization_metrics_invalid_time_range(override_dependencies, mock_monitoring_service, mock_current_user):
    """Test getting optimization metrics with invalid time range."""
    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/metrics/test_org",
        params={"time_range": "invalid"},
        headers={"Authorization": "Bearer test_token"}
    )

    # Assert
    assert response.status_code == 422

@pytest.mark.order(1)  # Run unauthorized tests FIRST to avoid state contamination
def test_get_optimization_metrics_unauthorized():
    """Test getting optimization metrics without authentication."""
    # Use a fresh client and explicitly clear any headers to avoid state contamination
    fresh_client = get_test_client()
    
    # Act - explicitly set empty headers dict to ensure no Authorization header
    # This prevents any default headers from being inherited
    response = fresh_client.get(
        "/api/v1/optimization-monitoring/metrics/test_org",
        params={"time_range": "24h"},
        headers={}  # Explicitly empty headers to clear any state
    )

    # Assert
    assert response.status_code == 401, f"Expected 401 but got {response.status_code}. Response: {response.text}"

@pytest.mark.order(2)  # Run error tests after unauthorized but early to avoid state issues
def test_get_optimization_metrics_error(override_dependencies, mock_monitoring_service, mock_current_user):
    """Test getting optimization metrics with service error."""
    # Arrange - patch the service get_optimization_metrics method
    from app.dashboard.api.v1.endpoints import optimization_monitoring
    
    # Reload module to clear any cached state
    importlib.reload(optimization_monitoring)
    
    # Patch the service class constructor to return a mock that raises
    original_service = optimization_monitoring.OptimizationMonitoringService
    try:
        class MockService:
            def __init__(self, db):
                pass
            async def get_optimization_metrics(self, org_id, time_range):
                raise Exception("Service error")
        
        optimization_monitoring.OptimizationMonitoringService = MockService

        # Act
        response = client.get(
            "/api/v1/optimization-monitoring/metrics/test_org",
            params={"time_range": "24h"},
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 500, f"Expected 500 but got {response.status_code}. Response: {response.text}"
        assert "error" in response.json().get("detail", "").lower() or "error" in str(response.json())
    finally:
        # Always restore original service
        optimization_monitoring.OptimizationMonitoringService = original_service
        importlib.reload(optimization_monitoring)

def test_get_optimization_insights_invalid_time_range(override_dependencies, mock_monitoring_service, mock_current_user):
    """Test getting optimization insights with invalid time range."""
    # Act
    response = client.get(
        "/api/v1/optimization-monitoring/insights/test_org",
        params={"time_range": "invalid"},
        headers={"Authorization": "Bearer test_token"}
    )

    # Assert
    assert response.status_code == 422

@pytest.mark.order(1)  # Run unauthorized tests FIRST to avoid state contamination
def test_get_optimization_insights_unauthorized():
    """Test getting optimization insights without authentication."""
    # Use a fresh client and explicitly clear any headers to avoid state contamination
    fresh_client = get_test_client()
    
    # Act - explicitly set empty headers dict to ensure no Authorization header
    # This prevents any default headers from being inherited
    response = fresh_client.get(
        "/api/v1/optimization-monitoring/insights/test_org",
        params={"time_range": "24h"},
        headers={}  # Explicitly empty headers to clear any state
    )

    # Assert
    assert response.status_code == 401, f"Expected 401 but got {response.status_code}. Response: {response.text}"

@pytest.mark.order(2)  # Run error tests after unauthorized but early to avoid state issues
def test_get_optimization_insights_error(override_dependencies, mock_monitoring_service, mock_current_user):
    """Test getting optimization insights with service error."""
    # Arrange - patch the service get_optimization_insights method
    from app.dashboard.api.v1.endpoints import optimization_monitoring
    
    # Reload module to clear any cached state
    importlib.reload(optimization_monitoring)
    
    # Patch the service class constructor to return a mock that raises
    original_service = optimization_monitoring.OptimizationMonitoringService
    try:
        class MockService:
            def __init__(self, db):
                pass
            async def get_optimization_insights(self, org_id, time_range):
                raise Exception("Service error")
        
        optimization_monitoring.OptimizationMonitoringService = MockService

        # Act
        response = client.get(
            "/api/v1/optimization-monitoring/insights/test_org",
            params={"time_range": "24h"},
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 500, f"Expected 500 but got {response.status_code}. Response: {response.text}"
        assert "error" in response.json().get("detail", "").lower() or "error" in str(response.json())
    finally:
        # Always restore original service
        optimization_monitoring.OptimizationMonitoringService = original_service
        importlib.reload(optimization_monitoring)

def test_get_optimization_metrics_filter_options(override_dependencies, mock_monitoring_service, mock_current_user):
    """Test getting optimization metrics with filter options."""
    # Reload module to clear any cached state
    from app.dashboard.api.v1.endpoints import optimization_monitoring
    importlib.reload(optimization_monitoring)
    
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

def test_get_optimization_insights_filter_options(override_dependencies, mock_monitoring_service, mock_current_user):
    """Test getting optimization insights with filter options."""
    # Reload module to clear any cached state
    from app.dashboard.api.v1.endpoints import optimization_monitoring
    importlib.reload(optimization_monitoring)
    
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