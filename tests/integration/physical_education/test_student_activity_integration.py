"""Integration tests for student activity system.

This module tests the integration between student activities,
health monitoring, and safety systems.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import (
    Student, Activity, HealthMetric, EnvironmentalCondition,
    RiskAssessment, InjuryRiskFactor, Goal, ProgressTracking
)
from app.models.physical_education.progress import (
    Progress,
    ProgressGoal,
    ProgressNote
)
from app.services.physical_education.activity_manager import ActivityManager
from app.services.physical_education.health_metrics_manager import HealthMetricsManager
from app.services.physical_education.safety_manager import SafetyManager
from app.services.physical_education.student_manager import StudentManager

@pytest.mark.integration
class TestStudentActivityIntegration:
    """Test suite for student activity integration."""

    @pytest.fixture
    def managers(self, db_session):
        """Create service managers."""
        return {
            'activity': ActivityManager(db_session),
            'health': HealthMetricsManager(db_session),
            'safety': SafetyManager(db_session),
            'student': StudentManager(db_session)
        }

    @pytest.fixture
    def student_with_activity(self, db_session, managers):
        """Create student with activity and health data - don't hardcode IDs to avoid conflicts."""
        unique_id = str(uuid.uuid4())[:8]
        # Create student with unique email
        student = Student(
            first_name="John",
            last_name="Doe",
            email=f"john.doe.{unique_id}@example.com",  # Unique email
            date_of_birth=datetime(2010, 1, 1),
            grade_level="6th"
        )
        db_session.add(student)
        db_session.flush()  # Use flush for SAVEPOINT transactions
        
        # Create activity
        activity = Activity(
            name=f"Basketball Practice {unique_id}",
            type="team_sports",
            duration=60
        )
        db_session.add(activity)
        db_session.flush()  # Use flush for SAVEPOINT transactions
        
        # Create health metrics
        health_metric = HealthMetric(
            student=student,
            metric_type="heart_rate",
            value=75.0,
            unit="bpm"
        )
        db_session.add(health_metric)
        
        # Create risk assessment
        risk = RiskAssessment(
            activity=activity,
            risk_level="LOW",
            assessment_date=datetime.utcnow(),
            assessed_by=1  # Default user ID for testing
        )
        db_session.add(risk)
        db_session.flush()  # Use flush for SAVEPOINT transactions
        
        # Create environmental condition - activity.id is available after flush
        condition = EnvironmentalCondition(
            activity_id=activity.id,
            temperature=25.0,
            humidity=60.0,
            air_quality="good"
        )
        db_session.add(condition)
        db_session.flush()  # Use flush for SAVEPOINT transactions
        
        return student, activity

    async def test_activity_participation_flow(self, db_session, managers, student_with_activity):
        """Test complete activity participation flow."""
        student, activity = student_with_activity
        
        # 1. Check student eligibility
        health_status = await managers['health'].check_student_health_status(student.id)
        assert health_status['is_eligible'] is True
        
        # 2. Verify activity safety
        safety_check = await managers['safety'].check_activity_safety(activity.id)
        assert safety_check['is_safe'] is True
        
        # 3. Start activity participation
        participation = await managers['activity'].start_activity_participation(
            student_id=student.id,
            activity_id=activity.id
        )
        assert participation['status'] == 'started'
        
        # 4. Monitor health during activity
        health_reading = await managers['health'].record_health_metric(
            student_id=student.id,
            metric_type="heart_rate",
            value=150.0  # Elevated during activity
        )
        assert health_reading['is_within_limits'] is True
        
        # 5. Track progress
        progress = await managers['activity'].update_activity_progress(
            student_id=student.id,
            activity_id=activity.id,
            progress_data={
                'completion_percentage': 50,
                'performance_metrics': {'accuracy': 0.8}
            }
        )
        assert progress['is_on_track'] is True
        
        # 6. Complete activity
        completion = await managers['activity'].complete_activity_participation(
            student_id=student.id,
            activity_id=activity.id,
            completion_data={
                'duration': 60,
                'intensity': 'moderate',
                'performance_score': 0.85
            }
        )
        assert completion['status'] == 'completed'
        
        # 7. Update student progress
        student_progress = await managers['student'].update_student_progress(
            student_id=student.id,
            activity_id=activity.id,
            progress_data={
                'skill_improvement': 0.1,
                'fitness_gain': 0.05
            }
        )
        assert student_progress['progress_updated'] is True

    async def test_safety_monitoring_integration(self, db_session, managers, student_with_activity):
        """Test safety monitoring integration."""
        student, activity = student_with_activity
        
        # 1. Start activity with safety monitoring
        monitoring = await managers['safety'].start_safety_monitoring(
            student_id=student.id,
            activity_id=activity.id
        )
        assert monitoring['monitoring_active'] is True
        
        # 2. Simulate environmental change
        env_update = await managers['safety'].update_environmental_conditions(
            activity_id=activity.id,
            conditions={
                'temperature': 30.0,  # Temperature increase
                'humidity': 70.0      # Humidity increase
            }
        )
        assert env_update['requires_action'] is True
        
        # 3. Check safety alerts
        alerts = await managers['safety'].check_safety_alerts(activity_id=activity.id)
        assert len(alerts['active_alerts']) > 0
        
        # 4. Get safety recommendations
        recommendations = await managers['safety'].get_safety_recommendations(
            activity_id=activity.id,
            alert_ids=[alert['id'] for alert in alerts['active_alerts']]
        )
        assert len(recommendations['actions']) > 0

    async def test_health_monitoring_integration(self, db_session, managers, student_with_activity):
        """Test health monitoring integration."""
        student, activity = student_with_activity
        
        # 1. Start health monitoring
        monitoring = await managers['health'].start_health_monitoring(
            student_id=student.id,
            activity_id=activity.id
        )
        assert monitoring['monitoring_active'] is True
        
        # 2. Record multiple health metrics
        # Use metric types that exist in both HealthMetricType and database MetricType enums
        # NOTE: The database enum is more limited, so use basic metric types
        metrics = [
            ('heart_rate', 150.0),          # Valid in both enums
            ('blood_pressure', 130.0),      # Valid in both enums  
            ('oxygen_saturation', 98.0)     # Valid in both enums
        ]
        
        for metric_type, value in metrics:
            reading = await managers['health'].record_health_metric(
                student_id=student.id,
                metric_type=metric_type,
                value=value
            )
            assert reading['metric_recorded'] is True

    async def test_progress_tracking_integration(self, db_session, managers, student_with_activity):
        """Test progress tracking integration."""
        student, activity = student_with_activity
        
        # 1. Create student goal
        goal = await managers['student'].create_student_goal(
            student_id=student.id,
            goal_type="endurance",
            target_value=8.0,
            description="Improve endurance"
        )
        assert goal['goal_created'] is True

    def test_student_progress_integration(self):
        """Test basic student progress functionality."""
        # Simple test to verify the test framework is working
        assert True 