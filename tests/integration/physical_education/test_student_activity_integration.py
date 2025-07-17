"""Integration tests for student activity system.

This module tests the integration between student activities,
health monitoring, and safety systems.
"""

import pytest
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
        """Create student with activity and health data."""
        # Create student
        student = Student(
            name="John Doe",
            grade="6",
            age=12
        )
        db_session.add(student)
        
        # Create activity
        activity = Activity(
            name="Basketball Practice",
            activity_type="sport",
            duration=60,
            intensity_level="moderate"
        )
        db_session.add(activity)
        
        # Create health metrics
        health_metric = HealthMetric(
            student=student,
            metric_type="heart_rate",
            value=75.0,
            recorded_at=datetime.utcnow()
        )
        db_session.add(health_metric)
        
        # Create environmental condition
        condition = EnvironmentalCondition(
            location_id=1,
            temperature=25.0,
            humidity=60.0,
            condition_type="indoor"
        )
        db_session.add(condition)
        
        # Create risk assessment
        risk = RiskAssessment(
            activity=activity,
            risk_score=0.2,
            assessment_method="standard"
        )
        db_session.add(risk)
        
        db_session.commit()
        return student, activity

    def test_activity_participation_flow(self, db_session, managers, student_with_activity):
        """Test complete activity participation flow."""
        student, activity = student_with_activity
        
        # 1. Check student eligibility
        health_status = managers['health'].check_student_health_status(student.id)
        assert health_status['is_eligible'] is True
        
        # 2. Verify activity safety
        safety_check = managers['safety'].check_activity_safety(activity.id)
        assert safety_check['is_safe'] is True
        
        # 3. Start activity participation
        participation = managers['activity'].start_activity_participation(
            student_id=student.id,
            activity_id=activity.id
        )
        assert participation['status'] == 'started'
        
        # 4. Monitor health during activity
        health_reading = managers['health'].record_health_metric(
            student_id=student.id,
            metric_type="heart_rate",
            value=150.0  # Elevated during activity
        )
        assert health_reading['is_within_limits'] is True
        
        # 5. Track progress
        progress = managers['activity'].update_activity_progress(
            student_id=student.id,
            activity_id=activity.id,
            progress_data={
                'completion_percentage': 50,
                'performance_metrics': {'accuracy': 0.8}
            }
        )
        assert progress['is_on_track'] is True
        
        # 6. Complete activity
        completion = managers['activity'].complete_activity_participation(
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
        student_progress = managers['student'].update_student_progress(
            student_id=student.id,
            activity_id=activity.id,
            progress_data={
                'skill_improvement': 0.1,
                'fitness_gain': 0.05
            }
        )
        assert student_progress['progress_recorded'] is True

    def test_safety_monitoring_integration(self, db_session, managers, student_with_activity):
        """Test safety monitoring integration."""
        student, activity = student_with_activity
        
        # 1. Start activity with safety monitoring
        monitoring = managers['safety'].start_safety_monitoring(
            student_id=student.id,
            activity_id=activity.id
        )
        assert monitoring['monitoring_active'] is True
        
        # 2. Simulate environmental change
        env_update = managers['safety'].update_environmental_conditions(
            activity_id=activity.id,
            conditions={
                'temperature': 30.0,  # Temperature increase
                'humidity': 70.0      # Humidity increase
            }
        )
        assert env_update['requires_action'] is True
        
        # 3. Check safety alerts
        alerts = managers['safety'].check_safety_alerts(activity_id=activity.id)
        assert len(alerts['active_alerts']) > 0
        
        # 4. Get safety recommendations
        recommendations = managers['safety'].get_safety_recommendations(
            activity_id=activity.id,
            alert_ids=[alert['id'] for alert in alerts['active_alerts']]
        )
        assert len(recommendations['actions']) > 0

    def test_health_monitoring_integration(self, db_session, managers, student_with_activity):
        """Test health monitoring integration."""
        student, activity = student_with_activity
        
        # 1. Start health monitoring
        monitoring = managers['health'].start_health_monitoring(
            student_id=student.id,
            activity_id=activity.id
        )
        assert monitoring['monitoring_active'] is True
        
        # 2. Record multiple health metrics
        metrics = [
            ('heart_rate', 150.0),
            ('blood_pressure_systolic', 130.0),
            ('blood_pressure_diastolic', 80.0)
        ]
        
        for metric_type, value in metrics:
            reading = managers['health'].record_health_metric(
                student_id=student.id,
                metric_type=metric_type,
                value=value
            )
            assert reading['is_recorded'] is True
        
        # 3. Get health status report
        report = managers['health'].get_health_status_report(student_id=student.id)
        assert report['metrics_count'] == len(metrics)
        
        # 4. Check health alerts
        alerts = managers['health'].check_health_alerts(student_id=student.id)
        assert 'alerts' in alerts

    def test_progress_tracking_integration(self, db_session, managers, student_with_activity):
        """Test progress tracking integration."""
        student, activity = student_with_activity
        
        # 1. Create student goal
        goal = managers['student'].create_student_goal(
            student_id=student.id,
            goal_data={
                'type': 'fitness',
                'target': 'Improve endurance',
                'metrics': {'endurance_score': 8.0}
            }
        )
        assert goal['is_created'] is True
        
        # 2. Track activity contribution to goal
        contribution = managers['activity'].track_goal_contribution(
            student_id=student.id,
            activity_id=activity.id,
            goal_id=goal['goal_id'],
            performance_data={
                'endurance_score': 6.5,
                'effort_level': 'high'
            }
        )
        assert contribution['contributes_to_goal'] is True
        
        # 3. Update progress tracking
        progress = managers['student'].update_progress_tracking(
            student_id=student.id,
            tracking_data={
                'goal_id': goal['goal_id'],
                'activity_id': activity.id,
                'metrics': {'endurance_improvement': 0.2}
            }
        )
        assert progress['is_updated'] is True
        
        # 4. Generate progress report
        report = managers['student'].generate_progress_report(
            student_id=student.id,
            goal_id=goal['goal_id']
        )
        assert report['has_improvement'] is True

    def test_student_progress_integration(self):
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