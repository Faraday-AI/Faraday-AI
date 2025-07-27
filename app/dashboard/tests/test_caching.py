"""
Tests for Redis caching integration in the dashboard services.
"""

import pytest
from unittest.mock import Mock, patch
import redis
import json
from datetime import datetime, timedelta

from app.dashboard.services.monitoring_service import MonitoringService
from app.dashboard.services.compatibility_service import CompatibilityService
from app.dashboard.models.gpt_models import GPTDefinition, GPTCategory, GPTType

@pytest.fixture
def mock_redis():
    with patch('redis.from_url') as mock:
        client = Mock()
        mock.return_value = client
        yield client

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def monitoring_service(mock_db, mock_redis):
    with patch('redis.from_url', return_value=mock_redis):
        return MonitoringService(mock_db, redis_url="redis://localhost:6379")

@pytest.fixture
def compatibility_service(mock_db, mock_redis):
    with patch('redis.from_url', return_value=mock_redis):
        return CompatibilityService(mock_db, redis_url="redis://localhost:6379")

@pytest.fixture
def sample_metrics_data():
    return {
        "active_contexts": 5,
        "average_context_duration": 300.5,
        "context_shares": 15,
        "gpt_switches": 20,
        "total_interactions": 100,
        "performance_metrics": {
            "accuracy": 0.95,
            "response_time": 0.85,
            "user_satisfaction": 0.9
        }
    }

@pytest.fixture
def compatibility_data():
    return {
        "status": "success",
        "compatibility_score": 0.95,
        "checks": {
            "dependencies": {"status": "passed"},
            "version": {"status": "passed"},
            "integrations": {"status": "passed"},
            "resources": {"status": "passed"}
        }
    }

async def test_cache_metrics(monitoring_service, mock_redis, sample_metrics_data):
    """Test caching of monitoring metrics."""
    cache_key = "metrics:user_123"
    
    # Test setting cache
    await monitoring_service._cache_metrics(cache_key, sample_metrics_data)
    mock_redis.setex.assert_called_once()
    
    # Verify cache TTL - setex takes (key, time, value) arguments
    call_args = mock_redis.setex.call_args
    assert call_args[0][0] == cache_key  # key
    assert call_args[0][1] == 300  # time (5 minutes TTL)
    assert call_args[0][2] == json.dumps(sample_metrics_data)  # value

async def test_get_cached_metrics(monitoring_service, mock_redis, sample_metrics_data):
    """Test retrieving cached metrics."""
    cache_key = "metrics:user_123"
    
    # Setup mock redis response
    mock_redis.get.return_value = json.dumps(sample_metrics_data)
    
    # Test getting cached data
    cached_data = await monitoring_service._get_cached_metrics(cache_key)
    assert cached_data == sample_metrics_data
    mock_redis.get.assert_called_once_with(cache_key)
    
    # Test cache miss
    mock_redis.get.return_value = None
    cached_data = await monitoring_service._get_cached_metrics(cache_key)
    assert cached_data is None

async def test_cache_compatibility_results(compatibility_service, mock_redis, compatibility_data):
    """Test caching of compatibility results."""
    gpt_id = "gpt-1"
    cache_key = f"compatibility:{gpt_id}"
    
    # Test setting cache
    await compatibility_service._cache_compatibility_results(gpt_id, compatibility_data)
    mock_redis.setex.assert_called_once()
    
    # Verify cache TTL - setex takes (key, time, value) arguments
    call_args = mock_redis.setex.call_args
    assert call_args[0][0] == cache_key  # key
    assert call_args[0][1] == 300  # time (5 minutes TTL)
    assert call_args[0][2] == json.dumps(compatibility_data)  # value

async def test_get_cached_compatibility(compatibility_service, mock_redis):
    """Test retrieving cached compatibility results."""
    gpt_id = "gpt-1"
    cache_key = f"compatibility:{gpt_id}"
    
    compatibility_data = {
        "status": "success",
        "compatibility_score": 0.95,
        "checks": {
            "dependencies": {"status": "passed"},
            "version": {"status": "passed"},
            "integrations": {"status": "passed"},
            "resources": {"status": "passed"}
        }
    }
    
    # Setup mock redis response
    mock_redis.get.return_value = json.dumps(compatibility_data)
    
    # Test getting cached data
    cached_data = await compatibility_service._get_cached_compatibility(gpt_id)
    assert cached_data == compatibility_data
    mock_redis.get.assert_called_once_with(cache_key)
    
    # Test cache miss
    mock_redis.get.return_value = None
    cached_data = await compatibility_service._get_cached_compatibility(gpt_id)
    assert cached_data is None

async def test_cache_invalidation(monitoring_service, mock_redis):
    """Test cache invalidation."""
    cache_key = "metrics:user_123"
    
    # Test cache invalidation
    await monitoring_service._invalidate_cache(cache_key)
    mock_redis.delete.assert_called_once_with(cache_key)
    
    # Test bulk cache invalidation
    cache_pattern = "metrics:user_*"
    mock_redis.keys.return_value = [b"metrics:user_123", b"metrics:user_456"]
    await monitoring_service._invalidate_cache_pattern(cache_pattern)
    mock_redis.delete.assert_called()

async def test_cache_expiration(monitoring_service, mock_redis, sample_metrics_data):
    """Test cache expiration handling."""
    cache_key = "metrics:user_123"
    
    # Test expired cache
    mock_redis.get.return_value = None
    cached_data = await monitoring_service._get_cached_metrics(cache_key)
    assert cached_data is None
    
    # Test setting new cache after expiration
    await monitoring_service._cache_metrics(cache_key, sample_metrics_data)
    mock_redis.setex.assert_called_once()

async def test_cache_error_handling(monitoring_service, mock_redis):
    """Test error handling in cache operations."""
    cache_key = "metrics:user_123"
    
    # Test redis connection error
    mock_redis.get.side_effect = redis.ConnectionError("Connection refused")
    cached_data = await monitoring_service._get_cached_metrics(cache_key)
    assert cached_data is None
    
    # Test redis timeout
    mock_redis.get.side_effect = redis.TimeoutError("Operation timed out")
    cached_data = await monitoring_service._get_cached_metrics(cache_key)
    assert cached_data is None
    
    # Test general redis error
    mock_redis.get.side_effect = redis.RedisError("Unknown error")
    cached_data = await monitoring_service._get_cached_metrics(cache_key)
    assert cached_data is None 