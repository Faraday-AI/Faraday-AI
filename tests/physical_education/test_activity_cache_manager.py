import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from app.services.physical_education.activity_cache_manager import ActivityCacheManager
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
def cache_manager(mock_db, mock_redis, mock_activity_manager):
    with patch('app.services.physical_education.services.activity_cache_manager.redis.Redis', return_value=mock_redis), \
         patch('app.services.physical_education.services.activity_cache_manager.ActivityManager', return_value=mock_activity_manager):
        return ActivityCacheManager(db=mock_db)

@pytest.mark.asyncio
async def test_get_cached_activity_found(cache_manager, mock_redis):
    # Setup
    activity_id = 'test_activity'
    activity_data = {'id': activity_id, 'name': 'Test Activity'}
    mock_redis.get.return_value = str(activity_data)
    
    # Test
    result = await cache_manager.get_cached_activity(activity_id)
    
    # Verify
    assert result == activity_data
    mock_redis.get.assert_called_once_with(f'activity:{activity_id}')

@pytest.mark.asyncio
async def test_get_cached_activity_not_found(cache_manager, mock_redis):
    # Setup
    activity_id = 'test_activity'
    mock_redis.get.return_value = None
    
    # Test
    result = await cache_manager.get_cached_activity(activity_id)
    
    # Verify
    assert result is None
    mock_redis.get.assert_called_once_with(f'activity:{activity_id}')

@pytest.mark.asyncio
async def test_cache_activity_success(cache_manager, mock_redis):
    # Setup
    activity_id = 'test_activity'
    activity_data = {'id': activity_id, 'name': 'Test Activity'}
    
    # Test
    result = await cache_manager.cache_activity(activity_id, activity_data)
    
    # Verify
    assert result is True
    mock_redis.setex.assert_called_once_with(
        f'activity:{activity_id}',
        cache_manager.settings['default_ttl'],
        str(activity_data)
    )

@pytest.mark.asyncio
async def test_cache_activity_error(cache_manager, mock_redis):
    # Setup
    activity_id = 'test_activity'
    activity_data = {'id': activity_id, 'name': 'Test Activity'}
    mock_redis.setex.side_effect = Exception("Redis error")
    
    # Test
    result = await cache_manager.cache_activity(activity_id, activity_data)
    
    # Verify
    assert result is False
    mock_redis.setex.assert_called_once()

@pytest.mark.asyncio
async def test_invalidate_activity_cache_success(cache_manager, mock_redis):
    # Setup
    activity_id = 'test_activity'
    
    # Test
    result = await cache_manager.invalidate_activity_cache(activity_id)
    
    # Verify
    assert result is True
    mock_redis.delete.assert_called_once_with(f'activity:{activity_id}')

@pytest.mark.asyncio
async def test_invalidate_activity_cache_error(cache_manager, mock_redis):
    # Setup
    activity_id = 'test_activity'
    mock_redis.delete.side_effect = Exception("Redis error")
    
    # Test
    result = await cache_manager.invalidate_activity_cache(activity_id)
    
    # Verify
    assert result is False
    mock_redis.delete.assert_called_once_with(f'activity:{activity_id}')

@pytest.mark.asyncio
async def test_get_cached_student_activities_found(cache_manager, mock_redis):
    # Setup
    student_id = 'test_student'
    activities = [
        {'id': 'activity1', 'name': 'Activity 1'},
        {'id': 'activity2', 'name': 'Activity 2'}
    ]
    mock_redis.get.return_value = str(activities)
    
    # Test
    result = await cache_manager.get_cached_student_activities(student_id)
    
    # Verify
    assert result == activities
    mock_redis.get.assert_called_once_with(f'student_activities:{student_id}')

@pytest.mark.asyncio
async def test_get_cached_student_activities_not_found(cache_manager, mock_redis):
    # Setup
    student_id = 'test_student'
    mock_redis.get.return_value = None
    
    # Test
    result = await cache_manager.get_cached_student_activities(student_id)
    
    # Verify
    assert result is None
    mock_redis.get.assert_called_once_with(f'student_activities:{student_id}')

@pytest.mark.asyncio
async def test_cache_student_activities_success(cache_manager, mock_redis):
    # Setup
    student_id = 'test_student'
    activities = [
        {'id': 'activity1', 'name': 'Activity 1'},
        {'id': 'activity2', 'name': 'Activity 2'}
    ]
    
    # Test
    result = await cache_manager.cache_student_activities(student_id, activities)
    
    # Verify
    assert result is True
    mock_redis.setex.assert_called_once_with(
        f'student_activities:{student_id}',
        cache_manager.settings['default_ttl'],
        str(activities)
    )

@pytest.mark.asyncio
async def test_cache_student_activities_error(cache_manager, mock_redis):
    # Setup
    student_id = 'test_student'
    activities = [
        {'id': 'activity1', 'name': 'Activity 1'},
        {'id': 'activity2', 'name': 'Activity 2'}
    ]
    mock_redis.setex.side_effect = Exception("Redis error")
    
    # Test
    result = await cache_manager.cache_student_activities(student_id, activities)
    
    # Verify
    assert result is False
    mock_redis.setex.assert_called_once()

@pytest.mark.asyncio
async def test_cleanup_cache_success(cache_manager, mock_redis):
    # Setup
    mock_redis.keys.return_value = ['key1', 'key2']
    mock_redis.ttl.side_effect = [0, 3600]  # First key expired, second not expired
    
    # Test
    result = await cache_manager.cleanup_cache()
    
    # Verify
    assert result is True
    assert mock_redis.delete.call_count == 1  # Only expired key should be deleted
    mock_redis.delete.assert_called_once_with('key1')

@pytest.mark.asyncio
async def test_cleanup_cache_error(cache_manager, mock_redis):
    # Setup
    mock_redis.keys.side_effect = Exception("Redis error")
    
    # Test
    result = await cache_manager.cleanup_cache()
    
    # Verify
    assert result is False
    mock_redis.keys.assert_called_once()

@pytest.mark.asyncio
async def test_get_cache_stats_success(cache_manager, mock_redis):
    # Setup
    mock_redis.keys.return_value = ['key1', 'key2']
    mock_redis.info.return_value = {'used_memory': 1024}
    
    # Test
    result = await cache_manager.get_cache_stats()
    
    # Verify
    assert result['total_entries'] == 2
    assert result['memory_usage'] == {'used_memory': 1024}
    assert 'last_cleanup' in result
    mock_redis.keys.assert_called_once()
    mock_redis.info.assert_called_once_with('memory')

@pytest.mark.asyncio
async def test_get_cache_stats_error(cache_manager, mock_redis):
    # Setup
    mock_redis.keys.side_effect = Exception("Redis error")
    
    # Test
    result = await cache_manager.get_cache_stats()
    
    # Verify
    assert result == {}
    mock_redis.keys.assert_called_once() 