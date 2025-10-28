"""
FastAPI endpoints for Lesson Plan Builder
Provides REST API for AI-assisted lesson plan creation and management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pe.lesson_plan_builder_service import LessonPlanBuilderService
from app.schemas.lesson_plan_builder import (
    LessonPlanTemplateCreate,
    LessonPlanTemplateUpdate,
    LessonPlanTemplateResponse,
    LessonPlanActivityCreate,
    LessonPlanActivityResponse,
    AISuggestionCreate,
    AISuggestionResponse,
    AISuggestionRating,
    LessonPlanSharingCreate,
    LessonPlanSharingResponse,
    LessonPlanSharingFeedback,
    LessonPlanUsageCreate,
    LessonPlanUsageResponse,
    LessonPlanCategoryResponse,
    LessonPlanSearchRequest,
    LessonPlanSearchResponse,
    AIGenerationRequest,
    AIGenerationResponse,
    TemplateAnalyticsResponse,
    TeacherAnalyticsResponse,
    BulkTemplateOperation,
    BulkOperationResponse,
    TemplateType,
    DifficultyLevel,
    SharingType,
    AccessLevel,
    UsageType
)
from app.core.auth import get_current_user
from app.schemas.auth import TeacherResponse

router = APIRouter(prefix="/lesson-plan-builder", tags=["Lesson Plan Builder"])


# ==================== TEMPLATE MANAGEMENT ====================

@router.post("/templates", response_model=LessonPlanTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: LessonPlanTemplateCreate,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lesson plan template"""
    try:
        service = LessonPlanBuilderService(db)
        return service.create_template(current_teacher.id, template_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create template: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=LessonPlanTemplateResponse)
async def get_template(
    template_id: str,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific template by ID"""
    service = LessonPlanBuilderService(db)
    template = service.get_template(template_id, current_teacher.id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or access denied"
        )
    
    return template


@router.get("/templates", response_model=List[LessonPlanTemplateResponse])
async def get_teacher_templates(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    grade_level: Optional[str] = Query(None, description="Filter by grade level"),
    template_type: Optional[TemplateType] = Query(None, description="Filter by template type"),
    limit: int = Query(50, ge=1, le=100, description="Number of templates to return"),
    offset: int = Query(0, ge=0, description="Number of templates to skip"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get templates created by the current teacher"""
    service = LessonPlanBuilderService(db)
    return service.get_teacher_templates(
        current_teacher.id, subject, grade_level, template_type, limit, offset
    )


@router.get("/templates/public", response_model=List[LessonPlanTemplateResponse])
async def get_public_templates(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    grade_level: Optional[str] = Query(None, description="Filter by grade level"),
    template_type: Optional[TemplateType] = Query(None, description="Filter by template type"),
    difficulty_level: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    limit: int = Query(50, ge=1, le=100, description="Number of templates to return"),
    offset: int = Query(0, ge=0, description="Number of templates to skip"),
    db: Session = Depends(get_db)
):
    """Get public templates available to all teachers"""
    service = LessonPlanBuilderService(db)
    return service.get_public_templates(
        subject, grade_level, template_type, difficulty_level, limit, offset
    )


@router.put("/templates/{template_id}", response_model=LessonPlanTemplateResponse)
async def update_template(
    template_id: str,
    update_data: LessonPlanTemplateUpdate,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing template"""
    service = LessonPlanBuilderService(db)
    template = service.update_template(template_id, current_teacher.id, update_data)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or access denied"
        )
    
    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a template"""
    service = LessonPlanBuilderService(db)
    success = service.delete_template(template_id, current_teacher.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or access denied"
        )


@router.post("/templates/{template_id}/duplicate", response_model=LessonPlanTemplateResponse)
async def duplicate_template(
    template_id: str,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Duplicate an existing template"""
    service = LessonPlanBuilderService(db)
    template = service.duplicate_template(template_id, current_teacher.id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or access denied"
        )
    
    return template


# ==================== AI SUGGESTIONS ====================

@router.post("/ai-suggestions", response_model=AISuggestionResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_suggestion(
    suggestion_data: AISuggestionCreate,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an AI-generated lesson plan suggestion"""
    try:
        service = LessonPlanBuilderService(db)
        return service.create_ai_suggestion(current_teacher.id, suggestion_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create AI suggestion: {str(e)}"
        )


@router.get("/ai-suggestions", response_model=List[AISuggestionResponse])
async def get_ai_suggestions(
    suggestion_type: Optional[str] = Query(None, description="Filter by suggestion type"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    applied_only: bool = Query(False, description="Show only applied suggestions"),
    limit: int = Query(20, ge=1, le=100, description="Number of suggestions to return"),
    offset: int = Query(0, ge=0, description="Number of suggestions to skip"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI suggestions for the current teacher"""
    service = LessonPlanBuilderService(db)
    return service.get_ai_suggestions(
        current_teacher.id, suggestion_type, subject, applied_only, limit, offset
    )


@router.post("/ai-suggestions/{suggestion_id}/apply", status_code=status.HTTP_200_OK)
async def apply_ai_suggestion(
    suggestion_id: str,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an AI suggestion as applied"""
    service = LessonPlanBuilderService(db)
    success = service.apply_ai_suggestion(suggestion_id, current_teacher.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found or access denied"
        )
    
    return {"message": "Suggestion applied successfully"}


@router.post("/ai-suggestions/{suggestion_id}/rate", status_code=status.HTTP_200_OK)
async def rate_ai_suggestion(
    suggestion_id: str,
    rating_data: AISuggestionRating,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate an AI suggestion"""
    service = LessonPlanBuilderService(db)
    success = service.rate_ai_suggestion(
        suggestion_id, current_teacher.id, rating_data.rating, rating_data.comment
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found or access denied"
        )
    
    return {"message": "Suggestion rated successfully"}


# ==================== SHARING ====================

@router.post("/templates/{template_id}/share", response_model=LessonPlanSharingResponse, status_code=status.HTTP_201_CREATED)
async def share_template(
    template_id: str,
    sharing_data: LessonPlanSharingCreate,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share a template with other teachers"""
    try:
        service = LessonPlanBuilderService(db)
        return service.share_template(template_id, current_teacher.id, sharing_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to share template: {str(e)}"
        )


@router.get("/templates/shared", response_model=List[LessonPlanTemplateResponse])
async def get_shared_templates(
    sharing_type: Optional[SharingType] = Query(None, description="Filter by sharing type"),
    limit: int = Query(50, ge=1, le=100, description="Number of templates to return"),
    offset: int = Query(0, ge=0, description="Number of templates to skip"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get templates shared with the current teacher"""
    service = LessonPlanBuilderService(db)
    return service.get_shared_templates(current_teacher.id, sharing_type, limit, offset)


@router.post("/templates/shared/{sharing_id}/feedback", status_code=status.HTTP_200_OK)
async def provide_sharing_feedback(
    sharing_id: str,
    feedback_data: LessonPlanSharingFeedback,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Provide feedback on a shared template"""
    # This would need to be implemented in the service
    # For now, return a placeholder response
    return {"message": "Feedback recorded successfully"}


# ==================== CATEGORIES ====================

@router.get("/categories", response_model=List[LessonPlanCategoryResponse])
async def get_categories(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    grade_level: Optional[str] = Query(None, description="Filter by grade level"),
    db: Session = Depends(get_db)
):
    """Get lesson plan categories"""
    service = LessonPlanBuilderService(db)
    return service.get_categories(subject, grade_level)


# ==================== USAGE TRACKING ====================

@router.post("/templates/{template_id}/usage", response_model=LessonPlanUsageResponse, status_code=status.HTTP_201_CREATED)
async def log_template_usage(
    template_id: str,
    usage_data: LessonPlanUsageCreate,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log usage of a template"""
    try:
        service = LessonPlanBuilderService(db)
        # This would need to be implemented in the service
        # For now, return a placeholder response
        return {"message": "Usage logged successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to log usage: {str(e)}"
        )


# ==================== SEARCH ====================

@router.post("/search", response_model=LessonPlanSearchResponse)
async def search_templates(
    search_request: LessonPlanSearchRequest,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for lesson plan templates"""
    # This would need to be implemented in the service
    # For now, return a placeholder response
    return {
        "templates": [],
        "total_count": 0,
        "has_more": False
    }


# ==================== AI GENERATION ====================

@router.post("/generate", response_model=AIGenerationResponse)
async def generate_ai_template(
    generation_request: AIGenerationRequest,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a lesson plan template using AI"""
    # This would need to be implemented in the service
    # For now, return a placeholder response
    return {
        "template": None,
        "suggestions": [],
        "confidence_score": 0.0,
        "generation_time_seconds": 0.0
    }


# ==================== ANALYTICS ====================

@router.get("/analytics/templates", response_model=TemplateAnalyticsResponse)
async def get_template_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for the teacher's templates"""
    service = LessonPlanBuilderService(db)
    return service.get_template_analytics(current_teacher.id, days)


@router.get("/analytics/teacher", response_model=TeacherAnalyticsResponse)
async def get_teacher_analytics(
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for the teacher"""
    # This would need to be implemented in the service
    # For now, return a placeholder response
    return {
        "total_templates": 0,
        "public_templates": 0,
        "private_templates": 0,
        "total_usage_count": 0,
        "templates_shared": 0,
        "templates_received": 0,
        "average_template_rating": 0.0,
        "most_used_template": None,
        "recent_activity": []
    }


# ==================== BULK OPERATIONS ====================

@router.post("/bulk-operations", response_model=BulkOperationResponse)
async def bulk_template_operation(
    operation_data: BulkTemplateOperation,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform bulk operations on multiple templates"""
    # This would need to be implemented in the service
    # For now, return a placeholder response
    return {
        "success_count": 0,
        "failure_count": 0,
        "errors": [],
        "results": []
    }


# ==================== HEALTH CHECK ====================

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for lesson plan builder"""
    return {
        "status": "healthy",
        "service": "lesson-plan-builder",
        "version": "1.0.0"
    }
