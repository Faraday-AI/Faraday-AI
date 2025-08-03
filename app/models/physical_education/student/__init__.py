"""
Student Models

This module exports student-related models for physical education.
"""

from .models import (
    Student,
    StudentAttendance,
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentAttendanceCreate,
    StudentAttendanceUpdate,
    StudentAttendanceResponse
)

from .student import (
    StudentHealthProfile,
    HealthRecord,
    FitnessAssessment,
    StudentHealthSkillAssessment,
    ActivityPreference,
    ActivityPerformance,
    HealthMetricThreshold,
    StudentHealthFitnessGoal,
    StudentHealthGoalProgress,
    StudentHealthGoalRecommendation,
    StudentCreate as StudentHealthCreate,
    StudentUpdate as StudentHealthUpdate,
    StudentResponse as StudentHealthResponse
)

from .health_metric import (
    HealthMetric,
    HealthMetricHistory
)

from .health import (
    HealthRecord as StudentHealthRecord,
    MedicalCondition,
    EmergencyContact,
    HealthRecordCreate,
    HealthRecordUpdate,
    HealthRecordResponse,
    HealthMetric as StudentHealthMetric,
    HealthMetricThreshold as StudentHealthMetricThreshold,
    FitnessGoal,
    FitnessGoalProgress,
    StudentHealthGoalProgress as HealthGoalProgress,
    GoalRecommendation,
    StudentHealth
)

__all__ = [
    # Main Student models
    'Student',
    'StudentAttendance',
    'StudentCreate',
    'StudentUpdate',
    'StudentResponse',
    'StudentAttendanceCreate',
    'StudentAttendanceUpdate',
    'StudentAttendanceResponse',
    
    # StudentHealthProfile models (renamed from StudentHealth)
    'StudentHealthProfile',
    'HealthRecord',
    'FitnessAssessment',
    'StudentHealthSkillAssessment',
    'ActivityPreference',
    'ActivityPerformance',
    'HealthMetricThreshold',
    'StudentHealthFitnessGoal',
    'StudentHealthGoalProgress',
    'StudentHealthGoalRecommendation',
    'StudentHealthCreate',
    'StudentHealthUpdate',
    'StudentHealthResponse',
    
    # Health metric models
    'HealthMetric',
    'HealthMetricHistory',
    
    # Health models from health.py
    'StudentHealthRecord',
    'MedicalCondition',
    'EmergencyContact',
    'HealthRecordCreate',
    'HealthRecordUpdate',
    'HealthRecordResponse',
    'StudentHealthMetric',
    'StudentHealthMetricThreshold',
    'FitnessGoal',
    'FitnessGoalProgress',
    'HealthGoalProgress',
    'GoalRecommendation',
    'StudentHealth',
] 