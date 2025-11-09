"""
FastAPI endpoints for Beta Assessment Service
Provides REST API for assessment management in the beta teacher system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pe.beta_assessment_service import BetaAssessmentService
from app.core.auth import get_current_user
from app.models.teacher_registration import TeacherRegistration

router = APIRouter(prefix="/beta/assessment", tags=["Beta Assessment"])


# ==================== SKILL BENCHMARKS ====================

@router.post("/benchmarks/load", response_model=Dict)
async def load_skill_benchmarks(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Load skill benchmarks for assessment template creation."""
    try:
        service = BetaAssessmentService(db, current_teacher.id)
        benchmarks = await service.load_skill_benchmarks()
        return {"status": "success", "benchmarks": benchmarks}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading skill benchmarks: {str(e)}"
        )


@router.get("/benchmarks", response_model=Dict)
async def get_skill_benchmarks(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get skill benchmarks for beta teacher."""
    try:
        service = BetaAssessmentService(db, current_teacher.id)
        benchmarks = await service.load_skill_benchmarks()
        return {"benchmarks": benchmarks}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving skill benchmarks: {str(e)}"
        )


# ==================== ASSESSMENT TEMPLATES ====================

@router.get("/templates", response_model=List[Dict])
async def get_assessment_templates(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assessment templates for beta teacher."""
    try:
        service = BetaAssessmentService(db, current_teacher.id)
        return await service.get_assessment_templates()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving assessment templates: {str(e)}"
        )


