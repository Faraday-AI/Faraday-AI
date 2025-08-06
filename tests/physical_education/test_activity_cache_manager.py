import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import uuid
from app.services.physical_education.services.activity_cache_manager import ActivityCacheManager
from app.services.physical_education.activity_manager import ActivityManager

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def cache_manager(mock_db):
    return ActivityCacheManager(db=mock_db)

@pytest.fixture(autouse=True)
async def redis_cleanup(cache_manager):
    """Clean up Redis before and after each test to ensure isolation."""
    # Clean up before test
    await cache_manager.clear_all_cache()
    yield
    # Clean up after test
    await cache_manager.clear_all_cache()

@pytest.fixture
def unique_test_id():
    """Generate a unique test ID to avoid key conflicts."""
    return str(uuid.uuid4())[:8]

@pytest.mark.asyncio
async def test_get_cached_activity_found(cache_manager, unique_test_id):
    # Setup
    activity_id = f'test_activity_{unique_test_id}'
    activity_data = {'id': activity_id, 'name': 'Test Activity'}
    
    # Cache the activity first
    await cache_manager.cache_activity(activity_id, activity_data)
    
    # Test
    result = await cache_manager.get_cached_activity(activity_id)
    
    # Verify
    assert result == activity_data
    
    # Cleanup
    await cache_manager.invalidate_activity_cache(activity_id)

@pytest.mark.asyncio
async def test_get_cached_activity_not_found(cache_manager, unique_test_id):
    # Setup
    activity_id = f'test_activity_{unique_test_id}'
    
    # Ensure the activity is not cached
    await cache_manager.invalidate_activity_cache(activity_id)
    
    # Test
    result = await cache_manager.get_cached_activity(activity_id)
    
    # Verify
    assert result is None

@pytest.mark.asyncio
async def test_cache_activity_success(cache_manager, unique_test_id):
    # Setup
    activity_id = f'test_activity_{unique_test_id}'
    activity_data = {'id': activity_id, 'name': 'Test Activity'}
    
    # Test
    result = await cache_manager.cache_activity(activity_id, activity_data)
    
    # Verify
    assert result is True
    
    # Verify the data was actually cached
    cached_data = await cache_manager.get_cached_activity(activity_id)
    assert cached_data == activity_data
    
    # Cleanup
    await cache_manager.invalidate_activity_cache(activity_id)

@pytest.mark.asyncio
async def test_invalidate_activity_cache_success(cache_manager, unique_test_id):
    # Setup
    activity_id = f'test_activity_{unique_test_id}'
    activity_data = {'id': activity_id, 'name': 'Test Activity'}
    
    # Cache the activity first
    await cache_manager.cache_activity(activity_id, activity_data)
    
    # Verify it's cached
    cached_data = await cache_manager.get_cached_activity(activity_id)
    assert cached_data == activity_data
    
    # Test invalidation
    result = await cache_manager.invalidate_activity_cache(activity_id)
    
    # Verify
    assert result is True
    
    # Verify it's no longer cached
    cached_data = await cache_manager.get_cached_activity(activity_id)
    assert cached_data is None

@pytest.mark.asyncio
async def test_get_cached_student_activities_found(cache_manager, unique_test_id):
    # Setup
    student_id = f'test_student_{unique_test_id}'
    activities = [
        {'id': 'activity1', 'name': 'Activity 1'},
        {'id': 'activity2', 'name': 'Activity 2'}
    ]
    
    # Cache the activities first
    await cache_manager.cache_student_activities(student_id, activities)
    
    # Test
    result = await cache_manager.get_cached_student_activities(student_id)
    
    # Verify
    assert result == activities
    
    # Cleanup
    await cache_manager.clear_all_cache()

@pytest.mark.asyncio
async def test_get_cached_student_activities_not_found(cache_manager, unique_test_id):
    # Setup
    student_id = f'test_student_{unique_test_id}'
    
    # Ensure no activities are cached
    await cache_manager.clear_all_cache()
    
    # Test
    result = await cache_manager.get_cached_student_activities(student_id)
    
    # Verify
    assert result is None

@pytest.mark.asyncio
async def test_cache_student_activities_success(cache_manager, unique_test_id):
    # Setup
    student_id = f'test_student_{unique_test_id}'
    activities = [
        {'id': 'activity1', 'name': 'Activity 1'},
        {'id': 'activity2', 'name': 'Activity 2'}
    ]
    
    # Test
    result = await cache_manager.cache_student_activities(student_id, activities)
    
    # Verify
    assert result is True
    
    # Verify the data was actually cached
    cached_data = await cache_manager.get_cached_student_activities(student_id)
    assert cached_data == activities
    
    # Cleanup
    await cache_manager.clear_all_cache()

@pytest.mark.asyncio
async def test_cleanup_cache_success(cache_manager, unique_test_id):
    # Setup - add some test data
    activity_id = f'test_activity_{unique_test_id}'
    activity_data = {'id': activity_id, 'name': 'Test Activity'}
    await cache_manager.cache_activity(activity_id, activity_data)
    
    # Test
    result = await cache_manager.cleanup_cache()
    
    # Verify
    assert result is True
    
    # Cleanup
    await cache_manager.clear_all_cache()

@pytest.mark.asyncio
async def test_get_cache_stats_success(cache_manager, unique_test_id):
    # Setup - add some test data
    activity_id = f'test_activity_{unique_test_id}'
    activity_data = {'id': activity_id, 'name': 'Test Activity'}
    await cache_manager.cache_activity(activity_id, activity_data)
    
    # Test
    result = await cache_manager.get_cache_stats()
    
    # Verify basic structure
    assert 'total_entries' in result
    assert 'memory_usage' in result
    assert 'last_cleanup' in result
    
    # Cleanup
    await cache_manager.clear_all_cache() 