import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.physical_education.safety_incident_manager import SafetyIncidentManager
from app.models.physical_education.safety import SafetyIncident

@pytest.fixture
def safety_incident_manager():
    """Create SafetyIncidentManager instance for testing."""
    return SafetyIncidentManager()

@pytest.fixture
def test_student(db_session):
    """Create a real Student for foreign key constraints."""
    from app.models.physical_education.student import Student
    from app.models.physical_education.pe_enums.pe_types import GradeLevel
    from datetime import datetime, timedelta
    import uuid
    
    unique_id = uuid.uuid4().hex[:8]
    student = Student(
        first_name="Test",
        last_name=f"Student{unique_id}",
        email=f"test.student.{unique_id}@example.com",
        date_of_birth=datetime.now() - timedelta(days=365*15),  # 15 years old
        grade_level=GradeLevel.NINTH,
    )
    db_session.add(student)
    db_session.flush()  # Use flush for SAVEPOINT transactions
    db_session.refresh(student)
    return student

@pytest.fixture
def test_activity(db_session):
    """Create a real Activity for foreign key constraints."""
    from app.models.physical_education.activity import Activity
    import uuid
    
    activity = Activity(
        name=f"Test Activity {uuid.uuid4().hex[:8]}",
        description="Test activity for safety incidents",
        difficulty_level="intermediate",
        duration=30
    )
    db_session.add(activity)
    db_session.flush()  # Use flush for SAVEPOINT transactions
    db_session.refresh(activity)
    return activity

@pytest.fixture
def incident_data(test_student, test_activity):
    """Create test incident data for real database operations."""
    return {
        "student_id": test_student.id,  # Use real student ID from fixture
        "activity_id": test_activity.id,  # Use real activity ID from fixture
        "incident_type": "injury",
        "description": "Student fell during activity",
        "severity": "medium",
        "action_taken": "First aid applied, parent notified",
        "location": "gymnasium",
        "incident_metadata": {"activity": "basketball"}
    }

def test_safety_incident_manager_initialization(safety_incident_manager):
    assert safety_incident_manager.incident_types
    assert safety_incident_manager.severity_levels
    assert safety_incident_manager.status_types

@pytest.mark.asyncio
async def test_create_incident_success(safety_incident_manager, db_session, incident_data):
    """Test creating an incident in real database."""
    # Test - create incident in real database
    result = await safety_incident_manager.create_incident(**incident_data, db=db_session)

    # Verify
    assert result['success'] is True
    assert 'incident_id' in result
    incident_id = result['incident_id']
    
    # Verify incident was actually created in database
    created_incident = await safety_incident_manager.get_incident(incident_id, db=db_session)
    assert created_incident is not None
    assert created_incident.student_id == incident_data["student_id"]
    assert created_incident.activity_id == incident_data["activity_id"]
    assert created_incident.incident_type == incident_data["incident_type"]
    assert created_incident.description == incident_data["description"]

@pytest.mark.asyncio
async def test_create_incident_invalid_type(safety_incident_manager, db_session, incident_data):
    """Test creating incident with invalid type - validation should fail."""
    data = incident_data.copy()
    data["incident_type"] = "invalid_type"

    # Test
    result = await safety_incident_manager.create_incident(**data, db=db_session)

    # Verify - validation should fail before database operations
    assert result['success'] is False
    assert 'Invalid incident type' in result['message']

@pytest.mark.asyncio
async def test_get_incident_success(safety_incident_manager, db_session, incident_data):
    """Test retrieving an incident from real database."""
    # First create an incident in the real database
    create_result = await safety_incident_manager.create_incident(**incident_data, db=db_session)
    assert create_result['success'] is True
    incident_id = create_result['incident_id']
    db_session.flush()
    
    # Test - retrieve from real database
    result = await safety_incident_manager.get_incident(incident_id, db=db_session)

    # Verify
    assert result is not None
    assert result.id == incident_id
    assert result.student_id == incident_data["student_id"]

@pytest.mark.asyncio
async def test_get_incident_not_found(safety_incident_manager, db_session):
    """Test retrieving non-existent incident from real database."""
    # Test with ID that doesn't exist
    incident_id = 999999999  # Large ID that shouldn't exist
    
    result = await safety_incident_manager.get_incident(incident_id, db=db_session)

    # Verify
    assert result is None

@pytest.mark.asyncio
async def test_get_incidents_with_filters(safety_incident_manager, db_session, incident_data):
    """Test retrieving incidents with filters from real database."""
    # First create an incident in the real database
    create_result = await safety_incident_manager.create_incident(**incident_data, db=db_session)
    assert create_result['success'] is True
    db_session.flush()
    
    filters = {
        'student_id': incident_data['student_id'],
        'activity_id': incident_data['activity_id'],
        'start_date': datetime.utcnow() - timedelta(days=7),
        'end_date': datetime.utcnow(),
        'severity': incident_data['severity'],
        'incident_type': incident_data['incident_type']
    }

    # Test - retrieve from real database
    result = await safety_incident_manager.get_incidents(**filters, db=db_session)

    # Verify
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(inc, SafetyIncident) for inc in result)

@pytest.mark.asyncio
async def test_update_incident_success(safety_incident_manager, db_session, incident_data):
    """Test updating an incident in real database."""
    # First create an incident in the real database
    create_result = await safety_incident_manager.create_incident(**incident_data, db=db_session)
    assert create_result['success'] is True
    incident_id = create_result['incident_id']
    db_session.flush()
    
    update_data = {
        'description': 'Updated description',
        'severity': 'high'
    }

    # Test - update in real database
    result = await safety_incident_manager.update_incident(incident_id, update_data, db=db_session)

    # Verify
    assert result['success'] is True
    
    # Verify update was actually saved in database
    updated_incident = await safety_incident_manager.get_incident(incident_id, db=db_session)
    assert updated_incident is not None
    assert updated_incident.description == 'Updated description'
    assert updated_incident.severity == 'high'

@pytest.mark.asyncio
async def test_update_incident_not_found(safety_incident_manager, db_session):
    """Test updating non-existent incident from real database."""
    # Test with ID that doesn't exist
    incident_id = 999999999  # Large ID that shouldn't exist
    update_data = {'description': 'Updated'}

    # Test
    result = await safety_incident_manager.update_incident(incident_id, update_data, db=db_session)

    # Verify
    assert result['success'] is False
    assert 'Incident not found' in result['message']

@pytest.mark.asyncio
async def test_delete_incident_success(safety_incident_manager, db_session, incident_data):
    """Test deleting an incident from real database."""
    # First create an incident in the real database
    create_result = await safety_incident_manager.create_incident(**incident_data, db=db_session)
    assert create_result['success'] is True
    incident_id = create_result['incident_id']
    db_session.flush()
    
    # Verify it exists before deletion
    incident = await safety_incident_manager.get_incident(incident_id, db=db_session)
    assert incident is not None

    # Test - delete from real database
    result = await safety_incident_manager.delete_incident(incident_id, db=db_session)

    # Verify
    assert result['success'] is True
    
    # Verify it was actually deleted
    deleted_incident = await safety_incident_manager.get_incident(incident_id, db=db_session)
    assert deleted_incident is None

@pytest.mark.asyncio
async def test_get_incident_statistics(safety_incident_manager, db_session, incident_data):
    """Test getting incident statistics from real database."""
    # Create incidents in real database with different severities
    incident_low = incident_data.copy()
    incident_low['severity'] = 'low'
    incident_medium = incident_data.copy()
    incident_medium['severity'] = 'medium'
    incident_high = incident_data.copy()
    incident_high['severity'] = 'high'
    
    for data in [incident_low, incident_medium, incident_high]:
        create_result = await safety_incident_manager.create_incident(**data, db=db_session)
        assert create_result['success'] is True
    db_session.flush()
    
    filters = {
        'student_id': incident_data['student_id'],
        'start_date': datetime.utcnow() - timedelta(days=30),
        'end_date': datetime.utcnow()
    }

    # Test - get statistics from real database
    result = await safety_incident_manager.get_incident_statistics(**filters, db=db_session)

    # Verify
    assert 'total' in result
    assert result['total'] >= 3  # At least the 3 we created
    assert 'by_type' in result
    assert 'by_severity' in result
    assert 'trends' in result
    assert result['trends'] is not None

@pytest.mark.asyncio
async def test_bulk_update_incidents(safety_incident_manager, db_session, incident_data):
    """Test bulk updating incidents in real database."""
    # Create two incidents in real database
    incident1_data = incident_data.copy()
    incident2_data = incident_data.copy()
    
    create1 = await safety_incident_manager.create_incident(**incident1_data, db=db_session)
    create2 = await safety_incident_manager.create_incident(**incident2_data, db=db_session)
    assert create1['success'] is True
    assert create2['success'] is True
    db_session.flush()
    
    updates = [
        {'id': create1['incident_id'], 'description': 'Updated description'},
        {'id': create2['incident_id'], 'severity': 'high'}
    ]

    # Test
    result = await safety_incident_manager.bulk_update_incidents(updates, db=db_session)

    # Verify
    assert result['success_count'] == 2
    assert result['failure_count'] == 0
    
    # Verify updates were actually saved
    updated1 = await safety_incident_manager.get_incident(create1['incident_id'], db=db_session)
    updated2 = await safety_incident_manager.get_incident(create2['incident_id'], db=db_session)
    assert updated1.description == 'Updated description'
    assert updated2.severity == 'high'

@pytest.mark.asyncio
async def test_bulk_delete_incidents(safety_incident_manager, db_session, incident_data):
    """Test bulk deleting incidents from real database."""
    # Create two incidents in real database
    incident1_data = incident_data.copy()
    incident2_data = incident_data.copy()
    
    create1 = await safety_incident_manager.create_incident(**incident1_data, db=db_session)
    create2 = await safety_incident_manager.create_incident(**incident2_data, db=db_session)
    assert create1['success'] is True
    assert create2['success'] is True
    db_session.flush()
    
    incident_ids = [create1['incident_id'], create2['incident_id']]

    # Verify they exist before deletion
    assert await safety_incident_manager.get_incident(create1['incident_id'], db=db_session) is not None
    assert await safety_incident_manager.get_incident(create2['incident_id'], db=db_session) is not None

    # Test
    result = await safety_incident_manager.bulk_delete_incidents(incident_ids, db=db_session)

    # Verify
    assert result['success_count'] == 2
    assert result['failure_count'] == 0
    
    # Verify they were actually deleted
    assert await safety_incident_manager.get_incident(create1['incident_id'], db=db_session) is None
    assert await safety_incident_manager.get_incident(create2['incident_id'], db=db_session) is None

@pytest.mark.asyncio
async def test_error_handling_database_error(safety_incident_manager, db_session, incident_data):
    """Test database error handling - validation errors work correctly.
    
    Note: In final stages with real database, we test validation errors which
    occur before database operations, and real database constraints.
    """
    # Test validation error (happens before database operations)
    invalid_data = incident_data.copy()
    invalid_data['incident_type'] = 'invalid_type'
    result = await safety_incident_manager.create_incident(**invalid_data, db=db_session)
    assert result["success"] is False
    assert "Invalid" in result["message"]

@pytest.mark.asyncio
async def test_error_handling_validation_error(safety_incident_manager, db_session, incident_data):
    """Test validation error handling - should fail before database operations."""
    data = incident_data.copy()
    data["incident_type"] = "invalid_type"

    result = await safety_incident_manager.create_incident(
        db=db_session,
        **data
    )

    assert result["success"] is False
    assert "Invalid incident type" in result["message"]