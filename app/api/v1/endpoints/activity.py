from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.models.physical_education.activity import Activity
from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse
)
from app.services.physical_education.activity_service import get_activity_service
from app.services.physical_education.safety_service import get_safety_service
from app.services.physical_education.student_service import get_student_service

router = APIRouter()

@router.post("/activities", response_model=ActivityResponse)
async def create_activity(
    activity: ActivityCreate,
    activity_service = Depends(get_activity_service)
) -> ActivityResponse:
    """Create a new physical education activity."""
    try:
        return await activity_service.create_activity(activity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: str,
    activity_service = Depends(get_activity_service)
) -> ActivityResponse:
    """Get a specific physical education activity."""
    try:
        activity = await activity_service.get_activity(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        return activity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: str,
    activity_update: ActivityUpdate,
    activity_service = Depends(get_activity_service)
) -> ActivityResponse:
    """Update a physical education activity."""
    try:
        activity = await activity_service.update_activity(activity_id, activity_update)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        return activity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/activities/{activity_id}")
async def delete_activity(
    activity_id: str,
    activity_service = Depends(get_activity_service)
) -> Dict[str, str]:
    """Delete a physical education activity."""
    try:
        success = await activity_service.delete_activity(activity_id)
        if not success:
            raise HTTPException(status_code=404, detail="Activity not found")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities", response_model=List[ActivityResponse])
async def list_activities(
    activity_service = Depends(get_activity_service)
) -> List[ActivityResponse]:
    """List all physical education activities."""
    try:
        return await activity_service.list_activities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activities/{activity_id}/safety-check")
async def check_activity_safety(
    activity_id: str,
    safety_service = Depends(get_safety_service)
) -> Dict[str, Any]:
    """Perform a safety check on an activity."""
    try:
        return await safety_service.check_activity_safety(activity_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activities/{activity_id}/student/{student_id}/progress")
async def track_student_progress(
    activity_id: str,
    student_id: str,
    progress_data: Dict[str, Any],
    student_service = Depends(get_student_service)
) -> Dict[str, Any]:
    """Track student progress in an activity."""
    try:
        return await student_service.track_progress(activity_id, student_id, progress_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 