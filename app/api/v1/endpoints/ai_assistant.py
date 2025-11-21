"""
AI Assistant API Endpoints
FastAPI endpoints for AI assistant integration
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Header, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import os

from app.core.database import get_db
from app.core.auth import get_current_user, oauth2_scheme
from app.core.auth_models import User as PydanticUser
from app.models.core.user import User
from app.models.teacher_registration import TeacherRegistration
import uuid

logger = logging.getLogger(__name__)
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
    AIAssistantBulkDeleteResponse,
    ContentGenerationRequest,
    LessonPlanRequest,
    AssessmentRequest
)

# Export schemas for test imports
__all__ = ['ContentGenerationRequest', 'LessonPlanRequest', 'AssessmentRequest']
# TeacherResponse doesn't exist - using User from auth_models instead

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])


def get_db_user_from_pydantic_user(pydantic_user: PydanticUser, db: Session, token: Optional[str] = None) -> User:
    """Get the database User model from a Pydantic User model.
    
    Tries multiple strategies (in order of reliability):
    1. Decode JWT token and look up by user ID (sub field) - most reliable
    2. Decode JWT token and look up by email from payload
    3. Look up by email from Pydantic User (fallback)
    """
    # Ensure database transaction is clean at the start (rollback any previous failed transaction)
    try:
        db.rollback()
    except Exception:
        pass
    
    # Log what we're working with
    logger.info(f"🔍 User lookup - Pydantic email: {pydantic_user.email}, has_token: {token is not None}, token_type: {type(token)}")
    
    # First, try to get user from JWT token payload (most reliable)
    if token and token != "test_token" and isinstance(token, str) and len(token.split('.')) == 3:  # Valid JWT has 3 parts
        try:
            from jose import jwt
            from app.core.config import get_settings
            settings = get_settings()
            
            # Try multiple secret keys (in case tokens were created with different secrets)
            secret_keys_to_try = [
                settings.JWT_SECRET_KEY,
                settings.SECRET_KEY,
                os.getenv("JWT_SECRET_KEY", ""),
                os.getenv("SECRET_KEY", "")
            ]
            # Remove duplicates and empty strings
            secret_keys_to_try = list(dict.fromkeys([k for k in secret_keys_to_try if k]))
            
            payload = None
            used_secret = None
            for secret_key in secret_keys_to_try:
                if not secret_key:
                    continue
                try:
                    payload = jwt.decode(token, secret_key, algorithms=[settings.JWT_ALGORITHM])
                    used_secret = secret_key[:10] + "..." if len(secret_key) > 10 else secret_key
                    logger.info(f"✅ Successfully decoded JWT token with secret key: {used_secret}")
                    break
                except Exception as decode_error:
                    logger.debug(f"Failed to decode with secret key {secret_key[:10] if secret_key else 'None'}...: {decode_error}")
                    continue
            
            if not payload:
                logger.warning("⚠️ Could not decode token with any available secret key")
            else:
                logger.info(f"📋 Token payload keys: {list(payload.keys())}")
                logger.info(f"📋 Token payload sub: {payload.get('sub')}, email: {payload.get('email')}")
                
                # Ensure database transaction is clean before queries
                try:
                    db.rollback()
                except Exception:
                    pass
                
                # Try email from token payload FIRST (most reliable, works regardless of ID type)
                email = payload.get('email')
                if email:
                    try:
                        db.rollback()  # Ensure clean transaction
                    except Exception:
                        pass
                    try:
                        db_user = db.query(User).filter(User.email == email).first()
                        if db_user:
                            logger.info(f"✅ Found user by email from token: {db_user.id} ({db_user.email})")
                            return db_user
                    except Exception as db_error:
                        logger.error(f"❌ Database error during user lookup by email: {db_error}")
                        db.rollback()
                        raise
                
                # Try to get user ID from token (sub is the standard field for user ID)
                # Note: sub might be a UUID string, not an integer
                user_id = payload.get('sub')
                if user_id:
                    try:
                        # Try as integer first (if ID is numeric)
                        user_id_int = int(user_id)
                        try:
                            db.rollback()  # Ensure clean transaction
                        except Exception:
                            pass
                        db_user = db.query(User).filter(User.id == user_id_int).first()
                        if db_user:
                            logger.info(f"✅ Found user by ID (int) from token: {db_user.id} ({db_user.email})")
                            return db_user
                    except (ValueError, TypeError):
                        # sub is not numeric (likely a UUID string)
                        # Since User.id is Integer, we can't query by UUID
                        # Skip ID lookup and rely on email (which we already tried above)
                        logger.debug(f"Token sub is not numeric (UUID?): {user_id}, skipping ID lookup")
                        pass
                    except Exception as db_error:
                        logger.error(f"❌ Database error during user lookup by ID: {db_error}")
                        db.rollback()
                        raise
        except Exception as e:
            logger.error(f"❌ Failed to decode JWT token for user lookup: {e}", exc_info=True)
    elif token == "test_token":
        logger.info("🧪 Test mode detected - using test token")
        # In test mode, try to find user by email from Pydantic User
        if pydantic_user.email and pydantic_user.email != "test@example.com":
            db_user = db.query(User).filter(User.email == pydantic_user.email).first()
            if db_user:
                logger.info(f"✅ Found user by email in test mode: {db_user.id} ({db_user.email})")
                return db_user
    
    # Fallback: Try to find user by email from Pydantic User
    # BUT skip if it's the test email - we want to use the real token email instead
    if pydantic_user.email and pydantic_user.email != "test@example.com":
        try:
            # Ensure clean transaction before query
            db.rollback()
        except Exception:
            pass
        try:
            db_user = db.query(User).filter(User.email == pydantic_user.email).first()
            if db_user:
                logger.info(f"✅ Found user by email from Pydantic User: {db_user.id} ({db_user.email})")
                return db_user
        except Exception as db_error:
            logger.error(f"❌ Database error during user lookup by email: {db_error}")
            db.rollback()
            raise
    
    # Last resort: Try to find any admin user if we're in a bind (for development/testing)
    # This should only happen if token decoding completely fails
    if pydantic_user.email and "@" in pydantic_user.email:
        # Try partial email match (domain part)
        email_domain = pydantic_user.email.split("@")[1] if "@" in pydantic_user.email else None
        if email_domain:
            db_user = db.query(User).filter(User.email.like(f"%@{email_domain}")).first()
            if db_user:
                logger.warning(f"⚠️ Found user by email domain match: {db_user.id} ({db_user.email})")
                return db_user
    
    # If all lookups fail, raise an error with helpful details
    error_details = {
        "pydantic_email": pydantic_user.email if pydantic_user.email else "None",
        "pydantic_username": pydantic_user.username if hasattr(pydantic_user, 'username') else "None",
        "has_token": token is not None,
        "token_preview": token[:20] + "..." if token and len(token) > 20 else "None"
    }
    logger.error(f"❌ User lookup failed. Details: {error_details}")
    
    # Log all users in database for debugging (only email, not sensitive data)
    try:
        all_users = db.query(User.email, User.id).limit(10).all()
        logger.error(f"📋 Sample users in database: {[(u.id, u.email) for u in all_users]}")
    except Exception as e:
        logger.error(f"❌ Could not query users for debugging: {e}")
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User not found in database. Email: {pydantic_user.email if pydantic_user.email else 'None'}. Please ensure you are logged in with a valid account."
    )


def get_or_create_teacher_registration(db_user: User, db: Session) -> str:
    """Get or create a TeacherRegistration for a User and return its UUID.
    
    The AI Assistant system uses TeacherRegistration (UUID) but authentication
    uses User (integer ID). This function bridges the gap by finding or creating
    a TeacherRegistration record for the user.
    
    Returns:
        str: The UUID of the TeacherRegistration (as a string)
    """
    try:
        # Try to find existing TeacherRegistration by email
        teacher_reg = db.query(TeacherRegistration).filter(
            TeacherRegistration.email == db_user.email
        ).first()
        
        if teacher_reg:
            logger.info(f"✅ Found existing TeacherRegistration: {teacher_reg.id} for user {db_user.id}")
            return str(teacher_reg.id)
        
        # Create a new TeacherRegistration if it doesn't exist
        # Note: We don't have the password_hash, so we'll use a placeholder
        # In production, you might want to sync passwords or use a different approach
        teacher_reg = TeacherRegistration(
            id=uuid.uuid4(),
            email=db_user.email,
            password_hash="",  # Placeholder - password sync would be handled separately
            first_name=db_user.first_name or "Teacher",
            last_name=db_user.last_name or "User",
            is_verified=True,
            is_active=db_user.is_active
        )
        
        db.add(teacher_reg)
        db.commit()
        db.refresh(teacher_reg)
        
        logger.info(f"✅ Created new TeacherRegistration: {teacher_reg.id} for user {db_user.id}")
        return str(teacher_reg.id)
        
    except Exception as e:
        logger.error(f"❌ Error getting/creating TeacherRegistration: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get or create teacher registration: {str(e)}"
        )


# ==================== CONFIGURATION ENDPOINTS ====================

@router.post("/configs", response_model=AIAssistantConfigResponse)
async def create_assistant_config(
    config_data: AIAssistantConfigCreate,
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AI assistant configuration"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        return service.create_assistant_config(teacher_registration_id, config_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create AI assistant config: {str(e)}"
        )


@router.get("/configs", response_model=List[AIAssistantConfigResponse])
async def get_assistant_configs(
    assistant_type: Optional[str] = Query(None, description="Filter by assistant type"),
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI assistant configurations for the current teacher"""
    try:
        service = AIAssistantService(db)
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        return service.get_teacher_assistant_configs(teacher_registration_id, assistant_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get AI assistant configs: {str(e)}"
        )


@router.get("/configs/{config_id}", response_model=AIAssistantConfigResponse)
async def get_assistant_config(
    config_id: str = Path(..., description="Configuration ID"),
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific AI assistant configuration"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        configs = service.get_teacher_assistant_configs(teacher_registration_id)
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
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an AI assistant configuration"""
    try:
        service = AIAssistantService(db)
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        config = service.update_assistant_config(config_id, teacher_registration_id, update_data)
        
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
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an AI assistant configuration"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        success = service.delete_assistant_config(config_id, teacher_registration_id)
        
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
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AI assistant conversation"""
    try:
        service = AIAssistantService(db)
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        return service.create_conversation(teacher_registration_id, conversation_data)
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
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversations for the current teacher"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        return service.get_teacher_conversations(
            teacher_registration_id, 
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
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a conversation"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        return service.get_conversation_messages(
            conversation_id, 
            teacher_registration_id, 
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
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    request: Request = None
):
    """Send a message to the AI assistant and get a response"""
    try:
        # Extract token from Authorization header directly (bypasses test mode issues)
        token = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:]  # Remove "Bearer " prefix
        elif authorization:
            token = authorization
        elif request:
            # Fallback: try to get from request headers directly
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
        
        logger.info(f"🔑 Extracted token from header: {token[:20] + '...' if token and len(token) > 20 else 'None'}")
        logger.info(f"🔑 Pydantic user email: {current_teacher.email}")
        
        # Ensure database transaction is clean before lookup
        try:
            db.rollback()  # Rollback any previous failed transaction
        except Exception:
            pass  # Ignore if no transaction to rollback
        
        db_user = get_db_user_from_pydantic_user(current_teacher, db, token)
        # Get or create TeacherRegistration UUID (AI Assistant uses UUID, not integer ID)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        return service.send_chat_message(teacher_registration_id, chat_request)
    except HTTPException:
        raise
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
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for an AI assistant interaction"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        return service.submit_feedback(teacher_registration_id, feedback_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/feedback", response_model=List[AIAssistantFeedbackResponse])
async def get_conversation_feedback(
    conversation_id: str = Path(..., description="Conversation ID"),
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback for a conversation"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        return service.get_conversation_feedback(conversation_id, teacher_registration_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get conversation feedback: {str(e)}"
        )


# ==================== ANALYTICS ENDPOINTS ====================

@router.get("/analytics", response_model=List[AIAssistantAnalyticsResponse])
async def get_teacher_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI assistant analytics for the current teacher"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        return service.get_teacher_analytics(teacher_registration_id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/analytics/summary", response_model=AIAssistantUsageSummary)
async def get_usage_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage summary for the current teacher"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        return service.get_usage_summary(teacher_registration_id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get usage summary: {str(e)}"
        )


@router.get("/dashboard/summary", response_model=AIAssistantDashboardSummary)
async def get_dashboard_summary(
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard summary for the current teacher"""
    try:
        service = AIAssistantService(db)
        
        # Get basic statistics
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        conversations = service.get_teacher_conversations(teacher_registration_id, limit=1000)
        total_conversations = len(conversations)
        active_conversations = len([c for c in conversations if c.is_active])
        
        # Get usage summary
        usage_summary = service.get_usage_summary(teacher_registration_id, 30)
        
        # Get recent activity
        recent_activity = service.get_teacher_conversations(
            teacher_registration_id, 
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
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk create AI assistant configurations"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        created_configs = []
        errors = []
        
        for config_data in bulk_request.configs:
            try:
                config = service.create_assistant_config(teacher_registration_id, config_data)
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
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk delete AI assistant configurations"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        deleted_count = 0
        errors = []
        
        for config_id in bulk_request.config_ids:
            try:
                success = service.delete_assistant_config(config_id, teacher_registration_id)
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
    current_teacher: PydanticUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI assistant service status for the current teacher"""
    try:
        db_user = get_db_user_from_pydantic_user(current_teacher, db)
        teacher_registration_id = get_or_create_teacher_registration(db_user, db)
        service = AIAssistantService(db)
        
        # Check if teacher has any configurations
        configs = service.get_teacher_assistant_configs(teacher_registration_id)
        has_configs = len(configs) > 0
        
        # Check recent usage
        usage_summary = service.get_usage_summary(teacher_registration_id, 7)
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