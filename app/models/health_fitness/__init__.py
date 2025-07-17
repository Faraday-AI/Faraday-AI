"""
Health and Fitness Models

This module exports health and fitness-related models.
"""

from app.models.health_fitness.metrics import (
    HealthMetric,
    HealthMetricHistory,
    HealthCondition,
    HealthAlert,
    HealthCheck,
    FitnessMetric,
    FitnessMetricHistory
)
from app.models.health_fitness.goals import (
    Goal,
    HealthFitnessGoalProgress,
    GoalMilestone,
    FitnessGoal,
    FitnessGoalProgress
)
from app.models.health_fitness.workouts import (
    HealthFitnessWorkout,
    HealthFitnessWorkoutSession,
    HealthFitnessExercise,
    ExerciseSet,
    HealthFitnessWorkoutExercise,
    HealthFitnessWorkoutPlan,
    HealthFitnessWorkoutPlanWorkout,
    InjuryPrevention,
    InjuryRiskAssessment,
    InjuryPreventionRiskAssessment,
    SafetyGuideline
)
from app.models.health_fitness.nutrition import (
    NutritionPlan,
    Meal,
    FoodItem,
    NutritionLog
)
from app.models.health_fitness.progress import (
    Progress,
    ProgressGoal,
    HealthFitnessProgressNote
)

__all__ = [
    # Metrics
    'HealthMetric',
    'HealthMetricHistory',
    'HealthCondition',
    'HealthAlert',
    'HealthCheck',
    'FitnessMetric',
    'FitnessMetricHistory',
    
    # Goals
    'Goal',
    'HealthFitnessGoalProgress',
    'GoalMilestone',
    'FitnessGoal',
    'FitnessGoalProgress',
    
    # Workouts
    'HealthFitnessWorkout',
    'HealthFitnessWorkoutSession',
    'HealthFitnessExercise',
    'ExerciseSet',
    'HealthFitnessWorkoutExercise',
    'HealthFitnessWorkoutPlan',
    'HealthFitnessWorkoutPlanWorkout',
    'InjuryPrevention',
    'InjuryRiskAssessment',
    'InjuryPreventionRiskAssessment',
    'SafetyGuideline',
    
    # Nutrition
    'NutritionPlan',
    'Meal',
    'FoodItem',
    'NutritionLog',
    
    # Progress
    'Progress',
    'ProgressGoal',
    'HealthFitnessProgressNote'
] 