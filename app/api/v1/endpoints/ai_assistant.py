"""
AI Assistant API Endpoints
FastAPI endpoints for AI assistant integration
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.pe.ai_assistant_service import AIAssistantService
from app.schemas.ai_assistant import (
    AIAssistantConfigCreate,
    AIAssistantConfigUpdate,
    AIAssistantConfigResponse,
    AIAssistantConversationCreate,
    AIAssistantConversationResponse,
    AIAssistantMessageResponse,
    AIAssistantUsageResponse,
    AIAssistantTemplateResponse,
    AIAssistantFeedbackCreate,
    AIAssistantFeedbackResponse,
    AIAssistantAnalyticsResponse,
    AIAssistantChatRequest,
    AIAssistantChatResponse,
    AIAssistantUsageSummary,
    AIAssistantDashboardSummary,
    AIAssistantBulkCreateRequest,
    AIAssistantBulkCreateResponse,
    AIAssistantBulkDeleteRequest,
    AIAssistantBulkDeleteResponse
)
from app.schemas.teacher_auth import TeacherResponse

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])


# ==================== CONFIGURATION ENDPOINTS ====================

@router.post("/configs", response_model=AIAssistantConfigResponse)
async def create_assistant_config(
    config_data: AIAssistantConfigCreate,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AI assistant configuration"""
    try:
        service = AIAssistantService(db)
        return service.create_assistant_config(current_teacher.id, config_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create AI assistant config: {str(e)}"
        )


@router.get("/configs", response_model=List[AIAssistantConfigResponse])
async def get_assistant_configs(
    assistant_type: Optional[str] = Query(None, description="Filter by assistant type"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI assistant configurations for the current teacher"""
    try:
        service = AIAssistantService(db)
        return service.get_teacher_assistant_configs(current_teacher.id, assistant_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get AI assistant configs: {str(e)}"
        )


@router.get("/configs/{config_id}", response_model=AIAssistantConfigResponse)
async def get_assistant_config(
    config_id: str = Path(..., description="Configuration ID"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific AI assistant configuration"""
    try:
        service = AIAssistantService(db)
        configs = service.get_teacher_assistant_configs(current_teacher.id)
        config = next((c for c in configs if c.id == config_id), None)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI assistant configuration not found"
            )
        
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get AI assistant config: {str(e)}"
        )


@router.put("/configs/{config_id}", response_model=AIAssistantConfigResponse)
async def update_assistant_config(
    config_id: str = Path(..., description="Configuration ID"),
    update_data: AIAssistantConfigUpdate = None,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an AI assistant configuration"""
    try:
        service = AIAssistantService(db)
        config = service.update_assistant_config(config_id, current_teacher.id, update_data)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI assistant configuration not found"
            )
        
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update AI assistant config: {str(e)}"
        )


@router.delete("/configs/{config_id}")
async def delete_assistant_config(
    config_id: str = Path(..., description="Configuration ID"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an AI assistant configuration"""
    try:
        service = AIAssistantService(db)
        success = service.delete_assistant_config(config_id, current_teacher.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI assistant configuration not found"
            )
        
        return {"message": "AI assistant configuration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete AI assistant config: {str(e)}"
        )


# ==================== CONVERSATION ENDPOINTS ====================

@router.post("/conversations", response_model=AIAssistantConversationResponse)
async def create_conversation(
    conversation_data: AIAssistantConversationCreate,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AI assistant conversation"""
    try:
        service = AIAssistantService(db)
        return service.create_conversation(current_teacher.id, conversation_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create conversation: {str(e)}"
        )


@router.get("/conversations", response_model=List[AIAssistantConversationResponse])
async def get_conversations(
    conversation_type: Optional[str] = Query(None, description="Filter by conversation type"),
    limit: int = Query(50, ge=1, le=100, description="Number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversations for the current teacher"""
    try:
        service = AIAssistantService(db)
        return service.get_teacher_conversations(
            current_teacher.id, 
            conversation_type, 
            limit, 
            offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get conversations: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[AIAssistantMessageResponse])
async def get_conversation_messages(
    conversation_id: str = Path(..., description="Conversation ID"),
    limit: int = Query(100, ge=1, le=200, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a conversation"""
    try:
        service = AIAssistantService(db)
        return service.get_conversation_messages(
            conversation_id, 
            current_teacher.id, 
            limit, 
            offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get conversation messages: {str(e)}"
        )


# ==================== CHAT ENDPOINTS ====================

@router.post("/chat", response_model=AIAssistantChatResponse)
async def send_chat_message(
    chat_request: AIAssistantChatRequest,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to the AI assistant and get a response"""
    try:
        service = AIAssistantService(db)
        return service.send_chat_message(current_teacher.id, chat_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process chat message: {str(e)}"
        )


# ==================== TEMPLATE ENDPOINTS ====================

@router.get("/templates", response_model=List[AIAssistantTemplateResponse])
async def get_available_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    db: Session = Depends(get_db)
):
    """Get available AI assistant templates"""
    try:
        service = AIAssistantService(db)
        return service.get_available_templates(template_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get templates: {str(e)}"
        )


@router.post("/templates/{template_id}/use")
async def use_template(
    template_id: str = Path(..., description="Template ID"),
    variables: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """Use a template with variables to generate content"""
    try:
        service = AIAssistantService(db)
        content = service.use_template(template_id, variables or {})
        return {"content": content}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to use template: {str(e)}"
        )


# ==================== FEEDBACK ENDPOINTS ====================

@router.post("/feedback", response_model=AIAssistantFeedbackResponse)
async def submit_feedback(
    feedback_data: AIAssistantFeedbackCreate,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for an AI assistant interaction"""
    try:
        service = AIAssistantService(db)
        return service.submit_feedback(current_teacher.id, feedback_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/feedback", response_model=List[AIAssistantFeedbackResponse])
async def get_conversation_feedback(
    conversation_id: str = Path(..., description="Conversation ID"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback for a conversation"""
    try:
        service = AIAssistantService(db)
        return service.get_conversation_feedback(conversation_id, current_teacher.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get conversation feedback: {str(e)}"
        )


# ==================== ANALYTICS ENDPOINTS ====================

@router.get("/analytics", response_model=List[AIAssistantAnalyticsResponse])
async def get_teacher_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI assistant analytics for the current teacher"""
    try:
        service = AIAssistantService(db)
        return service.get_teacher_analytics(current_teacher.id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/analytics/summary", response_model=AIAssistantUsageSummary)
async def get_usage_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage summary for the current teacher"""
    try:
        service = AIAssistantService(db)
        return service.get_usage_summary(current_teacher.id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get usage summary: {str(e)}"
        )


@router.get("/dashboard/summary", response_model=AIAssistantDashboardSummary)
async def get_dashboard_summary(
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard summary for the current teacher"""
    try:
        service = AIAssistantService(db)
        
        # Get basic statistics
        conversations = service.get_teacher_conversations(current_teacher.id, limit=1000)
        total_conversations = len(conversations)
        active_conversations = len([c for c in conversations if c.is_active])
        
        # Get usage summary
        usage_summary = service.get_usage_summary(current_teacher.id, 30)
        
        # Get recent activity
        recent_activity = service.get_teacher_conversations(
            current_teacher.id, 
            limit=10, 
            offset=0
        )
        recent_activity_count = len(recent_activity)
        last_interaction = recent_activity[0].updated_at if recent_activity else None
        
        return AIAssistantDashboardSummary(
            total_conversations=total_conversations,
            active_conversations=active_conversations,
            total_messages=usage_summary.total_requests,
            total_tokens_used=usage_summary.total_tokens,
            average_satisfaction=usage_summary.satisfaction_score,
            most_used_type=usage_summary.usage_by_type.get('most_used', 'general_chat'),
            recent_activity_count=recent_activity_count,
            last_interaction=last_interaction
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get dashboard summary: {str(e)}"
        )


# ==================== BULK OPERATIONS ENDPOINTS ====================

@router.post("/configs/bulk", response_model=AIAssistantBulkCreateResponse)
async def bulk_create_configs(
    bulk_request: AIAssistantBulkCreateRequest,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk create AI assistant configurations"""
    try:
        service = AIAssistantService(db)
        created_configs = []
        errors = []
        
        for config_data in bulk_request.configs:
            try:
                config = service.create_assistant_config(current_teacher.id, config_data)
                created_configs.append(config)
            except Exception as e:
                errors.append({
                    "error_code": "CREATE_FAILED",
                    "error_message": str(e),
                    "config_name": config_data.config_name
                })
        
        return AIAssistantBulkCreateResponse(
            created_count=len(created_configs),
            failed_count=len(errors),
            created_configs=created_configs,
            errors=errors
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to bulk create configs: {str(e)}"
        )


@router.delete("/configs/bulk", response_model=AIAssistantBulkDeleteResponse)
async def bulk_delete_configs(
    bulk_request: AIAssistantBulkDeleteRequest,
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk delete AI assistant configurations"""
    try:
        service = AIAssistantService(db)
        deleted_count = 0
        errors = []
        
        for config_id in bulk_request.config_ids:
            try:
                success = service.delete_assistant_config(config_id, current_teacher.id)
                if success:
                    deleted_count += 1
                else:
                    errors.append({
                        "error_code": "NOT_FOUND",
                        "error_message": f"Configuration {config_id} not found",
                        "config_id": config_id
                    })
            except Exception as e:
                errors.append({
                    "error_code": "DELETE_FAILED",
                    "error_message": str(e),
                    "config_id": config_id
                })
        
        return AIAssistantBulkDeleteResponse(
            deleted_count=deleted_count,
            failed_count=len(errors),
            errors=errors
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to bulk delete configs: {str(e)}"
        )


# ==================== HEALTH CHECK ENDPOINTS ====================

@router.get("/health")
async def health_check():
    """Health check for AI assistant service"""
    return {
        "status": "healthy",
        "service": "ai_assistant",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }


@router.get("/status")
async def get_service_status(
    current_teacher: TeacherResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI assistant service status for the current teacher"""
    try:
        service = AIAssistantService(db)
        
        # Check if teacher has any configurations
        configs = service.get_teacher_assistant_configs(current_teacher.id)
        has_configs = len(configs) > 0
        
        # Check recent usage
        usage_summary = service.get_usage_summary(current_teacher.id, 7)
        has_recent_usage = usage_summary.total_requests > 0
        
        return {
            "status": "active",
            "has_configurations": has_configs,
            "has_recent_usage": has_recent_usage,
            "total_configurations": len(configs),
            "recent_requests": usage_summary.total_requests,
            "last_7_days_tokens": usage_summary.total_tokens
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }