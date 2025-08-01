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
    AlertConfig
)
from app.core.load_balancer import RoutingStrategy

@pytest.fixture
def mock_cache():
    """Create a mock Redis cache."""
    cache = Mock()
    cache.get.return_value = None
    cache.set.return_value = True
    cache.delete.return_value = True
    return cache

@pytest.fixture
def lb_cache(mock_cache):
    """Create a load balancer cache instance with mocked Redis."""
    lb_cache = LoadBalancerCache()
    lb_cache.cache = mock_cache  # Replace the cache instance with our mock
    return lb_cache

@pytest.fixture
def sample_config():
    """Create a sample load balancer config."""
    config = LoadBalancerConfig()
    config.id = 1
    config.config_key = "routing_strategy"
    config.config_value = {"strategy": "adaptive"}
    config.config_type = "json"
    config.is_active = True
    return config

@pytest.fixture
def sample_region_config():
    """Create a sample region config."""
    config = RegionConfig()
    config.id = 1
    config.region_id = 1  # Reference to LoadBalancerRegion
    config.config_key = "weight"
    config.config_value = {"weight": 1.0}
    config.config_type = "json"
    config.is_active = True
    return config

@pytest.fixture
def sample_metrics():
    """Create sample metrics history."""
    metrics = MetricsHistory()
    metrics.id = 1
    metrics.region_id = 1  # Reference to LoadBalancerRegion
    metrics.metric_type = "requests"
    metrics.metric_value = 100.0
    metrics.timestamp = datetime.utcnow()
    metrics.metric_metadata = {"source": "test"}
    return metrics

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
            {
                'id': 1,
                'config_key': 'routing_strategy',
                'config_value': {'strategy': 'adaptive'},
                'config_type': 'json',
                'is_active': True
            },
            lb_cache.config_ttl
        )
        
        # Test cache hit
        mock_cache.get.return_value = {
            'id': 1,
            'config_key': 'routing_strategy',
            'config_value': {'strategy': 'adaptive'},
            'config_type': 'json',
            'is_active': True
        }
        result = lb_cache.get_config(1)
        assert result == {
            'id': 1,
            'config_key': 'routing_strategy',
            'config_value': {'strategy': 'adaptive'},
            'config_type': 'json',
            'is_active': True
        }
        
    def test_region_caching(self, lb_cache, sample_region_config, mock_cache):
        """Test region configuration caching."""
        # Test cache miss
        assert lb_cache.get_region_config(Region.NORTH_AMERICA) is None
        mock_cache.get.assert_called_once()
        
        # Test cache set - we need to mock the region key since sample_region_config doesn't have a region attribute
        with patch.object(lb_cache, '_get_region_key', return_value='lb:region:north_america'):
            lb_cache.set_region_config(sample_region_config)
            mock_cache.set.assert_called_once_with(
                'lb:region:north_america',
                {
                    'id': 1,
                    'region_id': 1,
                    'config_key': 'weight',
                    'config_value': {'weight': 1.0},
                    'config_type': 'json',
                    'is_active': True
                },
                lb_cache.config_ttl
            )
        
        # Test cache hit
        mock_cache.get.return_value = {
            'id': 1,
            'region_id': 1,
            'config_key': 'weight',
            'config_value': {'weight': 1.0},
            'config_type': 'json',
            'is_active': True
        }
        result = lb_cache.get_region_config(Region.NORTH_AMERICA)
        assert result == {
            'id': 1,
            'region_id': 1,
            'config_key': 'weight',
            'config_value': {'weight': 1.0},
            'config_type': 'json',
            'is_active': True
        }
        
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
            [{
                'id': 1,
                'region_id': 1,
                'metric_type': 'requests',
                'metric_value': 100.0,
                'timestamp': sample_metrics.timestamp.isoformat() if sample_metrics.timestamp else None,
                'metric_metadata': {'source': 'test'}
            }],
            lb_cache.metrics_ttl
        )
        
        # Test metrics expiration
        old_metrics = {
            'id': 1,
            'region_id': 1,
            'metric_type': 'requests',
            'metric_value': 100.0,
            'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            'metric_metadata': {'source': 'test'}
        }
        mock_cache.get.return_value = [old_metrics]
        
        lb_cache.add_metrics(Region.NORTH_AMERICA, sample_metrics)
        # Should only contain the new metrics
        mock_cache.set.assert_called_with(
            lb_cache._get_metrics_key(Region.NORTH_AMERICA),
            [{
                'id': 1,
                'region_id': 1,
                'metric_type': 'requests',
                'metric_value': 100.0,
                'timestamp': sample_metrics.timestamp.isoformat() if sample_metrics.timestamp else None,
                'metric_metadata': {'source': 'test'}
            }],
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