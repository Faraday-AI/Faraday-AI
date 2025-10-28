"""
AI Assistant Models
SQLAlchemy models for AI assistant integration
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, Date, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.models.shared_base import SharedBase as Base


class AIAssistantConfig(Base):
    """AI Assistant Configuration"""
    __tablename__ = "ai_assistant_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    config_name = Column(String(255), nullable=False)
    config_description = Column(Text)
    assistant_type = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    config_data = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="ai_assistant_configs")
    conversations = relationship("app.models.ai_assistant.AIAssistantConversation", back_populates="config")
    usage_records = relationship("app.models.ai_assistant.AIAssistantUsage", back_populates="config")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "assistant_type IN ('lesson_planning', 'assessment_creation', 'resource_generation', 'content_analysis', 'general_assistant')",
            name="ck_ai_configs_assistant_type"
        ),
        UniqueConstraint("teacher_id", "config_name", name="ux_ai_configs_teacher_name")
    )


class AIAssistantConversation(Base):
    """AI Assistant Conversation"""
    __tablename__ = "ai_assistant_conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    config_id = Column(UUID(as_uuid=True), ForeignKey("ai_assistant_configs.id", ondelete="SET NULL"))
    conversation_title = Column(String(255))
    conversation_type = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    conversation_metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="ai_conversations")
    config = relationship("app.models.ai_assistant.AIAssistantConfig", back_populates="conversations")
    messages = relationship("app.models.ai_assistant.AIAssistantMessage", back_populates="conversation", cascade="all, delete-orphan")
    feedback = relationship("app.models.ai_assistant.AIAssistantFeedback", back_populates="conversation")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "conversation_type IN ('lesson_planning', 'assessment_creation', 'resource_generation', 'content_analysis', 'general_chat')",
            name="ck_ai_conversations_type"
        ),
    )


class AIAssistantMessage(Base):
    """AI Assistant Message"""
    __tablename__ = "ai_assistant_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_assistant_conversations.id", ondelete="CASCADE"), nullable=False)
    message_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    conversation_metadata = Column(JSONB, default={})
    token_count = Column(Integer, default=0)
    processing_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    conversation = relationship("app.models.ai_assistant.AIAssistantConversation", back_populates="messages")
    feedback = relationship("app.models.ai_assistant.AIAssistantFeedback", back_populates="message")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "message_type IN ('user', 'assistant', 'system')",
            name="ck_ai_messages_type"
        ),
    )


class AIAssistantUsage(Base):
    """AI Assistant Usage Tracking"""
    __tablename__ = "ai_assistant_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    config_id = Column(UUID(as_uuid=True), ForeignKey("ai_assistant_configs.id", ondelete="SET NULL"))
    usage_type = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=False, default=0)
    requests_count = Column(Integer, nullable=False, default=1)
    processing_time_ms = Column(Integer, default=0)
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text)
    conversation_metadata = Column(JSONB, default={})
    usage_date = Column(Date, nullable=False, server_default=func.current_date())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="ai_usage")
    config = relationship("app.models.ai_assistant.AIAssistantConfig", back_populates="usage_records")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "usage_type IN ('lesson_planning', 'assessment_creation', 'resource_generation', 'content_analysis', 'general_chat')",
            name="ck_ai_usage_type"
        ),
    )


class AIAssistantTemplate(Base):
    """AI Assistant Template"""
    __tablename__ = "ai_assistant_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=True)
    template_name = Column(String(255), nullable=False)
    template_description = Column(Text)
    template_type = Column(String(100), nullable=False)
    template_content = Column(Text, nullable=False)
    template_variables = Column(JSONB, default={})
    is_system_template = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    usage_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="ai_templates")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "template_type IN ('lesson_planning', 'assessment_creation', 'resource_generation', 'content_analysis', 'general_assistant')",
            name="ck_ai_templates_type"
        ),
        UniqueConstraint("template_name", name="ux_ai_templates_name")
    )


class AIAssistantFeedback(Base):
    """AI Assistant Feedback"""
    __tablename__ = "ai_assistant_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_assistant_conversations.id", ondelete="SET NULL"))
    message_id = Column(UUID(as_uuid=True), ForeignKey("ai_assistant_messages.id", ondelete="SET NULL"))
    feedback_type = Column(String(50), nullable=False)
    feedback_value = Column(Integer)
    feedback_text = Column(Text)
    is_helpful = Column(Boolean)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="ai_feedback")
    conversation = relationship("app.models.ai_assistant.AIAssistantConversation", back_populates="feedback")
    message = relationship("app.models.ai_assistant.AIAssistantMessage", back_populates="feedback")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "feedback_type IN ('thumbs_up', 'thumbs_down', 'rating', 'comment')",
            name="ck_ai_feedback_type"
        ),
        CheckConstraint(
            "feedback_value IS NULL OR (feedback_value >= 1 AND feedback_value <= 5)",
            name="ck_ai_feedback_value"
        ),
    )


class AIAssistantAnalytics(Base):
    """AI Assistant Analytics"""
    __tablename__ = "ai_assistant_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    analytics_date = Column(Date, nullable=False, server_default=func.current_date())
    total_requests = Column(Integer, nullable=False, default=0)
    successful_requests = Column(Integer, nullable=False, default=0)
    failed_requests = Column(Integer, nullable=False, default=0)
    total_tokens_used = Column(Integer, nullable=False, default=0)
    total_processing_time_ms = Column(Integer, nullable=False, default=0)
    average_response_time_ms = Column(Numeric(10, 2), default=0)
    most_used_type = Column(String(100))
    satisfaction_score = Column(Numeric(3, 2))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="ai_analytics")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "satisfaction_score IS NULL OR (satisfaction_score >= 1.0 AND satisfaction_score <= 5.0)",
            name="ck_ai_analytics_satisfaction"
        ),
        UniqueConstraint("teacher_id", "analytics_date", name="ux_ai_analytics_teacher_date")
    )
