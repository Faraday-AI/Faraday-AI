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
] 