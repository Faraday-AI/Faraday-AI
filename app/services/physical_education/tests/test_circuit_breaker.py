import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from app.services.physical_education.services.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    circuit_breaker
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
def breaker(mock_logger):
    """Create a CircuitBreaker instance with mocked logger."""
    return CircuitBreaker(
        failure_threshold=3,
        reset_timeout=1,
        half_open_timeout=1,
        logger=mock_logger
    )

@pytest.mark.asyncio
async def test_circuit_breaker_initial_state(breaker):
    """Test initial state of circuit breaker."""
    assert breaker.state == "closed"
    assert breaker.failures == 0
    assert breaker.last_failure_time is None

@pytest.mark.asyncio
async def test_circuit_breaker_successful_operation(breaker):
    """Test successful operation with circuit breaker."""
    async def successful_operation():
        return "success"
    
    result = await breaker(successful_operation)()
    assert result == "success"
    assert breaker.state == "closed"

@pytest.mark.asyncio
async def test_circuit_breaker_failure_handling(breaker, mock_logger):
    """Test failure handling with circuit breaker."""
    async def failing_operation():
        raise Exception("Test failure")
    
    # First failure
    with pytest.raises(Exception):
        await breaker(failing_operation)()
    assert breaker.failures == 1
    assert breaker.state == "closed"
    
    # Second failure
    with pytest.raises(Exception):
        await breaker(failing_operation)()
    assert breaker.failures == 2
    assert breaker.state == "closed"
    
    # Third failure - should open circuit
    with pytest.raises(Exception):
        await breaker(failing_operation)()
    assert breaker.failures == 3
    assert breaker.state == "open"
    mock_logger.error.assert_called()

@pytest.mark.asyncio
async def test_circuit_breaker_open_state(breaker):
    """Test behavior when circuit breaker is open."""
    async def operation():
        return "success"
    
    # Force circuit breaker to open state
    breaker.state = "open"
    breaker.last_failure_time = datetime.utcnow()
    
    with pytest.raises(CircuitBreakerOpenError):
        await breaker(operation)()

@pytest.mark.asyncio
async def test_circuit_breaker_reset(breaker):
    """Test circuit breaker reset functionality."""
    # Set up failed state
    breaker.failures = 3
    breaker.state = "open"
    breaker.last_failure_time = datetime.utcnow() - timedelta(seconds=2)
    
    await breaker._reset()
    assert breaker.failures == 0
    assert breaker.state == "closed"
    assert breaker.last_failure_time is None

@pytest.mark.asyncio
async def test_circuit_breaker_half_open_state(breaker):
    """Test behavior in half-open state."""
    async def successful_operation():
        return "success"
    
    # Set up half-open state
    breaker.state = "half-open"
    
    result = await breaker(successful_operation)()
    assert result == "success"
    assert breaker.state == "closed"

@pytest.mark.asyncio
async def test_circuit_breaker_concurrent_operations(breaker):
    """Test concurrent operations with circuit breaker."""
    async def operation():
        await asyncio.sleep(0.1)
        return "success"
    
    # Run multiple concurrent operations
    tasks = [breaker(operation)() for _ in range(5)]
    results = await asyncio.gather(*tasks)
    
    assert all(result == "success" for result in results)
    assert breaker.state == "closed"

@pytest.mark.asyncio
async def test_circuit_breaker_decorator():
    """Test circuit breaker decorator."""
    @circuit_breaker(failure_threshold=2, reset_timeout=1)
    async def operation():
        return "success"
    
    result = await operation()
    assert result == "success"

@pytest.mark.asyncio
async def test_circuit_breaker_state_transitions(breaker, mock_logger):
    """Test state transitions of circuit breaker."""
    async def failing_operation():
        raise Exception("Test failure")
    
    # Closed -> Open
    for _ in range(3):
        with pytest.raises(Exception):
            await breaker(failing_operation)()
    assert breaker.state == "open"
    
    # Wait for reset timeout
    await asyncio.sleep(1.1)
    
    # Open -> Half-open
    assert breaker.state == "half-open"
    
    # Half-open -> Closed (success)
    async def successful_operation():
        return "success"
    
    result = await breaker(successful_operation)()
    assert result == "success"
    assert breaker.state == "closed"

@pytest.mark.asyncio
async def test_circuit_breaker_get_state(breaker):
    """Test getting circuit breaker state."""
    state = breaker.get_state()
    assert isinstance(state, dict)
    assert "state" in state
    assert "failures" in state
    assert "last_failure_time" in state
    assert "failure_threshold" in state
    assert "reset_timeout" in state 