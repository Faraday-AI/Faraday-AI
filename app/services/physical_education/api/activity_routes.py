from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.services.physical_education.models.activity import Activity
from app.services.physical_education.models.activity_types import ActivityType, DifficultyLevel, EquipmentRequirement
from app.services.physical_education.services.activity_service import ActivityService
from app.db.database import get_db
from pydantic import BaseModel, Field
from pydantic import ConfigDict

router = APIRouter(prefix="/activities", tags=["activities"])

class ActivityBase(BaseModel):
    """Base model for activity data."""
    name: str
    description: str
    activity_type: ActivityType
    difficulty: DifficultyLevel
    equipment_required: EquipmentRequirement
    duration_minutes: int
    categories: Optional[List[str]] = Field(default_factory=list)

class ActivityCreate(ActivityBase):
    """Model for creating a new activity."""
    pass

class ActivityUpdate(ActivityBase):
    """Model for updating an existing activity."""
    name: Optional[str] = None
    description: Optional[str] = None
    activity_type: Optional[ActivityType] = None
    difficulty: Optional[DifficultyLevel] = None
    equipment_required: Optional[EquipmentRequirement] = None
    duration_minutes: Optional[int] = None

class ActivityResponse(ActivityBase):
    """Model for activity response."""
    id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

@router.post("/", response_model=ActivityResponse)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    """Create a new physical education activity."""
    service = ActivityService(db)
    try:
        return service.create_activity(activity.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """Get an activity by ID."""
    service = ActivityService(db)
    activity = service.get_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.get("/", response_model=List[ActivityResponse])
def get_activities(
    activity_type: Optional[ActivityType] = None,
    difficulty: Optional[DifficultyLevel] = None,
    equipment: Optional[EquipmentRequirement] = None,
    max_duration: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get activities with optional filters."""
    service = ActivityService(db)
    
    if activity_type:
        return service.get_activities_by_type(activity_type)
    elif difficulty:
        return service.get_activities_by_difficulty(difficulty)
    elif equipment:
        return service.get_activities_by_equipment(equipment)
    elif max_duration:
        return service.get_activities_by_duration(max_duration)
    elif category:
        return service.get_activities_by_category(category)
    else:
        return service.get_all_activities()

@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    activity: ActivityUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing activity."""
    service = ActivityService(db)
    updated_activity = service.update_activity(activity_id, activity.model_dump(exclude_unset=True))
    if not updated_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return updated_activity

@router.delete("/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    """Delete an activity."""
    service = ActivityService(db)
    success = service.delete_activity(activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity not found")
    return {"message": "Activity deleted successfully"}

@router.get("/{activity_id}/categories", response_model=List[str])
def get_activity_categories(activity_id: int, db: Session = Depends(get_db)):
    """Get categories for an activity."""
    service = ActivityService(db)
    categories = service.get_activity_categories(activity_id)
    if not categories:
        raise HTTPException(status_code=404, detail="Activity not found")
    return categories 