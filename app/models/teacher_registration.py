"""
Teacher Registration Model

This module defines the TeacherRegistration model for the beta teacher system.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.shared_base import SharedBase as Base
import uuid


class TeacherRegistration(Base):
    """Teacher registration model for beta version"""
    __tablename__ = 'teacher_registrations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    school_name = Column(String(255))
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    educational_resources = relationship("app.models.resource_management.EducationalResource", back_populates="teacher")
    resource_usage = relationship("app.models.resource_management.ResourceUsage", back_populates="teacher")
    resource_reviews = relationship("app.models.resource_management.ResourceReview", back_populates="teacher")
    resource_favorites = relationship("app.models.resource_management.ResourceFavorite", back_populates="teacher")
    resource_downloads = relationship("app.models.resource_management.ResourceDownload", back_populates="teacher")
    resource_collections = relationship("app.models.resource_management.ResourceCollection", back_populates="teacher")
    owned_resources = relationship("app.models.resource_management.ResourceSharing", foreign_keys="[app.models.resource_management.ResourceSharing.shared_by_teacher_id]", back_populates="shared_by_teacher")
    received_resources = relationship("app.models.resource_management.ResourceSharing", foreign_keys="[app.models.resource_management.ResourceSharing.shared_with_teacher_id]", back_populates="shared_with_teacher")
    shared_collections = relationship("app.models.resource_management.CollectionSharing", foreign_keys="[app.models.resource_management.CollectionSharing.shared_by_teacher_id]", back_populates="shared_by_teacher")
    received_collections = relationship("app.models.resource_management.CollectionSharing", foreign_keys="[app.models.resource_management.CollectionSharing.shared_with_teacher_id]", back_populates="shared_with_teacher")
    
    # Lesson Plan Builder relationships
    lesson_plan_templates = relationship("app.models.lesson_plan_builder.LessonPlanTemplate", back_populates="teacher")
    ai_suggestions = relationship("app.models.lesson_plan_builder.AILessonSuggestion", back_populates="teacher")
    shared_templates = relationship("app.models.lesson_plan_builder.LessonPlanSharing", foreign_keys="[app.models.lesson_plan_builder.LessonPlanSharing.shared_by_teacher_id]", back_populates="shared_by_teacher")
    received_templates = relationship("app.models.lesson_plan_builder.LessonPlanSharing", foreign_keys="[app.models.lesson_plan_builder.LessonPlanSharing.shared_with_teacher_id]", back_populates="shared_with_teacher")
    template_usage = relationship("app.models.lesson_plan_builder.LessonPlanUsage", back_populates="teacher")
    
    # Assessment Tools relationships
    assessment_templates = relationship("app.models.assessment_tools.AssessmentTemplate", back_populates="teacher")
    assessment_template_sharing = relationship("app.models.assessment_tools.AssessmentTemplateSharing", foreign_keys="[app.models.assessment_tools.AssessmentTemplateSharing.shared_by_teacher_id]", back_populates="shared_by_teacher")
    received_assessment_templates = relationship("app.models.assessment_tools.AssessmentTemplateSharing", foreign_keys="[app.models.assessment_tools.AssessmentTemplateSharing.shared_with_teacher_id]", back_populates="shared_with_teacher")
    assessment_template_usage = relationship("app.models.assessment_tools.AssessmentTemplateUsage", back_populates="teacher")
    
    # AI Assistant relationships
    ai_assistant_configs = relationship("app.models.ai_assistant.AIAssistantConfig", back_populates="teacher")
    ai_conversations = relationship("app.models.ai_assistant.AIAssistantConversation", back_populates="teacher")
    ai_usage = relationship("app.models.ai_assistant.AIAssistantUsage", back_populates="teacher")
    ai_templates = relationship("app.models.ai_assistant.AIAssistantTemplate", back_populates="teacher")
    ai_feedback = relationship("app.models.ai_assistant.AIAssistantFeedback", back_populates="teacher")
    ai_analytics = relationship("app.models.ai_assistant.AIAssistantAnalytics", back_populates="teacher")
    
    # Beta Testing relationships
    beta_participants = relationship("app.models.beta_testing.BetaTestingParticipant", back_populates="teacher")
