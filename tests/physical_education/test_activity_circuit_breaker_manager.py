import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from app.services.physical_education.services.activity_circuit_breaker_manager import (
    ActivityCircuitBreakerManager,
    CircuitState
)
from app.services.physical_education.activity_manager import ActivityManager

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_redis():
    return AsyncMock()

@pytest.fixture
def mock_activity_manager():
    return AsyncMock(spec=ActivityManager)

@pytest.fixture
def circuit_breaker_manager(mock_db, mock_redis, mock_activity_manager):
    with patch('app.services.physical_education.services.activity_circuit_breaker_manager.redis.Redis', return_value=mock_redis), \
         patch('app.services.physical_education.services.activity_circuit_breaker_manager.ActivityManager', return_value=mock_activity_manager):
        return ActivityCircuitBreakerManager(db=mock_db)

@pytest.mark.asyncio
async def test_check_circuit_closed(circuit_breaker_manager, mock_redis):
    # Setup
    service_name = 'test_service'
    mock_redis.get.return_value = None
    
    # Test
    result = await circuit_breaker_manager.check_circuit(service_name)
    
    # Verify
    assert result is True
    mock_redis.get.assert_called_once_with(f'circuit:{service_name}:state')

@pytest.mark.asyncio
async def test_check_circuit_open_timeout_not_passed(circuit_breaker_manager, mock_redis):
    # Setup
    service_name = 'test_service'
    current_time = datetime.now()
    mock_redis.get.side_effect = [
        CircuitState.OPEN.value,  # state
        str(current_time.timestamp())  # last_failure
    ]
    
    # Test
    result = await circuit_breaker_manager.check_circuit(service_name)
    
    # Verify
    assert result is False
    assert mock_redis.get.call_count == 2

@pytest.mark.asyncio
async def test_check_circuit_open_timeout_passed(circuit_breaker_manager, mock_redis):
    # Setup
    service_name = 'test_service'
    old_time = datetime.now() - timedelta(seconds=61)  # More than reset_timeout
    mock_redis.get.side_effect = [
        CircuitState.OPEN.value,  # state
        str(old_time.timestamp())  # last_failure
    ]
    
    # Test
    result = await circuit_breaker_manager.check_circuit(service_name)
    
    # Verify
    assert result is True
    assert mock_redis.get.call_count == 2
    mock_redis.set.assert_called_once_with(
        f'circuit:{service_name}:state',
        CircuitState.HALF_OPEN.value
    )

@pytest.mark.asyncio
async def test_record_failure_below_threshold(circuit_breaker_manager, mock_redis):
    # Setup
    service_name = 'test_service'
    mock_redis.get.return_value = '3'  # Current failures
    
    # Test
    await circuit_breaker_manager.record_failure(service_name)
    
    # Verify
    assert mock_redis.set.call_count == 2  # last_failure and failures
    assert mock_redis.get.call_count == 1

@pytest.mark.asyncio
async def test_record_failure_above_threshold(circuit_breaker_manager, mock_redis):
    # Setup
    service_name = 'test_service'
    mock_redis.get.return_value = '4'  # One below threshold
    
    # Test
    await circuit_breaker_manager.record_failure(service_name)
    
    # Verify
    assert mock_redis.set.call_count == 3  # last_failure, failures, and state
    mock_redis.set.assert_any_call(
        f'circuit:{service_name}:state',
        CircuitState.OPEN.value
    )

@pytest.mark.asyncio
async def test_record_success_half_open_below_threshold(circuit_breaker_manager, mock_redis):
    # Setup
    service_name = 'test_service'
    mock_redis.get.side_effect = [
        '2',  # Current successes
        CircuitState.HALF_OPEN.value  # Current state
    ]
    
    # Test
    await circuit_breaker_manager.record_success(service_name)
    
    # Verify
    assert mock_redis.set.call_count == 1  # Only successes updated
    assert mock_redis.get.call_count == 2

@pytest.mark.asyncio
async def test_record_success_half_open_above_threshold(circuit_breaker_manager, mock_redis):
    # Setup
    service_name = 'test_service'
    mock_redis.get.side_effect = [
        '3',  # Current successes (at threshold)
        CircuitState.HALF_OPEN.value  # Current state
    ]
    
    # Test
    await circuit_breaker_manager.record_success(service_name)
    
    # Verify
    assert mock_redis.set.call_count == 1  # Successes updated
    assert mock_redis.get.call_count == 2
    mock_redis.delete.assert_called()  # Circuit reset

@pytest.mark.asyncio
async def test_reset_circuit(circuit_breaker_manager, mock_redis):
    # Setup
    service_name = 'test_service'
    
    # Test
    await circuit_breaker_manager.reset_circuit(service_name)
    
    # Verify
    assert mock_redis.delete.call_count == 3  # failures, successes, last_failure
    mock_redis.set.assert_called_once_with(
        f'circuit:{service_name}:state',
        CircuitState.CLOSED.value
    )

@pytest.mark.asyncio
async def test_get_circuit_stats(circuit_breaker_manager, mock_redis):
    # Setup
    service_name = 'test_service'
    current_time = datetime.now()
    mock_redis.get.side_effect = [
        '5',  # failures
        '10',  # successes
        CircuitState.CLOSED.value,  # state
        str(current_time.timestamp())  # last_failure
    ]
    
    # Test
    result = await circuit_breaker_manager.get_circuit_stats(service_name)
    
    # Verify
    assert result['state'] == CircuitState.CLOSED.value
    assert result['failures'] == 5
    assert result['successes'] == 10
    assert result['last_failure'] == current_time.isoformat()
    assert result['threshold'] == circuit_breaker_manager.settings['failure_threshold']

@pytest.mark.asyncio
async def test_get_circuit_stats_error(circuit_breaker_manager, mock_redis):
    # Setup
    service_name = 'test_service'
    mock_redis.get.side_effect = Exception("Redis error")
    
    # Test
    result = await circuit_breaker_manager.get_circuit_stats(service_name)
    
    # Verify
    assert result == {} 