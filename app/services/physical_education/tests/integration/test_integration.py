import pytest
import asyncio
import time
from datetime import datetime
import json

from app.services.physical_education.services.movement_analysis_service import MovementAnalysisService
from app.services.physical_education.services.rate_limiter import RateLimiter
from app.services.physical_education.services.circuit_breaker import CircuitBreaker
from app.services.physical_education.services.cache_monitor import CacheMonitor

@pytest.fixture(scope="module")
async def redis_client():
    """Create a Redis client for testing."""
    redis = await aioredis.from_url("redis://redis:6379/1")
    yield redis
    await redis.flushdb()
    await redis.close()

@pytest.fixture(scope="module")
async def rate_limiter():
    """Create a rate limiter for testing."""
    return RateLimiter(rate=10, burst=20, window=1)

@pytest.fixture(scope="module")
async def circuit_breaker():
    """Create a circuit breaker for testing."""
    return CircuitBreaker(failure_threshold=3, reset_timeout=1)

@pytest.fixture(scope="module")
async def cache_monitor():
    """Create a cache monitor for testing."""
    return CacheMonitor()

@pytest.fixture(scope="module")
async def service(redis_client, rate_limiter, circuit_breaker, cache_monitor):
    """Create a MovementAnalysisService instance with all components."""
    service = MovementAnalysisService(None, redis_client)
    service.rate_limiter = rate_limiter
    service.circuit_breaker = circuit_breaker
    service.cache_monitor = cache_monitor
    await service.initialize()
    yield service
    await service.cleanup()

@pytest.mark.asyncio
async def test_integration_basic(service, redis_client, rate_limiter, circuit_breaker, cache_monitor):
    """Test basic integration of all components."""
    # Test data
    test_key = "integration_test"
    test_value = {"data": "test"}
    
    # Track operation
    start_time = time.time()
    
    @rate_limiter
    @circuit_breaker
    async def monitored_operation():
        await cache_monitor.track_operation("set", start_time)
        await redis_client.set(test_key, json.dumps(test_value))
        await cache_monitor.track_operation("get", start_time)
        return await redis_client.get(test_key)
    
    # Successful operation
    result = await monitored_operation(client_id="test_client")
    assert result is not None
    assert json.loads(result) == test_value
    
    # Check health metrics
    health = await cache_monitor.check_health()
    assert health["status"] == "healthy"
    assert health["latency"] < 0.1
    assert health["hit_rate"] >= 0
    assert health["error_rate"] == 0
    
    # Check performance metrics
    metrics = await cache_monitor.get_metrics()
    assert metrics["total_operations"] == 2
    assert metrics["success_rate"] == 1.0
    assert metrics["average_latency"] < 0.1
    assert metrics["error_count"] == 0
    assert metrics["cache_size"] > 0

@pytest.mark.asyncio
async def test_integration_under_load(service, redis_client, rate_limiter, circuit_breaker, cache_monitor):
    """Test integration under load."""
    # Simulate load
    async def simulate_load():
        for i in range(10):
            @rate_limiter
            @circuit_breaker
            async def load_operation():
                await cache_monitor.track_operation("set", time.time())
                await redis_client.set(f"load_test_{i}", json.dumps({"data": f"test_{i}"}))
                await cache_monitor.track_operation("get", time.time())
                return await redis_client.get(f"load_test_{i}")
            
            await load_operation(client_id=f"client_{i}")
    
    # Run load test
    await simulate_load()
    
    # Check health metrics
    health = await cache_monitor.check_health()
    assert health["status"] == "healthy"
    assert health["latency"] < 0.2
    assert health["hit_rate"] >= 0
    assert health["error_rate"] == 0
    
    # Check performance metrics
    metrics = await cache_monitor.get_metrics()
    assert metrics["total_operations"] == 20
    assert metrics["success_rate"] == 1.0
    assert metrics["average_latency"] < 0.2
    assert metrics["error_count"] == 0
    assert metrics["cache_size"] > 0

@pytest.mark.asyncio
async def test_integration_error_handling(service, redis_client, rate_limiter, circuit_breaker, cache_monitor):
    """Test integration error handling."""
    # Simulate errors
    async def simulate_errors():
        for i in range(3):
            @rate_limiter
            @circuit_breaker
            async def error_operation():
                await cache_monitor.track_operation("set", time.time())
                raise Exception("Simulated error")
            
            try:
                await error_operation(client_id="error_client")
            except Exception:
                pass
    
    # Run error simulation
    await simulate_errors()
    
    # Check health metrics
    health = await cache_monitor.check_health()
    assert health["status"] == "degraded"
    assert health["error_rate"] > 0
    assert health["error_count"] == 3
    
    # Check performance metrics
    metrics = await cache_monitor.get_metrics()
    assert metrics["total_operations"] == 3
    assert metrics["success_rate"] == 0.0
    assert metrics["error_count"] == 3
    assert metrics["cache_size"] == 0

@pytest.mark.asyncio
async def test_integration_recovery(service, redis_client, rate_limiter, circuit_breaker, cache_monitor):
    """Test integration recovery."""
    # Simulate errors
    async def simulate_errors():
        for i in range(3):
            @rate_limiter
            @circuit_breaker
            async def error_operation():
                await cache_monitor.track_operation("set", time.time())
                raise Exception("Simulated error")
            
            try:
                await error_operation(client_id="error_client")
            except Exception:
                pass
    
    # Run error simulation
    await simulate_errors()
    
    # Wait for recovery
    await asyncio.sleep(1.1)
    
    # Run successful operations
    async def run_successful_operations():
        for i in range(5):
            @rate_limiter
            @circuit_breaker
            async def success_operation():
                await cache_monitor.track_operation("set", time.time())
                await redis_client.set(f"recovery_test_{i}", json.dumps({"data": f"test_{i}"}))
                await cache_monitor.track_operation("get", time.time())
                return await redis_client.get(f"recovery_test_{i}")
            
            await success_operation(client_id="recovery_client")
    
    # Run recovery test
    await run_successful_operations()
    
    # Check health metrics
    health = await cache_monitor.check_health()
    assert health["status"] == "healthy"
    assert health["error_rate"] < 0.5
    assert health["latency"] < 0.1
    
    # Check performance metrics
    metrics = await cache_monitor.get_metrics()
    assert metrics["total_operations"] == 13
    assert metrics["success_rate"] > 0.5
    assert metrics["error_count"] == 3
    assert metrics["cache_size"] > 0

@pytest.mark.asyncio
async def test_integration_concurrent(service, redis_client, rate_limiter, circuit_breaker, cache_monitor):
    """Test integration with concurrent operations."""
    # Run concurrent operations
    async def run_concurrent_operations():
        tasks = []
        for i in range(5):
            @rate_limiter
            @circuit_breaker
            async def concurrent_operation():
                await cache_monitor.track_operation("set", time.time())
                await redis_client.set(f"concurrent_test_{i}", json.dumps({"data": f"test_{i}"}))
                await cache_monitor.track_operation("get", time.time())
                return await redis_client.get(f"concurrent_test_{i}")
            
            tasks.append(concurrent_operation(client_id=f"concurrent_client_{i}"))
        
        await asyncio.gather(*tasks)
    
    # Run concurrent test
    await run_concurrent_operations()
    
    # Check health metrics
    health = await cache_monitor.check_health()
    assert health["status"] == "healthy"
    assert health["latency"] < 0.2
    assert health["hit_rate"] >= 0
    assert health["error_rate"] == 0
    
    # Check performance metrics
    metrics = await cache_monitor.get_metrics()
    assert metrics["total_operations"] == 10
    assert metrics["success_rate"] == 1.0
    assert metrics["average_latency"] < 0.2
    assert metrics["error_count"] == 0
    assert metrics["cache_size"] > 0 