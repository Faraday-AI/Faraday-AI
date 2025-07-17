"""
Fitness Models Package

This package contains models related to fitness tracking and goals.
"""

from app.models.physical_education.fitness.models import (
    FitnessGoal,
    FitnessAssessment,
    FitnessProgress,
    FitnessGoalCreate,
    FitnessGoalUpdate,
    FitnessGoalResponse
)

__all__ = [
    'FitnessGoal',
    'FitnessAssessment',
    'FitnessProgress',
    'FitnessGoalCreate',
    'FitnessGoalUpdate',
    'FitnessGoalResponse'
] 