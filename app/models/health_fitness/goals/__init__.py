"""
Health and Fitness Goals

This module exports all goal-related models.
"""

from app.models.health_fitness.goals.goal_setting import (
    Goal,
    HealthFitnessGoalProgress,
    GoalMilestone,
    GoalActivity
)
from app.models.health_fitness.goals.fitness_goals import (
    FitnessGoal,
    FitnessGoalProgressGeneral,
    GoalAdjustment,
    GoalRecommendation,
    FitnessGoalProgress
)

__all__ = [
    # General goals
    'Goal',
    'HealthFitnessGoalProgress',
    'GoalMilestone',
    'GoalActivity',
    
    # Fitness goals
    'FitnessGoal',
    'FitnessGoalProgressGeneral',
    'GoalAdjustment',
    'GoalRecommendation',
    'FitnessGoalProgress'
] 