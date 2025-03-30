from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.services.ai_analytics import PhysicalEducationAI
from pydantic import BaseModel

router = APIRouter()
pe_ai = PhysicalEducationAI()

class LessonPlanRequest(BaseModel):
    activity: str
    grade_level: str
    duration: str
    equipment: List[str]

class MovementAnalysisRequest(BaseModel):
    movement_type: str
    student_data: Dict[str, Any]

class ActivityDesignRequest(BaseModel):
    activity_type: str
    grade_level: str
    equipment: List[str]
    space_available: str

class SkillAssessmentRequest(BaseModel):
    skill: str
    grade_level: str
    assessment_type: str

@router.post("/lesson-plan")
async def create_pe_lesson_plan(request: LessonPlanRequest):
    """Generate a physical education lesson plan."""
    try:
        result = await pe_ai.generate_lesson_plan(
            activity=request.activity,
            grade_level=request.grade_level,
            duration=request.duration,
            equipment=request.equipment
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-movement")
async def analyze_student_movement(request: MovementAnalysisRequest):
    """Analyze student movement patterns and provide feedback."""
    try:
        result = await pe_ai.analyze_movement(
            movement_type=request.movement_type,
            student_data=request.student_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/design-activity")
async def design_pe_activity(request: ActivityDesignRequest):
    """Design a physical education activity."""
    try:
        result = await pe_ai.design_activity(
            activity_type=request.activity_type,
            grade_level=request.grade_level,
            equipment=request.equipment,
            space_available=request.space_available
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assess-skill")
async def assess_physical_skill(request: SkillAssessmentRequest):
    """Assess and provide feedback on physical education skills."""
    try:
        result = await pe_ai.assess_skill(
            skill=request.skill,
            grade_level=request.grade_level,
            assessment_type=request.assessment_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 