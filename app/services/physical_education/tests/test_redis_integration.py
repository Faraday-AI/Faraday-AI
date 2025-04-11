import pytest
import asyncio
import redis.asyncio as redis
from datetime import datetime
import json
import time

from app.services.physical_education.services.movement_analysis_service import MovementAnalysisService
from app.services.physical_education.models.movement_analysis.movement_models import MovementAnalysis, MovementPattern
from app.services.physical_education.services.rate_limiter import RateLimiter
from app.services.physical_education.services.circuit_breaker import CircuitBreaker
from app.services.physical_education.models.movement import Movement, MovementType, MovementQuality
from app.services.physical_education.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.services.physical_education.models.workout import Workout, WorkoutType, WorkoutStatus

@pytest.fixture
async def redis_client():
    client = redis.Redis(host='localhost', port=6379, db=0)
    yield client
    await client.close()

@pytest.fixture(scope="module")
async def rate_limiter():
    """Create a rate limiter for testing."""
    return RateLimiter(rate=10, burst=20, window=1)

@pytest.fixture(scope="module")
async def circuit_breaker():
    """Create a circuit breaker for testing."""
    return CircuitBreaker(failure_threshold=3, reset_timeout=1)

@pytest.fixture
async def movement_analysis_service(redis_client):
    service = MovementAnalysisService(redis_client=redis_client)
    yield service
    await service.close()

@pytest.mark.asyncio
async def test_redis_connection(redis_client):
    """Test Redis connection"""
    assert await redis_client.ping()
    assert isinstance(redis_client, redis.Redis)

@pytest.mark.asyncio
async def test_cache_operations(movement_analysis_service, redis_client):
    """Test basic cache operations"""
    # Test data
    movement = Movement(
        id="test-movement",
        type=MovementType.SQUAT,
        quality=MovementQuality.GOOD,
        timestamp=datetime.utcnow(),
        metadata={"test": "data"}
    )
    
    # Test caching
    await movement_analysis_service.cache_movement(movement)
    cached = await movement_analysis_service.get_cached_movement(movement.id)
    assert cached is not None
    assert cached.id == movement.id
    
    # Test cache expiration
    await asyncio.sleep(2)  # Wait for cache to expire
    expired = await movement_analysis_service.get_cached_movement(movement.id)
    assert expired is None

@pytest.mark.asyncio
async def test_batch_operations(movement_analysis_service):
    """Test batch cache operations"""
    movements = [
        Movement(
            id=f"test-movement-{i}",
            type=MovementType.SQUAT,
            quality=MovementQuality.GOOD,
            timestamp=datetime.utcnow(),
            metadata={"test": f"data-{i}"}
        )
        for i in range(3)
    ]
    
    # Cache multiple movements
    await movement_analysis_service.cache_movements(movements)
    
    # Retrieve cached movements
    cached = await movement_analysis_service.get_cached_movements([m.id for m in movements])
    assert len(cached) == 3
    assert all(m.id in [c.id for c in cached] for m in movements)

@pytest.mark.asyncio
async def test_cache_cleanup(movement_analysis_service, redis_client):
    """Test cache cleanup operations"""
    # Create test data
    movement = Movement(
        id="test-cleanup",
        type=MovementType.SQUAT,
        quality=MovementQuality.GOOD,
        timestamp=datetime.utcnow()
    )
    
    # Cache the movement
    await movement_analysis_service.cache_movement(movement)
    
    # Verify it's cached
    cached = await movement_analysis_service.get_cached_movement(movement.id)
    assert cached is not None
    
    # Cleanup cache
    await movement_analysis_service.cleanup_cache()
    
    # Verify cache is empty
    cleaned = await movement_analysis_service.get_cached_movement(movement.id)
    assert cleaned is None

@pytest.mark.asyncio
async def test_error_handling(movement_analysis_service):
    """Test error handling in cache operations"""
    # Test with invalid movement ID
    result = await movement_analysis_service.get_cached_movement("invalid-id")
    assert result is None
    
    # Test with None movement
    with pytest.raises(ValueError):
        await movement_analysis_service.cache_movement(None)

@pytest.mark.asyncio
async def test_concurrent_operations(movement_analysis_service):
    """Test concurrent cache operations"""
    async def cache_operation(movement_id):
        movement = Movement(
            id=movement_id,
            type=MovementType.SQUAT,
            quality=MovementQuality.GOOD,
            timestamp=datetime.utcnow()
        )
        await movement_analysis_service.cache_movement(movement)
        return await movement_analysis_service.get_cached_movement(movement_id)
    
    # Run concurrent operations
    tasks = [cache_operation(f"concurrent-{i}") for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    # Verify all operations completed successfully
    assert all(result is not None for result in results)
    assert len(results) == 5

@pytest.mark.asyncio
async def test_cache_operations_with_rate_limiting(movement_analysis_service, redis_client, rate_limiter):
    """Test basic cache operations with rate limiting."""
    # Test data
    test_key = "test_key"
    test_value = {"data": "test"}
    
    # Set value with rate limiting
    @rate_limiter
    async def set_value():
        await redis_client.set(test_key, json.dumps(test_value))
    
    await set_value(client_id="test_client")
    
    # Get value with rate limiting
    @rate_limiter
    async def get_value():
        return await redis_client.get(test_key)
    
    cached_value = await get_value(client_id="test_client")
    assert cached_value is not None
    assert json.loads(cached_value) == test_value
    
    # Delete value with rate limiting
    @rate_limiter
    async def delete_value():
        await redis_client.delete(test_key)
    
    await delete_value(client_id="test_client")
    assert await redis_client.get(test_key) is None

@pytest.mark.asyncio
async def test_rate_limiting_enforcement(movement_analysis_service, redis_client, rate_limiter):
    """Test rate limiting enforcement with Redis operations."""
    test_key = "rate_limit_test"
    test_value = {"data": "test"}
    
    # Make requests up to burst limit
    for i in range(rate_limiter.burst):
        @rate_limiter
        async def set_value():
            await redis_client.set(f"{test_key}_{i}", json.dumps(test_value))
        
        await set_value(client_id="test_client")
    
    # Next request should exceed rate limit
    with pytest.raises(Exception):
        @rate_limiter
        async def set_value():
            await redis_client.set(f"{test_key}_overflow", json.dumps(test_value))
        
        await set_value(client_id="test_client")

@pytest.mark.asyncio
async def test_circuit_breaker_with_redis(movement_analysis_service, redis_client, circuit_breaker):
    """Test circuit breaker with Redis operations."""
    test_key = "circuit_breaker_test"
    test_value = {"data": "test"}
    
    # Simulate Redis failures
    @circuit_breaker
    async def failing_operation():
        raise Exception("Redis error")
    
    # First failure
    with pytest.raises(Exception):
        await failing_operation()
    
    # Second failure
    with pytest.raises(Exception):
        await failing_operation()
    
    # Third failure - should open circuit
    with pytest.raises(Exception):
        await failing_operation()
    
    # Circuit should be open
    assert circuit_breaker.state == "open"
    
    # Wait for reset timeout
    await asyncio.sleep(1.1)
    
    # Circuit should be half-open
    assert circuit_breaker.state == "half-open"
    
    # Successful operation should close circuit
    @circuit_breaker
    async def successful_operation():
        await redis_client.set(test_key, json.dumps(test_value))
        return await redis_client.get(test_key)
    
    result = await successful_operation()
    assert result is not None
    assert circuit_breaker.state == "closed"

@pytest.mark.asyncio
async def test_combined_rate_limiting_and_circuit_breaker(movement_analysis_service, redis_client, rate_limiter, circuit_breaker):
    """Test combined rate limiting and circuit breaker."""
    test_key = "combined_test"
    test_value = {"data": "test"}
    
    @rate_limiter
    @circuit_breaker
    async def combined_operation():
        await redis_client.set(test_key, json.dumps(test_value))
        return await redis_client.get(test_key)
    
    # Successful operation
    result = await combined_operation(client_id="test_client")
    assert result is not None
    assert json.loads(result) == test_value
    
    # Simulate rate limit
    for _ in range(rate_limiter.burst):
        await combined_operation(client_id="test_client")
    
    # Should hit rate limit
    with pytest.raises(Exception):
        await combined_operation(client_id="test_client")
    
    # Simulate circuit breaker
    for _ in range(circuit_breaker.failure_threshold):
        with pytest.raises(Exception):
            await failing_operation()
    
    # Circuit should be open
    assert circuit_breaker.state == "open"

@pytest.mark.asyncio
async def test_performance_metrics(movement_analysis_service, redis_client, rate_limiter):
    """Test performance metrics with rate limiting."""
    test_key = "performance_test"
    test_value = {"data": "test"}
    
    # Measure operation time
    start_time = time.time()
    
    @rate_limiter
    async def timed_operation():
        await redis_client.set(test_key, json.dumps(test_value))
        return await redis_client.get(test_key)
    
    result = await timed_operation(client_id="test_client")
    operation_time = time.time() - start_time
    
    assert result is not None
    assert operation_time < 0.1  # Should complete within 100ms
    
    # Check rate limiter stats
    stats = rate_limiter.get_usage("test_client")
    assert stats["requests"] > 0
    assert stats["remaining_tokens"] < rate_limiter.burst

@pytest.mark.asyncio
async def test_cache_ttl(movement_analysis_service, redis_client):
    """Test cache TTL functionality."""
    test_key = "ttl_test"
    test_value = {"data": "test"}
    
    # Set with TTL
    await redis_client.set(test_key, json.dumps(test_value), ex=1)
    
    # Should exist
    assert await redis_client.get(test_key) is not None
    
    # Wait for TTL
    await asyncio.sleep(1.1)
    
    # Should be expired
    assert await redis_client.get(test_key) is None

@pytest.mark.asyncio
async def test_cache_memory_usage(movement_analysis_service, redis_client):
    """Test cache memory usage."""
    # Store multiple values
    for i in range(100):
        key = f"memory_test_{i}"
        value = {"data": "x" * 1000}  # 1KB per value
        await redis_client.set(key, json.dumps(value))
    
    # Check memory usage
    info = await redis_client.info("memory")
    used_memory = int(info["used_memory"])
    
    # Memory usage should be reasonable
    assert used_memory < 10 * 1024 * 1024  # Less than 10MB

@pytest.mark.asyncio
async def test_cache_recovery(movement_analysis_service, redis_client):
    """Test cache recovery after connection issues."""
    # Store value
    test_key = "recovery_test"
    test_value = {"data": "test"}
    await redis_client.set(test_key, json.dumps(test_value))
    
    # Simulate connection issue
    await redis_client.close()
    
    # Reconnect
    await redis_client.initialize()
    
    # Value should still exist
    cached_value = await redis_client.get(test_key)
    assert cached_value is not None
    assert json.loads(cached_value) == test_value

@pytest.mark.asyncio
async def test_concurrent_cache_access(movement_analysis_service, redis_client):
    """Test concurrent cache access."""
    test_key = "concurrent_test"
    test_value = {"data": "test"}
    
    # Set initial value
    await redis_client.set(test_key, json.dumps(test_value))
    
    # Simulate concurrent access
    async def access_cache():
        value = await redis_client.get(test_key)
        return value is not None
    
    # Run multiple concurrent accesses
    tasks = [access_cache() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    # All accesses should succeed
    assert all(results)

@pytest.mark.asyncio
async def test_cache_error_handling(movement_analysis_service, redis_client):
    """Test cache error handling."""
    # Test invalid key
    invalid_key = None
    with pytest.raises(Exception):
        await redis_client.get(invalid_key)
    
    # Test invalid value
    invalid_value = object()
    with pytest.raises(Exception):
        await redis_client.set("test_key", invalid_value)

@pytest.mark.asyncio
async def test_cache_performance(movement_analysis_service, redis_client):
    """Test cache performance."""
    test_key = "performance_test"
    test_value = {"data": "test"}
    
    # Measure set operation
    start_time = time.time()
    await redis_client.set(test_key, json.dumps(test_value))
    set_time = time.time() - start_time
    
    # Measure get operation
    start_time = time.time()
    await redis_client.get(test_key)
    get_time = time.time() - start_time
    
    # Operations should be fast
    assert set_time < 0.1  # 100ms
    assert get_time < 0.1  # 100ms

@pytest.mark.asyncio
async def test_cache_memory_usage(movement_analysis_service, redis_client):
    """Test cache memory usage."""
    # Store multiple values
    for i in range(100):
        key = f"memory_test_{i}"
        value = {"data": "x" * 1000}  # 1KB per value
        await redis_client.set(key, json.dumps(value))
    
    # Check memory usage
    info = await redis_client.info("memory")
    used_memory = int(info["used_memory"])
    
    # Memory usage should be reasonable
    assert used_memory < 10 * 1024 * 1024  # Less than 10MB

@pytest.mark.asyncio
async def test_cache_recovery(movement_analysis_service, redis_client):
    """Test cache recovery after connection issues."""
    # Store value
    test_key = "recovery_test"
    test_value = {"data": "test"}
    await redis_client.set(test_key, json.dumps(test_value))
    
    # Simulate connection issue
    await redis_client.close()
    
    # Reconnect
    await redis_client.initialize()
    
    # Value should still exist
    cached_value = await redis_client.get(test_key)
    assert cached_value is not None
    assert json.loads(cached_value) == test_value

@pytest.mark.asyncio
async def test_cache_cleanup(movement_analysis_service, redis_client):
    """Test cache cleanup."""
    # Store values
    for i in range(10):
        key = f"cleanup_test_{i}"
        value = {"data": f"test_{i}"}
        await redis_client.set(key, json.dumps(value))
    
    # Cleanup
    await redis_client.flushdb()
    
    # All keys should be gone
    for i in range(10):
        key = f"cleanup_test_{i}"
        assert await redis_client.get(key) is None 