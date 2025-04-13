import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from app.services.physical_education.services.activity_rate_limit_manager import ActivityRateLimitManager
from app.services.physical_education.services.activity_manager import ActivityManager

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
def rate_limit_manager(mock_db, mock_redis, mock_activity_manager):
    with patch('app.services.physical_education.services.activity_rate_limit_manager.redis.Redis', return_value=mock_redis), \
         patch('app.services.physical_education.services.activity_rate_limit_manager.ActivityManager', return_value=mock_activity_manager):
        return ActivityRateLimitManager(db=mock_db)

@pytest.mark.asyncio
async def test_check_rate_limit_first_request(rate_limit_manager, mock_redis):
    # Setup
    user_id = 'user1'
    action = 'create_activity'
    mock_redis.get.return_value = None
    
    # Test
    result = await rate_limit_manager.check_rate_limit(user_id, action)
    
    # Verify
    assert result is True
    mock_redis.setex.assert_called_once()
    args = mock_redis.setex.call_args[0]
    assert args[0] == f'rate_limit:{user_id}:{action}'
    assert args[1] == rate_limit_manager.settings['default_limits'][action]['time_window']
    assert args[2].startswith('1:')  # Count should be 1

@pytest.mark.asyncio
async def test_check_rate_limit_within_window(rate_limit_manager, mock_redis):
    # Setup
    user_id = 'user1'
    action = 'create_activity'
    current_time = datetime.now()
    mock_redis.get.return_value = f"5:{int(current_time.timestamp())}"
    
    # Test
    result = await rate_limit_manager.check_rate_limit(user_id, action)
    
    # Verify
    assert result is True
    mock_redis.setex.assert_called_once()
    args = mock_redis.setex.call_args[0]
    assert args[2].startswith('6:')  # Count should be incremented to 6

@pytest.mark.asyncio
async def test_check_rate_limit_exceeded(rate_limit_manager, mock_redis):
    # Setup
    user_id = 'user1'
    action = 'create_activity'
    current_time = datetime.now()
    mock_redis.get.return_value = f"10:{int(current_time.timestamp())}"  # Max requests reached
    
    # Test
    result = await rate_limit_manager.check_rate_limit(user_id, action)
    
    # Verify
    assert result is False
    mock_redis.setex.assert_not_called()

@pytest.mark.asyncio
async def test_check_rate_limit_window_expired(rate_limit_manager, mock_redis):
    # Setup
    user_id = 'user1'
    action = 'create_activity'
    old_time = datetime.now() - timedelta(seconds=61)  # Window expired
    mock_redis.get.return_value = f"10:{int(old_time.timestamp())}"
    
    # Test
    result = await rate_limit_manager.check_rate_limit(user_id, action)
    
    # Verify
    assert result is True
    mock_redis.setex.assert_called_once()
    args = mock_redis.setex.call_args[0]
    assert args[2].startswith('1:')  # Count should reset to 1

@pytest.mark.asyncio
async def test_block_user(rate_limit_manager, mock_redis):
    # Setup
    user_id = 'user1'
    reason = 'Too many failed attempts'
    
    # Test
    result = await rate_limit_manager.block_user(user_id, reason)
    
    # Verify
    assert result is True
    mock_redis.setex.assert_called_once_with(
        f'blocked:{user_id}',
        rate_limit_manager.settings['block_duration'],
        reason
    )

@pytest.mark.asyncio
async def test_is_user_blocked_true(rate_limit_manager, mock_redis):
    # Setup
    user_id = 'user1'
    reason = 'Too many failed attempts'
    mock_redis.get.return_value = reason
    
    # Test
    result = await rate_limit_manager.is_user_blocked(user_id)
    
    # Verify
    assert result == reason
    mock_redis.get.assert_called_once_with(f'blocked:{user_id}')

@pytest.mark.asyncio
async def test_is_user_blocked_false(rate_limit_manager, mock_redis):
    # Setup
    user_id = 'user1'
    mock_redis.get.return_value = None
    
    # Test
    result = await rate_limit_manager.is_user_blocked(user_id)
    
    # Verify
    assert result is None
    mock_redis.get.assert_called_once_with(f'blocked:{user_id}')

@pytest.mark.asyncio
async def test_unblock_user(rate_limit_manager, mock_redis):
    # Setup
    user_id = 'user1'
    
    # Test
    result = await rate_limit_manager.unblock_user(user_id)
    
    # Verify
    assert result is True
    mock_redis.delete.assert_called_once_with(f'blocked:{user_id}')

@pytest.mark.asyncio
async def test_get_rate_limit_stats(rate_limit_manager, mock_redis):
    # Setup
    user_id = 'user1'
    current_time = datetime.now()
    mock_redis.get.side_effect = [
        f"5:{int(current_time.timestamp())}",  # create_activity
        None,  # update_activity
        f"10:{int(current_time.timestamp())}",  # get_activities
        None  # delete_activity
    ]
    
    # Test
    result = await rate_limit_manager.get_rate_limit_stats(user_id)
    
    # Verify
    assert len(result) == 4  # All actions should be present
    assert result['create_activity']['current_count'] == 5
    assert result['update_activity']['current_count'] == 0
    assert result['get_activities']['current_count'] == 10
    assert result['delete_activity']['current_count'] == 0
    for action in result:
        assert 'max_allowed' in result[action]
        assert 'window_start' in result[action] 