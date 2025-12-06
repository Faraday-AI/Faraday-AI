"""
AI Assistant Integration Service
Handles AI assistant integration for beta teachers
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
import uuid
import json
import os
import openai
import re
import asyncio
import logging
from openai import OpenAI

from app.models.ai_assistant import (
    AIAssistantConfig,
    AIAssistantConversation,
    AIAssistantMessage,
    AIAssistantUsage,
    AIAssistantTemplate,
    AIAssistantFeedback,
    AIAssistantAnalytics
)
from app.schemas.ai_assistant import (
    AIAssistantConfigCreate,
    AIAssistantConfigUpdate,
    AIAssistantConfigResponse,
    AIAssistantConversationCreate,
    AIAssistantConversationResponse,
    AIAssistantMessageCreate,
    AIAssistantMessageResponse,
    AIAssistantUsageResponse,
    AIAssistantTemplateResponse,
    AIAssistantFeedbackCreate,
    AIAssistantFeedbackResponse,
    AIAssistantAnalyticsResponse,
    AIAssistantChatRequest,
    AIAssistantChatResponse
)


logger = logging.getLogger(__name__)

class AIAssistantService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Initialize ModelRouter for hybrid architecture
        from app.services.pe.model_router import ModelRouter
        self.model_router = ModelRouter(db, self.openai_client)

    # ==================== CONFIGURATION MANAGEMENT ====================
    
    def create_assistant_config(
        self, 
        teacher_id: str, 
        config_data: AIAssistantConfigCreate
    ) -> AIAssistantConfigResponse:
        """Create a new AI assistant configuration"""
        try:
            config = AIAssistantConfig(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                config_name=config_data.config_name,
                config_description=config_data.config_description,
                assistant_type=config_data.assistant_type,
                is_active=config_data.is_active,
                config_data=config_data.config_data
            )
            
            self.db.add(config)
            self.db.commit()
            
            return self._config_to_response(config)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create AI assistant config: {str(e)}")

    def get_teacher_assistant_configs(
        self, 
        teacher_id: str, 
        assistant_type: Optional[str] = None
    ) -> List[AIAssistantConfigResponse]:
        """Get AI assistant configurations for a teacher"""
        query = self.db.query(AIAssistantConfig).filter(
            AIAssistantConfig.teacher_id == teacher_id
        )
        
        if assistant_type:
            query = query.filter(AIAssistantConfig.assistant_type == assistant_type)
        
        configs = query.filter(AIAssistantConfig.is_active == True).order_by(asc(AIAssistantConfig.config_name)).all()
        
        return [self._config_to_response(config) for config in configs]

    def update_assistant_config(
        self, 
        config_id: str, 
        teacher_id: str, 
        update_data: AIAssistantConfigUpdate
    ) -> Optional[AIAssistantConfigResponse]:
        """Update an AI assistant configuration"""
        config = self.db.query(AIAssistantConfig).filter(
            and_(
                AIAssistantConfig.id == config_id,
                AIAssistantConfig.teacher_id == teacher_id
            )
        ).first()
        
        if not config:
            return None
        
        # Update config fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(config, field, value)
        
        config.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._config_to_response(config)

    def delete_assistant_config(self, config_id: str, teacher_id: str) -> bool:
        """Delete an AI assistant configuration"""
        config = self.db.query(AIAssistantConfig).filter(
            and_(
                AIAssistantConfig.id == config_id,
                AIAssistantConfig.teacher_id == teacher_id
            )
        ).first()
        
        if not config:
            return False
        
        self.db.delete(config)
        self.db.commit()
        
        return True

    # ==================== CONVERSATION MANAGEMENT ====================
    
    def create_conversation(
        self, 
        teacher_id: str, 
        conversation_data: AIAssistantConversationCreate
    ) -> AIAssistantConversationResponse:
        """Create a new AI assistant conversation"""
        conversation = AIAssistantConversation(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            config_id=conversation_data.config_id,
            conversation_title=conversation_data.conversation_title,
            conversation_type=conversation_data.conversation_type,
            metadata=conversation_data.metadata
        )
        
        self.db.add(conversation)
        self.db.commit()
        
        return self._conversation_to_response(conversation)

    def get_teacher_conversations(
        self, 
        teacher_id: str, 
        conversation_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AIAssistantConversationResponse]:
        """Get conversations for a teacher"""
        query = self.db.query(AIAssistantConversation).filter(
            AIAssistantConversation.teacher_id == teacher_id
        )
        
        if conversation_type:
            query = query.filter(AIAssistantConversation.conversation_type == conversation_type)
        
        conversations = query.filter(AIAssistantConversation.is_active == True).order_by(desc(AIAssistantConversation.updated_at)).offset(offset).limit(limit).all()
        
        return [self._conversation_to_response(conversation) for conversation in conversations]

    def get_conversation_messages(
        self, 
        conversation_id: str, 
        teacher_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[AIAssistantMessageResponse]:
        """Get messages for a conversation"""
        # Verify conversation ownership
        conversation = self.db.query(AIAssistantConversation).filter(
            and_(
                AIAssistantConversation.id == conversation_id,
                AIAssistantConversation.teacher_id == teacher_id
            )
        ).first()
        
        if not conversation:
            return []
        
        messages = self.db.query(AIAssistantMessage).filter(
            AIAssistantMessage.conversation_id == conversation_id
        ).order_by(asc(AIAssistantMessage.created_at)).offset(offset).limit(limit).all()
        
        return [self._message_to_response(message) for message in messages]

    # ==================== HELPER FUNCTIONS FOR WIDGET DETECTION ====================
    # NOTE: Legacy extraction methods removed - now handled by specialized services via ModelRouter
    # All extraction is done by:
    # - WorkoutService -> widget_handler._extract_workout_data
    # - MealPlanService -> widget_handler._extract_meal_plan_data  
    # - LessonPlanService -> widget_handler._extract_lesson_plan_data
    # - AttendanceService -> widget_handler._extract_attendance_data
    # Use widget_handler methods directly if needed for any edge cases

    # ==================== AI CHAT FUNCTIONALITY ====================
    
    def send_chat_message(
        self, 
        teacher_id: str, 
        chat_request: AIAssistantChatRequest
    ) -> AIAssistantChatResponse:
        """Send a message to the AI assistant and get a response"""
        try:
            # Get or create conversation
            conversation = None
            if chat_request.conversation_id:
                conversation = self.db.query(AIAssistantConversation).filter(
                    and_(
                        AIAssistantConversation.id == chat_request.conversation_id,
                        AIAssistantConversation.teacher_id == teacher_id
                    )
                ).first()
            
            if not conversation:
                # Create new conversation
                conversation_data = AIAssistantConversationCreate(
                    config_id=chat_request.config_id,
                    conversation_title=chat_request.conversation_title or "New Conversation",
                    conversation_type=chat_request.conversation_type or "general_chat",
                    metadata=chat_request.metadata or {}
                )
                conversation = self.create_conversation(teacher_id, conversation_data)
                conversation = self.db.query(AIAssistantConversation).filter(
                    AIAssistantConversation.id == conversation.id
                ).first()
            
            # Get AI configuration
            config = None
            if chat_request.config_id:
                config = self.db.query(AIAssistantConfig).filter(
                    and_(
                        AIAssistantConfig.id == chat_request.config_id,
                        AIAssistantConfig.teacher_id == teacher_id
                    )
                ).first()
            
            if not config:
                # Use default configuration
                config = self._get_default_config(teacher_id, chat_request.conversation_type)
            
            # Save user message
            user_message = AIAssistantMessage(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                message_type="user",
                content=chat_request.message,
                metadata=chat_request.metadata or {}
            )
            self.db.add(user_message)
            self.db.flush()
            
            # Get conversation history for context
            recent_messages = self.db.query(AIAssistantMessage).filter(
                AIAssistantMessage.conversation_id == conversation.id
            ).order_by(desc(AIAssistantMessage.created_at)).limit(10).all()
            
            # Build conversation history for ModelRouter (format: list of dicts with role/content)
            conversation_messages = []
            for msg in reversed(recent_messages):
                conversation_messages.append({
                    "role": msg.message_type,
                    "content": msg.content
                })
            # Add current user message
            conversation_messages.append({
                "role": "user",
                "content": chat_request.message
            })
            
            # Classify intent using widget_handler
            from app.services.pe.widget_handler import classify_intent
            user_intent = classify_intent(chat_request.message)
            logger.info(f"🎯 Classified intent: '{user_intent}' for message: '{chat_request.message[:50]}...'")
            
            # Get user info for context
            # teacher_id is a UUID (TeacherRegistration ID), not a numeric User ID
            # Get the user via TeacherRegistration
            from app.models.core.user import User
            from app.models.teacher_registration import TeacherRegistration
            teacher_reg = self.db.query(TeacherRegistration).filter(
                TeacherRegistration.id == teacher_id
            ).first()
            user_first_name = None
            if teacher_reg:
                db_user = self.db.query(User).filter(User.email == teacher_reg.email).first()
                user_first_name = db_user.first_name if db_user else None
            
            # Build context for ModelRouter
            context = {
                "teacher_id": teacher_id,
                "conversation_id": str(conversation.id),
                "user_intent": user_intent,
                "conversation_messages": conversation_messages,
                "user_first_name": user_first_name,
                "config": config.config_data if config else {}
            }
            
            # Route through ModelRouter (hybrid architecture)
            start_time = datetime.utcnow()
            try:
                router_result = self.model_router.route(
                    intent=user_intent,
                    user_request=chat_request.message,
                    context=context
                )
                end_time = datetime.utcnow()
                
                # Extract response from router result
                ai_response = router_result.get("response", "")
                extracted_data = router_result.get("widget_data")
                usage_metadata = router_result.get("usage", {})
                
                # Extract generated content (images, documents, OneDrive links)
                extracted_content = {
                    "images": router_result.get("images", []),
                    "file_content": router_result.get("file_content"),
                    "filename": router_result.get("filename"),
                    "web_url": router_result.get("web_url"),
                    "file_id": router_result.get("file_id"),
                    "num_slides": router_result.get("num_slides")
                }
                
                # Get token count from usage metadata
                token_count = usage_metadata.get("total_tokens", 0) if isinstance(usage_metadata, dict) else 0
                processing_time = int((end_time - start_time).total_seconds() * 1000)
                
                logger.info(f"✅ ModelRouter response received: {len(ai_response)} chars, {token_count} tokens, {processing_time}ms")
                logger.info(f"🔍 Extraction result: {type(extracted_data)}, is_list={isinstance(extracted_data, list)}")
                
            except Exception as router_error:
                logger.error(f"❌ ModelRouter error: {router_error}", exc_info=True)
                # Fallback to direct OpenAI call if ModelRouter fails
                logger.warning("⚠️ Falling back to direct OpenAI call")
                messages = []
                if config.config_data.get('system_prompt'):
                    messages.append({
                        "role": "system",
                        "content": config.config_data['system_prompt']
                    })
                for msg in reversed(recent_messages):
                    messages.append({
                        "role": msg.message_type,
                        "content": msg.content
                    })
                messages.append({"role": "user", "content": chat_request.message})
                
                response = self.openai_client.chat.completions.create(
                    model=config.config_data.get('model', 'gpt-4-turbo'),  # Full production model for authorized users
                    messages=messages,
                    temperature=config.config_data.get('temperature', 0.7),
                    max_tokens=config.config_data.get('max_tokens', 2000)
                )
                end_time = datetime.utcnow()
                ai_response = response.choices[0].message.content
                token_count = response.usage.total_tokens
                processing_time = int((end_time - start_time).total_seconds() * 1000)
                extracted_data = None
                # Initialize router_result as empty dict for fallback case
                router_result = {}
            
            # Save AI response
            ai_message = AIAssistantMessage(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                message_type="assistant",
                content=ai_response,
                metadata={
                    "model": config.config_data.get('model', 'gpt-4-turbo'),  # Full production model for authorized users
                    "temperature": config.config_data.get('temperature', 0.7),
                    "max_tokens": config.config_data.get('max_tokens', 2000)
                },
                token_count=token_count,
                processing_time_ms=processing_time
            )
            self.db.add(ai_message)
            
            # Update conversation
            conversation.updated_at = datetime.utcnow()
            
            # Track usage
            self._track_usage(
                teacher_id=teacher_id,
                config_id=config.id,
                usage_type=conversation.conversation_type,
                tokens_used=token_count,
                processing_time_ms=processing_time,
                success=True
            )
            
            self.db.commit()
            
            # Handle widget_data from ModelRouter extraction
            widget_data = None
            widgets = None
            widgets_list = []
            
            # Process extracted_data from ModelRouter (can be single dict or list of multiple widgets)
            if extracted_data:
                if isinstance(extracted_data, list):
                    # Multiple widgets extracted - add all to widgets_list
                    for widget in extracted_data:
                        if isinstance(widget, dict):
                            # Ensure proper format: {"type": "...", "data": {...}}
                            if "type" in widget and "data" in widget:
                                widgets_list.append(widget)
                            elif "type" in widget:
                                widgets_list.append({
                                    "type": widget.get("type"),
                                    "data": widget
                                })
                            else:
                                widgets_list.append({
                                    "type": user_intent,
                                    "data": widget
                                })
                    logger.info(f"✅ Extracted {len(extracted_data)} widgets from ModelRouter for intent '{user_intent}': {[w.get('type') if isinstance(w, dict) else 'unknown' for w in extracted_data]}")
                elif isinstance(extracted_data, dict):
                    # Single widget (backward compatible)
                    # If it already has "type" and "data", use it as-is
                    if "type" in extracted_data and "data" in extracted_data:
                        widget_data = extracted_data
                    # If it has "type" but no "data", wrap the whole thing in "data"
                    elif "type" in extracted_data:
                        widget_data = {
                            "type": extracted_data.get("type"),
                            "data": extracted_data
                        }
                    # Otherwise, wrap it with the widget_type from intent
                    else:
                        widget_data = {
                            "type": user_intent,
                            "data": extracted_data
                        }
                    logger.info(f"✅ Extracted widget_data from ModelRouter for intent '{user_intent}': type={widget_data.get('type')}")
                else:
                    # Non-dict/list data, wrap it
                    widget_data = {
                        "type": user_intent,
                        "data": extracted_data
                    }
                    logger.info(f"✅ Wrapped widget_data from ModelRouter for intent '{user_intent}'")
            
            # If we have widgets_list, set widgets and widget_data appropriately
            if widgets_list:
                if len(widgets_list) == 1:
                    # Single widget - use widget_data for backward compatibility
                    widget_data = widgets_list[0]
                    widgets = None
                else:
                    # Multiple widgets - use widgets list, set first as widget_data for compatibility
                    widget_data = widgets_list[0]
                    widgets = widgets_list
                    logger.info(f"✅ Returning {len(widgets_list)} widgets: {[w.get('type') for w in widgets_list]}")
            
            # Legacy fallback block removed - ModelRouter handles all widget extraction via specialized services
            # Build response with extracted content from router
            response_kwargs = {
                "conversation_id": str(conversation.id) if conversation.id else None,
                "message_id": str(ai_message.id) if ai_message.id else None,
                "response": ai_response,
                "token_count": token_count,
                "processing_time_ms": processing_time,
                "model_used": config.config_data.get('model', 'gpt-4-turbo'),  # Full production model for authorized users
                "widget_data": widget_data,
                "widgets": widgets
            }
            
            # Include generated content if present (from ContentGenerationService)
            # Only check router_result if it was successfully created (not in fallback case)
            if router_result:
                if router_result.get("images"):
                    response_kwargs["images"] = router_result.get("images")
                if router_result.get("file_content"):
                    response_kwargs["file_content"] = router_result.get("file_content")
                    response_kwargs["filename"] = router_result.get("filename")
                if router_result.get("web_url"):
                    response_kwargs["web_url"] = router_result.get("web_url")
                    response_kwargs["file_id"] = router_result.get("file_id")
                if router_result.get("num_slides"):
                    response_kwargs["num_slides"] = router_result.get("num_slides")
            
            # Also extract file_content and filename from widget_data.data if present (for generated documents)
            # This ensures chat display works even if they're nested in widget_data
            if widget_data and isinstance(widget_data, dict) and widget_data.get("data"):
                widget_data_content = widget_data.get("data", {})
                if isinstance(widget_data_content, dict):
                    # Extract file_content and filename from widget_data.data if not already at top level
                    if widget_data_content.get("file_content") and not response_kwargs.get("file_content"):
                        response_kwargs["file_content"] = widget_data_content.get("file_content")
                        logger.info("📄 Extracted file_content from widget_data.data for chat display")
                    if widget_data_content.get("filename") and not response_kwargs.get("filename"):
                        response_kwargs["filename"] = widget_data_content.get("filename")
                        logger.info("📄 Extracted filename from widget_data.data for chat display")
                    # Also extract web_url if present
                    if widget_data_content.get("web_url") and not response_kwargs.get("web_url"):
                        response_kwargs["web_url"] = widget_data_content.get("web_url")
                        logger.info("☁️ Extracted web_url from widget_data.data for chat display")
            
            return AIAssistantChatResponse(**response_kwargs)
            
        except Exception as e:
            self.db.rollback()
            
            # Track failed usage
            if 'config' in locals() and config:
                self._track_usage(
                    teacher_id=teacher_id,
                    config_id=config.id,
                    usage_type=chat_request.conversation_type or "general_chat",
                    tokens_used=0,
                    processing_time_ms=0,
                    success=False,
                    error_message=str(e)
                )
            
            raise Exception(f"Failed to process AI chat request: {str(e)}")

    # ==================== TEMPLATE MANAGEMENT ====================
    
    def get_available_templates(
        self, 
        template_type: Optional[str] = None
    ) -> List[AIAssistantTemplateResponse]:
        """Get available AI assistant templates"""
        query = self.db.query(AIAssistantTemplate).filter(
            AIAssistantTemplate.is_active == True
        )
        
        if template_type:
            query = query.filter(AIAssistantTemplate.template_type == template_type)
        
        templates = query.order_by(asc(AIAssistantTemplate.template_name)).all()
        
        return [self._template_to_response(template) for template in templates]

    def use_template(
        self, 
        template_id: str, 
        variables: Dict[str, Any]
    ) -> str:
        """Use a template with variables to generate content"""
        template = self.db.query(AIAssistantTemplate).filter(
            AIAssistantTemplate.id == template_id
        ).first()
        
        if not template:
            raise Exception("Template not found")
        
        # Replace variables in template content
        content = template.template_content
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", str(value))
        
        # Update usage count
        template.usage_count += 1
        self.db.commit()
        
        return content

    # ==================== FEEDBACK MANAGEMENT ====================
    
    def submit_feedback(
        self, 
        teacher_id: str, 
        feedback_data: AIAssistantFeedbackCreate
    ) -> AIAssistantFeedbackResponse:
        """Submit feedback for an AI assistant interaction"""
        feedback = AIAssistantFeedback(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            conversation_id=feedback_data.conversation_id,
            message_id=feedback_data.message_id,
            feedback_type=feedback_data.feedback_type,
            feedback_value=feedback_data.feedback_value,
            feedback_text=feedback_data.feedback_text,
            is_helpful=feedback_data.is_helpful
        )
        
        self.db.add(feedback)
        self.db.commit()
        
        return self._feedback_to_response(feedback)

    def get_conversation_feedback(
        self, 
        conversation_id: str, 
        teacher_id: str
    ) -> List[AIAssistantFeedbackResponse]:
        """Get feedback for a conversation"""
        # Verify conversation ownership
        conversation = self.db.query(AIAssistantConversation).filter(
            and_(
                AIAssistantConversation.id == conversation_id,
                AIAssistantConversation.teacher_id == teacher_id
            )
        ).first()
        
        if not conversation:
            return []
        
        feedback = self.db.query(AIAssistantFeedback).filter(
            AIAssistantFeedback.conversation_id == conversation_id
        ).order_by(desc(AIAssistantFeedback.created_at)).all()
        
        return [self._feedback_to_response(f) for f in feedback]

    # ==================== ANALYTICS ====================
    
    def get_teacher_analytics(
        self, 
        teacher_id: str, 
        days: int = 30
    ) -> List[AIAssistantAnalyticsResponse]:
        """Get AI assistant analytics for a teacher"""
        start_date = date.today() - timedelta(days=days)
        
        analytics = self.db.query(AIAssistantAnalytics).filter(
            and_(
                AIAssistantAnalytics.teacher_id == teacher_id,
                AIAssistantAnalytics.analytics_date >= start_date
            )
        ).order_by(desc(AIAssistantAnalytics.analytics_date)).all()
        
        return [self._analytics_to_response(stat) for stat in analytics]

    def get_usage_summary(
        self, 
        teacher_id: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get usage summary for a teacher"""
        start_date = date.today() - timedelta(days=days)
        
        # Get total usage
        total_usage = self.db.query(
            func.sum(AIAssistantUsage.tokens_used).label('total_tokens'),
            func.sum(AIAssistantUsage.requests_count).label('total_requests'),
            func.sum(AIAssistantUsage.processing_time_ms).label('total_time'),
            func.avg(AIAssistantUsage.processing_time_ms).label('avg_time')
        ).filter(
            and_(
                AIAssistantUsage.teacher_id == teacher_id,
                AIAssistantUsage.usage_date >= start_date,
                AIAssistantUsage.success == True
            )
        ).first()
        
        # Get usage by type
        usage_by_type = self.db.query(
            AIAssistantUsage.usage_type,
            func.sum(AIAssistantUsage.requests_count).label('requests'),
            func.sum(AIAssistantUsage.tokens_used).label('tokens')
        ).filter(
            and_(
                AIAssistantUsage.teacher_id == teacher_id,
                AIAssistantUsage.usage_date >= start_date,
                AIAssistantUsage.success == True
            )
        ).group_by(AIAssistantUsage.usage_type).all()
        
        # Get satisfaction score
        satisfaction = self.db.query(
            func.avg(AIAssistantFeedback.feedback_value).label('avg_satisfaction')
        ).filter(
            and_(
                AIAssistantFeedback.teacher_id == teacher_id,
                AIAssistantFeedback.feedback_type == 'rating',
                AIAssistantFeedback.created_at >= datetime.utcnow() - timedelta(days=days)
            )
        ).scalar()
        
        return {
            "total_tokens": total_usage.total_tokens or 0,
            "total_requests": total_usage.total_requests or 0,
            "total_processing_time_ms": total_usage.total_time or 0,
            "average_response_time_ms": float(total_usage.avg_time or 0),
            "usage_by_type": {item.usage_type: {"requests": item.requests, "tokens": item.tokens} for item in usage_by_type},
            "satisfaction_score": float(satisfaction or 0),
            "period_days": days
        }

    # ==================== HELPER METHODS ====================
    
    def _get_default_config(
        self, 
        teacher_id: str, 
        conversation_type: str
    ) -> AIAssistantConfig:
        """Get or create default configuration for a teacher"""
        # Map conversation_type to assistant_type (database constraint uses 'general_assistant' not 'general_chat')
        assistant_type_map = {
            "general_chat": "general_assistant",
            "lesson_planning": "lesson_planning",
            "assessment_creation": "assessment_creation",
            "resource_generation": "resource_generation",
            "content_analysis": "content_analysis"
        }
        assistant_type = assistant_type_map.get(conversation_type, conversation_type)
        
        config = self.db.query(AIAssistantConfig).filter(
            and_(
                AIAssistantConfig.teacher_id == teacher_id,
                AIAssistantConfig.assistant_type == assistant_type,
                AIAssistantConfig.is_active == True
            )
        ).first()
        
        if not config:
            # Create default config with comprehensive system prompt
            # Import the enhanced system prompt (same as guest_chat.py and gpt_function_service.py)
            from app.core.ai_system_prompts import ENHANCED_SYSTEM_PROMPT
            comprehensive_system_prompt = ENHANCED_SYSTEM_PROMPT
            
            default_config_data = {
                "model": "gpt-4-turbo",  # Full production model for authorized users
                "temperature": 0.7,
                "max_tokens": 2000,
                "system_prompt": comprehensive_system_prompt
            }
            
            config = AIAssistantConfig(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                config_name=f"Default {assistant_type.replace('_', ' ').title()} Config",
                config_description=f"Default configuration for {assistant_type.replace('_', ' ')}",
                assistant_type=assistant_type,
                is_active=True,
                config_data=default_config_data
            )
            
            self.db.add(config)
            self.db.commit()
        
        return config

    def _track_usage(
        self, 
        teacher_id: str, 
        config_id: str,
        usage_type: str,
        tokens_used: int,
        processing_time_ms: int,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Track AI assistant usage"""
        usage = AIAssistantUsage(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            config_id=config_id,
            usage_type=usage_type,
            tokens_used=tokens_used,
            requests_count=1,
            processing_time_ms=processing_time_ms,
            success=success,
            error_message=error_message
        )
        
        self.db.add(usage)
        
        # Update daily analytics
        self._update_daily_analytics(teacher_id, usage_type, tokens_used, processing_time_ms, success)

    def _update_daily_analytics(
        self, 
        teacher_id: str, 
        usage_type: str,
        tokens_used: int,
        processing_time_ms: int,
        success: bool
    ) -> None:
        """Update daily analytics for AI assistant usage"""
        today = date.today()
        
        analytics = self.db.query(AIAssistantAnalytics).filter(
            and_(
                AIAssistantAnalytics.teacher_id == teacher_id,
                AIAssistantAnalytics.analytics_date == today
            )
        ).first()
        
        if analytics:
            # Update existing analytics
            analytics.total_requests += 1
            analytics.total_tokens_used += tokens_used
            analytics.total_processing_time_ms += processing_time_ms
            
            if success:
                analytics.successful_requests += 1
            else:
                analytics.failed_requests += 1
            
            analytics.average_response_time_ms = analytics.total_processing_time_ms / analytics.total_requests
            analytics.updated_at = datetime.utcnow()
        else:
            # Create new analytics
            analytics = AIAssistantAnalytics(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                analytics_date=today,
                total_requests=1,
                successful_requests=1 if success else 0,
                failed_requests=0 if success else 1,
                total_tokens_used=tokens_used,
                total_processing_time_ms=processing_time_ms,
                average_response_time_ms=processing_time_ms,
                most_used_type=usage_type
            )
            
            self.db.add(analytics)
        
        self.db.commit()

    # ==================== RESPONSE CONVERTERS ====================
    
    def _config_to_response(self, config: AIAssistantConfig) -> AIAssistantConfigResponse:
        """Convert config model to response"""
        return AIAssistantConfigResponse(
            id=str(config.id) if config.id else None,
            teacher_id=str(config.teacher_id) if config.teacher_id else None,
            config_name=config.config_name,
            config_description=config.config_description,
            assistant_type=config.assistant_type,
            is_active=config.is_active,
            config_data=config.config_data,
            created_at=config.created_at,
            updated_at=config.updated_at
        )

    def _conversation_to_response(self, conversation: AIAssistantConversation) -> AIAssistantConversationResponse:
        """Convert conversation model to response"""
        return AIAssistantConversationResponse(
            id=str(conversation.id) if conversation.id else None,
            teacher_id=str(conversation.teacher_id) if conversation.teacher_id else None,
            config_id=str(conversation.config_id) if conversation.config_id else None,
            conversation_title=conversation.conversation_title,
            conversation_type=conversation.conversation_type,
            is_active=conversation.is_active,
            metadata=conversation.metadata,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )

    def _message_to_response(self, message: AIAssistantMessage) -> AIAssistantMessageResponse:
        """Convert message model to response"""
        return AIAssistantMessageResponse(
            id=str(message.id) if message.id else None,
            conversation_id=str(message.conversation_id) if message.conversation_id else None,
            message_type=message.message_type,
            content=message.content,
            metadata=message.metadata,
            token_count=message.token_count,
            processing_time_ms=message.processing_time_ms,
            created_at=message.created_at
        )

    def _template_to_response(self, template: AIAssistantTemplate) -> AIAssistantTemplateResponse:
        """Convert template model to response"""
        return AIAssistantTemplateResponse(
            id=str(template.id) if template.id else None,
            template_name=template.template_name,
            template_description=template.template_description,
            template_type=template.template_type,
            template_content=template.template_content,
            template_variables=template.template_variables,
            is_system_template=template.is_system_template,
            is_active=template.is_active,
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    def _feedback_to_response(self, feedback: AIAssistantFeedback) -> AIAssistantFeedbackResponse:
        """Convert feedback model to response"""
        return AIAssistantFeedbackResponse(
            id=str(feedback.id) if feedback.id else None,
            teacher_id=str(feedback.teacher_id) if feedback.teacher_id else None,
            conversation_id=str(feedback.conversation_id) if feedback.conversation_id else None,
            message_id=str(feedback.message_id) if feedback.message_id else None,
            feedback_type=feedback.feedback_type,
            feedback_value=feedback.feedback_value,
            feedback_text=feedback.feedback_text,
            is_helpful=feedback.is_helpful,
            created_at=feedback.created_at
        )

    def _analytics_to_response(self, analytics: AIAssistantAnalytics) -> AIAssistantAnalyticsResponse:
        """Convert analytics model to response"""
        return AIAssistantAnalyticsResponse(
            id=str(analytics.id) if analytics.id else None,
            teacher_id=str(analytics.teacher_id) if analytics.teacher_id else None,
            analytics_date=analytics.analytics_date,
            total_requests=analytics.total_requests,
            successful_requests=analytics.successful_requests,
            failed_requests=analytics.failed_requests,
            total_tokens_used=analytics.total_tokens_used,
            total_processing_time_ms=analytics.total_processing_time_ms,
            average_response_time_ms=analytics.average_response_time_ms,
            most_used_type=analytics.most_used_type,
            satisfaction_score=analytics.satisfaction_score,
            created_at=analytics.created_at,
            updated_at=analytics.updated_at
        )
