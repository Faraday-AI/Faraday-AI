"""
Beta Testing Infrastructure API Endpoints
Provides endpoints for managing beta testing programs, feedback collection, and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.beta_testing import (
    BetaTestingProgramCreate,
    BetaTestingProgramResponse,
    BetaTestingProgramUpdate,
    BetaTestingParticipantCreate,
    BetaTestingParticipantResponse,
    BetaTestingFeedbackCreate,
    BetaTestingFeedbackResponse,
    BetaTestingSurveyCreate,
    BetaTestingSurveyResponse,
    BetaTestingSurveyResponseCreate,
    BetaTestingSurveyResponseResponse,
    BetaTestingUsageAnalyticsResponse,
    BetaTestingFeatureFlagCreate,
    BetaTestingFeatureFlagResponse,
    BetaTestingNotificationCreate,
    BetaTestingNotificationResponse,
    BetaTestingReportResponse,
    BetaTestingDashboardResponse
)
from app.services.pe.beta_testing_service import BetaTestingService
from app.models.teacher_registration import TeacherRegistration

router = APIRouter()

# Helper function to get service instance
def get_beta_testing_service(db: Session = Depends(get_db)) -> BetaTestingService:
    return BetaTestingService(db)

@router.post("/programs", response_model=BetaTestingProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_beta_program(
    program_data: BetaTestingProgramCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    service: BetaTestingService = Depends(get_beta_testing_service)
):
    """Create a new beta testing program"""
    try:
        program = await service.create_program(
            program_data=program_data,
            created_by=current_teacher.id
        )
        return program
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create beta program: {str(e)}"
        )

@router.get("/programs", response_model=List[BetaTestingProgramResponse])
async def get_beta_programs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get beta testing programs"""
    try:
        programs = await beta_testing_service.get_programs(
            db=db,
            teacher_id=current_teacher.id,
            skip=skip,
            limit=limit,
            status_filter=status_filter
        )
        return programs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get beta programs: {str(e)}"
        )

@router.get("/programs/{program_id}", response_model=BetaTestingProgramResponse)
async def get_beta_program(
    program_id: uuid.UUID,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific beta testing program"""
    try:
        program = await beta_testing_service.get_program(
            db=db,
            program_id=program_id,
            teacher_id=current_teacher.id
        )
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beta program not found"
            )
        return program
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get beta program: {str(e)}"
        )

@router.put("/programs/{program_id}", response_model=BetaTestingProgramResponse)
async def update_beta_program(
    program_id: uuid.UUID,
    program_data: BetaTestingProgramUpdate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a beta testing program"""
    try:
        program = await beta_testing_service.update_program(
            db=db,
            program_id=program_id,
            program_data=program_data,
            teacher_id=current_teacher.id
        )
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beta program not found"
            )
        return program
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update beta program: {str(e)}"
        )

@router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_beta_program(
    program_id: uuid.UUID,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a beta testing program"""
    try:
        success = await beta_testing_service.delete_program(
            db=db,
            program_id=program_id,
            teacher_id=current_teacher.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beta program not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete beta program: {str(e)}"
        )

@router.post("/programs/{program_id}/participants", response_model=BetaTestingParticipantResponse, status_code=status.HTTP_201_CREATED)
async def add_participant(
    program_id: uuid.UUID,
    participant_data: BetaTestingParticipantCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a participant to a beta testing program"""
    try:
        participant = await beta_testing_service.add_participant(
            db=db,
            program_id=program_id,
            participant_data=participant_data,
            teacher_id=current_teacher.id
        )
        return participant
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add participant: {str(e)}"
        )

@router.get("/programs/{program_id}/participants", response_model=List[BetaTestingParticipantResponse])
async def get_participants(
    program_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get participants for a beta testing program"""
    try:
        participants = await beta_testing_service.get_participants(
            db=db,
            program_id=program_id,
            teacher_id=current_teacher.id,
            skip=skip,
            limit=limit
        )
        return participants
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get participants: {str(e)}"
        )

@router.post("/feedback", response_model=BetaTestingFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: BetaTestingFeedbackCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit beta testing feedback"""
    try:
        feedback = await beta_testing_service.submit_feedback(
            db=db,
            feedback_data=feedback_data,
            teacher_id=current_teacher.id
        )
        return feedback
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit feedback: {str(e)}"
        )

@router.get("/feedback", response_model=List[BetaTestingFeedbackResponse])
async def get_feedback(
    program_id: Optional[uuid.UUID] = Query(None),
    feedback_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get beta testing feedback"""
    try:
        feedback = await beta_testing_service.get_feedback(
            db=db,
            teacher_id=current_teacher.id,
            program_id=program_id,
            feedback_type=feedback_type,
            skip=skip,
            limit=limit
        )
        return feedback
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get feedback: {str(e)}"
        )

@router.post("/surveys", response_model=BetaTestingSurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(
    survey_data: BetaTestingSurveyCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a beta testing survey"""
    try:
        survey = await beta_testing_service.create_survey(
            db=db,
            survey_data=survey_data,
            teacher_id=current_teacher.id
        )
        return survey
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create survey: {str(e)}"
        )

@router.get("/surveys", response_model=List[BetaTestingSurveyResponse])
async def get_surveys(
    program_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get beta testing surveys"""
    try:
        surveys = await beta_testing_service.get_surveys(
            db=db,
            teacher_id=current_teacher.id,
            program_id=program_id,
            skip=skip,
            limit=limit
        )
        return surveys
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get surveys: {str(e)}"
        )

@router.post("/surveys/{survey_id}/responses", response_model=BetaTestingSurveyResponseResponse, status_code=status.HTTP_201_CREATED)
async def submit_survey_response(
    survey_id: uuid.UUID,
    response_data: BetaTestingSurveyResponseCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a survey response"""
    try:
        response = await beta_testing_service.submit_survey_response(
            db=db,
            survey_id=survey_id,
            response_data=response_data,
            teacher_id=current_teacher.id
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit survey response: {str(e)}"
        )

@router.get("/analytics/usage", response_model=BetaTestingUsageAnalyticsResponse)
async def get_usage_analytics(
    program_id: Optional[uuid.UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage analytics for beta testing"""
    try:
        analytics = await beta_testing_service.get_usage_analytics(
            db=db,
            teacher_id=current_teacher.id,
            program_id=program_id,
            start_date=start_date,
            end_date=end_date
        )
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get usage analytics: {str(e)}"
        )

@router.post("/feature-flags", response_model=BetaTestingFeatureFlagResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_flag(
    flag_data: BetaTestingFeatureFlagCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a feature flag for beta testing"""
    try:
        flag = await beta_testing_service.create_feature_flag(
            db=db,
            flag_data=flag_data,
            teacher_id=current_teacher.id
        )
        return flag
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create feature flag: {str(e)}"
        )

@router.get("/feature-flags", response_model=List[BetaTestingFeatureFlagResponse])
async def get_feature_flags(
    program_id: Optional[uuid.UUID] = Query(None),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feature flags for beta testing"""
    try:
        flags = await beta_testing_service.get_feature_flags(
            db=db,
            teacher_id=current_teacher.id,
            program_id=program_id
        )
        return flags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get feature flags: {str(e)}"
        )

@router.post("/notifications", response_model=BetaTestingNotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: BetaTestingNotificationCreate,
    background_tasks: BackgroundTasks,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a beta testing notification"""
    try:
        notification = await beta_testing_service.create_notification(
            db=db,
            notification_data=notification_data,
            teacher_id=current_teacher.id,
            background_tasks=background_tasks
        )
        return notification
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create notification: {str(e)}"
        )

@router.get("/notifications", response_model=List[BetaTestingNotificationResponse])
async def get_notifications(
    program_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get beta testing notifications"""
    try:
        notifications = await beta_testing_service.get_notifications(
            db=db,
            teacher_id=current_teacher.id,
            program_id=program_id,
            skip=skip,
            limit=limit
        )
        return notifications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get notifications: {str(e)}"
        )

@router.get("/reports", response_model=List[BetaTestingReportResponse])
async def get_reports(
    program_id: Optional[uuid.UUID] = Query(None),
    report_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get beta testing reports"""
    try:
        reports = await beta_testing_service.get_reports(
            db=db,
            teacher_id=current_teacher.id,
            program_id=program_id,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date
        )
        return reports
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get reports: {str(e)}"
        )

@router.get("/dashboard", response_model=BetaTestingDashboardResponse)
async def get_dashboard(
    program_id: Optional[uuid.UUID] = Query(None),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get beta testing dashboard data"""
    try:
        dashboard = await beta_testing_service.get_dashboard(
            db=db,
            teacher_id=current_teacher.id,
            program_id=program_id
        )
        return dashboard
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get dashboard: {str(e)}"
        )

@router.post("/programs/{program_id}/export")
async def export_program_data(
    program_id: uuid.UUID,
    export_format: str = Query("json", regex="^(json|csv|excel)$"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export beta testing program data"""
    try:
        export_data = await beta_testing_service.export_program_data(
            db=db,
            program_id=program_id,
            teacher_id=current_teacher.id,
            export_format=export_format
        )
        return export_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to export program data: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for beta testing infrastructure"""
    return {"status": "healthy", "service": "beta_testing_infrastructure"}
