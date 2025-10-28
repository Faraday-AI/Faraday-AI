"""
Pydantic schemas for Resource Management
Defines request/response models for educational resource upload and management
"""

from typing import List, Optional, Dict, Any, BinaryIO
from datetime import datetime
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum


class ResourceType(str, Enum):
    DOCUMENT = "document"
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    LINK = "link"
    INTERACTIVE = "interactive"
    PRESENTATION = "presentation"
    WORKSHEET = "worksheet"
    ASSESSMENT = "assessment"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LicenseType(str, Enum):
    PUBLIC_DOMAIN = "public_domain"
    CREATIVE_COMMONS = "creative_commons"
    FAIR_USE = "fair_use"
    EDUCATIONAL_USE = "educational_use"
    COPYRIGHTED = "copyrighted"
    CUSTOM = "custom"


class CollectionType(str, Enum):
    CUSTOM = "custom"
    CURRICULUM = "curriculum"
    UNIT = "unit"
    LESSON = "lesson"
    TOPIC = "topic"
    GRADE_LEVEL = "grade_level"


class SharingType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    SCHOOL_ONLY = "school_only"


class AccessLevel(str, Enum):
    VIEW = "view"
    DOWNLOAD = "download"
    EDIT = "edit"


class UsageType(str, Enum):
    CREATED = "created"
    VIEWED = "viewed"
    DOWNLOADED = "downloaded"
    SHARED = "shared"
    USED_IN_CLASS = "used_in_class"
    MODIFIED = "modified"


# ==================== RESOURCE SCHEMAS ====================

class EducationalResourceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    resource_type: ResourceType
    external_url: Optional[HttpUrl] = None
    subject: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=20)
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE)
    duration_minutes: Optional[int] = Field(None, ge=1, le=300)
    language: str = Field(default="en", min_length=2, max_length=10)
    accessibility_features: List[str] = Field(default_factory=list)
    copyright_info: Optional[str] = None
    license_type: LicenseType = Field(default=LicenseType.EDUCATIONAL_USE)
    attribution_required: bool = Field(default=False)
    attribution_text: Optional[str] = None
    is_public: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    ai_generated: bool = Field(default=False)
    category_ids: Optional[List[str]] = None

    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v

    @validator('keywords')
    def validate_keywords(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 keywords allowed')
        return v


class EducationalResourceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    external_url: Optional[HttpUrl] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    grade_level: Optional[str] = Field(None, min_length=1, max_length=20)
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=300)
    language: Optional[str] = Field(None, min_length=2, max_length=10)
    accessibility_features: Optional[List[str]] = None
    copyright_info: Optional[str] = None
    license_type: Optional[LicenseType] = None
    attribution_required: Optional[bool] = None
    attribution_text: Optional[str] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    category_ids: Optional[List[str]] = None


class EducationalResourceResponse(BaseModel):
    id: str
    teacher_id: str
    title: str
    description: Optional[str]
    resource_type: ResourceType
    file_path: Optional[str]
    file_name: Optional[str]
    file_size_bytes: Optional[int]
    mime_type: Optional[str]
    external_url: Optional[str]
    thumbnail_path: Optional[str]
    subject: str
    grade_level: str
    tags: List[str]
    keywords: List[str]
    difficulty_level: DifficultyLevel
    duration_minutes: Optional[int]
    language: str
    accessibility_features: List[str]
    copyright_info: Optional[str]
    license_type: LicenseType
    attribution_required: bool
    attribution_text: Optional[str]
    is_public: bool
    is_featured: bool
    download_count: int
    view_count: int
    rating_average: float
    rating_count: int
    ai_generated: bool
    created_at: datetime
    updated_at: datetime
    categories: List['ResourceCategoryResponse'] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ==================== COLLECTION SCHEMAS ====================

class ResourceCollectionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    subject: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=20)
    collection_type: CollectionType = Field(default=CollectionType.CUSTOM)
    is_public: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    resource_ids: Optional[List[str]] = None


class ResourceCollectionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    grade_level: Optional[str] = Field(None, min_length=1, max_length=20)
    collection_type: Optional[CollectionType] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None


class ResourceCollectionResponse(BaseModel):
    id: str
    teacher_id: str
    title: str
    description: Optional[str]
    subject: str
    grade_level: str
    collection_type: CollectionType
    is_public: bool
    is_featured: bool
    resource_count: int
    view_count: int
    download_count: int
    rating_average: float
    rating_count: int
    created_at: datetime
    updated_at: datetime
    resources: List[EducationalResourceResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ==================== REVIEW SCHEMAS ====================

class ResourceReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    would_recommend: bool = Field(default=True)
    used_in_class: bool = Field(default=False)
    student_feedback: Optional[str] = None

    @validator('pros')
    def validate_pros(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 pros allowed')
        return v

    @validator('cons')
    def validate_cons(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 cons allowed')
        return v

    @validator('suggestions')
    def validate_suggestions(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 suggestions allowed')
        return v


class ResourceReviewResponse(BaseModel):
    id: str
    resource_id: str
    teacher_id: str
    rating: int
    review_text: Optional[str]
    pros: List[str]
    cons: List[str]
    suggestions: List[str]
    would_recommend: bool
    used_in_class: bool
    student_feedback: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== SHARING SCHEMAS ====================

class ResourceSharingCreate(BaseModel):
    shared_with_teacher_id: Optional[str] = None
    sharing_type: SharingType
    access_level: AccessLevel = Field(default=AccessLevel.VIEW)
    expires_at: Optional[datetime] = None


class ResourceSharingResponse(BaseModel):
    id: str
    resource_id: str
    shared_by_teacher_id: str
    shared_with_teacher_id: Optional[str]
    sharing_type: SharingType
    access_level: AccessLevel
    shared_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    usage_count: int
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_comment: Optional[str]

    class Config:
        from_attributes = True


# ==================== USAGE SCHEMAS ====================

class ResourceUsageCreate(BaseModel):
    resource_id: str
    usage_type: UsageType
    context: Optional[str] = None
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)
    effectiveness_notes: Optional[str] = None
    student_engagement_level: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    time_spent_minutes: Optional[int] = Field(None, ge=1)
    issues_encountered: List[str] = Field(default_factory=list)
    improvements_suggested: List[str] = Field(default_factory=list)


class ResourceUsageResponse(BaseModel):
    id: str
    resource_id: str
    teacher_id: str
    usage_type: UsageType
    usage_date: datetime
    context: Optional[str]
    effectiveness_rating: Optional[int]
    effectiveness_notes: Optional[str]
    student_engagement_level: Optional[str]
    completion_percentage: Optional[float]
    time_spent_minutes: Optional[int]
    issues_encountered: List[str]
    improvements_suggested: List[str]

    class Config:
        from_attributes = True


# ==================== CATEGORY SCHEMAS ====================

class ResourceCategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    parent_category_id: Optional[str]
    subject: str
    grade_level_range: str
    icon_name: str
    color_code: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== SEARCH SCHEMAS ====================

class ResourceSearchRequest(BaseModel):
    query: Optional[str] = None
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    duration_min: Optional[int] = Field(None, ge=1)
    duration_max: Optional[int] = Field(None, le=300)
    tags: Optional[List[str]] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    language: Optional[str] = None
    accessibility_features: Optional[List[str]] = None
    license_type: Optional[LicenseType] = None
    ai_generated_only: Optional[bool] = None
    featured_only: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ResourceSearchResponse(BaseModel):
    resources: List[EducationalResourceResponse]
    total_count: int
    has_more: bool


# ==================== UPLOAD SCHEMAS ====================

class ResourceUploadRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    subject: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=20)
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE)
    duration_minutes: Optional[int] = Field(None, ge=1, le=300)
    language: str = Field(default="en", min_length=2, max_length=10)
    accessibility_features: List[str] = Field(default_factory=list)
    copyright_info: Optional[str] = None
    license_type: LicenseType = Field(default=LicenseType.EDUCATIONAL_USE)
    attribution_required: bool = Field(default=False)
    attribution_text: Optional[str] = None
    is_public: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    category_ids: Optional[List[str]] = None


class ResourceUploadResponse(BaseModel):
    resource: EducationalResourceResponse
    upload_successful: bool
    file_size_bytes: int
    mime_type: str
    processing_status: str  # pending, processing, completed, failed
    thumbnail_generated: bool = False


# ==================== ANALYTICS SCHEMAS ====================

class ResourceAnalyticsResponse(BaseModel):
    resources_created: int
    usage_by_type: Dict[str, int]
    popular_resources: List[Dict[str, Any]]
    total_downloads: int
    total_views: int
    average_rating: float
    sharing_stats: Dict[str, int]
    resource_type_distribution: Dict[str, int]
    subject_distribution: Dict[str, int]
    grade_level_distribution: Dict[str, int]


class TeacherResourceAnalyticsResponse(BaseModel):
    total_resources: int
    public_resources: int
    private_resources: int
    total_downloads: int
    total_views: int
    resources_shared: int
    resources_received: int
    average_resource_rating: float
    most_downloaded_resource: Optional[Dict[str, Any]]
    most_viewed_resource: Optional[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    resource_type_breakdown: Dict[str, int]
    subject_distribution: Dict[str, int]
    collection_stats: Dict[str, int]


# ==================== BULK OPERATIONS ====================

class BulkResourceOperation(BaseModel):
    resource_ids: List[str] = Field(..., min_items=1)
    operation: str = Field(..., pattern="^(delete|duplicate|share|export|add_to_collection)$")
    parameters: Optional[Dict[str, Any]] = None


class BulkResourceOperationResponse(BaseModel):
    success_count: int
    failure_count: int
    errors: List[Dict[str, str]]
    results: List[Dict[str, Any]]


# ==================== FILE MANAGEMENT SCHEMAS ====================

class FileUploadResponse(BaseModel):
    file_id: str
    file_name: str
    file_size_bytes: int
    mime_type: str
    upload_path: str
    thumbnail_path: Optional[str] = None
    processing_status: str
    error_message: Optional[str] = None


class FileDownloadResponse(BaseModel):
    file_name: str
    file_content: bytes
    mime_type: str
    file_size_bytes: int


# ==================== COLLECTION MANAGEMENT SCHEMAS ====================

class CollectionResourceAssociationRequest(BaseModel):
    resource_id: str
    order_index: Optional[int] = None


class CollectionResourceAssociationResponse(BaseModel):
    id: str
    collection_id: str
    resource_id: str
    order_index: int
    added_at: datetime

    class Config:
        from_attributes = True


# ==================== FAVORITES SCHEMAS ====================

class ResourceFavoriteResponse(BaseModel):
    id: str
    resource_id: str
    teacher_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Update forward references
EducationalResourceResponse.model_rebuild()
ResourceCategoryResponse.model_rebuild()
ResourceCollectionResponse.model_rebuild()
