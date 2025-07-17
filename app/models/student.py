"""Re-export of Student model for backward compatibility."""

from app.models.physical_education.student.student import (
    StudentHealthProfile,
    HealthMetricThreshold,
    StudentHealthFitnessGoal,
    StudentHealthGoalProgress,
    StudentHealthGoalRecommendation
)
# from app.models.physical_education.student.health_metric import HealthMetric, HealthMetricHistory
from app.models.physical_education.student.models import Student
from app.models.physical_education.pe_enums.pe_types import (
    MetricType,
    MeasurementUnit,
    HealthMetricLevel,
    HealthMetricStatus,
    HealthMetricTrigger,
    GoalType,
    GoalStatus
)

# Backward compatibility alias - now points to the main Student model
# Student = StudentHealth  # Commented out to avoid conflicts

__all__ = [
    'Student',
    'StudentHealthProfile',
    'HealthMetricThreshold',
    'StudentHealthFitnessGoal',
    'StudentHealthGoalProgress',
    'StudentHealthGoalRecommendation',
    # 'HealthMetric',
    # 'HealthMetricHistory',
    'MetricType',
    'MeasurementUnit',
    'HealthMetricLevel',
    'HealthMetricStatus',
    'HealthMetricTrigger',
    'GoalType',
    'GoalStatus'
] 