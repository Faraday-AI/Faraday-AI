"""
SQLAlchemy models for Resource Management
Defines database models for educational resource upload and management
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, ARRAY, DECIMAL, BigInteger, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.shared_base import SharedBase as Base
import uuid


class ResourceCategory(Base):
    """Categories for organizing educational resources"""
    __tablename__ = "resource_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey("resource_categories.id", ondelete="SET NULL"))
    subject = Column(String(100), nullable=False)
    grade_level_range = Column(String(20), nullable=False)
    icon_name = Column(String(50), default="default")
    color_code = Column(String(7), default="#007bff")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    parent_category = relationship("ResourceCategory", remote_side=[id], back_populates="subcategories")
    subcategories = relationship("ResourceCategory", back_populates="parent_category")
    resource_associations = relationship("ResourceCategoryAssociation", back_populates="category", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_resource_categories_subject", "subject"),
        Index("idx_resource_categories_active", "is_active"),
        Index("idx_resource_categories_parent", "parent_category_id"),
    )


class EducationalResource(Base):
    """Educational resources uploaded by teachers"""
    __tablename__ = "educational_resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    resource_type = Column(String(50), nullable=False)
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size_bytes = Column(BigInteger)
    mime_type = Column(String(100))
    external_url = Column(Text)
    thumbnail_path = Column(String(500))
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(20), nullable=False)
    tags = Column(ARRAY(Text), default=[])
    keywords = Column(ARRAY(Text), default=[])
    difficulty_level = Column(String(20), default="intermediate")
    duration_minutes = Column(Integer)
    language = Column(String(10), default="en")
    accessibility_features = Column(ARRAY(Text), default=[])
    copyright_info = Column(Text)
    license_type = Column(String(50), default="educational_use")
    attribution_required = Column(Boolean, default=False)
    attribution_text = Column(Text)
    is_public = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    rating_average = Column(DECIMAL(3, 2), default=0.00)
    rating_count = Column(Integer, default=0)
    ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="educational_resources")
    category_associations = relationship("ResourceCategoryAssociation", back_populates="resource", cascade="all, delete-orphan")
    sharing_records = relationship("ResourceSharing", back_populates="resource", cascade="all, delete-orphan")
    usage_records = relationship("ResourceUsage", back_populates="resource", cascade="all, delete-orphan")
    reviews = relationship("ResourceReview", back_populates="resource", cascade="all, delete-orphan")
    favorites = relationship("ResourceFavorite", back_populates="resource", cascade="all, delete-orphan")
    downloads = relationship("ResourceDownload", back_populates="resource", cascade="all, delete-orphan")
    collection_associations = relationship("CollectionResourceAssociation", back_populates="resource", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_educational_resources_teacher_id", "teacher_id"),
        Index("idx_educational_resources_subject", "subject"),
        Index("idx_educational_resources_grade_level", "grade_level"),
        Index("idx_educational_resources_type", "resource_type"),
        Index("idx_educational_resources_public", "is_public"),
        Index("idx_educational_resources_featured", "is_featured"),
        Index("idx_educational_resources_created_at", "created_at"),
        Index("idx_educational_resources_tags", "tags", postgresql_using="gin"),
        Index("idx_educational_resources_keywords", "keywords", postgresql_using="gin"),
    )


class ResourceCategoryAssociation(Base):
    """Many-to-many relationship between resources and categories"""
    __tablename__ = "resource_category_associations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("educational_resources.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("resource_categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resource = relationship("EducationalResource", back_populates="category_associations")
    category = relationship("ResourceCategory", back_populates="resource_associations")

    # Indexes
    __table_args__ = (
        Index("idx_resource_category_resource_id", "resource_id"),
        Index("idx_resource_category_category_id", "category_id"),
        UniqueConstraint("resource_id", "category_id", name="ux_resource_category_unique"),
    )


class ResourceSharing(Base):
    """Resource sharing between teachers"""
    __tablename__ = "resource_sharing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("educational_resources.id", ondelete="CASCADE"), nullable=False)
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
    resource = relationship("EducationalResource", back_populates="sharing_records")
    shared_by_teacher = relationship("app.models.teacher_registration.TeacherRegistration", foreign_keys=[shared_by_teacher_id], back_populates="owned_resources")
    shared_with_teacher = relationship("app.models.teacher_registration.TeacherRegistration", foreign_keys=[shared_with_teacher_id], back_populates="received_resources")

    # Indexes
    __table_args__ = (
        Index("idx_resource_sharing_resource_id", "resource_id"),
        Index("idx_resource_sharing_shared_by", "shared_by_teacher_id"),
        Index("idx_resource_sharing_shared_with", "shared_with_teacher_id"),
        Index("idx_resource_sharing_type", "sharing_type"),
        Index("idx_resource_sharing_active", "is_active"),
    )


class ResourceUsage(Base):
    """Resource usage tracking for analytics"""
    __tablename__ = "resource_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("educational_resources.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    usage_type = Column(String(50), nullable=False)
    usage_date = Column(DateTime(timezone=True), server_default=func.now())
    context = Column(Text)
    effectiveness_rating = Column(Integer)
    effectiveness_notes = Column(Text)
    student_engagement_level = Column(String(20))
    completion_percentage = Column(DECIMAL(5, 2))
    time_spent_minutes = Column(Integer)
    issues_encountered = Column(ARRAY(Text), default=[])
    improvements_suggested = Column(ARRAY(Text), default=[])

    # Relationships
    resource = relationship("EducationalResource", back_populates="usage_records")
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="resource_usage")

    # Indexes
    __table_args__ = (
        Index("idx_resource_usage_resource_id", "resource_id"),
        Index("idx_resource_usage_teacher_id", "teacher_id"),
        Index("idx_resource_usage_date", "usage_date"),
        Index("idx_resource_usage_type", "usage_type"),
    )


class ResourceCollection(Base):
    """Collections of educational resources"""
    __tablename__ = "resource_collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(20), nullable=False)
    collection_type = Column(String(50), default="custom")
    is_public = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    resource_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    rating_average = Column(DECIMAL(3, 2), default=0.00)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="resource_collections")
    resource_associations = relationship("CollectionResourceAssociation", back_populates="collection", cascade="all, delete-orphan")
    sharing_records = relationship("CollectionSharing", back_populates="collection", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_resource_collections_teacher_id", "teacher_id"),
        Index("idx_resource_collections_subject", "subject"),
        Index("idx_resource_collections_grade_level", "grade_level"),
        Index("idx_resource_collections_public", "is_public"),
        Index("idx_resource_collections_featured", "is_featured"),
        Index("idx_resource_collections_created_at", "created_at"),
    )


class CollectionResourceAssociation(Base):
    """Many-to-many relationship between collections and resources"""
    __tablename__ = "collection_resource_associations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("resource_collections.id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("educational_resources.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    collection = relationship("ResourceCollection", back_populates="resource_associations")
    resource = relationship("EducationalResource", back_populates="collection_associations")

    # Indexes
    __table_args__ = (
        Index("idx_collection_resource_collection_id", "collection_id"),
        Index("idx_collection_resource_resource_id", "resource_id"),
        Index("idx_collection_resource_order", "order_index"),
        UniqueConstraint("collection_id", "resource_id", name="ux_collection_resource_unique"),
    )


class CollectionSharing(Base):
    """Collection sharing between teachers"""
    __tablename__ = "collection_sharing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("resource_collections.id", ondelete="CASCADE"), nullable=False)
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
    collection = relationship("ResourceCollection", back_populates="sharing_records")
    shared_by_teacher = relationship("app.models.teacher_registration.TeacherRegistration", foreign_keys=[shared_by_teacher_id], back_populates="shared_collections")
    shared_with_teacher = relationship("app.models.teacher_registration.TeacherRegistration", foreign_keys=[shared_with_teacher_id], back_populates="received_collections")

    # Indexes
    __table_args__ = (
        Index("idx_collection_sharing_collection_id", "collection_id"),
        Index("idx_collection_sharing_shared_by", "shared_by_teacher_id"),
        Index("idx_collection_sharing_shared_with", "shared_with_teacher_id"),
        Index("idx_collection_sharing_type", "sharing_type"),
        Index("idx_collection_sharing_active", "is_active"),
    )


class ResourceReview(Base):
    """Teacher reviews and ratings for resources"""
    __tablename__ = "resource_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("educational_resources.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text)
    pros = Column(ARRAY(Text), default=[])
    cons = Column(ARRAY(Text), default=[])
    suggestions = Column(ARRAY(Text), default=[])
    would_recommend = Column(Boolean, default=True)
    used_in_class = Column(Boolean, default=False)
    student_feedback = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    resource = relationship("EducationalResource", back_populates="reviews")
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="resource_reviews")

    # Indexes
    __table_args__ = (
        Index("idx_resource_reviews_resource_id", "resource_id"),
        Index("idx_resource_reviews_teacher_id", "teacher_id"),
        Index("idx_resource_reviews_rating", "rating"),
        Index("idx_resource_reviews_created_at", "created_at"),
        UniqueConstraint("resource_id", "teacher_id", name="ux_resource_review_unique"),
    )


class ResourceFavorite(Base):
    """Teacher's favorite resources"""
    __tablename__ = "resource_favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("educational_resources.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resource = relationship("EducationalResource", back_populates="favorites")
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="resource_favorites")

    # Indexes
    __table_args__ = (
        Index("idx_resource_favorites_resource_id", "resource_id"),
        Index("idx_resource_favorites_teacher_id", "teacher_id"),
        Index("idx_resource_favorites_created_at", "created_at"),
        UniqueConstraint("resource_id", "teacher_id", name="ux_resource_favorite_unique"),
    )


class ResourceDownload(Base):
    """Resource download tracking"""
    __tablename__ = "resource_downloads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("educational_resources.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    download_date = Column(DateTime(timezone=True), server_default=func.now())
    file_size_bytes = Column(BigInteger)
    download_successful = Column(Boolean, default=True)
    error_message = Column(Text)

    # Relationships
    resource = relationship("EducationalResource", back_populates="downloads")
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="resource_downloads")

    # Indexes
    __table_args__ = (
        Index("idx_resource_downloads_resource_id", "resource_id"),
        Index("idx_resource_downloads_teacher_id", "teacher_id"),
        Index("idx_resource_downloads_date", "download_date"),
        Index("idx_resource_downloads_successful", "download_successful"),
    )
