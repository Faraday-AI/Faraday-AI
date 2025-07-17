"""
Activity Adaptation Models

This module exports all activity adaptation related models.
"""

from app.models.activity_adaptation.activity.activity import (
    AdaptedActivityCategory,
    ActivityCategoryAssociation,
    ActivityPlan,
    ActivityPlanActivity
)
from app.models.activity_adaptation.activity.activity_log import ActivityLog
from app.models.activity_adaptation.activity.activity_adaptation import ActivityAdaptation

from app.models.activity_adaptation.student.activity_student import (
    StudentActivityPerformance,
    StudentActivityPreference,
    ActivityProgression,
    ActivityAdaptation as StudentActivityAdaptation,
    AdaptationHistory
)

from app.models.activity_adaptation.exercise import AdaptedExercise, AdaptedWorkout, AdaptedWorkoutExercise

from app.models.activity_adaptation.routine import (
    AdaptedRoutine,
    AdaptedRoutineActivity,
    AdaptedRoutinePerformance
)

__all__ = [
    # Activity models
    'ActivityLog',
    'ActivityAdaptation',
    
    # Category models
    'AdaptedActivityCategory',
    'ActivityCategoryAssociation',
    
    # Student models
    'StudentActivityPerformance',
    'StudentActivityPreference',
    'ActivityProgression',
    'StudentActivityAdaptation',
    'AdaptationHistory',
    
    # Exercise models
    'AdaptedExercise',
    'AdaptedWorkout',
    'AdaptedWorkoutExercise',
    
    # Routine models
    'AdaptedRoutine',
    'AdaptedRoutineActivity',
    'AdaptedRoutinePerformance',
    
    # Activity Plan models
    'ActivityPlan',
    'ActivityPlanActivity'
] 