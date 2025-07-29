import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch
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
def db_session():
    """Create a mock database session."""
    return Mock()

@pytest.fixture
def safety_manager(db_session):
    """Create a SafetyManager instance with a mock database session."""
    return SafetyManager(db_session)

@pytest.fixture
def mock_activity():
    """Create mock activity data."""
    return {
        "id": 1,
        "name": "Running",
        "type": "cardio",
        "intensity": "high"
    }

@pytest.fixture
def mock_student():
    """Create mock student data."""
    return {
        "id": 1,
        "name": "John Doe",
        "grade": 10,
        "medical_conditions": ["asthma"]
    }

@pytest.fixture
def mock_incident_data():
    """Create mock incident data."""
    return {
        "activity_id": 1,
        "student_id": 1,
        "incident_type": IncidentType.INJURY,
        "severity": IncidentSeverity.MEDIUM,
        "description": "Sprained ankle during running",
        "response_taken": "Applied ice and elevated foot",
        "reported_by": 1,
        "location": "Track field",
        "equipment_involved": ["running shoes"],
        "witnesses": ["Coach Smith"],
        "follow_up_required": ["Physical therapy"]
    }

@pytest.fixture
def mock_risk_assessment_data():
    """Create mock risk assessment data."""
    return {
        "activity_id": 1,
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
        }
    }

@pytest.fixture
def mock_alert_data():
    """Create mock alert data."""
    return {
        "activity_id": 1,
        "alert_type": AlertType.RISK_THRESHOLD,
        "severity": IncidentSeverity.HIGH,
        "message": "High risk of injury detected",
        "recipients": [1, 2]
    }

@pytest.fixture
def mock_protocol_data():
    """Create mock protocol data."""
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
async def test_create_risk_assessment(safety_manager, mock_risk_assessment_data):
    """Test creating a risk assessment."""
    assessment = await safety_manager.create_risk_assessment(**mock_risk_assessment_data)
    assert assessment is not None
    assert assessment.activity_id == mock_risk_assessment_data['activity_id']
    assert assessment.risk_level == mock_risk_assessment_data['risk_level']
    assert assessment.factors == mock_risk_assessment_data['factors']
    assert assessment.mitigation_measures == mock_risk_assessment_data['mitigation_measures']

@pytest.mark.asyncio
async def test_get_risk_assessment(safety_manager, mock_risk_assessment_data):
    """Test retrieving a risk assessment."""
    assessment = await safety_manager.get_risk_assessment(mock_risk_assessment_data['activity_id'])
    assert assessment is not None
    assert assessment.activity_id == mock_risk_assessment_data['activity_id']

@pytest.mark.asyncio
async def test_report_incident(safety_manager, mock_incident_data):
    """Test reporting a safety incident."""
    incident = await safety_manager.report_incident(**mock_incident_data)
    assert incident is not None
    assert incident.activity_id == mock_incident_data['activity_id']
    assert incident.incident_type == mock_incident_data['incident_type']
    assert incident.severity == mock_incident_data['severity']

@pytest.mark.asyncio
async def test_get_incident(safety_manager, mock_incident_data):
    """Test retrieving a safety incident."""
    incident = await safety_manager.get_incident(1)  # Assuming incident_id 1
    assert incident is not None
    assert isinstance(incident, SafetyIncident)

@pytest.mark.asyncio
async def test_get_activity_incidents(safety_manager, mock_incident_data):
    """Test retrieving incidents for an activity."""
    incidents = await safety_manager.get_activity_incidents(mock_incident_data['activity_id'])
    assert isinstance(incidents, list)
    assert all(isinstance(incident, SafetyIncident) for incident in incidents)

@pytest.mark.asyncio
async def test_create_alert(safety_manager, mock_alert_data):
    """Test creating a safety alert."""
    alert = await safety_manager.create_alert(**mock_alert_data)
    assert alert is not None
    assert alert.alert_type == mock_alert_data['alert_type']
    assert alert.severity == mock_alert_data['severity']
    assert alert.message == mock_alert_data['message']

@pytest.mark.asyncio
async def test_resolve_alert(safety_manager, mock_alert_data):
    """Test resolving a safety alert."""
    alert = await safety_manager.resolve_alert(1, "Issue resolved")  # Assuming alert_id 1
    assert alert is not None
    assert alert.resolved_at is not None
    assert alert.resolution_notes == "Issue resolved"

@pytest.mark.asyncio
async def test_get_active_alerts(safety_manager):
    """Test retrieving active alerts."""
    alerts = await safety_manager.get_active_alerts()
    assert isinstance(alerts, list)
    assert all(isinstance(alert, SafetyAlert) for alert in alerts)

@pytest.mark.asyncio
async def test_create_safety_protocol(safety_manager, mock_protocol_data):
    """Test creating a safety protocol."""
    protocol = await safety_manager.create_safety_protocol(**mock_protocol_data)
    assert protocol is not None
    assert protocol.name == mock_protocol_data['name']
    assert protocol.description == mock_protocol_data['description']
    assert protocol.steps == mock_protocol_data['steps']

@pytest.mark.asyncio
async def test_get_protocol(safety_manager, mock_protocol_data):
    """Test retrieving a safety protocol."""
    protocol = await safety_manager.get_protocol(1)  # Assuming protocol_id 1
    assert protocol is not None
    assert isinstance(protocol, SafetyProtocol)

@pytest.mark.asyncio
async def test_get_activity_protocols(safety_manager, mock_protocol_data):
    """Test retrieving protocols for an activity type."""
    protocols = await safety_manager.get_activity_protocols(mock_protocol_data['activity_type'])
    assert isinstance(protocols, list)
    assert all(isinstance(protocol, SafetyProtocol) for protocol in protocols)

@pytest.mark.asyncio
async def test_update_protocol_review(safety_manager):
    """Test updating protocol review dates."""
    protocol = await safety_manager.update_protocol_review(1)  # Assuming protocol_id 1
    assert protocol is not None
    assert protocol.last_reviewed is not None
    assert protocol.next_review is not None

@pytest.mark.asyncio
async def test_error_handling(safety_manager):
    """Test error handling in safety operations."""
    with pytest.raises(Exception):
        await safety_manager.create_risk_assessment(None, None, None, None)
    
    with pytest.raises(Exception):
        await safety_manager.report_incident(None, None, None, None, None, None)

@pytest.mark.asyncio
async def test_database_interaction(safety_manager, db_session):
    """Test database interaction patterns."""
    # Test session management
    assert safety_manager.db == db_session
    
    # Test commit is called after operations
    await safety_manager.create_risk_assessment(
        activity_id=1,
        risk_level=RiskLevel.MEDIUM,
        factors=['test'],
        mitigation_measures=['test']
    )
    db_session.commit.assert_called_once()
    
    # Test rollback on error
    db_session.commit.side_effect = Exception("Test error")
    with pytest.raises(Exception):
        await safety_manager.create_risk_assessment(
            activity_id=1,
            risk_level=RiskLevel.MEDIUM,
            factors=['test'],
            mitigation_measures=['test']
        )
    db_session.rollback.assert_called_once() 