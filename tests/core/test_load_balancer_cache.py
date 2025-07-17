"""
Tests for the load balancer cache implementation.
"""

import pytest
from datetime import datetime, timedelta
import json
from unittest.mock import Mock, patch

from app.core.load_balancer_cache import LoadBalancerCache
from app.core.regional_failover import Region
from app.models.load_balancer import (
    LoadBalancerConfig,
    RegionConfig,
    MetricsHistory,
    AlertConfig,
    RoutingStrategy
)

@pytest.fixture
def mock_cache():
    """Create a mock Redis cache."""
    with patch('app.core.cache.Cache') as mock:
        cache = mock.return_value
        cache.get.return_value = None
        cache.set.return_value = True
        cache.delete.return_value = True
        yield cache

@pytest.fixture
def lb_cache(mock_cache):
    """Create a load balancer cache instance with mocked Redis."""
    return LoadBalancerCache()

@pytest.fixture
def sample_config():
    """Create a sample load balancer config."""
    return LoadBalancerConfig(
        id=1,
        routing_strategy=RoutingStrategy.ADAPTIVE,
        is_active=True,
        settings={"key": "value"}
    )

@pytest.fixture
def sample_region_config():
    """Create a sample region config."""
    return RegionConfig(
        id=1,
        load_balancer_config_id=1,
        region=Region.NORTH_AMERICA,
        weight=1.0,
        is_active=True,
        health_check_settings={"interval": 30},
        circuit_breaker_settings={"threshold": 5}
    )

@pytest.fixture
def sample_metrics():
    """Create sample metrics history."""
    return MetricsHistory(
        id=1,
        region_config_id=1,
        metrics_type="requests",
        value=100.0,
        timestamp=datetime.utcnow(),
        metadata={"source": "test"}
    )

class TestLoadBalancerCache:
    """Test cases for LoadBalancerCache."""
    
    def test_config_caching(self, lb_cache, sample_config, mock_cache):
        """Test load balancer configuration caching."""
        # Test cache miss
        assert lb_cache.get_config(1) is None
        mock_cache.get.assert_called_once()
        
        # Test cache set
        lb_cache.set_config(sample_config)
        mock_cache.set.assert_called_once_with(
            lb_cache._get_config_key(1),
            sample_config.dict(),
            lb_cache.config_ttl
        )
        
        # Test cache hit
        mock_cache.get.return_value = sample_config.dict()
        result = lb_cache.get_config(1)
        assert result == sample_config.dict()
        
    def test_region_caching(self, lb_cache, sample_region_config, mock_cache):
        """Test region configuration caching."""
        # Test cache miss
        assert lb_cache.get_region_config(Region.NORTH_AMERICA) is None
        mock_cache.get.assert_called_once()
        
        # Test cache set
        lb_cache.set_region_config(sample_region_config)
        mock_cache.set.assert_called_once_with(
            lb_cache._get_region_key(Region.NORTH_AMERICA),
            sample_region_config.dict(),
            lb_cache.config_ttl
        )
        
        # Test cache hit
        mock_cache.get.return_value = sample_region_config.dict()
        result = lb_cache.get_region_config(Region.NORTH_AMERICA)
        assert result == sample_region_config.dict()
        
    def test_metrics_caching(self, lb_cache, sample_metrics, mock_cache):
        """Test metrics caching."""
        # Test cache miss
        assert lb_cache.get_recent_metrics(Region.NORTH_AMERICA) is None
        mock_cache.get.assert_called_once()
        
        # Test adding metrics
        lb_cache.add_metrics(Region.NORTH_AMERICA, sample_metrics)
        mock_cache.get.return_value = []  # No existing metrics
        mock_cache.set.assert_called_with(
            lb_cache._get_metrics_key(Region.NORTH_AMERICA),
            [sample_metrics.dict()],
            lb_cache.metrics_ttl
        )
        
        # Test metrics expiration
        old_metrics = sample_metrics.dict()
        old_metrics['timestamp'] = (datetime.utcnow() - timedelta(hours=2)).isoformat()
        mock_cache.get.return_value = [old_metrics]
        
        lb_cache.add_metrics(Region.NORTH_AMERICA, sample_metrics)
        # Should only contain the new metrics
        mock_cache.set.assert_called_with(
            lb_cache._get_metrics_key(Region.NORTH_AMERICA),
            [sample_metrics.dict()],
            lb_cache.metrics_ttl
        )
        
    def test_health_caching(self, lb_cache, mock_cache):
        """Test health status caching."""
        health_status = {
            "status": "healthy",
            "last_check": datetime.utcnow().isoformat(),
            "metrics": {"latency": 45.7}
        }
        
        # Test cache miss
        assert lb_cache.get_health_status(Region.NORTH_AMERICA) is None
        mock_cache.get.assert_called_once()
        
        # Test cache set
        lb_cache.set_health_status(Region.NORTH_AMERICA, health_status)
        mock_cache.set.assert_called_once_with(
            lb_cache._get_health_key(Region.NORTH_AMERICA),
            health_status,
            lb_cache.health_ttl
        )
        
        # Test cache hit
        mock_cache.get.return_value = health_status
        result = lb_cache.get_health_status(Region.NORTH_AMERICA)
        assert result == health_status
        
    def test_cache_invalidation(self, lb_cache, mock_cache):
        """Test cache invalidation methods."""
        # Test config invalidation
        lb_cache.invalidate_config(1)
        mock_cache.delete.assert_called_with(lb_cache._get_config_key(1))
        
        # Test region invalidation
        lb_cache.invalidate_region(Region.NORTH_AMERICA)
        mock_cache.delete.assert_called_with(lb_cache._get_region_key(Region.NORTH_AMERICA))
        
        # Test metrics invalidation
        lb_cache.invalidate_metrics(Region.NORTH_AMERICA)
        mock_cache.delete.assert_called_with(lb_cache._get_metrics_key(Region.NORTH_AMERICA))
        
        # Test health invalidation
        lb_cache.invalidate_health(Region.NORTH_AMERICA)
        mock_cache.delete.assert_called_with(lb_cache._get_health_key(Region.NORTH_AMERICA))
        
    def test_clear_all(self, lb_cache, mock_cache):
        """Test clearing all cache entries."""
        mock_client = Mock()
        mock_client.scan_iter.return_value = ["lb:key1", "lb:key2"]
        
        with patch('app.core.load_balancer_cache.redis_cluster') as mock_cluster:
            mock_cluster.clients = {"region1": mock_client}
            lb_cache.clear_all()
            
            mock_client.scan_iter.assert_called_once_with("lb:*")
            assert mock_client.delete.call_count == 2 