"""Activity schemas for request/response validation."""
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    ActivityCategoryType
)

class ActivityBase(BaseModel):
    """Base schema for activity data."""
    name: str
    description: str
    activity_type: ActivityType
    difficulty: DifficultyLevel
    equipment_required: EquipmentRequirement
    duration_minutes: int
    instructions: str
    safety_guidelines: Optional[str] = None
    variations: Optional[str] = None
    benefits: Optional[str] = None
    activity_metadata: Optional[Dict] = None
    categories: Optional[List[str]] = None

class ActivityCreate(ActivityBase):
    """Schema for creating a new activity."""
    pass

class ActivityUpdate(BaseModel):
    """Schema for updating an activity."""
    name: Optional[str] = None
    description: Optional[str] = None
    activity_type: Optional[ActivityType] = None
    difficulty: Optional[DifficultyLevel] = None
    equipment_required: Optional[EquipmentRequirement] = None
    duration_minutes: Optional[int] = None
    instructions: Optional[str] = None
    safety_guidelines: Optional[str] = None
    variations: Optional[str] = None
    benefits: Optional[str] = None
    activity_metadata: Optional[Dict] = None
    categories: Optional[List[str]] = None

class ActivityResponse(ActivityBase):
    """Schema for activity response."""
    id: int
    created_at: datetime
    updated_at: datetime
    status: str

    class Config:
        """Pydantic config."""
        from_attributes = True 