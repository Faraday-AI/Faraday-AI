"""
FastAPI endpoints for Beta Safety Service
Provides REST API for safety management in the beta teacher system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pe.beta_safety_service import BetaSafetyService
from app.core.auth import get_current_user
from app.models.teacher_registration import TeacherRegistration

router = APIRouter(prefix="/beta/safety", tags=["Beta Safety"])


# ==================== SAFETY PROTOCOLS ====================

@router.get("/protocols", response_model=List[Dict])
async def get_safety_protocols(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get safety protocols for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        return await service.get_safety_protocols()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving safety protocols: {str(e)}"
        )


@router.post("/protocols", response_model=Dict)
async def create_safety_protocol(
    protocol: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new safety protocol for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        return await service.create_safety_protocol(protocol)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating safety protocol: {str(e)}"
        )


@router.put("/protocols/{protocol_id}", response_model=Dict)
async def update_safety_protocol(
    protocol_id: int,
    protocol: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a safety protocol for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        return await service.update_safety_protocol(protocol_id, protocol)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating safety protocol: {str(e)}"
        )


@router.delete("/protocols/{protocol_id}")
async def delete_safety_protocol(
    protocol_id: int,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a safety protocol for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        return await service.delete_safety_protocol(protocol_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting safety protocol: {str(e)}"
        )


# ==================== EMERGENCY PROCEDURES ====================

@router.get("/emergency-procedures", response_model=List[Dict])
async def get_emergency_procedures(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get emergency procedures for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        return await service.get_emergency_procedures()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving emergency procedures: {str(e)}"
        )


@router.post("/emergency-procedures", response_model=Dict)
async def create_emergency_procedure(
    procedure: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new emergency procedure for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        return await service.create_emergency_procedure(procedure)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating emergency procedure: {str(e)}"
        )


# ==================== RISK ASSESSMENTS ====================

@router.get("/risk-assessments", response_model=List[Dict])
async def get_risk_assessments(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get risk assessments for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        return await service.get_risk_assessments()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving risk assessments: {str(e)}"
        )


@router.post("/risk-assessments", response_model=Dict)
async def create_risk_assessment(
    assessment: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new risk assessment for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        return await service.create_risk_assessment(assessment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating risk assessment: {str(e)}"
        )


# ==================== INCIDENT REPORTS ====================

@router.get("/incidents", response_model=List[Dict])
async def get_incident_reports(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get incident reports for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        return await service.get_incident_reports()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving incident reports: {str(e)}"
        )


@router.post("/incidents", response_model=Dict)
async def create_incident_report(
    incident: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new incident report for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        return await service.create_incident_report(incident)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating incident report: {str(e)}"
        )


# ==================== MIGRATION ====================

@router.post("/migrate")
async def migrate_safety_data(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Migrate existing safety data for beta teacher."""
    try:
        service = BetaSafetyService(db, current_teacher.id)
        result = await service.migrate_existing_safety_data()
        return {"status": "success", "migrated": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error migrating safety data: {str(e)}"
        )


