import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.physical_education.activity_scheduling_manager import ActivitySchedulingManager
from datetime import datetime, timedelta

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_activity_manager():
    return MagicMock()

@pytest.fixture
def mock_scheduling_service():
    with patch('app.services.scheduling.SchedulingService') as mock:
        mock.return_value = AsyncMock()
        yield mock

@pytest.fixture
def scheduling_manager(mock_db, mock_activity_manager, mock_scheduling_service):
    return ActivitySchedulingManager(db=mock_db, activity_manager=mock_activity_manager)

@pytest.mark.asyncio
async def test_schedule_activity(scheduling_manager, mock_activity_manager, mock_scheduling_service):
    # Setup
    activity_id = "test_activity"
    schedule_data = {
        "start_time": datetime.now() + timedelta(hours=1),
        "end_time": datetime.now() + timedelta(hours=2),
        "location": "Gymnasium",
        "max_participants": 20
    }
    mock_activity_manager.get_activity.return_value = {
        "id": activity_id,
        "name": "Morning Workout",
        "duration": 60
    }
    
    # Test
    result = await scheduling_manager.schedule_activity(activity_id, schedule_data)
    
    # Verify
    assert result['scheduled'] is True
    assert 'schedule_id' in result
    assert 'confirmation_details' in result
    mock_activity_manager.get_activity.assert_called_once_with(activity_id)
    mock_scheduling_service.return_value.create_schedule.assert_called_once()

@pytest.mark.asyncio
async def test_check_schedule_availability(scheduling_manager, mock_scheduling_service):
    # Setup
    location = "Gymnasium"
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=2)
    mock_scheduling_service.return_value.check_availability.return_value = {
        "available": True,
        "conflicting_events": []
    }
    
    # Test
    result = await scheduling_manager.check_schedule_availability(location, start_time, end_time)
    
    # Verify
    assert result['available'] is True
    assert 'conflicting_events' in result
    mock_scheduling_service.return_value.check_availability.assert_called_once()

@pytest.mark.asyncio
async def test_update_schedule(scheduling_manager, mock_scheduling_service):
    # Setup
    schedule_id = "test_schedule"
    update_data = {
        "start_time": datetime.now() + timedelta(hours=2),
        "end_time": datetime.now() + timedelta(hours=3),
        "location": "Outdoor Track"
    }
    mock_scheduling_service.return_value.update_schedule.return_value = {
        "updated": True,
        "new_schedule": update_data
    }
    
    # Test
    result = await scheduling_manager.update_schedule(schedule_id, update_data)
    
    # Verify
    assert result['updated'] is True
    assert 'new_schedule' in result
    mock_scheduling_service.return_value.update_schedule.assert_called_once()

@pytest.mark.asyncio
async def test_cancel_schedule(scheduling_manager, mock_scheduling_service):
    # Setup
    schedule_id = "test_schedule"
    reason = "Weather conditions"
    mock_scheduling_service.return_value.cancel_schedule.return_value = {
        "cancelled": True,
        "cancellation_time": datetime.now()
    }
    
    # Test
    result = await scheduling_manager.cancel_schedule(schedule_id, reason)
    
    # Verify
    assert result['cancelled'] is True
    assert 'cancellation_time' in result
    mock_scheduling_service.return_value.cancel_schedule.assert_called_once()

@pytest.mark.asyncio
async def test_get_schedule_history(scheduling_manager, mock_db):
    # Setup
    activity_id = "test_activity"
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        {
            "id": "schedule1",
            "start_time": datetime.now() - timedelta(days=1),
            "end_time": datetime.now() - timedelta(days=1) + timedelta(hours=1),
            "status": "completed",
            "location": "Gymnasium"
        }
    ]
    
    # Test
    result = await scheduling_manager.get_schedule_history(activity_id)
    
    # Verify
    assert len(result) > 0
    assert all('id' in item for item in result)
    assert all('start_time' in item for item in result)
    assert all('end_time' in item for item in result)
    assert all('status' in item for item in result)
    mock_db.query.assert_called_once()

@pytest.mark.asyncio
async def test_handle_schedule_conflict(scheduling_manager, mock_scheduling_service):
    # Setup
    schedule_id = "test_schedule"
    conflict_data = {
        "conflicting_event": "Other Activity",
        "conflict_type": "location",
        "suggested_resolutions": ["Change location", "Adjust time"]
    }
    mock_scheduling_service.return_value.resolve_conflict.return_value = {
        "resolved": True,
        "resolution": "Changed location to Outdoor Track",
        "new_schedule": {
            "location": "Outdoor Track",
            "start_time": datetime.now() + timedelta(hours=1)
        }
    }
    
    # Test
    result = await scheduling_manager.handle_schedule_conflict(schedule_id, conflict_data)
    
    # Verify
    assert result['resolved'] is True
    assert 'resolution' in result
    assert 'new_schedule' in result
    mock_scheduling_service.return_value.resolve_conflict.assert_called_once() 