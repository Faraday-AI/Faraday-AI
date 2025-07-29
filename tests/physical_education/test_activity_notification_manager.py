import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.physical_education.notification_service import NotificationService
from datetime import datetime, timedelta

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_activity_manager():
    return MagicMock()

@pytest.fixture
def mock_notification_service():
    with patch('app.services.notification.NotificationService') as mock:
        mock.return_value = AsyncMock()
        yield mock

@pytest.fixture
def notification_manager(mock_db, mock_activity_manager, mock_notification_service):
    return NotificationService(db=mock_db, activity_manager=mock_activity_manager)

@pytest.mark.asyncio
async def test_send_activity_reminder(notification_manager, mock_notification_service):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    activity_data = {
        "name": "Morning Run",
        "scheduled_time": datetime.now() + timedelta(hours=1),
        "location": "Track Field"
    }
    mock_activity_manager.get_activity.return_value = activity_data
    
    # Test
    result = await notification_manager.send_activity_reminder(student_id, activity_id)
    
    # Verify
    assert result['notification_sent'] is True
    assert 'message_id' in result
    assert 'delivery_status' in result
    mock_notification_service.return_value.send.assert_called_once()

@pytest.mark.asyncio
async def test_send_progress_update(notification_manager, mock_notification_service):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    progress_data = {
        "current_score": 85,
        "improvement": 5,
        "milestones_achieved": ["First goal", "Second goal"]
    }
    
    # Test
    result = await notification_manager.send_progress_update(student_id, activity_id, progress_data)
    
    # Verify
    assert result['notification_sent'] is True
    assert 'message_id' in result
    assert 'delivery_status' in result
    mock_notification_service.return_value.send.assert_called_once()

@pytest.mark.asyncio
async def test_send_safety_alert(notification_manager, mock_notification_service):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    alert_data = {
        "type": "weather_alert",
        "severity": "high",
        "message": "Thunderstorm warning",
        "action_required": "Seek shelter immediately"
    }
    
    # Test
    result = await notification_manager.send_safety_alert(student_id, activity_id, alert_data)
    
    # Verify
    assert result['alert_sent'] is True
    assert 'message_id' in result
    assert 'delivery_status' in result
    mock_notification_service.return_value.send.assert_called_once()

@pytest.mark.asyncio
async def test_send_achievement_notification(notification_manager, mock_notification_service):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    achievement_data = {
        "type": "milestone",
        "title": "First 5K Run",
        "description": "Completed first 5K run under 30 minutes",
        "badge": "5k_runner"
    }
    
    # Test
    result = await notification_manager.send_achievement_notification(student_id, activity_id, achievement_data)
    
    # Verify
    assert result['notification_sent'] is True
    assert 'message_id' in result
    assert 'delivery_status' in result
    mock_notification_service.return_value.send.assert_called_once()

@pytest.mark.asyncio
async def test_get_notification_history(notification_manager, mock_db):
    # Setup
    student_id = "test_student"
    activity_id = "test_activity"
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        {
            "id": "notif1",
            "timestamp": datetime.now() - timedelta(days=1),
            "type": "reminder",
            "status": "delivered",
            "message": "Activity reminder"
        }
    ]
    
    # Test
    result = await notification_manager.get_notification_history(student_id, activity_id)
    
    # Verify
    assert len(result) > 0
    assert all('id' in item for item in result)
    assert all('timestamp' in item for item in result)
    assert all('type' in item for item in result)
    assert all('status' in item for item in result)
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_update_notification_preferences(notification_manager, mock_db):
    # Setup
    student_id = "test_student"
    preferences = {
        "reminders": True,
        "progress_updates": True,
        "safety_alerts": True,
        "achievements": True,
        "quiet_hours": {"start": "22:00", "end": "07:00"}
    }
    mock_db.query.return_value.filter.return_value.first.return_value = {
        "id": student_id,
        "notification_preferences": {}
    }
    
    # Test
    result = await notification_manager.update_notification_preferences(student_id, preferences)
    
    # Verify
    assert result['preferences_updated'] is True
    assert 'updated_preferences' in result
    mock_db.query.assert_called_once() 