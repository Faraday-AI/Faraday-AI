"""
SQLAlchemy models for Assessment Tools
Defines database models for assessment template creation and management
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, ARRAY, DECIMAL, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.shared_base import SharedBase as Base
import uuid


class AssessmentTemplate(Base):
    """Assessment templates created by teachers"""
    __tablename__ = "assessment_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(20), nullable=False)
    assessment_type = Column(String(50), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    total_points = Column(Integer, nullable=False, default=100)
    instructions = Column(Text, nullable=False)
    materials_needed = Column(ARRAY(Text), default=[])
    safety_considerations = Column(ARRAY(Text), default=[])
    ai_generated = Column(Boolean, default=True)
    difficulty_level = Column(String(20), default="intermediate")
    equipment_required = Column(ARRAY(Text), default=[])
    space_requirements = Column(String(100), default="gymnasium")
    weather_dependent = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    rating_average = Column(DECIMAL(3, 2), default=0.00)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    criteria = relationship("app.models.assessment_tools.AssessmentCriteria", back_populates="template", cascade="all, delete-orphan")
    rubrics = relationship("app.models.assessment_tools.AssessmentRubric", back_populates="template", cascade="all, delete-orphan")
    questions = relationship("app.models.assessment_tools.AssessmentQuestion", back_populates="template", cascade="all, delete-orphan")
    checklists = relationship("app.models.assessment_tools.AssessmentChecklist", back_populates="template", cascade="all, delete-orphan")
    standards = relationship("app.models.assessment_tools.AssessmentStandard", back_populates="template", cascade="all, delete-orphan")
    sharing_records = relationship("app.models.assessment_tools.AssessmentTemplateSharing", back_populates="template", cascade="all, delete-orphan")
    usage_records = relationship("app.models.assessment_tools.AssessmentTemplateUsage", back_populates="template", cascade="all, delete-orphan")
    category_associations = relationship("app.models.assessment_tools.AssessmentTemplateCategoryAssociation", back_populates="template", cascade="all, delete-orphan")
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="assessment_templates")

    # Indexes
    __table_args__ = (
        Index("idx_assessment_templates_teacher_id", "teacher_id"),
        Index("idx_assessment_templates_subject", "subject"),
        Index("idx_assessment_templates_grade_level", "grade_level"),
        Index("idx_assessment_templates_type", "assessment_type"),
        Index("idx_assessment_templates_public", "is_public"),
        Index("idx_assessment_templates_created_at", "created_at"),
        Index("idx_assessment_templates_difficulty", "difficulty_level"),
    )


class AssessmentCriteria(Base):
    """Specific criteria being assessed"""
    __tablename__ = "assessment_criteria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("assessment_templates.id", ondelete="CASCADE"), nullable=False)
    criterion_name = Column(String(255), nullable=False)
    criterion_description = Column(Text, nullable=False)
    max_points = Column(Integer, nullable=False)
    weight_percentage = Column(DECIMAL(5, 2), nullable=False)
    assessment_method = Column(String(50), nullable=False)
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template = relationship("app.models.assessment_tools.AssessmentTemplate", back_populates="criteria")
    rubrics = relationship("app.models.assessment_tools.AssessmentRubric", back_populates="criteria", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_assessment_criteria_template_id", "template_id"),
        Index("idx_assessment_criteria_order", "order_index"),
        Index("idx_assessment_criteria_method", "assessment_method"),
    )


class AssessmentRubric(Base):
    """Detailed scoring rubrics"""
    __tablename__ = "assessment_rubrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("assessment_templates.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(UUID(as_uuid=True), ForeignKey("assessment_criteria.id", ondelete="CASCADE"))
    rubric_name = Column(String(255), nullable=False)
    rubric_description = Column(Text)
    performance_levels = Column(ARRAY(Text), nullable=False)
    performance_descriptions = Column(ARRAY(Text), nullable=False)
    point_values = Column(ARRAY(Integer), nullable=False)
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template = relationship("app.models.assessment_tools.AssessmentTemplate", back_populates="rubrics")
    criteria = relationship("app.models.assessment_tools.AssessmentCriteria", back_populates="rubrics")

    # Indexes
    __table_args__ = (
        Index("idx_assessment_rubrics_template_id", "template_id"),
        Index("idx_assessment_rubrics_criterion_id", "criterion_id"),
        Index("idx_assessment_rubrics_order", "order_index"),
    )


class AssessmentQuestion(Base):
    """Questions for written/verbal assessments"""
    __tablename__ = "assessment_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("assessment_templates.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)
    correct_answer = Column(Text)
    possible_answers = Column(ARRAY(Text))
    points = Column(Integer, nullable=False)
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template = relationship("app.models.assessment_tools.AssessmentTemplate", back_populates="questions")

    # Indexes
    __table_args__ = (
        Index("idx_assessment_questions_template_id", "template_id"),
        Index("idx_assessment_questions_type", "question_type"),
        Index("idx_assessment_questions_order", "order_index"),
    )


class AssessmentChecklist(Base):
    """Checklists for observational assessments"""
    __tablename__ = "assessment_checklists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("assessment_templates.id", ondelete="CASCADE"), nullable=False)
    checklist_item = Column(String(255), nullable=False)
    item_description = Column(Text)
    is_required = Column(Boolean, default=True)
    points = Column(Integer, nullable=False)
    order_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template = relationship("app.models.assessment_tools.AssessmentTemplate", back_populates="checklists")

    # Indexes
    __table_args__ = (
        Index("idx_assessment_checklists_template_id", "template_id"),
        Index("idx_assessment_checklists_order", "order_index"),
        Index("idx_assessment_checklists_required", "is_required"),
    )


class AssessmentTemplateSharing(Base):
    """Template sharing between teachers"""
    __tablename__ = "assessment_template_sharing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("assessment_templates.id", ondelete="CASCADE"), nullable=False)
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
    template = relationship("app.models.assessment_tools.AssessmentTemplate", back_populates="sharing_records")
    shared_by_teacher = relationship("app.models.teacher_registration.TeacherRegistration", foreign_keys=[shared_by_teacher_id], back_populates="assessment_template_sharing")
    shared_with_teacher = relationship("app.models.teacher_registration.TeacherRegistration", foreign_keys=[shared_with_teacher_id], back_populates="received_assessment_templates")

    # Indexes
    __table_args__ = (
        Index("idx_assessment_template_sharing_template_id", "template_id"),
        Index("idx_assessment_template_sharing_shared_by", "shared_by_teacher_id"),
        Index("idx_assessment_template_sharing_shared_with", "shared_with_teacher_id"),
        Index("idx_assessment_template_sharing_type", "sharing_type"),
        Index("idx_assessment_template_sharing_active", "is_active"),
    )


class AssessmentTemplateUsage(Base):
    """Template usage tracking for analytics"""
    __tablename__ = "assessment_template_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("assessment_templates.id", ondelete="CASCADE"), nullable=False)
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
    template = relationship("app.models.assessment_tools.AssessmentTemplate", back_populates="usage_records")
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="assessment_template_usage")

    # Indexes
    __table_args__ = (
        Index("idx_assessment_template_usage_template_id", "template_id"),
        Index("idx_assessment_template_usage_teacher_id", "teacher_id"),
        Index("idx_assessment_template_usage_date", "usage_date"),
        Index("idx_assessment_template_usage_type", "usage_type"),
    )


class AssessmentCategory(Base):
    """Categories for organizing assessment templates"""
    __tablename__ = "assessment_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey("assessment_categories.id", ondelete="SET NULL"))
    subject = Column(String(100), nullable=False)
    grade_level_range = Column(String(20), nullable=False)
    icon_name = Column(String(50), default="default")
    color_code = Column(String(7), default="#007bff")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    parent_category = relationship("app.models.assessment_tools.AssessmentCategory", remote_side=[id], back_populates="subcategories")
    subcategories = relationship("app.models.assessment_tools.AssessmentCategory", back_populates="parent_category")
    template_associations = relationship("app.models.assessment_tools.AssessmentTemplateCategoryAssociation", back_populates="category", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_assessment_categories_subject", "subject"),
        Index("idx_assessment_categories_active", "is_active"),
        Index("idx_assessment_categories_parent", "parent_category_id"),
    )


class AssessmentTemplateCategoryAssociation(Base):
    """Many-to-many relationship between templates and categories"""
    __tablename__ = "assessment_template_category_associations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("assessment_templates.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("assessment_categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template = relationship("app.models.assessment_tools.AssessmentTemplate", back_populates="category_associations")
    category = relationship("app.models.assessment_tools.AssessmentCategory", back_populates="template_associations")

    # Indexes
    __table_args__ = (
        Index("idx_assessment_template_category_template_id", "template_id"),
        Index("idx_assessment_template_category_category_id", "category_id"),
        UniqueConstraint("template_id", "category_id", name="ux_assessment_template_category_unique"),
    )


class AssessmentStandard(Base):
    """Educational standards alignment"""
    __tablename__ = "assessment_standards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("assessment_templates.id", ondelete="CASCADE"), nullable=False)
    standard_code = Column(String(50), nullable=False)
    standard_description = Column(Text, nullable=False)
    standard_framework = Column(String(100), nullable=False)
    grade_level = Column(String(20), nullable=False)
    subject = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template = relationship("app.models.assessment_tools.AssessmentTemplate", back_populates="standards")

    # Indexes
    __table_args__ = (
        Index("idx_assessment_standards_template_id", "template_id"),
        Index("idx_assessment_standards_framework", "standard_framework"),
        Index("idx_assessment_standards_subject", "subject"),
        Index("idx_assessment_standards_grade_level", "grade_level"),
    )
