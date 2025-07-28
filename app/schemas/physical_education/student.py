from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class StudentPreferences(BaseModel):
    """Schema for student preferences in physical education."""
    difficulty_level: Optional[str] = Field(None, description="Preferred difficulty level")
    activity_types: Optional[List[str]] = Field(None, description="Preferred activity types")
    duration_minutes: Optional[int] = Field(None, description="Preferred duration in minutes")
    equipment_preferences: Optional[List[str]] = Field(None, description="Preferred equipment")
    group_size: Optional[str] = Field(None, description="Preferred group size")
    indoor_outdoor: Optional[str] = Field(None, description="Indoor or outdoor preference")
    intensity_level: Optional[str] = Field(None, description="Preferred intensity level")
    notes: Optional[str] = Field(None, description="Additional preference notes") 