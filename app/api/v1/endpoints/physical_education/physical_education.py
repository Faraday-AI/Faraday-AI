from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Dict, Any
from app.services.ai.ai_analytics import PhysicalEducationAI
from pydantic import BaseModel
import json

from ..safety import router as safety_router
from app.models.physical_education.activity.models import Activity

router = APIRouter()
router.include_router(safety_router, prefix="/safety", tags=["safety"])

pe_ai = PhysicalEducationAI()

@router.get("/health")
async def health_check():
    """Health check endpoint for Physical Education system."""
    return {
        "status": "healthy",
        "service": "physical_education",
        "version": "1.0.0",
        "features": [
            "activity_management",
            "movement_analysis",
            "safety_monitoring",
            "student_progress",
            "lesson_planning"
        ]
    }

class LessonPlanRequest(BaseModel):
    activity: str
    grade_level: str
    duration: str
    equipment: List[str]

class MovementAnalysisRequest(BaseModel):
    activity: str
    data_points: Dict[str, Any]

class ActivityAdaptationRequest(BaseModel):
    activity: str
    needs: Dict[str, Any]
    environment: Dict[str, Any]

class HealthPlanRequest(BaseModel):
    profile: Dict[str, Any]
    goals: List[str]
    current_level: str

class ClassroomOptimizationRequest(BaseModel):
    size: int
    space: Dict[str, Any]
    equipment: List[str]

class SkillAssessmentRequest(BaseModel):
    activity: str
    performance: Dict[str, Any]
    previous: List[Dict[str, Any]]

class CurriculumIntegrationRequest(BaseModel):
    subject: str
    grade_level: str
    standards: List[str]

class SafetyAnalysisRequest(BaseModel):
    activity: str
    environment: Dict[str, Any]
    equipment: List[str]

class ProfessionalDevelopmentRequest(BaseModel):
    experience: str
    focus_areas: List[str]
    goals: List[str]

@router.post("/api/v1/phys-ed/lesson-plan")
async def create_lesson_plan(request: LessonPlanRequest):
    """Create a physical education lesson plan."""
    try:
        return await pe_ai.generate_lesson_plan(
            request.activity,
            request.grade_level,
            request.duration
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/phys-ed/movement-analysis")
async def analyze_movement(request: MovementAnalysisRequest):
    """Analyze movement patterns and provide feedback."""
    try:
        return await pe_ai.analyze_movement(
            request.activity,
            request.data_points
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/phys-ed/activity-adaptation")
async def adapt_activity(request: ActivityAdaptationRequest):
    """Adapt activities based on student needs and environment."""
    try:
        return await pe_ai.adapt_activity(
            request.activity,
            request.needs,
            request.environment
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/phys-ed/health-plan")
async def create_health_plan(request: HealthPlanRequest):
    """Create personalized health and wellness plans."""
    try:
        return await pe_ai.create_health_plan(
            request.profile,
            request.goals,
            request.current_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/phys-ed/classroom-optimization")
async def optimize_classroom(request: ClassroomOptimizationRequest):
    """Optimize classroom management and organization."""
    try:
        return await pe_ai.optimize_classroom(
            request.size,
            request.space,
            request.equipment
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/phys-ed/skill-assessment")
async def assess_skills(request: SkillAssessmentRequest):
    """Assess student skills and track progress."""
    try:
        return await pe_ai.assess_skills(
            request.activity,
            request.performance,
            request.previous
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/phys-ed/curriculum-integration")
async def integrate_curriculum(request: CurriculumIntegrationRequest):
    """Integrate PE with other subjects and standards."""
    try:
        return await pe_ai.integrate_curriculum(
            request.subject,
            request.grade_level,
            request.standards
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/phys-ed/safety-analysis")
async def analyze_safety(request: SafetyAnalysisRequest):
    """Analyze safety considerations and provide guidelines."""
    try:
        return await pe_ai.analyze_safety(
            request.activity,
            request.environment,
            request.equipment
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/phys-ed/professional-development")
async def create_professional_plan(request: ProfessionalDevelopmentRequest):
    """Create professional development plans."""
    try:
        return await pe_ai.create_professional_plan(
            request.experience,
            request.focus_areas,
            request.goals
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple activity management endpoints
@router.post("/activities/simple")
async def create_simple_activity(activity_data: Dict[str, Any]):
    """Create a simple physical education activity."""
    try:
        from app.services.physical_education.activity_service import ActivityService
        from app.core.database import get_db
        
        db = next(get_db())
        activity_service = ActivityService(db)
        
        # Create the activity
        activity = activity_service.create_activity(activity_data)
        
        return {
            "status": "success",
            "activity_id": activity.id,
            "name": activity.name,
            "message": "Activity created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/simple")
async def list_simple_activities():
    """List all simple physical education activities."""
    try:
        from app.services.physical_education.activity_service import ActivityService
        from app.core.database import get_db
        
        db = next(get_db())
        activity_service = ActivityService(db)
        
        # Get all activities
        activities = db.query(Activity).all()
        
        return {
            "status": "success",
            "activities": [
                {
                    "id": activity.id,
                    "name": activity.name,
                    "description": activity.description,
                    "type": str(activity.type) if activity.type else None
                }
                for activity in activities
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/phys-ed/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video for movement analysis."""
    try:
        # Save the uploaded file temporarily
        contents = await file.read()
        # Process the video with MediaPipe
        # Return analysis results
        return {"message": "Video uploaded successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 