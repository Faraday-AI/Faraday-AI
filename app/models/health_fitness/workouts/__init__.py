"""
Workouts and Injury Prevention

This module exports all workout and injury prevention-related models.
"""

from app.models.health_fitness.workouts.workout import (
    HealthFitnessWorkout,
    HealthFitnessWorkoutSession,
    HealthFitnessExercise,
    ExerciseSet,
    HealthFitnessWorkoutExercise,
    HealthFitnessWorkoutPlan,
    HealthFitnessWorkoutPlanWorkout
)
from app.models.health_fitness.workouts.injury_prevention import (
    InjuryPrevention,
    InjuryRiskAssessment,
    InjuryPreventionRiskAssessment,
    SafetyGuideline
)

__all__ = [
    # Workout models
    'HealthFitnessWorkout',
    'HealthFitnessWorkoutSession',
    'HealthFitnessExercise',
    'ExerciseSet',
    'HealthFitnessWorkoutExercise',
    'HealthFitnessWorkoutPlan',
    'HealthFitnessWorkoutPlanWorkout',
    
    # Injury prevention models
    'InjuryPrevention',
    'InjuryRiskAssessment',
    'InjuryPreventionRiskAssessment',
    'SafetyGuideline'
] 