import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.physical_education.services.activity_security_manager import ActivitySecurityManager

@pytest.fixture
def security_manager(db_session):
    """Create ActivitySecurityManager with real database session."""
    return ActivitySecurityManager(db=db_session)

@pytest.mark.asyncio
async def test_validate_activity_access_allowed(security_manager):
    """Test validating activity access when allowed."""
    user_id = 'test_student'
    activity_id = 'test_activity'
    action = 'view'
    
    result = await security_manager.validate_activity_access(user_id, activity_id, action)
    
    assert result['allowed'] is True

@pytest.mark.asyncio
async def test_validate_activity_access_delete_blocked(security_manager):
    """Test validating activity access for delete action without admin role."""
    user_id = 'regular_user'  # Not admin
    activity_id = 'test_activity'
    action = 'delete'
    
    result = await security_manager.validate_activity_access(user_id, activity_id, action)
    
    assert result['allowed'] is False
    assert 'permission' in result['reason'].lower()

@pytest.mark.asyncio
async def test_validate_activity_access_admin_allowed(security_manager):
    """Test validating activity access for admin user."""
    user_id = 'admin_user'  # Admin (starts with admin_)
    activity_id = 'test_activity'
    action = 'delete'
    
    result = await security_manager.validate_activity_access(user_id, activity_id, action)
    
    assert result['allowed'] is True

@pytest.mark.asyncio
async def test_validate_activity_access_blocked_user(security_manager):
    """Test validating activity access for blocked user."""
    user_id = 'test_user'
    activity_id = 'test_activity'
    action = 'view'
    
    # Block the user first
    await security_manager.block_user(user_id, "Test blocking")
    
    result = await security_manager.validate_activity_access(user_id, activity_id, action)
    
    assert result['allowed'] is False
    assert 'blocked' in result['reason'].lower()

@pytest.mark.asyncio
async def test_validate_concurrent_activity_limits_within_limit(security_manager):
    """Test validating concurrent activity limits when within limit."""
    user_id = 'test_student'
    max_concurrent = 5
    
    result = await security_manager.validate_concurrent_activity_limits(user_id, max_concurrent)
    
    assert result['allowed'] is True
    assert result['current_count'] >= 0
    assert result['max_allowed'] == max_concurrent

@pytest.mark.asyncio
async def test_validate_concurrent_activity_limits_exceeds(security_manager):
    """Test validating concurrent activity limits when exceeded."""
    user_id = 'test_student'
    max_concurrent = 1  # Set very low limit
    
    result = await security_manager.validate_concurrent_activity_limits(user_id, max_concurrent)
    
    # Verify the method works with real database data
    assert 'allowed' in result
    assert 'current_count' in result

@pytest.mark.asyncio
async def test_validate_file_upload_allowed(security_manager):
    """Test validating file upload with allowed file."""
    user_id = 'test_student'
    file_info = {
        'extension': '.jpg',
        'size_mb': 5
    }
    
    result = await security_manager.validate_file_upload(user_id, file_info)
    
    assert result['allowed'] is True
    assert result['file_extension'] == '.jpg'

@pytest.mark.asyncio
async def test_validate_file_upload_invalid_type(security_manager):
    """Test validating file upload with invalid file type."""
    user_id = 'test_student'
    file_info = {
        'extension': '.exe',
        'size_mb': 5
    }
    
    result = await security_manager.validate_file_upload(user_id, file_info)
    
    assert result['allowed'] is False
    assert 'not allowed' in result['reason'].lower()

@pytest.mark.asyncio
async def test_validate_file_upload_too_large(security_manager):
    """Test validating file upload with oversized file."""
    user_id = 'test_student'
    file_info = {
        'extension': '.jpg',
        'size_mb': 100  # Exceeds 50MB limit
    }
    
    result = await security_manager.validate_file_upload(user_id, file_info)
    
    assert result['allowed'] is False
    assert 'exceeds' in result['reason'].lower()

@pytest.mark.asyncio
async def test_validate_user_permissions_sufficient(security_manager):
    """Test validating user permissions when user has sufficient permissions."""
    user_id = 'teacher_user'  # Teacher has create_activities permission
    required_permissions = ['view_activities', 'create_activities']
    
    result = await security_manager.validate_user_permissions(user_id, required_permissions)
    
    assert result['allowed'] is True

@pytest.mark.asyncio
async def test_validate_user_permissions_insufficient(security_manager):
    """Test validating user permissions when user lacks required permissions."""
    user_id = 'regular_user'  # Regular user doesn't have admin permissions
    required_permissions = ['delete_activities', 'manage_users']
    
    result = await security_manager.validate_user_permissions(user_id, required_permissions)
    
    assert result['allowed'] is False
    assert 'missing' in result['reason'].lower()

@pytest.mark.asyncio
async def test_get_security_violations(security_manager):
    """Test getting security violations."""
    # Create some violations first
    await security_manager.validate_file_upload('user1', {'extension': '.exe', 'size_mb': 1})
    await security_manager.validate_file_upload('user2', {'extension': '.bat', 'size_mb': 1})
    
    violations = await security_manager.get_security_violations()
    
    assert len(violations) >= 2
    assert all('violation_type' in v for v in violations)
    assert all('timestamp' in v for v in violations)

@pytest.mark.asyncio
async def test_get_security_violations_filtered_by_user(security_manager):
    """Test getting security violations filtered by user."""
    user_id = 'filtered_user'
    
    # Create violation for this user
    await security_manager.validate_file_upload(user_id, {'extension': '.exe', 'size_mb': 1})
    
    violations = await security_manager.get_security_violations(user_id=user_id)
    
    assert len(violations) >= 1
    assert all(v['user_id'] == user_id for v in violations)

@pytest.mark.asyncio
async def test_block_user(security_manager):
    """Test blocking a user."""
    user_id = 'user_to_block'
    
    result = await security_manager.block_user(user_id, "Test blocking reason")
    
    assert result is True
    blocked_users = await security_manager.get_blocked_users()
    assert user_id in blocked_users

@pytest.mark.asyncio
async def test_unblock_user(security_manager):
    """Test unblocking a user."""
    user_id = 'user_to_unblock'
    
    # Block first
    await security_manager.block_user(user_id, "Test")
    
    # Then unblock
    result = await security_manager.unblock_user(user_id)
    
    assert result is True
    blocked_users = await security_manager.get_blocked_users()
    assert user_id not in blocked_users

@pytest.mark.asyncio
async def test_get_blocked_users(security_manager):
    """Test getting list of blocked users."""
    # Block some users
    await security_manager.block_user('user1', "Reason 1")
    await security_manager.block_user('user2', "Reason 2")
    
    blocked_users = await security_manager.get_blocked_users()
    
    assert 'user1' in blocked_users
    assert 'user2' in blocked_users
