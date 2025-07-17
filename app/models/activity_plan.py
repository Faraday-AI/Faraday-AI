"""Re-export of activity plan models for backward compatibility."""

from app.models.physical_education.activity_plan.models import (
    ActivityPlan,
    ActivityPlanActivity
)

__all__ = [
    'ActivityPlan',
    'ActivityPlanActivity'
] 