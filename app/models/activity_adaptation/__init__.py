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

# Create ActivityAdaptationModel class for compatibility
class ActivityAdaptationModel:
    """Model for activity adaptation analysis and management."""
    
    def __init__(self):
        """Initialize the adaptation model."""
        pass
    
    async def analyze(self, activity_id: str, student_id: str, performance_data: dict) -> dict:
        """Analyze adaptation needs for an activity and student."""
        # Mock implementation for testing
        return {
            "needs_adaptation": True,
            "adaptation_type": "simplification",
            "confidence": 0.85
        }
    
    async def generate_plan(self, activity_id: str, student_id: str, adaptation_type: str) -> dict:
        """Generate an adaptation plan."""
        # Mock implementation for testing
        return {
            "plan_id": "plan123",
            "adaptations": [
                {"type": "simplify_instructions", "priority": "high"},
                {"type": "reduce_complexity", "priority": "medium"}
            ],
            "estimated_impact": 0.75
        }
    
    async def apply(self, activity_id: str, student_id: str, adaptation_plan: dict) -> dict:
        """Apply adaptations to an activity."""
        # Mock implementation for testing
        return {
            "applied": True,
            "modified_activity": {
                "id": activity_id,
                "instructions": "simplified",
                "complexity": "reduced"
            }
        }
    
    async def evaluate(self, activity_id: str, student_id: str, adaptation_data: dict) -> dict:
        """Evaluate the effectiveness of adaptations."""
        # Mock implementation for testing
        return {
            "effectiveness_score": 0.8,
            "improvement": 0.15,
            "recommendations": ["Continue current adaptations"]
        }
    
    async def optimize(self, activity_id: str, student_id: str, performance_history: list) -> dict:
        """Optimize adaptations based on performance history."""
        # Mock implementation for testing
        return {
            "optimized_plan": {
                "adaptations": [
                    {"type": "optimized_instruction", "priority": "high"}
                ]
            },
            "optimization_score": 0.9
        }

__all__ = [
    # Activity models
    'ActivityLog',
    'ActivityAdaptation',
    'ActivityAdaptationModel',  # Added missing model
    
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