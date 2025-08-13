"""
Integration tests for the enhanced cache manager.
"""

import pytest
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any
import redis
from app.dashboard.services.cache_manager import (
    CacheManager,
    CacheStrategy,
    CacheType
)

@pytest.fixture
def redis_client():
    """Create a Redis client for testing."""
    client = redis.Redis(host='redis', port=6379, db=0)
    client.flushdb()  # Clear Redis before tests
    yield client
    client.flushdb()  # Clear Redis after tests

@pytest.fixture
def cache_manager(redis_client):
    """Create a cache manager instance for testing."""
    manager = CacheManager(
        redis_url='redis://redis:6379/0',
        default_ttl=1,
        max_memory_size=100,
        compression_threshold=1024,
        connection_pool_size=5,
        eviction_strategy=CacheStrategy.LRU,
        warmup_enabled=True,
        batch_size=10,
        monitoring_enabled=True
    )
    yield manager
    manager.clear()

def test_basic_operations(cache_manager):
    """Test basic cache operations."""
    # Test set and get
    cache_manager.set('key1', 'value1')
    assert cache_manager.get('key1') == 'value1'
    
    # Test TTL
    time.sleep(2)  # Wait for TTL to expire
    assert cache_manager.get('key1') is None
    
    # Test delete
    cache_manager.set('key2', 'value2')
    cache_manager.delete('key2')
    assert cache_manager.get('key2') is None

def test_batch_operations(cache_manager):
    """Test batch operations."""
    # Test batch set
    items = {f'key{i}': f'value{i}' for i in range(5)}
    cache_manager.batch_set(items)
    
    # Test get_multi
    results = cache_manager.get_multi(list(items.keys()))
    assert results == items
    
    # Test batch delete
    cache_manager.batch_delete(list(items.keys()))
    results = cache_manager.get_multi(list(items.keys()))
    assert not results

def test_cache_warming(cache_manager):
    """Test cache warming functionality."""
    # Queue items for warmup
    for i in range(5):
        cache_manager.warmup_cache(f'warmup_key{i}', f'warmup_value{i}')
    
    # Wait for warmup to complete
    time.sleep(0.5)
    
    # Verify items are in cache
    for i in range(5):
        assert cache_manager.get(f'warmup_key{i}') == f'warmup_value{i}'

def test_eviction_strategies(cache_manager):
    """Test different eviction strategies."""
    strategies = [
        CacheStrategy.LRU,
        CacheStrategy.LFU,
        CacheStrategy.FIFO,
        CacheStrategy.RANDOM
    ]
    
    for strategy in strategies:
        cache_manager.eviction_strategy = strategy
        
        # Fill cache to capacity
        for i in range(110):  # More than max_memory_size
            cache_manager.set(f'key_{strategy.value}_{i}', f'value_{i}')
        
        # Verify cache size is within limits
        assert len(cache_manager._memory_cache) <= cache_manager.max_memory_size

def test_compression(cache_manager):
    """Test data compression."""
    # Create large value
    large_value = 'x' * 2048  # 2KB
    
    # Set value (should be compressed)
    cache_manager.set('large_key', large_value)
    
    # Get value (should be decompressed)
    assert cache_manager.get('large_key') == large_value
    
    # Verify compression stats
    stats = cache_manager.get_stats()
    assert stats['compression_stats']['compressed'] > 0
    assert stats['compression_stats']['decompressed'] > 0

def test_monitoring_metrics(cache_manager):
    """Test monitoring metrics."""
    # Perform operations
    cache_manager.set('metric_key1', 'value1')
    cache_manager.get('metric_key1')
    cache_manager.get('non_existent_key')
    
    # Get stats
    stats = cache_manager.get_stats()
    
    # Verify metrics
    assert stats['stats']['hits']['redis'] + stats['stats']['hits']['memory'] > 0
    assert stats['stats']['misses']['redis'] + stats['stats']['misses']['memory'] > 0
    assert stats['memory_usage']['total'] > 0

def test_concurrent_operations(cache_manager):
    """Test concurrent cache operations."""
    def worker(worker_id: int, results: Dict[str, Any]):
        for i in range(10):
            key = f'concurrent_key_{worker_id}_{i}'
            value = f'value_{worker_id}_{i}'
            cache_manager.set(key, value)
            results[key] = cache_manager.get(key)
    
    # Run multiple workers
    results = {}
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i, results))
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    # Verify results
    for key, value in results.items():
        assert cache_manager.get(key) == value

def test_error_handling(cache_manager, redis_client):
    """Test error handling and fallback."""
    # Simulate Redis failure
    redis_client.shutdown()
    
    # Operations should fall back to memory cache
    cache_manager.set('fallback_key', 'fallback_value')
    assert cache_manager.get('fallback_key') == 'fallback_value'
    
    # Verify Redis is marked as unavailable
    assert not cache_manager._redis_available
    
    # Restore Redis
    redis_client.start()
    cache_manager._redis_available = True
    
    # Verify operations work again
    cache_manager.set('restored_key', 'restored_value')
    assert cache_manager.get('restored_key') == 'restored_value'

def test_performance_benchmark(cache_manager):
    """Test cache performance."""
    import timeit
    
    def benchmark_set():
        cache_manager.set('benchmark_key', 'benchmark_value')
    
    def benchmark_get():
        cache_manager.get('benchmark_key')
    
    # Measure operation times
    set_time = timeit.timeit(benchmark_set, number=1000)
    get_time = timeit.timeit(benchmark_get, number=1000)
    
    # Verify performance is within acceptable limits
    assert set_time < 1.0  # Less than 1 second for 1000 operations
    assert get_time < 1.0  # Less than 1 second for 1000 operations

def test_cleanup(cache_manager):
    """Test cache cleanup."""
    # Fill cache
    for i in range(200):
        cache_manager.set(f'cleanup_key_{i}', f'value_{i}')
    
    # Force cleanup
    cache_manager._clean_memory_cache()
    
    # Verify cache size is within limits
    assert len(cache_manager._memory_cache) <= cache_manager.max_memory_size 