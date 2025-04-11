import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from app.services.physical_education.services.rate_limiter import (
    RateLimiter,
    RateLimitExceededError,
    rate_limit
)

@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger

@pytest.fixture
def limiter(mock_logger):
    """Create a RateLimiter instance with mocked logger."""
    return RateLimiter(
        rate=5,
        burst=10,
        window=1,
        logger=mock_logger
    )

@pytest.mark.asyncio
async def test_rate_limiter_initial_state(limiter):
    """Test initial state of rate limiter."""
    assert limiter.tokens == limiter.burst
    assert limiter.request_times == {}
    assert limiter._cleanup_task is None

@pytest.mark.asyncio
async def test_rate_limiter_successful_operation(limiter):
    """Test successful operation with rate limiter."""
    async def operation():
        return "success"
    
    result = await limiter(operation)(client_id="test_client")
    assert result == "success"
    assert len(limiter.request_times["test_client"]) == 1

@pytest.mark.asyncio
async def test_rate_limiter_rate_limit(limiter):
    """Test rate limit enforcement."""
    async def operation():
        return "success"
    
    # Make requests up to burst limit
    for _ in range(limiter.burst):
        result = await limiter(operation)(client_id="test_client")
        assert result == "success"
    
    # Next request should exceed rate limit
    with pytest.raises(RateLimitExceededError):
        await limiter(operation)(client_id="test_client")

@pytest.mark.asyncio
async def test_rate_limiter_token_refill(limiter):
    """Test token refill mechanism."""
    async def operation():
        return "success"
    
    # Use all tokens
    for _ in range(limiter.burst):
        await limiter(operation)(client_id="test_client")
    
    # Wait for token refill
    await asyncio.sleep(limiter.window)
    
    # Should be able to make more requests
    result = await limiter(operation)(client_id="test_client")
    assert result == "success"

@pytest.mark.asyncio
async def test_rate_limiter_multiple_clients(limiter):
    """Test rate limiting with multiple clients."""
    async def operation():
        return "success"
    
    # Make requests for different clients
    for client_id in ["client1", "client2", "client3"]:
        result = await limiter(operation)(client_id=client_id)
        assert result == "success"
        assert len(limiter.request_times[client_id]) == 1

@pytest.mark.asyncio
async def test_rate_limiter_cleanup(limiter):
    """Test cleanup of old request records."""
    async def operation():
        return "success"
    
    # Make some requests
    for _ in range(5):
        await limiter(operation)(client_id="test_client")
    
    # Start cleanup task
    limiter._cleanup_task = asyncio.create_task(limiter._cleanup_old_requests())
    
    # Wait for cleanup
    await asyncio.sleep(limiter.window + 0.1)
    
    # Old requests should be cleaned up
    assert len(limiter.request_times["test_client"]) < 5

@pytest.mark.asyncio
async def test_rate_limiter_concurrent_operations(limiter):
    """Test concurrent operations with rate limiter."""
    async def operation():
        await asyncio.sleep(0.1)
        return "success"
    
    # Run multiple concurrent operations
    tasks = [limiter(operation)(client_id="test_client") for _ in range(5)]
    results = await asyncio.gather(*tasks)
    
    assert all(result == "success" for result in results)
    assert len(limiter.request_times["test_client"]) == 5

@pytest.mark.asyncio
async def test_rate_limiter_decorator():
    """Test rate limiter decorator."""
    @rate_limit(rate=5, burst=10, window=1)
    async def operation():
        return "success"
    
    result = await operation(client_id="test_client")
    assert result == "success"

@pytest.mark.asyncio
async def test_rate_limiter_usage_stats(limiter):
    """Test usage statistics."""
    async def operation():
        return "success"
    
    # Make some requests
    for _ in range(3):
        await limiter(operation)(client_id="test_client")
    
    # Get usage stats
    stats = limiter.get_usage("test_client")
    assert stats["requests"] == 3
    assert stats["remaining_tokens"] <= limiter.burst
    assert stats["rate_limit"] == limiter.rate
    assert stats["burst_limit"] == limiter.burst
    assert stats["window"] == limiter.window

@pytest.mark.asyncio
async def test_rate_limiter_cleanup_task_cancellation(limiter):
    """Test cleanup task cancellation."""
    # Start cleanup task
    limiter._cleanup_task = asyncio.create_task(limiter._cleanup_old_requests())
    
    # Cancel cleanup task
    await limiter.cleanup()
    
    assert limiter._cleanup_task.cancelled() 