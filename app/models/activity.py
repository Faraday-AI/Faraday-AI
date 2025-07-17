"""Re-export of activity models for backward compatibility."""

from app.models.physical_education.activity.models import (
    Activity,
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    StudentActivityPerformance,
    StudentActivityPreference,
    ActivityProgression
)
from app.models.activity_adaptation.categories.activity_categories import ActivityCategoryAssociation
from app.models.physical_education.pe_enums.pe_types import ActivityType, DifficultyLevel, EquipmentRequirement

__all__ = [
    'Activity',
    'ActivityCreate',
    'ActivityUpdate',
    'ActivityResponse',
    'StudentActivityPerformance',
    'StudentActivityPreference',
    'ActivityProgression',
    'ActivityCategoryAssociation',
    'ActivityType',
    'DifficultyLevel',
    'EquipmentRequirement'
] 