"""Physical Education Activity Models for managing PE activities."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ActivityModel(BaseModel):
    """Base activity model."""
    id: str = Field(..., description="Activity ID")
    name: str = Field(..., description="Activity name")
    description: Optional[str] = Field(None, description="Activity description")
    activity_type: str = Field(..., description="Type of activity")
    difficulty_level: str = Field(..., description="Difficulty level")
    duration_minutes: int = Field(..., description="Duration in minutes")
    equipment_needed: List[str] = Field(default=[], description="Required equipment")
    skills_focused: List[str] = Field(default=[], description="Skills focused on")
    target_age_group: str = Field(..., description="Target age group")
    max_participants: Optional[int] = Field(None, description="Maximum participants")
    safety_considerations: List[str] = Field(default=[], description="Safety considerations")
    instructions: List[str] = Field(default=[], description="Activity instructions")
    variations: List[str] = Field(default=[], description="Activity variations")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    is_active: bool = Field(True, description="Activity active status")

class ActivityCreate(BaseModel):
    """Schema for creating an activity."""
    name: str = Field(..., description="Activity name")
    description: Optional[str] = Field(None, description="Activity description")
    activity_type: str = Field(..., description="Type of activity")
    difficulty_level: str = Field(..., description="Difficulty level")
    duration_minutes: int = Field(..., description="Duration in minutes")
    equipment_needed: Optional[List[str]] = Field(default=[], description="Required equipment")
    skills_focused: Optional[List[str]] = Field(default=[], description="Skills focused on")
    target_age_group: str = Field(..., description="Target age group")
    max_participants: Optional[int] = Field(None, description="Maximum participants")
    safety_considerations: Optional[List[str]] = Field(default=[], description="Safety considerations")
    instructions: Optional[List[str]] = Field(default=[], description="Activity instructions")
    variations: Optional[List[str]] = Field(default=[], description="Activity variations")

class ActivityUpdate(BaseModel):
    """Schema for updating an activity."""
    name: Optional[str] = Field(None, description="Activity name")
    description: Optional[str] = Field(None, description="Activity description")
    activity_type: Optional[str] = Field(None, description="Type of activity")
    difficulty_level: Optional[str] = Field(None, description="Difficulty level")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    equipment_needed: Optional[List[str]] = Field(None, description="Required equipment")
    skills_focused: Optional[List[str]] = Field(None, description="Skills focused on")
    target_age_group: Optional[str] = Field(None, description="Target age group")
    max_participants: Optional[int] = Field(None, description="Maximum participants")
    safety_considerations: Optional[List[str]] = Field(None, description="Safety considerations")
    instructions: Optional[List[str]] = Field(None, description="Activity instructions")
    variations: Optional[List[str]] = Field(None, description="Activity variations")
    is_active: Optional[bool] = Field(None, description="Activity active status")

class ActivityResponse(BaseModel):
    """Schema for activity response."""
    id: str = Field(..., description="Activity ID")
    name: str = Field(..., description="Activity name")
    description: Optional[str] = Field(None, description="Activity description")
    activity_type: str = Field(..., description="Type of activity")
    difficulty_level: str = Field(..., description="Difficulty level")
    duration_minutes: int = Field(..., description="Duration in minutes")
    equipment_needed: List[str] = Field(default=[], description="Required equipment")
    skills_focused: List[str] = Field(default=[], description="Skills focused on")
    target_age_group: str = Field(..., description="Target age group")
    max_participants: Optional[int] = Field(None, description="Maximum participants")
    safety_considerations: List[str] = Field(default=[], description="Safety considerations")
    instructions: List[str] = Field(default=[], description="Activity instructions")
    variations: List[str] = Field(default=[], description="Activity variations")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Activity active status")
    usage_count: int = Field(default=0, description="Number of times used")
    average_rating: Optional[float] = Field(None, description="Average rating")

    class Config:
        from_attributes = True

# Export Activity class for backward compatibility
Activity = ActivityModel

class ActivityCategory:
    """Model for activity categories."""
    pass

class ActivityRecommendation:
    """Model for activity recommendations."""
    pass

class Student:
    """Model for student data."""
    pass

class Class:
    """Model for class data."""
    pass

class ActivityType:
    """Model for activity types."""
    pass

class DifficultyLevel:
    """Model for difficulty levels."""
    pass

class EquipmentRequirement:
    """Model for equipment requirements."""
    pass

class StudentActivityPerformance:
    """Model for student activity performance."""
    pass 