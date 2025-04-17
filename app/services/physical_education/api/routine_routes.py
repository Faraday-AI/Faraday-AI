from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.physical_education.models.routine import Routine
from app.services.physical_education.models.routine_types import RoutineStatus
from app.services.physical_education.models.activity import Activity
from app.services.physical_education.models.class_ import Class
from app.services.physical_education.services.routine_service import RoutineService
from pydantic import BaseModel, Field, ConfigDict

router = APIRouter(prefix="/routines", tags=["routines"])

class ActivityInRoutine(BaseModel):
    """Model for an activity in a routine."""
    activity_id: int
    order: int
    duration_minutes: int
    activity_type: str

class RoutineBase(BaseModel):
    """Base model for routine data."""
    name: str
    description: str
    class_id: int
    focus_areas: List[str]
    status: RoutineStatus
    activities: Optional[List[ActivityInRoutine]] = Field(default_factory=list)

class RoutineCreate(RoutineBase):
    """Model for creating a new routine."""
    pass

class RoutineUpdate(BaseModel):
    """Model for updating an existing routine."""
    name: Optional[str] = None
    description: Optional[str] = None
    class_id: Optional[int] = None
    focus_areas: Optional[List[str]] = None
    status: Optional[RoutineStatus] = None
    activities: Optional[List[ActivityInRoutine]] = None

class RoutineResponse(RoutineBase):
    """Model for routine response."""
    id: int
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

@router.post("/", response_model=RoutineResponse)
def create_routine(routine: RoutineCreate, db: Session = Depends(get_db)):
    """Create a new physical education routine."""
    service = RoutineService(db)
    try:
        return service.create_routine(routine.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{routine_id}", response_model=RoutineResponse)
def get_routine(routine_id: int, db: Session = Depends(get_db)):
    """Get a routine by ID."""
    service = RoutineService(db)
    routine = service.get_routine(routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    return routine

@router.get("/", response_model=List[RoutineResponse])
def get_routines(
    class_id: Optional[int] = None,
    status: Optional[RoutineStatus] = None,
    db: Session = Depends(get_db)
):
    """Get routines with optional filters."""
    service = RoutineService(db)
    
    if class_id:
        return service.get_routines_by_class(class_id)
    elif status:
        return service.get_routines_by_status(status)
    else:
        return service.get_all_routines()

@router.put("/{routine_id}", response_model=RoutineResponse)
def update_routine(
    routine_id: int,
    routine: RoutineUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing routine."""
    service = RoutineService(db)
    updated_routine = service.update_routine(routine_id, routine.model_dump(exclude_unset=True))
    if not updated_routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    return updated_routine

@router.delete("/{routine_id}")
def delete_routine(routine_id: int, db: Session = Depends(get_db)):
    """Delete a routine."""
    service = RoutineService(db)
    success = service.delete_routine(routine_id)
    if not success:
        raise HTTPException(status_code=404, detail="Routine not found")
    return {"message": "Routine deleted successfully"}

@router.post("/{routine_id}/activities")
def add_activity_to_routine(
    routine_id: int,
    activity: ActivityInRoutine,
    db: Session = Depends(get_db)
):
    """Add an activity to a routine."""
    service = RoutineService(db)
    success = service.add_activity_to_routine(
        routine_id=routine_id,
        activity_id=activity.activity_id,
        order=activity.order,
        duration_minutes=activity.duration_minutes,
        activity_type=activity.activity_type
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add activity to routine")
    return {"message": "Activity added to routine successfully"}

@router.delete("/{routine_id}/activities/{activity_id}")
def remove_activity_from_routine(
    routine_id: int,
    activity_id: int,
    db: Session = Depends(get_db)
):
    """Remove an activity from a routine."""
    service = RoutineService(db)
    success = service.remove_activity_from_routine(routine_id, activity_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove activity from routine")
    return {"message": "Activity removed from routine successfully"}

@router.get("/{routine_id}/activities", response_model=List[Activity])
def get_routine_activities(routine_id: int, db: Session = Depends(get_db)):
    """Get all activities in a routine."""
    service = RoutineService(db)
    activities = service.get_routine_activities(routine_id)
    if not activities:
        raise HTTPException(status_code=404, detail="Routine not found")
    return activities

@router.get("/{routine_id}/class", response_model=Class)
def get_routine_class(routine_id: int, db: Session = Depends(get_db)):
    """Get the class associated with a routine."""
    service = RoutineService(db)
    class_ = service.get_routine_class(routine_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Routine not found")
    return class_ 