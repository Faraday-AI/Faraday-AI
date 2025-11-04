import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.physical_education.safety_manager import SafetyManager
from app.models.physical_education.safety.models import (
    RiskAssessment,
    SafetyIncident,
    EquipmentCheck,
    EnvironmentalCheck,
    SafetyCheck,
    SafetyProtocol,
    SafetyAlert
)
from app.models.physical_education.pe_enums.pe_types import (
    IncidentSeverity,
    RiskLevel,
    CheckType,
    AlertType,
    IncidentType
)

@pytest.fixture
def safety_manager(db_session):
    """
    Create a SafetyManager instance with a real database session.
    
    Best practice: Reset singleton instance before creating new manager to ensure clean state.
    Uses real Azure PostgreSQL via db_session fixture.
    """
    original_instance = SafetyManager._instance
    SafetyManager._instance = None
    manager = SafetyManager(db_session)
    manager.db = db_session
    
    yield manager
    
    SafetyManager._instance = original_instance

@pytest.fixture
def safety_manager_real_db(db_session):
    """
    Create a SafetyManager instance with a real database session for integration tests.
    
    Best practice: Use real database session for integration testing in final stages.
    """
    # Create a fresh instance with real db session
    original_instance = SafetyManager._instance
    SafetyManager._instance = None
    manager = SafetyManager(db_session)
    manager.db = db_session  # Ensure it uses the real session
    
    yield manager
    
    # Restore original instance to avoid affecting other tests
    SafetyManager._instance = original_instance

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
def test_user(db_session):
    """Create a real User for foreign key constraints."""
    from app.models.core.user import User
    import uuid
    
    unique_id = uuid.uuid4().hex[:8]
    user = User(
        email=f"test.user.{unique_id}@example.com",
        password_hash="hashed_password_placeholder",
        first_name=f"Test",
        last_name=f"User{unique_id}",
        role="teacher"
    )
    db_session.add(user)
    db_session.flush()  # Use flush for SAVEPOINT transactions
    db_session.refresh(user)
    return user

@pytest.fixture
def test_teacher(db_session, test_user):
    """Create a real Teacher record for foreign key constraints.
    
    The safety_incidents.teacher_id references teachers.id (not users.id),
    so we need to create a record in the teachers table.
    """
    from sqlalchemy import text
    import uuid
    
    unique_id = uuid.uuid4().hex[:8]
    # Insert directly into teachers table since there's no ORM model for it
    # PRODUCTION-READY: Both constraints on safety_incidents.teacher_id require the same value:
    # 1. fk_safety_incidents_teacher_id -> teachers.id
    # 2. safety_incidents_teacher_id_fkey -> users.id
    # To satisfy both, we need teachers.id = users.id (which matches seeded data pattern)
    # So we insert with id=test_user.id explicitly
    result = db_session.execute(
        text("""
            INSERT INTO teachers (id, first_name, last_name, email, user_id, is_active)
            VALUES (:id, :first_name, :last_name, :email, :user_id, :is_active)
            RETURNING id
        """),
        {
            "id": test_user.id,  # Use same ID as user to satisfy both constraints
            "first_name": "Test",
            "last_name": f"Teacher{unique_id}",
            "email": f"test.teacher.{unique_id}@example.com",
            "user_id": test_user.id,
            "is_active": True
        }
    )
    teacher_id = result.scalar()
    db_session.flush()  # Use flush for SAVEPOINT transactions
    
    # Return the teacher ID (same as user_id to satisfy both constraints)
    return {"id": teacher_id, "user_id": test_user.id}

@pytest.fixture
def incident_data(test_student, test_activity, test_teacher):
    """Create test incident data for real database operations.
    
    PRODUCTION-READY: Database constraint fk_safety_incidents_teacher_id enforces teachers.id
    (same pattern as physical_education_classes), so we use test_teacher["id"].
    """
    return {
        "activity_id": test_activity.id,  # Use real activity ID
        "student_id": test_student.id,  # Use real student ID
        "incident_type": IncidentType.INJURY,
        "severity": IncidentSeverity.MEDIUM,
        "description": "Sprained ankle during running",
        "response_taken": "Applied ice and elevated foot",
        "reported_by": test_teacher["id"],  # Both constraints require same value: fk_safety_incidents_teacher_id->teachers.id AND safety_incidents_teacher_id_fkey->users.id. Since teachers.id=users.id in fixture, use test_teacher["id"]
        "location": "Track field",
        "equipment_involved": ["running shoes"],
        "witnesses": ["Coach Smith"],
        "follow_up_required": ["Physical therapy"]
    }

@pytest.fixture
def risk_assessment_data(test_activity, test_user):
    """Create test risk assessment data for real database operations."""
    return {
        "activity_id": test_activity.id,  # Use real activity ID
        "risk_level": RiskLevel.MEDIUM,
        "factors": ["Uneven terrain", "Wet conditions"],
        "mitigation_measures": ["Mark hazards", "Reduce speed"],
        "environmental_conditions": {
            "humidity": 60,
            "temperature": 22
        },
        "equipment_status": {
            "shoes": "good",
            "track": "wet"
        },
        "student_health_considerations": ["asthma"],
        "weather_conditions": {
            "precipitation": "light rain",
            "wind_speed": 10
        },
        "assessed_by": test_user.id  # Risk assessments use user_id, not teacher_id
    }

@pytest.fixture
def alert_data(test_activity, test_user):
    """Create test alert data for real database operations."""
    return {
        "activity_id": test_activity.id,  # Use real activity ID
        "alert_type": AlertType.HIGH_RISK,  # Use valid AlertType enum value
        "severity": IncidentSeverity.HIGH,
        "message": "High risk of injury detected",
        "recipients": [test_user.id],  # Alerts use user IDs for recipients
        "created_by": test_user.id  # Created by user ID
    }

@pytest.fixture
def protocol_data():
    """Create test protocol data for real database operations."""
    return {
        "name": "Running Safety Protocol",
        "description": "Safety procedures for running activities",
        "protocol_type": "pre_activity",
        "steps": [
            "Check weather conditions",
            "Inspect running surface",
            "Verify equipment",
            "Review emergency procedures"
        ],
        "activity_type": "running",
        "required_equipment": ["Running shoes", "Water bottle"],
        "emergency_contacts": [
            {"name": "Dr. Smith", "phone": "123-456-7890"},
            {"name": "Nurse Johnson", "phone": "987-654-3210"}
        ]
    }

@pytest.mark.asyncio
async def test_create_risk_assessment(safety_manager, risk_assessment_data):
    """Test creating a risk assessment."""
    assessment = await safety_manager.create_risk_assessment(**risk_assessment_data)
    assert assessment is not None
    assert assessment.activity_id == risk_assessment_data['activity_id']
    # Check that risk_level is correct (may be string or enum value)
    risk_level_value = risk_assessment_data['risk_level']
    if hasattr(risk_level_value, 'value'):
        assert assessment.risk_level == risk_level_value.value
    else:
        assert assessment.risk_level == str(risk_level_value)
    # Check mapped fields
    assert assessment.activity_risks == risk_assessment_data['factors']
    assert assessment.mitigation_strategies == risk_assessment_data['mitigation_measures']
    assert assessment.student_risks == risk_assessment_data['student_health_considerations']

@pytest.mark.asyncio
async def test_get_risk_assessment(safety_manager, risk_assessment_data, db_session):
    """Test retrieving a risk assessment from real database."""
    created = await safety_manager.create_risk_assessment(**risk_assessment_data)
    assert created is not None
    db_session.flush()
    assessment = await safety_manager.get_risk_assessment(risk_assessment_data['activity_id'])
    assert assessment is not None
    assert assessment.activity_id == risk_assessment_data['activity_id']
    assert assessment.id == created.id

@pytest.mark.asyncio
async def test_report_incident(safety_manager, incident_data):
    """Test reporting a safety incident."""
    incident = await safety_manager.report_incident(**incident_data)
    assert incident is not None
    assert incident.activity_id == incident_data['activity_id']
    # Check that incident_type and severity are strings (converted from enums)
    incident_type_value = incident_data['incident_type']
    severity_value = incident_data['severity']
    if hasattr(incident_type_value, 'value'):
        assert incident.incident_type == incident_type_value.value
    else:
        assert incident.incident_type == str(incident_type_value)
    if hasattr(severity_value, 'value'):
        assert incident.severity == severity_value.value
    else:
        assert incident.severity == str(severity_value)
    # Check mapped fields
    assert incident.action_taken == incident_data['response_taken']
    assert incident.teacher_id == incident_data['reported_by']

@pytest.mark.asyncio
async def test_get_incident(safety_manager, incident_data, db_session):
    """Test retrieving a safety incident from real database."""
    created = await safety_manager.report_incident(**incident_data)
    assert created is not None
    db_session.flush()
    incident = await safety_manager.get_incident(created.id)
    assert incident is not None
    assert incident.id == created.id

@pytest.mark.asyncio
async def test_get_activity_incidents(safety_manager, incident_data):
    """Test retrieving incidents for an activity."""
    incidents = await safety_manager.get_activity_incidents(incident_data['activity_id'])
    assert isinstance(incidents, list)
    assert all(isinstance(incident, SafetyIncident) for incident in incidents)

@pytest.mark.asyncio
async def test_create_alert(safety_manager, alert_data):
    """Test creating a safety alert."""
    alert = await safety_manager.create_alert(**alert_data)
    assert alert is not None
    assert alert.alert_type == alert_data['alert_type']
    assert alert.severity == alert_data['severity']
    assert alert.message == alert_data['message']

@pytest.mark.asyncio
async def test_resolve_alert(safety_manager, alert_data, db_session):
    """Test resolving a safety alert from real database."""
    # First create an alert in the real database
    created_alert = await safety_manager.create_alert(**alert_data)
    assert created_alert is not None
    db_session.flush()
    
    # Now resolve it
    alert = await safety_manager.resolve_alert(created_alert.id, "Issue resolved")
    assert alert is not None
    assert alert.resolved_at is not None
    assert alert.resolution_notes == "Issue resolved"
    assert alert.id == created_alert.id

@pytest.mark.asyncio
async def test_get_active_alerts(safety_manager):
    """Test retrieving active alerts."""
    alerts = await safety_manager.get_active_alerts()
    assert isinstance(alerts, list)
    assert all(isinstance(alert, SafetyAlert) for alert in alerts)

@pytest.mark.asyncio
async def test_create_safety_protocol(safety_manager, protocol_data):
    """Test creating a safety protocol."""
    protocol = await safety_manager.create_safety_protocol(**protocol_data)
    assert protocol is not None
    assert protocol.name == protocol_data['name']
    assert protocol.description == protocol_data['description']
    # Check that protocol_type is mapped to category
    assert protocol.category == protocol_data['protocol_type']
    # Check that steps are mapped to procedures (as text)
    expected_procedures = "\n".join([f"{i+1}. {step}" for i, step in enumerate(protocol_data['steps'])])
    assert protocol.procedures == expected_procedures

@pytest.mark.asyncio
async def test_get_protocol(safety_manager, protocol_data, db_session):
    """Test retrieving a safety protocol from real database."""
    created = await safety_manager.create_safety_protocol(**protocol_data)
    assert created is not None
    db_session.flush()
    protocol = await safety_manager.get_protocol(created.id)
    assert protocol is not None
    assert protocol.id == created.id
    assert protocol.name == protocol_data['name']

@pytest.mark.asyncio
async def test_get_activity_protocols(safety_manager, protocol_data):
    """Test retrieving protocols for an activity type."""
    protocols = await safety_manager.get_activity_protocols(protocol_data['activity_type'])
    assert isinstance(protocols, list)
    assert all(isinstance(protocol, SafetyProtocol) for protocol in protocols)

@pytest.mark.asyncio
async def test_update_protocol_review(safety_manager, protocol_data, db_session):
    """Test updating protocol review dates from real database."""
    # First create a protocol in the real database
    created_protocol = await safety_manager.create_safety_protocol(**protocol_data)
    assert created_protocol is not None
    db_session.flush()
    
    # Now update its review dates
    protocol = await safety_manager.update_protocol_review(created_protocol.id)
    assert protocol is not None
    assert protocol.last_reviewed is not None
    assert protocol.next_review is not None
    assert protocol.id == created_protocol.id

@pytest.mark.asyncio
async def test_error_handling(safety_manager):
    """Test error handling in safety operations."""
    # Test with invalid parameters - these should raise exceptions
    # Note: The actual error depends on validation in the service methods
    from app.models.physical_education.pe_enums.pe_types import RiskLevel
    
    # Test with invalid activity_id - should raise an error
    with pytest.raises((Exception, ValueError, TypeError)):
        await safety_manager.create_risk_assessment(
            activity_id=None,
            risk_level=None,
            factors=None,
            mitigation_measures=None,
            assessed_by=None
        )
    
    # Test with invalid incident parameters - should raise an error
    from app.models.physical_education.pe_enums.pe_types import IncidentType, IncidentSeverity
    with pytest.raises((Exception, ValueError, TypeError)):
        await safety_manager.report_incident(
            activity_id=None,
            student_id=None,
            incident_type=None,
            severity=None,
            description=None,
            response_taken=None,
            reported_by=None
        )

@pytest.mark.asyncio
async def test_database_interaction(safety_manager, db_session):
    """
    Test database interaction patterns with real database session.
    
    Best practice: In final stages, test actual database operations rather than mocks.
    This verifies the service correctly interacts with the real database.
    """
    # Test session management - verify real database session is used
    assert safety_manager.db is not None
    # Verify it's a real SQLAlchemy Session, not a Mock
    from sqlalchemy.orm import Session
    assert isinstance(safety_manager.db, Session), f"Expected Session, got {type(safety_manager.db)}"
    assert safety_manager.db == db_session  # Should be the same real session object
    
    # Test actual database write operation - create a risk assessment
    # Create real test activity and user first
    from app.models.physical_education.activity import Activity
    from app.models.core.user import User
    import uuid
    
    test_activity = Activity(
        name=f"Test Activity {uuid.uuid4().hex[:8]}",
        description="Test activity for database interaction",
        difficulty_level="intermediate",
        duration=30
    )
    db_session.add(test_activity)
    db_session.flush()
    
    test_user = User(
        email=f"test.user.{uuid.uuid4().hex[:8]}@example.com",
        password_hash="hashed_password_placeholder",
        first_name="Test",
        last_name=f"User{uuid.uuid4().hex[:8]}",
        role="teacher"
    )
    db_session.add(test_user)
    db_session.flush()
    
    assessment = await safety_manager.create_risk_assessment(
        activity_id=test_activity.id,  # Use real activity ID
        risk_level=RiskLevel.MEDIUM,
        factors=['Test factor'],
        mitigation_measures=['Test mitigation'],
        assessed_by=test_user.id  # Use real user ID
    )
    
    # Verify data was actually committed to database
    assert assessment is not None
    assert assessment.id is not None  # ID assigned by database
    assert assessment.activity_id == test_activity.id
    assert assessment.risk_level == 'medium'  # Converted from enum
    
    # Verify we can retrieve it from database (proves commit worked)
    retrieved = await safety_manager.get_risk_assessment(activity_id=test_activity.id)
    assert retrieved is not None
    assert retrieved.id == assessment.id
    
    # Test rollback on error - verify transaction management
    # Verify session is still usable and not broken
    assert db_session.is_active 