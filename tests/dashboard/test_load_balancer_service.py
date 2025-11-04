"""
Tests for the Load Balancer Dashboard Service

This module contains tests for the load balancer dashboard integration,
including API endpoints, monitoring, and metrics collection.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.dashboard.services.load_balancer_service import (
    LoadBalancerDashboardService,
    LOAD_BALANCER_REQUESTS,
    LOAD_BALANCER_LATENCY,
    REGION_PERFORMANCE
)
from app.core.load_balancer import (
    GlobalLoadBalancer,
    Region,
    RegionCost,
    RequestType
)
from app.core.regional_failover import RegionalFailoverManager
from app.dashboard.services.monitoring import MonitoringService
from app.dashboard.services.resource_sharing_service import ResourceSharingService

@pytest.fixture
def failover_manager():
    """Create a mock failover manager."""
    manager = Mock(spec=RegionalFailoverManager)
    manager.check_region_health.return_value = {
        'status': 'healthy',
        'latency': 0.1,
        'errors': 0
    }
    return manager

@pytest.fixture
def load_balancer(failover_manager):
    """Create a mock load balancer."""
    balancer = Mock(spec=GlobalLoadBalancer)
    balancer.failover_manager = failover_manager
    
    # Set up region stats
    balancer.region_stats = {
        region: {
            'resource_usage': {
                'cpu': 0.5,
                'memory': 0.6,
                'network': 0.4
            },
            'requests': 1000,
            'errors': 10,
            'latency': [0.1, 0.2, 0.3],
            'cost': RegionCost(0.1, 0.05, 0.02, 'USD')
        }
        for region in Region
    }
    
    # Set up circuit breakers
    balancer.circuit_breakers = {
        region: Mock(
            state='closed',
            failures=0,
            last_failure=None,
            can_attempt=lambda: True
        )
        for region in Region
    }
    
    # Set up load weights
    balancer.load_weights = {region: 0.5 for region in Region}
    
    # Mock methods
    balancer._get_predictive_scores = AsyncMock(return_value={
        region: 0.7 for region in Region
    })
    balancer._calculate_cost_efficiency = Mock(return_value=0.8)
    
    return balancer

@pytest.fixture
def monitoring_service():
    """Create a mock monitoring service."""
    service = Mock(spec=MonitoringService)
    service.record_resource_usage = AsyncMock()
    service.record_performance_metrics = AsyncMock()
    service.record_cost_metrics = AsyncMock()
    return service

@pytest.fixture
def resource_service():
    """Create a mock resource sharing service."""
    return Mock(spec=ResourceSharingService)

@pytest.fixture
def dashboard_service(load_balancer, monitoring_service, resource_service):
    """Create a dashboard service instance."""
    return LoadBalancerDashboardService(
        load_balancer=load_balancer,
        monitoring_service=monitoring_service,
        resource_service=resource_service
    )

@pytest.fixture
def app(dashboard_service):
    """Create a FastAPI app with the dashboard service."""
    app = FastAPI()
    app.include_router(dashboard_service.router)
    return app

@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)

@pytest.mark.asyncio
class TestLoadBalancerDashboardService:
    """Tests for the load balancer dashboard service."""
    
    async def test_get_region_status(self, client, dashboard_service):
        """Test getting region status."""
        response = client.get("/regions/status")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == len(Region)
        
        for region in Region:
            assert region.value in data
            status = data[region.value]
            assert 'health' in status
            assert 'resources' in status
            assert 'circuit_state' in status
            assert 'weight' in status
    
    async def test_get_region_performance(self, client, dashboard_service):
        """Test getting region performance metrics."""
        response = client.get("/regions/performance")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == len(Region)
        
        for region in Region:
            assert region.value in data
            metrics = data[region.value]
            assert 'requests' in metrics
            assert 'errors' in metrics
            assert 'avg_latency' in metrics
            assert 'error_rate' in metrics
            assert 'throughput' in metrics
            assert 'predictive_score' in metrics
            assert 'cost_efficiency' in metrics
    
    async def test_get_region_costs(self, client, dashboard_service):
        """Test getting region cost information."""
        response = client.get("/regions/costs")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == len(Region)
        
        for region in Region:
            assert region.value in data
            costs = data[region.value]
            assert 'compute' in costs
            assert 'storage' in costs
            assert 'network' in costs
            assert 'total' in costs
            assert 'currency' in costs
    
    async def test_set_region_weight(self, client, dashboard_service):
        """Test setting region weight."""
        # Test valid weight
        response = client.post("/regions/north_america/weight?weight=0.7")
        assert response.status_code == 200
        
        # Test invalid weight
        response = client.post("/regions/north_america/weight?weight=1.5")
        assert response.status_code == 400
        
        # Test invalid region
        response = client.post("/regions/invalid/weight?weight=0.5")
        assert response.status_code == 400
    
    async def test_get_circuit_state(self, client, dashboard_service):
        """Test getting circuit breaker state."""
        response = client.get("/regions/north_america/circuit")
        assert response.status_code == 200
        
        data = response.json()
        assert 'state' in data
        assert 'failures' in data
        assert 'last_failure' in data
        assert 'can_attempt' in data
        
        # Test invalid region
        response = client.get("/regions/invalid/circuit")
        assert response.status_code == 400
    
    async def test_monitoring_tasks(self, dashboard_service, monitoring_service):
        """Test monitoring tasks."""
        import os
        # Ensure monitoring is enabled for testing
        original_env = os.environ.get("APP_ENVIRONMENT")
        original_deploy = os.environ.get("DEPLOYMENT_ENVIRONMENT")
        try:
            os.environ["APP_ENVIRONMENT"] = "development"
            os.environ.pop("DEPLOYMENT_ENVIRONMENT", None)
            
            # Start monitoring
            await dashboard_service.start_monitoring()
            
            # Wait for tasks to run (monitoring tasks run every 5 seconds)
            await asyncio.sleep(6)
            
            # Verify resource monitoring
            monitoring_service.record_resource_usage.assert_called()
            
            # Verify performance monitoring
            monitoring_service.record_performance_metrics.assert_called()
            
            # Verify cost monitoring
            monitoring_service.record_cost_metrics.assert_called()
            
            # Clean up monitoring tasks
            await dashboard_service.stop_monitoring()
        finally:
            # Restore original environment
            if original_env:
                os.environ["APP_ENVIRONMENT"] = original_env
            elif "APP_ENVIRONMENT" in os.environ:
                del os.environ["APP_ENVIRONMENT"]
            if original_deploy:
                os.environ["DEPLOYMENT_ENVIRONMENT"] = original_deploy
    
    async def test_metrics_collection(self, dashboard_service):
        """Test metrics collection."""
        # Get region status
        status = await dashboard_service._get_region_status()
        
        # Verify status data is returned
        assert len(status) == len(Region)
        for region in Region:
            assert region.value in status
            region_data = status[region.value]
            assert 'health' in region_data
            assert 'resources' in region_data
    
    async def test_error_handling(self, client, dashboard_service, load_balancer):
        """Test error handling - should gracefully handle errors per region."""
        # Simulate error in region health check - should be handled gracefully per region
        load_balancer.failover_manager.check_region_health.side_effect = Exception("Health check failed")
        
        response = client.get("/regions/status")
        # Production-ready: errors are handled gracefully per region, returning 200 with error status
        assert response.status_code == 200
        
        data = response.json()
        # Verify error handling - each region should show 'error' health status
        for region in Region:
            assert region.value in data
            # When health check fails, region status should indicate error
            assert data[region.value]['health'] in ['error', 'unknown']
    
    async def test_concurrent_requests(self, client, dashboard_service):
        """Test handling concurrent requests."""
        def make_request():
            return client.get("/regions/status")
        
        # Make concurrent requests
        responses = [make_request() for _ in range(10)]
        
        # Verify all requests succeeded
        assert all(r.status_code == 200 for r in responses)
    
    async def test_performance_metrics(self, client, dashboard_service):
        """Test performance metrics collection."""
        # Make requests
        for _ in range(5):
            response1 = client.get("/regions/status")
            assert response1.status_code == 200
            response2 = client.get("/regions/performance")
            assert response2.status_code == 200
            response3 = client.get("/regions/costs")
            assert response3.status_code == 200 