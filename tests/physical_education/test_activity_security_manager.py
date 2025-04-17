import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from app.services.physical_education.services.activity_security_manager import ActivitySecurityManager
from app.services.physical_education.activity_manager import ActivityManager
from app.services.physical_education.security_service import SecurityService

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_activity_manager():
    return AsyncMock(spec=ActivityManager)

@pytest.fixture
def mock_security_service():
    return MagicMock(spec=SecurityService)

@pytest.fixture
def security_manager(mock_db, mock_activity_manager, mock_security_service):
    with patch('app.services.physical_education.services.activity_security_manager.ActivityManager', return_value=mock_activity_manager), \
         patch('app.services.physical_education.services.activity_security_manager.SecurityService', return_value=mock_security_service):
        return ActivitySecurityManager(db=mock_db)

@pytest.mark.asyncio
async def test_validate_activity_creation_success(security_manager, mock_activity_manager):
    # Setup
    activity_data = {
        'student_id': 'test_student',
        'duration': 3600,  # 1 hour
        'attachments': [
            {'size': 1024 * 1024, 'type': 'mp4'},  # 1MB
            {'size': 2 * 1024 * 1024, 'type': 'jpg'}  # 2MB
        ]
    }
    mock_activity_manager.get_student_activities.return_value = [{'id': 'activity1'}]  # Below limit
    
    # Test
    result = await security_manager.validate_activity_creation(activity_data)
    
    # Verify
    assert result is True
    mock_activity_manager.get_student_activities.assert_called_once_with('test_student')

@pytest.mark.asyncio
async def test_validate_activity_creation_exceeds_student_limit(security_manager, mock_activity_manager):
    # Setup
    activity_data = {
        'student_id': 'test_student',
        'duration': 3600
    }
    # Create list of activities that exceeds the limit
    mock_activity_manager.get_student_activities.return_value = [
        {'id': f'activity{i}'} for i in range(security_manager.settings['max_activities_per_student'])
    ]
    
    # Test
    result = await security_manager.validate_activity_creation(activity_data)
    
    # Verify
    assert result is False
    mock_activity_manager.get_student_activities.assert_called_once_with('test_student')

@pytest.mark.asyncio
async def test_validate_activity_creation_exceeds_duration(security_manager, mock_activity_manager):
    # Setup
    activity_data = {
        'student_id': 'test_student',
        'duration': security_manager.settings['max_activity_duration'] + 1
    }
    mock_activity_manager.get_student_activities.return_value = []
    
    # Test
    result = await security_manager.validate_activity_creation(activity_data)
    
    # Verify
    assert result is False
    mock_activity_manager.get_student_activities.assert_called_once_with('test_student')

@pytest.mark.asyncio
async def test_validate_activity_creation_invalid_file_type(security_manager, mock_activity_manager):
    # Setup
    activity_data = {
        'student_id': 'test_student',
        'duration': 3600,
        'attachments': [{'size': 1024 * 1024, 'type': 'pdf'}]  # Invalid type
    }
    mock_activity_manager.get_student_activities.return_value = []
    
    # Test
    result = await security_manager.validate_activity_creation(activity_data)
    
    # Verify
    assert result is False
    mock_activity_manager.get_student_activities.assert_called_once_with('test_student')

@pytest.mark.asyncio
async def test_validate_activity_update_success(security_manager, mock_activity_manager):
    # Setup
    activity_id = 'test_activity'
    update_data = {'name': 'Updated Activity'}
    mock_activity_manager.get_activity.return_value = {'id': activity_id}
    
    # Test
    result = await security_manager.validate_activity_update(activity_id, update_data)
    
    # Verify
    assert result is True
    mock_activity_manager.get_activity.assert_called_once_with(activity_id)

@pytest.mark.asyncio
async def test_validate_activity_update_not_found(security_manager, mock_activity_manager):
    # Setup
    activity_id = 'test_activity'
    update_data = {'name': 'Updated Activity'}
    mock_activity_manager.get_activity.return_value = None
    
    # Test
    result = await security_manager.validate_activity_update(activity_id, update_data)
    
    # Verify
    assert result is False
    mock_activity_manager.get_activity.assert_called_once_with(activity_id)

@pytest.mark.asyncio
async def test_validate_activity_update_completion_success(security_manager, mock_activity_manager):
    # Setup
    activity_id = 'test_activity'
    update_data = {'status': 'completed'}
    activity = {
        'id': activity_id,
        'duration': 3600,
        'performance_metrics': {'score': 0.8},
        'feedback': 'Good job!'
    }
    mock_activity_manager.get_activity.return_value = activity
    
    # Test
    result = await security_manager.validate_activity_update(activity_id, update_data)
    
    # Verify
    assert result is True
    mock_activity_manager.get_activity.assert_called_once_with(activity_id)

@pytest.mark.asyncio
async def test_validate_activity_update_completion_missing_fields(security_manager, mock_activity_manager):
    # Setup
    activity_id = 'test_activity'
    update_data = {'status': 'completed'}
    activity = {
        'id': activity_id,
        'duration': 3600,
        'performance_metrics': {'score': 0.8}
        # Missing feedback field
    }
    mock_activity_manager.get_activity.return_value = activity
    
    # Test
    result = await security_manager.validate_activity_update(activity_id, update_data)
    
    # Verify
    assert result is False
    mock_activity_manager.get_activity.assert_called_once_with(activity_id)

@pytest.mark.asyncio
async def test_validate_activity_update_completion_low_score(security_manager, mock_activity_manager):
    # Setup
    activity_id = 'test_activity'
    update_data = {'status': 'completed'}
    activity = {
        'id': activity_id,
        'duration': 3600,
        'performance_metrics': {'score': 0.3},  # Below threshold
        'feedback': 'Needs improvement'
    }
    mock_activity_manager.get_activity.return_value = activity
    
    # Test
    result = await security_manager.validate_activity_update(activity_id, update_data)
    
    # Verify
    assert result is False
    mock_activity_manager.get_activity.assert_called_once_with(activity_id)

@pytest.mark.asyncio
async def test_check_concurrent_activities_within_limit(security_manager, mock_activity_manager):
    # Setup
    student_id = 'test_student'
    mock_activity_manager.get_active_activities.return_value = [
        {'id': f'activity{i}'} for i in range(3)
    ]
    
    # Test
    result = await security_manager.check_concurrent_activities(student_id)
    
    # Verify
    assert result is True
    mock_activity_manager.get_active_activities.assert_called_once_with(student_id)

@pytest.mark.asyncio
async def test_check_concurrent_activities_exceeds_limit(security_manager, mock_activity_manager):
    # Setup
    student_id = 'test_student'
    mock_activity_manager.get_active_activities.return_value = [
        {'id': f'activity{i}'} for i in range(security_manager.settings['max_concurrent_activities'])
    ]
    
    # Test
    result = await security_manager.check_concurrent_activities(student_id)
    
    # Verify
    assert result is False
    mock_activity_manager.get_active_activities.assert_called_once_with(student_id)

@pytest.mark.asyncio
async def test_validate_activity_access_authorized(security_manager, mock_activity_manager):
    # Setup
    activity_id = 'test_activity'
    user_id = 'test_student'
    activity = {'id': activity_id, 'student_id': user_id}
    mock_activity_manager.get_activity.return_value = activity
    
    # Test
    result = await security_manager.validate_activity_access(activity_id, user_id)
    
    # Verify
    assert result is True
    mock_activity_manager.get_activity.assert_called_once_with(activity_id)

@pytest.mark.asyncio
async def test_validate_activity_access_unauthorized(security_manager, mock_activity_manager):
    # Setup
    activity_id = 'test_activity'
    user_id = 'test_student'
    activity = {'id': activity_id, 'student_id': 'other_student'}
    mock_activity_manager.get_activity.return_value = activity
    
    # Test
    result = await security_manager.validate_activity_access(activity_id, user_id)
    
    # Verify
    assert result is False
    mock_activity_manager.get_activity.assert_called_once_with(activity_id)

@pytest.mark.asyncio
async def test_validate_activity_access_not_found(security_manager, mock_activity_manager):
    # Setup
    activity_id = 'test_activity'
    user_id = 'test_student'
    mock_activity_manager.get_activity.return_value = None
    
    # Test
    result = await security_manager.validate_activity_access(activity_id, user_id)
    
    # Verify
    assert result is False
    mock_activity_manager.get_activity.assert_called_once_with(activity_id) 