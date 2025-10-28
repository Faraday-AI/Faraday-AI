"""
SQLAlchemy models for Lesson Plan Builder
Defines database models for AI-assisted lesson plan creation and management
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, ARRAY, DECIMAL, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.shared_base import SharedBase as Base
import uuid


class LessonPlanTemplate(Base):
    """Lesson plan templates created by teachers"""
    __tablename__ = "lesson_plan_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(20), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    learning_objectives = Column(ARRAY(Text), nullable=False)
    materials_needed = Column(ARRAY(Text), nullable=False, default=[])
    safety_considerations = Column(ARRAY(Text), nullable=False, default=[])
    assessment_methods = Column(ARRAY(Text), nullable=False, default=[])
    ai_generated = Column(Boolean, default=True)
    template_type = Column(String(50), default="standard")
    difficulty_level = Column(String(20), default="intermediate")
    equipment_required = Column(ARRAY(Text), default=[])
    space_requirements = Column(String(100), default="gymnasium")
    weather_dependent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    rating_average = Column(DECIMAL(3, 2), default=0.00)
    rating_count = Column(Integer, default=0)

    # Relationships
    activities = relationship("app.models.lesson_plan_builder.LessonPlanActivity", back_populates="template", cascade="all, delete-orphan")
    sharing_records = relationship("app.models.lesson_plan_builder.LessonPlanSharing", back_populates="template", cascade="all, delete-orphan")
    usage_records = relationship("app.models.lesson_plan_builder.LessonPlanUsage", back_populates="template", cascade="all, delete-orphan")
    category_associations = relationship("app.models.lesson_plan_builder.TemplateCategoryAssociation", back_populates="template", cascade="all, delete-orphan")
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="lesson_plan_templates")

    # Indexes
    __table_args__ = (
        Index("idx_lesson_plan_templates_teacher_id", "teacher_id"),
        Index("idx_lesson_plan_templates_subject", "subject"),
        Index("idx_lesson_plan_templates_grade_level", "grade_level"),
        Index("idx_lesson_plan_templates_public", "is_public"),
        Index("idx_lesson_plan_templates_created_at", "created_at"),
        Index("idx_lesson_plan_templates_template_type", "template_type"),
        Index("idx_lesson_plan_templates_difficulty", "difficulty_level"),
    )


class LessonPlanActivity(Base):
    """Individual activities within a lesson plan (beta teacher system)"""
    __tablename__ = "beta_lesson_plan_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("lesson_plan_templates.id", ondelete="CASCADE"), nullable=False)
    activity_name = Column(String(255), nullable=False)
    activity_description = Column(Text, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    activity_type = Column(String(50), nullable=False)
    equipment_needed = Column(ARRAY(Text), default=[])
    space_required = Column(String(100), default="gymnasium")
    safety_notes = Column(ARRAY(Text), default=[])
    instructions = Column(ARRAY(Text), nullable=False)
    modifications = Column(ARRAY(Text), default=[])
    success_criteria = Column(ARRAY(Text), default=[])
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template = relationship("app.models.lesson_plan_builder.LessonPlanTemplate", back_populates="activities")

    # Indexes
    __table_args__ = (
        Index("idx_lesson_plan_activities_template_id", "template_id"),
        Index("idx_lesson_plan_activities_type", "activity_type"),
        Index("idx_lesson_plan_activities_order", "order_index"),
    )


class AILessonSuggestion(Base):
    """AI-generated lesson plan suggestions"""
    __tablename__ = "ai_lesson_suggestions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    suggestion_type = Column(String(50), nullable=False)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(20), nullable=False)
    context = Column(Text, nullable=False)
    ai_suggestion = Column(Text, nullable=False)
    confidence_score = Column(DECIMAL(3, 2), default=0.00)
    tags = Column(ARRAY(Text), default=[])
    is_applied = Column(Boolean, default=False)
    applied_at = Column(DateTime(timezone=True))
    feedback_rating = Column(Integer)
    feedback_comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="ai_suggestions")

    # Indexes
    __table_args__ = (
        Index("idx_ai_suggestions_teacher_id", "teacher_id"),
        Index("idx_ai_suggestions_type", "suggestion_type"),
        Index("idx_ai_suggestions_subject", "subject"),
        Index("idx_ai_suggestions_applied", "is_applied"),
        Index("idx_ai_suggestions_created_at", "created_at"),
    )


class LessonPlanSharing(Base):
    """Template sharing between teachers"""
    __tablename__ = "lesson_plan_sharing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("lesson_plan_templates.id", ondelete="CASCADE"), nullable=False)
    shared_by_teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    shared_with_teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"))
    sharing_type = Column(String(20), nullable=False)
    access_level = Column(String(20), default="view")
    shared_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    feedback_rating = Column(Integer)
    feedback_comment = Column(Text)

    # Relationships
    template = relationship("app.models.lesson_plan_builder.LessonPlanTemplate", back_populates="sharing_records")
    shared_by_teacher = relationship("app.models.teacher_registration.TeacherRegistration", foreign_keys=[shared_by_teacher_id], back_populates="shared_templates")
    shared_with_teacher = relationship("app.models.teacher_registration.TeacherRegistration", foreign_keys=[shared_with_teacher_id], back_populates="received_templates")

    # Indexes
    __table_args__ = (
        Index("idx_lesson_plan_sharing_template_id", "template_id"),
        Index("idx_lesson_plan_sharing_shared_by", "shared_by_teacher_id"),
        Index("idx_lesson_plan_sharing_shared_with", "shared_with_teacher_id"),
        Index("idx_lesson_plan_sharing_type", "sharing_type"),
        Index("idx_lesson_plan_sharing_active", "is_active"),
    )


class LessonPlanUsage(Base):
    """Template usage tracking for analytics"""
    __tablename__ = "lesson_plan_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("lesson_plan_templates.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    usage_type = Column(String(50), nullable=False)
    usage_date = Column(DateTime(timezone=True), server_default=func.now())
    modifications_made = Column(ARRAY(Text), default=[])
    effectiveness_rating = Column(Integer)
    effectiveness_notes = Column(Text)
    student_engagement_level = Column(String(20))
    completion_percentage = Column(DECIMAL(5, 2))
    time_spent_minutes = Column(Integer)
    issues_encountered = Column(ARRAY(Text), default=[])
    improvements_suggested = Column(ARRAY(Text), default=[])

    # Relationships
    template = relationship("app.models.lesson_plan_builder.LessonPlanTemplate", back_populates="usage_records")
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="template_usage")

    # Indexes
    __table_args__ = (
        Index("idx_lesson_plan_usage_template_id", "template_id"),
        Index("idx_lesson_plan_usage_teacher_id", "teacher_id"),
        Index("idx_lesson_plan_usage_date", "usage_date"),
        Index("idx_lesson_plan_usage_type", "usage_type"),
    )


class LessonPlanCategory(Base):
    """Categories for organizing lesson plan templates"""
    __tablename__ = "lesson_plan_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey("lesson_plan_categories.id", ondelete="SET NULL"))
    subject = Column(String(100), nullable=False)
    grade_level_range = Column(String(20), nullable=False)
    icon_name = Column(String(50), default="default")
    color_code = Column(String(7), default="#007bff")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    parent_category = relationship("app.models.lesson_plan_builder.LessonPlanCategory", remote_side=[id], back_populates="subcategories")
    subcategories = relationship("app.models.lesson_plan_builder.LessonPlanCategory", back_populates="parent_category")
    template_associations = relationship("app.models.lesson_plan_builder.TemplateCategoryAssociation", back_populates="category", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_lesson_plan_categories_subject", "subject"),
        Index("idx_lesson_plan_categories_active", "is_active"),
        Index("idx_lesson_plan_categories_parent", "parent_category_id"),
    )


class TemplateCategoryAssociation(Base):
    """Many-to-many relationship between templates and categories"""
    __tablename__ = "template_category_associations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("lesson_plan_templates.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("lesson_plan_categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template = relationship("app.models.lesson_plan_builder.LessonPlanTemplate", back_populates="category_associations")
    category = relationship("app.models.lesson_plan_builder.LessonPlanCategory", back_populates="template_associations")

    # Indexes
    __table_args__ = (
        Index("idx_template_category_template_id", "template_id"),
        Index("idx_template_category_category_id", "category_id"),
        UniqueConstraint("template_id", "category_id", name="ux_template_category_unique"),
    )
