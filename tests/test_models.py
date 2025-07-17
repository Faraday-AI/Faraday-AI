"""
Tests for the physical education models.

This module contains comprehensive tests for all PE-related models,
including validation, relationships, and data integrity.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import (
    # Base models
    BaseModel, MetadataModel, AuditableModel, ValidatableModel,
    
    # Core models
    Student, Activity, Class, Assessment,
    Exercise, HealthMetric, Equipment,
    
    # Tracking models
    ProgressTracking, ProgressMilestone, ProgressReport,
    Goal, GoalMilestone, GoalActivity,
    MovementAnalysis, MovementPattern, MovementFeedback,
    
    # Safety models
    Safety, SafetyIncident, RiskAssessment, SafetyAlert,
    SafetyProtocol, SafetyCheck, EnvironmentalCheck, EquipmentCheck,
    IncidentSeverity, IncidentType, RiskLevel, AlertType, CheckType,
    
    # Curriculum models
    Curriculum, CurriculumUnit, CurriculumStandard,
    
    # Competition models
    Competition, CompetitionEvent, CompetitionParticipant, EventParticipant
)

from app.models.physical_education.progress import (
    Progress,
    ProgressGoal,
    ProgressNote
)

@pytest.fixture
def db_session():
    """Create a test database session."""
    # This will be implemented based on your database configuration
    pass

def test_base_model_validation():
    """Test base model validation functionality."""
    model = ValidatableModel()
    validation_rules = {
        'test_field': {
            'validator': lambda x: isinstance(x, str) and len(x) > 0,
            'message': 'Field must be non-empty string'
        }
    }
    assert not model.validate(validation_rules)
    assert model.validation_errors is not None

def test_progress_tracking():
    """Test progress tracking model functionality."""
    tracking = ProgressTracking(
        student_id=1,
        tracking_period="weekly",
        start_date=datetime.utcnow(),
        progress_metrics={"fitness": 80},
        baseline_data={"initial_fitness": 70},
        current_data={"current_fitness": 85}
    )
    assert tracking.improvement_rate is None
    assert tracking.is_on_track is True

def test_goal_relationships():
    """Test goal model relationships."""
    goal = Goal(
        student_id=1,
        goal_type="fitness",
        title="Improve Endurance",
        description="Run 5k under 30 minutes",
        target_date=datetime.utcnow() + timedelta(days=30),
        status="active",
        priority="high",
        target_metrics={"distance": "5k", "time": "30min"}
    )
    milestone = GoalMilestone(
        goal=goal,
        title="Run 3k",
        target_date=datetime.utcnow() + timedelta(days=15),
        status="pending",
        metrics={"distance": "3k"}
    )
    assert milestone in goal.milestones

def test_environmental_conditions():
    """Test environmental conditions model."""
    condition = EnvironmentalCondition(
        location_id=1,
        condition_type="weather",
        temperature=25.0,
        humidity=60.0,
        wind_speed=10.0,
        weather_condition="sunny"
    )
    assert condition.risk_level is None
    assert condition.safety_concerns == []

def test_injury_prevention():
    """Test injury prevention model."""
    risk_factor = InjuryRiskFactor(
        name="Overexertion",
        description="Excessive physical effort",
        risk_level="high",
        category="physical",
        monitoring_frequency="daily"
    )
    measure = PreventionMeasure(
        risk_factor=risk_factor,
        name="Proper Warm-up",
        description="Complete warm-up routine",
        implementation_steps=["stretch", "light cardio"],
        status="active"
    )
    assert measure in risk_factor.prevention_measures

def test_curriculum():
    """Test curriculum model."""
    curriculum = Curriculum(
        name="PE Grade 6",
        description="Physical Education for 6th Grade",
        grade_level="6",
        academic_year="2024",
        learning_standards={"standard1": "Basic movement"},
        learning_objectives={"objective1": "Master basic movements"},
        core_competencies={"competency1": "Movement control"}
    )
    unit = CurriculumUnit(
        curriculum=curriculum,
        name="Basic Movements",
        description="Fundamental movement skills",
        sequence_number=1,
        duration_weeks=4,
        learning_objectives={"objective1": "Master running"},
        key_concepts={"concept1": "Balance"},
        skill_focus={"focus1": "Coordination"}
    )
    assert unit in curriculum.units

def test_competition():
    """Test competition model."""
    competition = Competition(
        name="School Athletics Meet",
        description="Annual athletics competition",
        competition_type="meet",
        sport_type="athletics",
        start_date=datetime.utcnow(),
        location="School Ground",
        organizer="PE Department"
    )
    event = CompetitionEvent(
        competition=competition,
        name="100m Sprint",
        event_type="track",
        start_time=datetime.utcnow(),
        location="Track",
        status="scheduled"
    )
    assert event in competition.events

def test_model_auditing():
    """Test model auditing functionality."""
    model = AuditableModel()
    model.add_audit_entry(
        action="create",
        user="test_user",
        details={"field": "value"}
    )
    assert len(model.audit_trail) == 1
    assert model.audit_trail[0]["action"] == "create"

def test_model_metadata():
    """Test model metadata functionality."""
    model = MetadataModel()
    model.metadata = {"key": "value"}
    model.add_tag("test_tag")
    assert "test_tag" in model.tags
    assert model.metadata["key"] == "value"

def test_validation_rules():
    """Test PE-specific validation rules."""
    model = ValidatableModel()
    rules = model.common_validation_rules()
    
    # Test heart rate validation
    assert rules["heart_rate"]["validator"](60)
    assert not rules["heart_rate"]["validator"](250)
    
    # Test blood pressure validation
    assert rules["blood_pressure_systolic"]["validator"](120)
    assert not rules["blood_pressure_systolic"]["validator"](250)

def test_relationship_cascades():
    """Test relationship cascade behavior."""
    curriculum = Curriculum(
        name="Test Curriculum",
        description="Test Description",
        grade_level="7",
        academic_year="2024",
        learning_standards={},
        learning_objectives={},
        core_competencies={}
    )
    unit1 = CurriculumUnit(
        curriculum=curriculum,
        name="Unit 1",
        description="Test Unit",
        sequence_number=1,
        duration_weeks=4,
        learning_objectives={},
        key_concepts={},
        skill_focus={}
    )
    unit2 = CurriculumUnit(
        curriculum=curriculum,
        name="Unit 2",
        description="Test Unit",
        sequence_number=2,
        duration_weeks=4,
        learning_objectives={},
        key_concepts={},
        skill_focus={}
    )
    
    # Test cascade delete
    assert len(curriculum.units) == 2
    curriculum.units.remove(unit1)
    assert len(curriculum.units) == 1

def test_model_versioning():
    """Test model versioning functionality."""
    model = MetadataModel()
    model.update_metadata("test_key", "test_value")
    assert model.version == 2
    assert len(model.version_history) == 1
    
    model.update_metadata("test_key", "new_value")
    assert model.version == 3
    assert len(model.version_history) == 2

def test_safety_models():
    """Test safety model relationships and inheritance."""
    # Create a safety instance
    safety = Safety(
        activity_id=1,
        risk_level=RiskLevel.MEDIUM,
        safety_notes="Test safety notes",
        safety_metadata={"key": "value"}
    )
    
    # Create a safety incident
    incident = SafetyIncident(
        activity_id=1,
        student_id=1,
        incident_type=IncidentType.INJURY,
        severity=IncidentSeverity.MEDIUM,
        description="Test incident",
        response_taken="Test response",
        reported_by=1
    )
    safety.incidents.append(incident)
    
    # Create a safety protocol
    protocol = SafetyProtocol(
        name="Test Protocol",
        description="Test protocol description",
        protocol_type="emergency",
        steps=["step1", "step2"],
        created_by=1
    )
    safety.protocols.append(protocol)
    
    # Create a safety check
    check = SafetyCheck(
        check_type=CheckType.EQUIPMENT,
        activity_id=1,
        performed_by=1,
        status="passed",
        notes="Test check"
    )
    safety.checks.append(check)
    
    # Create environmental check
    env_check = EnvironmentalCheck(
        safety_check=check,
        temperature=25,
        humidity=60,
        lighting_level="adequate",
        ventilation_status="good",
        surface_condition="dry"
    )
    
    # Create equipment check
    equip_check = EquipmentCheck(
        safety_check=check,
        equipment_id=1,
        condition="good",
        maintenance_needed=False
    )
    
    # Test relationships
    assert incident in safety.incidents
    assert protocol in safety.protocols
    assert check in safety.checks
    assert env_check in check.environmental_details
    assert equip_check in check.equipment_details
    
    # Test inheritance
    assert isinstance(safety, BaseModel)
    assert isinstance(safety, TimestampedMixin)
    assert isinstance(safety, StatusMixin)
    
    assert isinstance(incident, BaseModel)
    assert isinstance(incident, TimestampedMixin)
    
    assert isinstance(protocol, BaseModel)
    assert isinstance(protocol, NamedMixin)
    assert isinstance(protocol, TimestampedMixin)
    
    assert isinstance(check, BaseModel)
    assert isinstance(check, TimestampedMixin)
    
    assert isinstance(env_check, BaseModel)
    assert isinstance(env_check, TimestampedMixin)
    
    assert isinstance(equip_check, BaseModel)
    assert isinstance(equip_check, TimestampedMixin)

def test_safety_risk_assessment():
    """Test risk assessment model."""
    assessment = RiskAssessment(
        activity_id=1,
        risk_level=RiskLevel.HIGH,
        factors=["factor1", "factor2"],
        mitigation_measures=["measure1", "measure2"],
        assessed_by=1
    )
    
    assert isinstance(assessment, BaseModel)
    assert isinstance(assessment, TimestampedMixin)
    assert assessment.risk_level == RiskLevel.HIGH

def test_safety_alert():
    """Test safety alert model."""
    alert = SafetyAlert(
        alert_type=AlertType.EMERGENCY,
        severity=IncidentSeverity.HIGH,
        message="Test alert",
        recipients=[1, 2],
        created_by=1
    )
    
    assert isinstance(alert, BaseModel)
    assert isinstance(alert, TimestampedMixin)
    assert alert.alert_type == AlertType.EMERGENCY
    assert alert.severity == IncidentSeverity.HIGH

def test_progress_models():
    progress = Progress(
        student_id=1,
        tracking_period="2024-Q1",
        start_date=datetime.now(),
        progress_metrics={},
        baseline_data={},
        current_data={}
    )
    assert progress.student_id == 1
    assert progress.tracking_period == "2024-Q1" 