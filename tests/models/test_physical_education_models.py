"""Tests for physical education models.

Following testing guidelines from TESTING.md, this module provides
comprehensive tests for all PE-related models.
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
    EnvironmentalCondition, ActivityEnvironmentalImpact, EnvironmentalAlert,
    InjuryRiskFactor, PreventionMeasure, PreventionAssessment, RiskAssessment,
    
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

@pytest.mark.models
class TestBaseModels:
    """Test suite for base model functionality."""

    def test_base_model_validation(self, db_session):
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

    def test_model_auditing(self, db_session):
        """Test model auditing functionality."""
        model = AuditableModel()
        model.add_audit_entry(
            action="create",
            user="test_user",
            details={"field": "value"}
        )
        assert len(model.audit_trail) == 1
        assert model.audit_trail[0]["action"] == "create"

    def test_model_metadata(self, db_session):
        """Test model metadata functionality."""
        model = MetadataModel()
        model.metadata = {"key": "value"}
        model.add_tag("test_tag")
        assert "test_tag" in model.tags
        assert model.metadata["key"] == "value"

    def test_model_versioning(self, db_session):
        """Test model versioning functionality."""
        model = MetadataModel()
        model.update_metadata("test_key", "test_value")
        assert model.version == 2
        assert len(model.version_history) == 1
        
        model.update_metadata("test_key", "new_value")
        assert model.version == 3
        assert len(model.version_history) == 2

    def test_validation_error_handling(self, db_session):
        """Test validation error handling."""
        model = ValidatableModel()
        with pytest.raises(ValueError):
            model.validate_not_empty("test_field", "")

    def test_audit_trail_history(self, db_session):
        """Test audit trail history tracking."""
        model = AuditableModel()
        actions = ["create", "update", "delete"]
        for action in actions:
            model.add_audit_entry(action, f"user_{action}", {"action": action})
        
        assert len(model.audit_trail) == 3
        assert [entry["action"] for entry in model.audit_trail] == actions

@pytest.mark.models
class TestProgress:
    def test_progress_creation(self):
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

    def test_progress_goal_creation(self):
        progress = Progress(
            student_id=1,
            tracking_period="2024-Q1",
            start_date=datetime.now(),
            progress_metrics={},
            baseline_data={},
            current_data={}
        )
        goal = ProgressGoal(
            progress_id=progress.id,
            goal_type="fitness",
            target_date=datetime.now(),
            target_metrics={}
        )
        assert goal.progress_id == progress.id
        assert goal.goal_type == "fitness"

    def test_progress_note_creation(self):
        progress = Progress(
            student_id=1,
            tracking_period="2024-Q1",
            start_date=datetime.now(),
            progress_metrics={},
            baseline_data={},
            current_data={}
        )
        note = ProgressNote(
            progress_id=progress.id,
            note_type="weekly",
            note_period="weekly",
            note_data={},
            performance_summary={}
        )
        assert note.progress_id == progress.id
        assert note.note_type == "weekly"

@pytest.mark.models
@pytest.mark.relationships
class TestGoalRelationships:
    """Test suite for goal relationships."""

    @pytest.fixture
    def sample_goal(self, db_session):
        """Create sample goal with milestone."""
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
        db_session.add(goal)
        db_session.commit()
        return goal

    def test_goal_milestone_relationship(self, sample_goal):
        """Test goal-milestone relationship."""
        assert len(sample_goal.milestones) == 1
        milestone = sample_goal.milestones[0]
        assert milestone.title == "Run 3k"

@pytest.mark.models
class TestEnvironmentalConditions:
    """Test suite for environmental conditions."""

    @pytest.fixture
    def sample_condition(self, db_session):
        """Create sample environmental condition."""
        condition = EnvironmentalCondition(
            location_id=1,
            condition_type="weather",
            temperature=25.0,
            humidity=60.0,
            wind_speed=10.0,
            weather_condition="sunny"
        )
        db_session.add(condition)
        db_session.commit()
        return condition

    def test_environmental_condition(self, sample_condition):
        """Test environmental condition model."""
        assert sample_condition.risk_level is None
        assert sample_condition.safety_concerns == []

@pytest.mark.models
@pytest.mark.relationships
class TestCurriculumRelationships:
    """Test suite for curriculum relationships."""

    @pytest.fixture
    def sample_curriculum(self, db_session):
        """Create sample curriculum with units."""
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
        db_session.add(curriculum)
        db_session.commit()
        return curriculum

    def test_curriculum_unit_relationship(self, sample_curriculum):
        """Test curriculum-unit relationship."""
        assert len(sample_curriculum.units) == 2
        sample_curriculum.units.remove(sample_curriculum.units[0])
        assert len(sample_curriculum.units) == 1

@pytest.mark.models
@pytest.mark.relationships
class TestCompetitionRelationships:
    """Test suite for competition relationships."""

    @pytest.fixture
    def sample_competition(self, db_session):
        """Create sample competition with events."""
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
        db_session.add(competition)
        db_session.commit()
        return competition

    def test_competition_event_relationship(self, sample_competition):
        """Test competition-event relationship."""
        assert len(sample_competition.events) == 1
        event = sample_competition.events[0]
        assert event.name == "100m Sprint"

@pytest.mark.models
@pytest.mark.relationships
class TestStudentRelationships:
    """Test suite for student relationships."""

    @pytest.fixture
    def sample_student_data(self, db_session):
        """Create comprehensive student test data."""
        student = Student(
            name="John Doe",
            grade="6",
            age=12
        )
        
        # Add health metrics
        health = HealthMetric(
            student=student,
            metric_type="heart_rate",
            value=75.0,
            recorded_at=datetime.utcnow()
        )
        
        # Add goals
        goal = Goal(
            student=student,
            title="Fitness Goal",
            description="Improve overall fitness",
            status="active"
        )
        
        # Add progress tracking
        tracking = ProgressTracking(
            student=student,
            tracking_period="weekly",
            progress_metrics={"fitness": 80}
        )
        
        db_session.add(student)
        db_session.commit()
        return student

    def test_student_health_metrics(self, sample_student_data):
        """Test student-health metrics relationship."""
        assert len(sample_student_data.health_metrics) == 1
        metric = sample_student_data.health_metrics[0]
        assert metric.metric_type == "heart_rate"
        assert metric.value == 75.0

    def test_student_goals(self, sample_student_data):
        """Test student-goals relationship."""
        assert len(sample_student_data.goals) == 1
        goal = sample_student_data.goals[0]
        assert goal.title == "Fitness Goal"

    def test_student_progress(self, sample_student_data):
        """Test student-progress relationship."""
        assert len(sample_student_data.progress_tracking) == 1
        tracking = sample_student_data.progress_tracking[0]
        assert tracking.tracking_period == "weekly"

@pytest.mark.models
class TestHealthMetrics:
    """Test suite for health metrics."""

    @pytest.fixture
    def sample_health_data(self, db_session):
        """Create sample health metric data."""
        metric = HealthMetric(
            student_id=1,
            metric_type="blood_pressure",
            value=120.0,
            unit="mmHg",
            recorded_at=datetime.utcnow()
        )
        db_session.add(metric)
        db_session.commit()
        return metric

    def test_health_metric_validation(self, sample_health_data):
        """Test health metric validation."""
        assert sample_health_data.validate_health_metrics({
            "blood_pressure_systolic": 120,
            "heart_rate": 75
        })
        
        assert not sample_health_data.validate_health_metrics({
            "blood_pressure_systolic": 250,  # Invalid value
            "heart_rate": 75
        })

@pytest.mark.models
@pytest.mark.relationships
class TestActivityRelationships:
    """Test suite for activity relationships."""

    @pytest.fixture
    def sample_activity_data(self, db_session):
        """Create comprehensive activity test data."""
        activity = Activity(
            name="Basketball Training",
            activity_type="sport",
            duration=60,
            intensity_level="moderate"
        )
        
        # Add environmental impact
        impact = ActivityEnvironmentalImpact(
            activity=activity,
            impact_level="low",
            description="Indoor activity"
        )
        
        # Add risk assessment
        risk = RiskAssessment(
            activity=activity,
            risk_score=0.2,
            assessment_method="standard"
        )
        
        db_session.add(activity)
        db_session.commit()
        return activity

    def test_activity_environmental_impact(self, sample_activity_data):
        """Test activity-environmental impact relationship."""
        assert len(sample_activity_data.environmental_impacts) == 1
        impact = sample_activity_data.environmental_impacts[0]
        assert impact.impact_level == "low"

    def test_activity_risk_assessment(self, sample_activity_data):
        """Test activity-risk assessment relationship."""
        assert len(sample_activity_data.risk_assessments) == 1
        risk = sample_activity_data.risk_assessments[0]
        assert risk.risk_score == 0.2

@pytest.mark.models
class TestCurriculumValidation:
    """Test suite for curriculum validation."""

    def test_curriculum_grade_validation(self, db_session):
        """Test curriculum grade level validation."""
        with pytest.raises(ValueError):
            Curriculum(
                name="Invalid Grade",
                grade_level="invalid",
                academic_year="2024",
                learning_standards={},
                learning_objectives={},
                core_competencies={}
            )

    def test_curriculum_standards_validation(self, db_session):
        """Test curriculum standards validation."""
        curriculum = Curriculum(
            name="Test Curriculum",
            grade_level="6",
            academic_year="2024",
            learning_standards={"invalid": None},
            learning_objectives={},
            core_competencies={}
        )
        assert not curriculum.validate({
            "learning_standards": {
                "validator": lambda x: all(isinstance(v, str) for v in x.values()),
                "message": "Standards must be strings"
            }
        })

@pytest.mark.models
class TestCompetitionValidation:
    """Test suite for competition validation."""

    def test_competition_date_validation(self, db_session):
        """Test competition date validation."""
        with pytest.raises(ValueError):
            Competition(
                name="Invalid Dates",
                competition_type="meet",
                sport_type="athletics",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() - timedelta(days=1)  # End before start
            )

    def test_competition_participant_validation(self, db_session):
        """Test competition participant validation."""
        competition = Competition(
            name="Test Competition",
            competition_type="meet",
            sport_type="athletics",
            start_date=datetime.utcnow(),
            max_participants=2
        )
        
        # Add participants
        for i in range(3):  # Exceeds max
            participant = CompetitionParticipant(
                competition=competition,
                student_id=i,
                status="registered"
            )
        
        assert not competition.validate({
            "participants": {
                "validator": lambda x: len(x) <= competition.max_participants,
                "message": "Exceeded maximum participants"
            }
        }) 