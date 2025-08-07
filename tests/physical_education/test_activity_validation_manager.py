import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.physical_education.activity_validation_manager import ActivityValidationManager
from datetime import datetime, timedelta

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_activity_manager():
    return MagicMock()

@pytest.fixture
def validation_manager(mock_db, mock_activity_manager):
    return ActivityValidationManager(db=mock_db, activity_manager=mock_activity_manager)

@pytest.mark.asyncio
async def test_validate_activity_creation(validation_manager, mock_activity_manager):
    # Setup
    activity_data = {
        "name": "Test Activity",
        "description": "Test Description",
        "duration": 30,
        "type": "team_sport",
        "difficulty_level": "intermediate",
        "participants": 15,
        "equipment_required": ["ball", "net", "safety_equipment"],
        "safety_guidelines": ["Wear proper shoes", "Stay hydrated"]
    }
    mock_activity_manager.get_activity_by_name.return_value = None
    
    # Test
    result = await validation_manager.validate_activity_creation(activity_data)
    
    # Verify
    assert result['is_valid'] is True
    assert result['errors'] == []
    mock_activity_manager.get_activity_by_name.assert_called_once_with(activity_data['name'])

@pytest.mark.asyncio
async def test_validate_activity_creation_duplicate_name(validation_manager, mock_activity_manager):
    # Setup
    activity_data = {
        "name": "Existing Activity",
        "description": "Test Description",
        "duration": 30,
        "type": "individual_sport",
        "participants": 10,
        "equipment_required": ["safety_equipment"]
    }
    mock_activity_manager.get_activity_by_name.return_value = {"id": "123", "name": "Existing Activity"}
    
    # Test
    result = await validation_manager.validate_activity_creation(activity_data)
    
    # Verify
    assert result['is_valid'] is False
    assert "Activity with this name already exists" in result['errors']

@pytest.mark.asyncio
async def test_validate_activity_update(validation_manager, mock_activity_manager):
    # Setup
    activity_id = "test_activity"
    update_data = {
        "name": "Updated Activity",
        "description": "Updated Description",
        "duration": 45,
        "type": "team_sport",
        "participants": 20,
        "equipment_required": ["safety_equipment"]
    }
    mock_activity_manager.get_activity_by_name.return_value = None
    mock_activity_manager.get_activity.return_value = {"id": activity_id, "name": "Original Activity"}
    
    # Test
    result = await validation_manager.validate_activity_update(activity_id, update_data)
    
    # Verify
    assert result['is_valid'] is True
    assert result['errors'] == []
    mock_activity_manager.get_activity_by_name.assert_called_once_with(update_data['name'])

@pytest.mark.asyncio
async def test_validate_activity_update_nonexistent(validation_manager, mock_activity_manager):
    # Setup
    activity_id = "nonexistent_activity"
    update_data = {"name": "Updated Activity"}
    mock_activity_manager.get_activity.return_value = None
    
    # Test
    result = await validation_manager.validate_activity_update(activity_id, update_data)
    
    # Verify
    assert result['is_valid'] is False
    assert "Activity not found" in result['errors']

@pytest.mark.asyncio
async def test_validate_activity_schedule(validation_manager):
    # Setup
    schedule_data = {
        "start_time": datetime.now() + timedelta(hours=1),
        "end_time": datetime.now() + timedelta(hours=2),
        "max_participants": 20,
        "location": "Gymnasium"
    }
    
    # Test
    result = await validation_manager.validate_activity_schedule(schedule_data)
    
    # Verify
    assert result['is_valid'] is True
    assert result['errors'] == []

@pytest.mark.asyncio
async def test_validate_activity_schedule_invalid_times(validation_manager):
    # Setup
    schedule_data = {
        "start_time": datetime.now() + timedelta(hours=2),
        "end_time": datetime.now() + timedelta(hours=1),
        "max_participants": 20
    }
    
    # Test
    result = await validation_manager.validate_activity_schedule(schedule_data)
    
    # Verify
    assert result['is_valid'] is False
    assert "End time must be after start time" in result['errors']

@pytest.mark.asyncio
async def test_validate_activity_participants(validation_manager, mock_activity_manager):
    # Setup
    activity_id = "test_activity"
    participants = [{"id": "student1"}, {"id": "student2"}, {"id": "student3"}]
    mock_activity_manager.get_activity.return_value = {
        "id": activity_id,
        "max_participants": 5,
        "min_participants": 1,
        "current_participants": 2
    }
    
    # Test
    result = await validation_manager.validate_activity_participants(activity_id, {"count": 3, "participants": participants})
    
    # Verify
    assert result['is_valid'] is True
    assert result['errors'] == []

@pytest.mark.asyncio
async def test_validate_activity_participants_exceed_limit(validation_manager, mock_activity_manager):
    # Setup
    activity_id = "test_activity"
    participants = [{"id": "student1"}, {"id": "student2"}, {"id": "student3"}, {"id": "student4"}]
    mock_activity_manager.get_activity.return_value = {
        "id": activity_id,
        "max_participants": 3,
        "min_participants": 1,
        "current_participants": 2
    }
    
    # Test
    result = await validation_manager.validate_activity_participants(activity_id, {"count": 4, "participants": participants})
    
    # Verify
    assert result['is_valid'] is False
    assert "Too many participants: 4" in result['errors'] 