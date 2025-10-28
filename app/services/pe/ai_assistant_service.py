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
import openai
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


class AIAssistantService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
            
            # Prepare messages for OpenAI
            messages = []
            
            # Add system message from config
            if config.config_data.get('system_prompt'):
                messages.append({
                    "role": "system",
                    "content": config.config_data['system_prompt']
                })
            
            # Add conversation history (reverse order for proper context)
            for msg in reversed(recent_messages):
                messages.append({
                    "role": msg.message_type,
                    "content": msg.content
                })
            
            # Call OpenAI API
            start_time = datetime.utcnow()
            response = self.openai_client.chat.completions.create(
                model=config.config_data.get('model', 'gpt-4'),
                messages=messages,
                temperature=config.config_data.get('temperature', 0.7),
                max_tokens=config.config_data.get('max_tokens', 2000)
            )
            end_time = datetime.utcnow()
            
            # Extract response
            ai_response = response.choices[0].message.content
            token_count = response.usage.total_tokens
            processing_time = int((end_time - start_time).total_seconds() * 1000)
            
            # Save AI response
            ai_message = AIAssistantMessage(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                message_type="assistant",
                content=ai_response,
                metadata={
                    "model": config.config_data.get('model', 'gpt-4'),
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
            
            return AIAssistantChatResponse(
                conversation_id=conversation.id,
                message_id=ai_message.id,
                response=ai_response,
                token_count=token_count,
                processing_time_ms=processing_time,
                model_used=config.config_data.get('model', 'gpt-4')
            )
            
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
        config = self.db.query(AIAssistantConfig).filter(
            and_(
                AIAssistantConfig.teacher_id == teacher_id,
                AIAssistantConfig.assistant_type == conversation_type,
                AIAssistantConfig.is_active == True
            )
        ).first()
        
        if not config:
            # Create default config
            default_config_data = {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000,
                "system_prompt": f"You are an expert AI assistant specializing in {conversation_type.replace('_', ' ')} for physical education teachers."
            }
            
            config = AIAssistantConfig(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                config_name=f"Default {conversation_type.replace('_', ' ').title()} Config",
                config_description=f"Default configuration for {conversation_type.replace('_', ' ')}",
                assistant_type=conversation_type,
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
            id=config.id,
            teacher_id=config.teacher_id,
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
            id=conversation.id,
            teacher_id=conversation.teacher_id,
            config_id=conversation.config_id,
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
            id=message.id,
            conversation_id=message.conversation_id,
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
            id=template.id,
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
            id=feedback.id,
            teacher_id=feedback.teacher_id,
            conversation_id=feedback.conversation_id,
            message_id=feedback.message_id,
            feedback_type=feedback.feedback_type,
            feedback_value=feedback.feedback_value,
            feedback_text=feedback.feedback_text,
            is_helpful=feedback.is_helpful,
            created_at=feedback.created_at
        )

    def _analytics_to_response(self, analytics: AIAssistantAnalytics) -> AIAssistantAnalyticsResponse:
        """Convert analytics model to response"""
        return AIAssistantAnalyticsResponse(
            id=analytics.id,
            teacher_id=analytics.teacher_id,
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
