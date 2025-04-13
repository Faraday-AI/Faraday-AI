import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from sqlalchemy.orm import Session
from app.services.physical_education.services.safety_incident_manager import SafetyIncidentManager
from app.services.physical_education.models.safety import SafetyIncident

@pytest.fixture
def safety_incident_manager():
    """Create SafetyIncidentManager instance for testing."""
    return SafetyIncidentManager()

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = Mock(spec=Session)
    return db

@pytest.fixture
def mock_incident_data():
    return {
        "class_id": "class123",
        "incident_type": "injury",
        "description": "Student fell during activity",
        "severity": "medium",
        "affected_students": ["student1", "student2"],
        "actions_taken": ["first_aid", "parent_notification"],
        "metadata": {"location": "gymnasium", "activity": "basketball"}
    }

@pytest.fixture
def mock_incident():
    incident = Mock(spec=SafetyIncident)
    incident.id = "incident123"
    incident.class_id = "class123"
    incident.incident_type = "injury"
    incident.description = "Student fell during activity"
    incident.severity = "medium"
    incident.affected_students = ["student1", "student2"]
    incident.actions_taken = ["first_aid", "parent_notification"]
    incident.date = datetime.utcnow()
    incident.status = "open"
    incident.reported = False
    incident.metadata = {"location": "gymnasium", "activity": "basketball"}
    return incident

@pytest.fixture
def sample_incident_data():
    """Create sample incident data."""
    return {
        "class_id": "class1",
        "incident_type": "injury",
        "description": "Student fell during activity",
        "severity": "medium",
        "affected_students": ["student1", "student2"],
        "actions_taken": ["First aid applied", "Parent notified"],
        "metadata": {"location": "gymnasium", "activity": "basketball"}
    }

def test_safety_incident_manager_initialization(safety_incident_manager):
    assert safety_incident_manager.incident_types
    assert safety_incident_manager.severity_levels
    assert safety_incident_manager.status_types

@pytest.mark.asyncio
async def test_create_incident_success(safety_incident_manager, mock_db, mock_incident_data):
    # Setup
    mock_incident_obj = Mock(spec=SafetyIncident)
    mock_incident_obj.id = 'incident1'

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    def refresh_side_effect(obj):
        obj.some_refreshed_attribute = "value"
    mock_db.refresh.side_effect = refresh_side_effect

    with patch('app.services.physical_education.services.safety_incident_manager.SafetyIncident', return_value=mock_incident_obj) as mock_model_init:
        # Test
        result = await safety_incident_manager.create_incident(**mock_incident_data, db=mock_db)

        # Verify
        assert result['success'] is True
        assert 'incident_id' in result
        mock_db.add.assert_called_once()
        added_instance = mock_db.add.call_args[0][0]
        assert added_instance == mock_incident_obj
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(added_instance)
        mock_model_init.assert_called_once_with(**mock_incident_data, date=pytest.approx(datetime.utcnow(), abs=timedelta(seconds=1)), status='open')

@pytest.mark.asyncio
async def test_create_incident_invalid_type(safety_incident_manager, mock_db, mock_incident_data):
    # Setup
    data = mock_incident_data.copy()
    data["incident_type"] = "invalid_type"

    # Test
    result = await safety_incident_manager.create_incident(**data, db=mock_db)

    # Verify
    assert result['success'] is False
    assert 'Invalid incident type' in result['message']
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_get_incident_success(safety_incident_manager, mock_db, mock_incident):
    # Setup
    incident_id = 'incident123'
    mock_db.query.return_value.filter.return_value.first.return_value = mock_incident

    # Test
    result = await safety_incident_manager.get_incident(incident_id, db=mock_db)

    # Verify
    assert result == mock_incident
    mock_db.query.assert_called_once_with(SafetyIncident)

@pytest.mark.asyncio
async def test_get_incident_not_found(safety_incident_manager, mock_db):
    # Setup
    incident_id = 'nonexistent'
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Test
    result = await safety_incident_manager.get_incident(incident_id, db=mock_db)

    # Verify
    assert result is None
    mock_db.query.assert_called_once_with(SafetyIncident)

@pytest.mark.asyncio
async def test_get_incidents_with_filters(safety_incident_manager, mock_db, mock_incident):
    # Setup
    filters = {
        'class_id': 'class123',
        'start_date': datetime.utcnow() - timedelta(days=7),
        'end_date': datetime.utcnow(),
        'severity': 'medium',
        'status': 'open'
    }
    mock_incidents = [mock_incident]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_incidents

    # Test
    result = await safety_incident_manager.get_incidents(**filters, db=mock_db)

    # Verify
    assert len(result) == 1
    assert result[0] == mock_incident
    mock_db.query.assert_called_once_with(SafetyIncident)

@pytest.mark.asyncio
async def test_update_incident_success(safety_incident_manager, mock_db, mock_incident):
    # Setup
    incident_id = 'incident123'
    update_data = {
        'status': 'resolved',
        'description': 'Updated description'
    }
    mock_db.query.return_value.filter.return_value.first.return_value = mock_incident

    # Test
    result = await safety_incident_manager.update_incident(incident_id, update_data, db=mock_db)

    # Verify
    assert result['success'] is True
    assert mock_incident.status == 'resolved'
    assert mock_incident.description == 'Updated description'
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_incident)

@pytest.mark.asyncio
async def test_update_incident_not_found(safety_incident_manager, mock_db):
    # Setup
    incident_id = 'nonexistent'
    update_data = {'status': 'resolved'}
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Test
    result = await safety_incident_manager.update_incident(incident_id, update_data, db=mock_db)

    # Verify
    assert result['success'] is False
    assert 'Incident not found' in result['message']
    mock_db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_delete_incident_success(safety_incident_manager, mock_db, mock_incident):
    # Setup
    incident_id = 'incident123'
    mock_db.query.return_value.filter.return_value.first.return_value = mock_incident

    # Test
    result = await safety_incident_manager.delete_incident(incident_id, db=mock_db)

    # Verify
    assert result['success'] is True
    mock_db.delete.assert_called_once_with(mock_incident)
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_get_incident_statistics(safety_incident_manager, mock_db):
    # Setup
    filters = {
        'class_id': 'class123',
        'start_date': datetime.utcnow() - timedelta(days=30),
        'end_date': datetime.utcnow()
    }
    mock_incidents = [
        Mock(severity="low", incident_type="type1", status="open"),
        Mock(severity="medium", incident_type="type2", status="resolved"),
        Mock(severity="high", incident_type="type1", status="open")
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_incidents

    # Test
    result = await safety_incident_manager.get_incident_statistics(**filters, db=mock_db)

    # Verify
    assert 'total' in result and result['total'] == len(mock_incidents)
    assert 'by_type' in result
    assert 'by_severity' in result
    assert 'by_status' in result
    assert result['by_severity'] == {'low': 1, 'medium': 1, 'high': 1}
    assert result['trends'] is not None

@pytest.mark.asyncio
async def test_bulk_update_incidents(safety_incident_manager, mock_db):
    # Setup
    updates = [
        {'id': 'incident1', 'status': 'resolved'},
        {'id': 'incident2', 'severity': 'high'}
    ]
    mock_incident1 = Mock(spec=SafetyIncident)
    mock_incident2 = Mock(spec=SafetyIncident)
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_incident1, mock_incident2]

    # Test
    result = await safety_incident_manager.bulk_update_incidents(updates, db=mock_db)

    # Verify
    assert result['success_count'] == 2
    assert result['failure_count'] == 0
    assert mock_incident1.status == 'resolved'
    assert mock_incident2.severity == 'high'
    assert mock_db.commit.call_count == 1
    assert mock_db.refresh.call_count == 2

@pytest.mark.asyncio
async def test_bulk_delete_incidents(safety_incident_manager, mock_db):
    # Setup
    incident_ids = ['incident1', 'incident2']
    mock_incident1 = Mock(spec=SafetyIncident)
    mock_incident2 = Mock(spec=SafetyIncident)
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_incident1, mock_incident2]

    # Test
    result = await safety_incident_manager.bulk_delete_incidents(incident_ids, db=mock_db)

    # Verify
    assert result['success_count'] == 2
    assert result['failure_count'] == 0
    assert mock_db.delete.call_count == 2
    assert mock_db.delete.call_args_list[0][0][0] == mock_incident1
    assert mock_db.delete.call_args_list[1][0][0] == mock_incident2
    assert mock_db.commit.call_count == 1

@pytest.mark.asyncio
async def test_error_handling_database_error(safety_incident_manager, mock_db, mock_incident_data):
    """Test database error handling across operations."""
    # Test error in create
    mock_db.commit.side_effect = Exception("DB Commit Error")
    result_create = await safety_incident_manager.create_incident(**mock_incident_data, db=mock_db)
    assert result_create["success"] is False
    assert "Error creating incident" in result_create["message"]
    mock_db.rollback.assert_called_once()
    mock_db.commit.reset_mock()
    mock_db.rollback.reset_mock()

    # Reset side effect for next tests
    mock_db.commit.side_effect = None

    # Setup for get/update/delete tests
    incident_id = "incident123"
    mock_incident_obj = Mock(spec=SafetyIncident)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_incident_obj

    # Test error in get (simulating query error)
    mock_db.query.side_effect = Exception("DB Query Error")
    result_get = await safety_incident_manager.get_incident(incident_id, db=mock_db)
    assert result_get is None
    mock_db.query.side_effect = None

    # Test error in update
    mock_db.commit.side_effect = Exception("DB Commit Error Update")
    result_update = await safety_incident_manager.update_incident(incident_id, {"status": "closed"}, mock_db)
    assert result_update["success"] is False
    assert "Error updating incident" in result_update["message"]
    mock_db.rollback.assert_called_once()
    mock_db.commit.reset_mock()
    mock_db.rollback.reset_mock()
    mock_db.commit.side_effect = None

    # Test error in delete
    mock_db.commit.side_effect = Exception("DB Commit Error Delete")
    result_delete = await safety_incident_manager.delete_incident(incident_id, mock_db)
    assert result_delete["success"] is False
    assert "Error deleting incident" in result_delete["message"]
    mock_db.rollback.assert_called_once()
    mock_db.commit.reset_mock()
    mock_db.rollback.reset_mock()
    mock_db.commit.side_effect = None

@pytest.mark.asyncio
async def test_error_handling_validation_error(safety_incident_manager, mock_db, mock_incident_data):
    data = mock_incident_data.copy()
    data["incident_type"] = "invalid_type"

    result = await safety_incident_manager.create_incident(
        db=mock_db,
        **data
    )

    assert result["success"] is False
    assert "Invalid incident type" in result["message"]
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called() 