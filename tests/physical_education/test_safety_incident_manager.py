import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
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
    db = MagicMock(spec=Session)
    return db

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

@pytest.mark.asyncio
async def test_create_incident(safety_incident_manager, mock_db, sample_incident_data):
    """Test creating a safety incident."""
    # Mock the database session
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    
    # Create a mock SafetyIncident object
    mock_incident = MagicMock(spec=SafetyIncident)
    mock_incident.id = "incident1"
    mock_db.refresh.return_value = mock_incident
    
    # Test successful creation
    result = await safety_incident_manager.create_incident(
        class_id=sample_incident_data["class_id"],
        incident_type=sample_incident_data["incident_type"],
        description=sample_incident_data["description"],
        severity=sample_incident_data["severity"],
        affected_students=sample_incident_data["affected_students"],
        actions_taken=sample_incident_data["actions_taken"],
        metadata=sample_incident_data["metadata"],
        db=mock_db
    )
    
    assert result["success"] is True
    assert result["message"] == "Incident created successfully"
    assert result["incident_id"] == "incident1"
    
    # Test with invalid incident type
    with pytest.raises(ValueError):
        await safety_incident_manager.create_incident(
            class_id="class1",
            incident_type="invalid",
            description="Test",
            severity="low",
            affected_students=[],
            actions_taken=[],
            db=mock_db
        )
    
    # Test with invalid severity
    with pytest.raises(ValueError):
        await safety_incident_manager.create_incident(
            class_id="class1",
            incident_type="injury",
            description="Test",
            severity="invalid",
            affected_students=[],
            actions_taken=[],
            db=mock_db
        )

@pytest.mark.asyncio
async def test_get_incident(safety_incident_manager, mock_db):
    """Test retrieving a safety incident."""
    # Create a mock SafetyIncident object
    mock_incident = MagicMock(spec=SafetyIncident)
    mock_incident.id = "incident1"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_incident
    
    # Test successful retrieval
    result = await safety_incident_manager.get_incident("incident1", mock_db)
    assert result == mock_incident
    
    # Test with non-existent incident
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = await safety_incident_manager.get_incident("nonexistent", mock_db)
    assert result is None

@pytest.mark.asyncio
async def test_get_incidents(safety_incident_manager, mock_db):
    """Test retrieving multiple incidents with filters."""
    # Create mock SafetyIncident objects
    mock_incidents = [
        MagicMock(spec=SafetyIncident),
        MagicMock(spec=SafetyIncident)
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = mock_incidents
    
    # Test with all filters
    result = await safety_incident_manager.get_incidents(
        class_id="class1",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        severity="medium",
        status="open",
        db=mock_db
    )
    
    assert len(result) == 2
    assert result == mock_incidents

@pytest.mark.asyncio
async def test_update_incident(safety_incident_manager, mock_db):
    """Test updating a safety incident."""
    # Create a mock SafetyIncident object
    mock_incident = MagicMock(spec=SafetyIncident)
    mock_incident.id = "incident1"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_incident
    
    # Test successful update
    update_data = {
        "incident_type": "equipment_failure",
        "severity": "high",
        "status": "investigating"
    }
    
    result = await safety_incident_manager.update_incident("incident1", update_data, mock_db)
    assert result["success"] is True
    assert result["message"] == "Incident updated successfully"
    
    # Test with non-existent incident
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = await safety_incident_manager.update_incident("nonexistent", update_data, mock_db)
    assert result["success"] is False
    assert result["message"] == "Incident not found"
    
    # Test with invalid incident type
    with pytest.raises(ValueError):
        await safety_incident_manager.update_incident(
            "incident1",
            {"incident_type": "invalid"},
            mock_db
        )
    
    # Test with invalid severity
    with pytest.raises(ValueError):
        await safety_incident_manager.update_incident(
            "incident1",
            {"severity": "invalid"},
            mock_db
        )
    
    # Test with invalid status
    with pytest.raises(ValueError):
        await safety_incident_manager.update_incident(
            "incident1",
            {"status": "invalid"},
            mock_db
        )

@pytest.mark.asyncio
async def test_delete_incident(safety_incident_manager, mock_db):
    """Test deleting a safety incident."""
    # Create a mock SafetyIncident object
    mock_incident = MagicMock(spec=SafetyIncident)
    mock_incident.id = "incident1"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_incident
    
    # Test successful deletion
    result = await safety_incident_manager.delete_incident("incident1", mock_db)
    assert result["success"] is True
    assert result["message"] == "Incident deleted successfully"
    
    # Test with non-existent incident
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = await safety_incident_manager.delete_incident("nonexistent", mock_db)
    assert result["success"] is False
    assert result["message"] == "Incident not found"

@pytest.mark.asyncio
async def test_get_incident_statistics(safety_incident_manager, mock_db):
    """Test getting incident statistics."""
    # Create mock SafetyIncident objects
    mock_incidents = [
        MagicMock(spec=SafetyIncident),
        MagicMock(spec=SafetyIncident)
    ]
    mock_incidents[0].incident_type = "injury"
    mock_incidents[0].severity = "medium"
    mock_incidents[0].status = "open"
    mock_incidents[0].date = datetime.now()
    mock_incidents[1].incident_type = "equipment_failure"
    mock_incidents[1].severity = "high"
    mock_incidents[1].status = "investigating"
    mock_incidents[1].date = datetime.now()
    
    mock_db.query.return_value.filter.return_value.all.return_value = mock_incidents
    
    # Test getting statistics
    result = await safety_incident_manager.get_incident_statistics(
        class_id="class1",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        db=mock_db
    )
    
    assert "total" in result
    assert "by_type" in result
    assert "by_severity" in result
    assert "by_status" in result
    assert "trends" in result

@pytest.mark.asyncio
async def test_bulk_update_incidents(safety_incident_manager, mock_db):
    """Test bulk updating incidents."""
    updates = [
        {"incident_id": "incident1", "status": "resolved"},
        {"incident_id": "incident2", "severity": "low"}
    ]
    
    # Mock the database operations
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        MagicMock(spec=SafetyIncident),
        MagicMock(spec=SafetyIncident)
    ]
    
    result = await safety_incident_manager.bulk_update_incidents(updates, mock_db)
    assert "successful" in result
    assert "failed" in result
    assert result["successful"] == 2
    assert result["failed"] == 0

@pytest.mark.asyncio
async def test_bulk_delete_incidents(safety_incident_manager, mock_db):
    """Test bulk deleting incidents."""
    incident_ids = ["incident1", "incident2"]
    
    # Mock the database operations
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        MagicMock(spec=SafetyIncident),
        MagicMock(spec=SafetyIncident)
    ]
    
    result = await safety_incident_manager.bulk_delete_incidents(incident_ids, mock_db)
    assert "successful" in result
    assert "failed" in result
    assert result["successful"] == 2
    assert result["failed"] == 0

@pytest.mark.asyncio
async def test_error_handling(safety_incident_manager, mock_db):
    """Test error handling in safety incident operations."""
    # Test database error in create
    mock_db.commit.side_effect = Exception("Database error")
    result = await safety_incident_manager.create_incident(
        class_id="class1",
        incident_type="injury",
        description="Test",
        severity="low",
        affected_students=[],
        actions_taken=[],
        db=mock_db
    )
    assert result["success"] is False
    assert "Error creating incident" in result["message"]
    
    # Test database error in update
    mock_db.commit.side_effect = Exception("Database error")
    result = await safety_incident_manager.update_incident(
        "incident1",
        {"status": "resolved"},
        mock_db
    )
    assert result["success"] is False
    assert "Error updating incident" in result["message"]
    
    # Test database error in delete
    mock_db.commit.side_effect = Exception("Database error")
    result = await safety_incident_manager.delete_incident("incident1", mock_db)
    assert result["success"] is False
    assert "Error deleting incident" in result["message"] 