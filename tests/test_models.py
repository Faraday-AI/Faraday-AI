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

from app.models import (
    Student, HealthMetric, Goal, CurriculumUnit, PreventionMeasure, 
    PreventionAssessment, User, Role, Permission, UserProfile, 
    UserOrganization, UserSession, ProgressTracking, ProgressMilestone, 
    ProgressReport, Lesson, Progress, ProgressGoal, PhysicalEducationProgressNote,
    Curriculum, Competition, CompetitionEvent, AuditableModel, MetadataModel, 
    ValidatableModel, EnvironmentalCondition, InjuryRiskFactor, SafetyIncident,
    RiskAssessment, SafetyAlert, SafetyProtocol, SafetyCheck, EnvironmentalCheck,
    EquipmentCheck, IncidentType, IncidentSeverity, EquipmentStatus, RiskLevel,
    AlertType, CheckType, Activity, PhysicalEducationClass, ClassStudent,
    Routine, RoutineActivity, RoutinePerformance, GoalMilestone, GoalActivity,
    HealthFitnessGoalProgress, Class, Safety, EventParticipant
)

@pytest.fixture
def db_session():
    """Create a test database session."""
    # This will be implemented based on your database configuration
    pass

def test_base_model_validation():
    """Test base model validation."""
    model = ValidatableModel()
    model.test_field = ""  # Set an empty field to test validation failure
    
    validation_rules = {
        'test_field': {
            'message': 'Field must be non-empty string',
            'validator': lambda x: x and len(x.strip()) > 0
        }
    }
    
    # Validation should fail because test_field is empty
    assert not model.validate(validation_rules)
    assert len(model.validation_errors) > 0
    assert 'Field must be non-empty string' in model.validation_errors

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
        name="Improve Endurance",  # Changed from title to name
        description="Run 5k under 30 minutes",
        target_date=datetime.utcnow() + timedelta(days=30),
        status="active",
        priority="high",
        target_metrics={"distance": "5k", "time": "30min"}
    )
    milestone = GoalMilestone(
        goal=goal,
        name="Run 3k",  # Changed from title to name
        target_date=datetime.utcnow() + timedelta(days=15),
        status="pending",
        metrics={"distance": "3k"}
    )
    assert milestone in goal.milestones

def test_environmental_conditions():
    """Test environmental condition model."""
    condition = EnvironmentalCondition(
        activity_id=1,  # Changed from location_id to activity_id
        temperature=25.0,
        humidity=60.0,
        air_quality="good",
        wind_speed=10.0,  # Added wind_speed field
        precipitation="none"  # Added precipitation field
    )
    assert condition.temperature == 25.0
    assert condition.humidity == 60.0
    assert condition.air_quality == "good"
    assert condition.wind_speed == 10.0

def test_injury_prevention():
    """Test injury prevention models."""
    risk_factor = InjuryRiskFactor(
        name="Overuse Injury",  # Changed from risk_level
        description="Risk of overuse injuries from repetitive activities",
        risk_level="high",  # This is the correct field name
        factor_metadata={"category": "musculoskeletal"}
    )
    
    # PreventionMeasure doesn't take risk_factor as a parameter
    # It's linked through PreventionAssessment
    measure = PreventionMeasure(
        name="Proper Warm-up",  # Changed from name
        description="Complete warm-up routine",
        effectiveness="high",  # Changed from status
        measure_metadata={"implementation_steps": ["stretch", "light cardio"]}
    )
    
    # Create an assessment to link them
    assessment = PreventionAssessment(
        activity_id=1,
        risk_factor_id=risk_factor.id if hasattr(risk_factor, 'id') else 1,
        measure_id=measure.id if hasattr(measure, 'id') else 1,
        assessment_date=datetime.now(),
        effectiveness="high",
        assessment_notes="Effective prevention measure"
    )
    
    assert risk_factor.name == "Overuse Injury"
    assert measure.name == "Proper Warm-up"
    assert assessment.effectiveness == "high"

def test_curriculum():
    """Test curriculum model."""
    curriculum = Curriculum(
        name="PE Grade 6",
        description="Physical Education for 6th Grade",
        grade_level="6",
        academic_year="2024"
    )
    unit = CurriculumUnit(
        curriculum=curriculum,
        name="Basic Movements",
        description="Fundamental movement skills",
        sequence=1,  # Changed from sequence_number to sequence
        duration=4,  # Changed from duration_weeks to duration
        unit_metadata={  # Changed from individual fields to unit_metadata
            "learning_objectives": {"objective1": "Master running"},
            "key_concepts": {"concept1": "Balance"},
            "skill_focus": {"focus1": "Coordination"}
        }
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
        academic_year="2024"
    )
    unit1 = CurriculumUnit(
        curriculum=curriculum,
        name="Unit 1",
        description="Test Unit",
        sequence=1,  # Changed from sequence_number to sequence
        duration=4,  # Changed from duration_weeks to duration
        unit_metadata={}  # Changed to unit_metadata
    )
    unit2 = CurriculumUnit(
        curriculum=curriculum,
        name="Unit 2",
        description="Test Unit",
        sequence=2,  # Changed from sequence_number to sequence
        duration=4,  # Changed from duration_weeks to duration
        unit_metadata={}  # Changed to unit_metadata
    )
    assert len(curriculum.units) == 2
    assert unit1 in curriculum.units
    assert unit2 in curriculum.units

def test_model_versioning():
    """Test model versioning functionality."""
    model = MetadataModel()
    # Version starts at 1 (initial version)
    # First update increments to 2 (version after first change)
    model.update_metadata("key1", "value1")
    assert model.version == 2  # Version increments after first update
    
    # Second update increments to 3 (version after second change)
    model.update_metadata("key1", "value2")
    assert model.version == 3  # Version increments after second update
    
    # Version history only tracks changes to existing keys
    # First update creates the key, second update changes it
    assert len(model.version_history) == 1  # Only the second update is tracked
    assert model.version_history[0]["old_value"] == "value1"
    assert model.version_history[0]["new_value"] == "value2"
    # The version stored in history is the version BEFORE incrementing
    # So for the second update: we record version=2, then increment to 3
    assert model.version_history[0]["version"] == 2  # Version before incrementing to 3

def test_safety_models():
    """Test safety model relationships."""
    safety = Safety(
        name="Test Safety",
        description="Test safety system",
        created_by=1
    )
    
    # Create a safety incident - using correct field names
    incident = SafetyIncident(
        incident_type=IncidentType.INJURY,
        severity=IncidentSeverity.MEDIUM,
        description="Test incident",
        location="Gym",
        teacher_id=1,  # Changed from reported_by to teacher_id
        incident_date=datetime.now()  # Added required field
    )
    safety.incidents.append(incident)
    
    # Create a safety protocol
    protocol = SafetyProtocol(
        name="Test Protocol",
        description="Test safety protocol",
        category="General",  # Added required field
        requirements="Test requirements",  # Added required field
        procedures="Test procedures",  # Added required field
        created_by=1
    )
    safety.protocols.append(protocol)
    
    # Create a safety check - using correct field names
    check = SafetyCheck(
        check_type=CheckType.EQUIPMENT,
        activity_id=1,
        performed_by=1,
        checked_by=1,  # Added required field
        check_date=datetime.now(),  # Changed from status to check_date
        status="passed",
        notes="Test check"
    )
    safety.checks.append(check)
    
    # Create environmental check - using correct field names
    env_check = EnvironmentalCheck(
        class_id=1,  # Changed from safety_check to class_id
        check_date=datetime.now(),  # Added required field
        checked_by=1,  # Added required field
        temperature=25,
        humidity=60,
        lighting_conditions="adequate",  # Changed from lighting_level
        surface_condition="dry"
    )
    
    # Create equipment check - using correct field names
    equip_check = EquipmentCheck(
        class_id=1,  # Changed from safety_check to class_id
        equipment_id=1,
        check_date=datetime.now(),  # Added required field
        maintenance_status=True,  # Changed from condition
        damage_status=False,  # Added required field
        age_status=True  # Added required field
    )
    
    # Test relationships
    assert incident in safety.incidents
    assert protocol in safety.protocols
    assert check in safety.checks
    
    # Test inheritance
    assert isinstance(safety, Safety)
    assert isinstance(incident, SafetyIncident)
    assert isinstance(protocol, SafetyProtocol)
    assert isinstance(check, SafetyCheck)
    assert isinstance(env_check, EnvironmentalCheck)
    assert isinstance(equip_check, EquipmentCheck)

def test_safety_risk_assessment():
    """Test risk assessment model."""
    assessment = RiskAssessment(
        activity_id=1,
        risk_level=RiskLevel.HIGH,
        environmental_risks=["factor1", "factor2"],  # Changed from risk_factors
        mitigation_strategies=["measure1", "measure2"],  # Changed from mitigation_measures
        assessed_by=1,
        assessment_date=datetime.now()  # Added required field
    )
    
    assert isinstance(assessment, RiskAssessment)
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
    
    assert isinstance(alert, SafetyAlert)
    assert alert.alert_type == AlertType.EMERGENCY
    assert alert.severity == IncidentSeverity.HIGH

def test_progress_models():
    """Test progress models."""
    progress = ProgressTracking(  # Changed from Progress to ProgressTracking
        student_id=1,
        tracking_period="2024-Q1",
        start_date=datetime.now(),
        progress_metrics={},
        baseline_data={},
        current_data={}
    )
    assert progress.student_id == 1
    assert progress.tracking_period == "2024-Q1" 