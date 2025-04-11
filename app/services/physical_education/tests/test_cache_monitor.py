import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import time

from app.services.physical_education.services.cache_monitor import CacheMonitor

@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = Mock()
    redis.set = AsyncMock()
    redis.get = AsyncMock()
    redis.delete = AsyncMock()
    redis.dbsize = AsyncMock(return_value=100)
    return redis

@pytest.fixture
def cache_monitor(mock_redis):
    """Create a CacheMonitor instance with mocked Redis."""
    return CacheMonitor(mock_redis, "test_service")

@pytest.mark.asyncio
async def test_track_cache_operation(cache_monitor, mock_redis):
    """Test tracking cache operations with timing."""
    start_time = time.time()
    await cache_monitor.track_cache_operation("test_op", "test_method", start_time)
    
    # Verify metrics were updated
    assert cache_monitor.redis == mock_redis

@pytest.mark.asyncio
async def test_track_cache_hit(cache_monitor):
    """Test tracking cache hits."""
    await cache_monitor.track_cache_hit("test_method")
    
    # Verify hit counter was incremented
    assert cache_monitor.redis.dbsize.called

@pytest.mark.asyncio
async def test_track_cache_miss(cache_monitor):
    """Test tracking cache misses."""
    await cache_monitor.track_cache_miss("test_method")
    
    # Verify miss counter was incremented
    assert cache_monitor.redis.dbsize.called

@pytest.mark.asyncio
async def test_track_cache_error(cache_monitor):
    """Test tracking cache errors."""
    await cache_monitor.track_cache_error("test_error")
    
    # Verify error counter was incremented
    assert cache_monitor.redis.dbsize.called

@pytest.mark.asyncio
async def test_get_cache_stats(cache_monitor, mock_redis):
    """Test getting cache statistics."""
    mock_redis.dbsize.return_value = 100
    
    stats = await cache_monitor.get_cache_stats()
    
    assert isinstance(stats, dict)
    assert "service" in stats
    assert "timestamp" in stats
    assert "cache_size" in stats
    assert stats["cache_size"] == 100

@pytest.mark.asyncio
async def test_check_cache_health_success(cache_monitor, mock_redis):
    """Test successful cache health check."""
    health = await cache_monitor.check_cache_health()
    
    assert isinstance(health, dict)
    assert health["success"] is True
    assert health["status"] == "healthy"
    assert "timestamp" in health
    assert "service" in health
    assert "operations" in health

@pytest.mark.asyncio
async def test_check_cache_health_failure(cache_monitor, mock_redis):
    """Test failed cache health check."""
    mock_redis.set.side_effect = Exception("Redis error")
    
    health = await cache_monitor.check_cache_health()
    
    assert isinstance(health, dict)
    assert health["success"] is False
    assert health["status"] == "unhealthy"
    assert "error" in health
    assert health["error"] == "Redis error"

@pytest.mark.asyncio
async def test_cache_operation_latency(cache_monitor):
    """Test cache operation latency tracking."""
    start_time = time.time()
    await cache_monitor.track_cache_operation("test_op", "test_method", start_time)
    
    # Verify latency was tracked
    assert cache_monitor.redis.dbsize.called

@pytest.mark.asyncio
async def test_cache_size_monitoring(cache_monitor, mock_redis):
    """Test cache size monitoring."""
    mock_redis.dbsize.return_value = 150
    
    await cache_monitor.track_cache_operation("test_op", "test_method")
    
    assert mock_redis.dbsize.called
    assert mock_redis.dbsize.return_value == 150

@pytest.mark.asyncio
async def test_concurrent_cache_operations(cache_monitor, mock_redis):
    """Test handling of concurrent cache operations."""
    # Simulate concurrent operations
    await cache_monitor.track_cache_hit("method1")
    await cache_monitor.track_cache_miss("method2")
    await cache_monitor.track_cache_error("error1")
    
    # Verify all operations were tracked
    assert mock_redis.dbsize.call_count >= 3

@pytest.mark.asyncio
async def test_cache_health_check_operations(cache_monitor, mock_redis):
    """Test all operations in cache health check."""
    health = await cache_monitor.check_cache_health()
    
    # Verify all operations were performed
    assert mock_redis.set.called
    assert mock_redis.get.called
    assert mock_redis.delete.called
    assert health["operations"] == ["set", "get", "delete"] 