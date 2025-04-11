import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from fastapi import Depends

from app.services.physical_education.services.safety_incident_manager import SafetyIncidentManager
from app.services.physical_education.models.safety import SafetyIncident

@pytest.fixture
def safety_incident_manager():
    return SafetyIncidentManager()

@pytest.fixture
def mock_db():
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

# Tests for initialization
def test_safety_incident_manager_initialization(safety_incident_manager):
    assert safety_incident_manager.incident_types
    assert safety_incident_manager.severity_levels
    assert safety_incident_manager.status_types

# Tests for create_incident
@pytest.mark.asyncio
async def test_create_incident_success(safety_incident_manager, mock_db, mock_incident_data):
    with patch.object(mock_db, 'add') as mock_add, \
         patch.object(mock_db, 'commit') as mock_commit, \
         patch.object(mock_db, 'refresh') as mock_refresh:
        
        result = await safety_incident_manager.create_incident(
            db=mock_db,
            **mock_incident_data
        )
        
        assert result["success"] is True
        assert "incident_id" in result
        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        mock_refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_incident_invalid_type(safety_incident_manager, mock_db, mock_incident_data):
    mock_incident_data["incident_type"] = "invalid_type"
    
    result = await safety_incident_manager.create_incident(
        db=mock_db,
        **mock_incident_data
    )
    
    assert result["success"] is False
    assert "Invalid incident type" in result["message"]

# Tests for get_incident
@pytest.mark.asyncio
async def test_get_incident_success(safety_incident_manager, mock_db, mock_incident):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = mock_incident
        
        result = await safety_incident_manager.get_incident(
            incident_id="incident123",
            db=mock_db
        )
        
        assert result == mock_incident

@pytest.mark.asyncio
async def test_get_incident_not_found(safety_incident_manager, mock_db):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        
        result = await safety_incident_manager.get_incident(
            incident_id="nonexistent",
            db=mock_db
        )
        
        assert result is None

# Tests for get_incidents
@pytest.mark.asyncio
async def test_get_incidents_with_filters(safety_incident_manager, mock_db, mock_incident):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.all.return_value = [mock_incident]
        
        result = await safety_incident_manager.get_incidents(
            class_id="class123",
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow(),
            severity="medium",
            status="open",
            db=mock_db
        )
        
        assert len(result) == 1
        assert result[0] == mock_incident

# Tests for update_incident
@pytest.mark.asyncio
async def test_update_incident_success(safety_incident_manager, mock_db, mock_incident):
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'commit') as mock_commit, \
         patch.object(mock_db, 'refresh') as mock_refresh:
        
        mock_query.return_value.filter.return_value.first.return_value = mock_incident
        
        result = await safety_incident_manager.update_incident(
            incident_id="incident123",
            update_data={"status": "resolved"},
            db=mock_db
        )
        
        assert result["success"] is True
        mock_commit.assert_called_once()
        mock_refresh.assert_called_once()

# Tests for delete_incident
@pytest.mark.asyncio
async def test_delete_incident_success(safety_incident_manager, mock_db, mock_incident):
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'delete') as mock_delete, \
         patch.object(mock_db, 'commit') as mock_commit:
        
        mock_query.return_value.filter.return_value.first.return_value = mock_incident
        
        result = await safety_incident_manager.delete_incident(
            incident_id="incident123",
            db=mock_db
        )
        
        assert result["success"] is True
        mock_delete.assert_called_once()
        mock_commit.assert_called_once()

# Tests for get_incident_statistics
@pytest.mark.asyncio
async def test_get_incident_statistics(safety_incident_manager, mock_db):
    with patch.object(mock_db, 'query') as mock_query:
        mock_query.return_value.filter.return_value.all.return_value = [
            Mock(severity="low"),
            Mock(severity="medium"),
            Mock(severity="high")
        ]
        
        result = await safety_incident_manager.get_incident_statistics(
            class_id="class123",
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow(),
            db=mock_db
        )
        
        assert "total_incidents" in result
        assert "severity_distribution" in result

# Tests for bulk operations
@pytest.mark.asyncio
async def test_bulk_update_incidents(safety_incident_manager, mock_db):
    updates = [
        {"incident_id": "incident1", "status": "resolved"},
        {"incident_id": "incident2", "status": "closed"}
    ]
    
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'commit') as mock_commit:
        
        mock_query.return_value.filter.return_value.first.return_value = Mock()
        
        result = await safety_incident_manager.bulk_update_incidents(
            updates=updates,
            db=mock_db
        )
        
        assert "successful_updates" in result
        assert "failed_updates" in result

@pytest.mark.asyncio
async def test_bulk_delete_incidents(safety_incident_manager, mock_db):
    incident_ids = ["incident1", "incident2"]
    
    with patch.object(mock_db, 'query') as mock_query, \
         patch.object(mock_db, 'delete') as mock_delete, \
         patch.object(mock_db, 'commit') as mock_commit:
        
        mock_query.return_value.filter.return_value.first.return_value = Mock()
        
        result = await safety_incident_manager.bulk_delete_incidents(
            incident_ids=incident_ids,
            db=mock_db
        )
        
        assert "successful_deletions" in result
        assert "failed_deletions" in result

# Tests for error handling
@pytest.mark.asyncio
async def test_error_handling_database_error(safety_incident_manager, mock_db):
    with patch.object(mock_db, 'query', side_effect=Exception("Database error")):
        result = await safety_incident_manager.get_incident(
            incident_id="incident123",
            db=mock_db
        )
        
        assert result is None

@pytest.mark.asyncio
async def test_error_handling_validation_error(safety_incident_manager, mock_db, mock_incident_data):
    mock_incident_data["incident_type"] = "invalid_type"
    
    result = await safety_incident_manager.create_incident(
        db=mock_db,
        **mock_incident_data
    )
    
    assert result["success"] is False
    assert "Invalid incident type" in result["message"] 