"""
GPT Models

This module defines the database models for GPT categories, subscriptions,
and related functionality in the Faraday AI Dashboard.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Enum, Table, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.shared_base import SharedBase
from .association_tables import gpt_sharing, dashboard_context_gpts
from .category import Category

class GPTCategory(enum.Enum):
    """Enumeration of GPT categories."""
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"
    PARENT = "parent"
    ADDITIONAL = "additional"
    # Extensible for future categories

class GPTType(enum.Enum):
    """Enumeration of GPT types within categories."""
    # Teacher GPTs
    MATH_TEACHER = "math_teacher"
    SCIENCE_TEACHER = "science_teacher"
    LANGUAGE_ARTS_TEACHER = "language_arts_teacher"
    HISTORY_TEACHER = "history_teacher"
    PHYSICAL_ED_TEACHER = "physical_ed_teacher"
    ADMIN_ASSISTANT = "admin_assistant"
    
    # Student GPTs
    MATH_TUTOR = "math_tutor"
    SCIENCE_TUTOR = "science_tutor"
    LANGUAGE_ARTS_TUTOR = "language_arts_tutor"
    HISTORY_TUTOR = "history_tutor"
    STUDY_SKILLS_COACH = "study_skills_coach"
    WRITING_ASSISTANT = "writing_assistant"
    
    # Additional Service GPTs
    LEARNING_ANALYTICS = "learning_analytics"
    CONTENT_GENERATION = "content_generation"
    ADAPTIVE_LEARNING = "adaptive_learning"
    ASSESSMENT_GRADING = "assessment_grading"
    MEMORY_CONTEXT = "memory_context"
    LMS_INTEGRATION = "lms_integration"
    COLLABORATION = "collaboration"
    RESOURCE_RECOMMENDATION = "resource_recommendation"
    MULTIMEDIA_PROCESSING = "multimedia_processing"
    TRANSLATION_LOCALIZATION = "translation_localization"
    CALENDAR_SCHEDULING = "calendar_scheduling"
    FILE_PROCESSING = "file_processing"
    COMMUNICATION = "communication"
    EMOTION_FEEDBACK = "emotion_feedback"
    
    # Parent GPTs (placeholder for future expansion)
    PARENT_COMMUNICATION = "parent_communication"
    PROGRESS_TRACKING = "progress_tracking"
    
    # Extensible for future GPT types

class GPTDefinition(SharedBase):
    """Model for storing GPT model definitions and configurations."""
    __tablename__ = "gpt_definitions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # e.g., 'gpt-4', 'gpt-3.5-turbo'
    version = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(GPTCategory), nullable=True)
    type = Column(Enum(GPTType), nullable=True)
    
    # Configuration
    max_tokens = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    top_p = Column(Float, nullable=False)
    frequency_penalty = Column(Float, nullable=False)
    presence_penalty = Column(Float, nullable=False)
    
    # Capabilities and limitations
    capabilities = Column(JSON, nullable=True)  # List of supported features
    limitations = Column(JSON, nullable=True)  # List of known limitations
    context_window = Column(Integer, nullable=False)  # Maximum context length
    
    # Usage tracking
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("dashboard_users.id", ondelete="CASCADE"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Relationships
    # user = relationship("app.dashboard.models.user.DashboardUser", back_populates="gpt_definitions", foreign_keys=[user_id])
    project = relationship("DashboardProject", back_populates="gpt_definitions")
    organization = relationship("Organization", back_populates="gpt_definitions")
    contexts = relationship("app.dashboard.models.context.GPTContext", secondary=dashboard_context_gpts, back_populates="active_gpts")
    performance_metrics = relationship("GPTPerformance", back_populates="model")
    context_data = relationship("app.models.gpt.context.models.ContextData", back_populates="gpt")
    subscriptions = relationship("DashboardGPTSubscription", back_populates="gpt_definition")
    
    # Additional metadata
    meta_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DashboardGPTSubscription(SharedBase):
    """Model for Dashboard GPT subscriptions."""
    __tablename__ = "dashboard_gpt_subscriptions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    gpt_definition_id = Column(Integer, ForeignKey("gpt_definitions.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    model = Column(String, nullable=False)
    configuration = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("app.dashboard.models.user.DashboardUser", back_populates="dashboard_gpt_subscriptions")
    organization = relationship("Organization", back_populates="dashboard_gpt_subscriptions")
    gpt_definition = relationship("GPTDefinition", back_populates="subscriptions")
    # shared_with = relationship("app.dashboard.models.user.DashboardUser", secondary=gpt_sharing, back_populates="shared_gpts")
    usage = relationship("GPTUsage", back_populates="subscription")
    analytics = relationship("GPTAnalytics", back_populates="subscription")
    feedback = relationship("GPTFeedback", back_populates="subscription")
    performance_metrics = relationship("GPTPerformance", back_populates="subscription")
    usage_history = relationship("GPTUsageHistory", back_populates="subscription")
    categories = relationship("Category", secondary="gpt_categories", back_populates="gpts")
    versions = relationship("GPTVersion", back_populates="subscription")
    webhooks = relationship("Webhook", back_populates="subscription")

class GPTUsage(SharedBase):
    """Model for GPT usage tracking."""
    __tablename__ = "gpt_usage"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    subscription_id = Column(Integer, ForeignKey("dashboard_gpt_subscriptions.id"), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("app.dashboard.models.user.DashboardUser", back_populates="gpt_usage")
    organization = relationship("Organization", back_populates="gpt_usage")
    subscription = relationship("DashboardGPTSubscription", back_populates="usage")

class GPTIntegration(SharedBase):
    """Model for GPT integrations."""
    __tablename__ = "dashboard_gpt_integrations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    integration_type = Column(String, nullable=False)
    configuration = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("app.dashboard.models.user.DashboardUser", back_populates="gpt_integrations")
    organization = relationship("Organization", back_populates="gpt_integrations")

class GPTAnalytics(SharedBase):
    """Model for GPT analytics."""
    __tablename__ = "gpt_analytics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    subscription_id = Column(Integer, ForeignKey("dashboard_gpt_subscriptions.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("app.dashboard.models.user.DashboardUser", back_populates="gpt_analytics")
    organization = relationship("Organization", back_populates="gpt_analytics")
    subscription = relationship("DashboardGPTSubscription", back_populates="analytics")

class GPTFeedback(SharedBase):
    """Model for GPT feedback."""
    __tablename__ = "gpt_feedback"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    subscription_id = Column(Integer, ForeignKey("dashboard_gpt_subscriptions.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("app.dashboard.models.user.DashboardUser", back_populates="gpt_feedback")
    organization = relationship("Organization", back_populates="gpt_feedback")
    subscription = relationship("DashboardGPTSubscription", back_populates="feedback")

class GPTPerformance(SharedBase):
    """Performance metrics for GPT subscriptions."""
    __tablename__ = "gpt_performance"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)  # Changed from String to Integer
    subscription_id = Column(Integer, ForeignKey("dashboard_gpt_subscriptions.id"), nullable=False)  # Changed from String to Integer
    model_id = Column(Integer, ForeignKey("gpt_definitions.id"), nullable=False)  # Fixed foreign key reference
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)  # Added missing foreign key
    metrics = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Float)  # Added response time tracking
    error_rate = Column(Float)  # Added error rate tracking
    usage_count = Column(Integer)  # Added usage count tracking

    # Relationships
    subscription = relationship("DashboardGPTSubscription", back_populates="performance_metrics")
    model = relationship("app.dashboard.models.gpt_models.GPTDefinition", back_populates="performance_metrics")  # Fixed relationship reference
    user = relationship("app.dashboard.models.user.DashboardUser", back_populates="gpt_performance")
    
    # Additional metadata
    meta_data = Column(JSON)

class GPTUsageHistory(SharedBase):
    """Model for tracking GPT usage history."""
    __tablename__ = "dashboard_gpt_usage_history"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("dashboard_gpt_subscriptions.id"), nullable=False)
    interaction_type = Column(String, nullable=False)  # API call, function call, etc.
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscription = relationship("DashboardGPTSubscription", back_populates="usage_history")

# Re-export the classes
__all__ = [
    'GPTCategory',
    'GPTType',
    'GPTDefinition',
    'DashboardGPTSubscription',
    'GPTUsage',
    'GPTIntegration',
    'GPTAnalytics',
    'GPTFeedback',
    'GPTPerformance',
    'GPTUsageHistory'
] 