"""
Pydantic schemas for Lesson Plan Builder
Defines request/response models for AI-assisted lesson plan creation
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class TemplateType(str, Enum):
    STANDARD = "standard"
    WARMUP = "warmup"
    COOLDOWN = "cooldown"
    ASSESSMENT = "assessment"
    GAME = "game"
    SKILL_DEVELOPMENT = "skill_development"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ActivityType(str, Enum):
    WARMUP = "warmup"
    MAIN_ACTIVITY = "main_activity"
    COOLDOWN = "cooldown"
    ASSESSMENT = "assessment"
    TRANSITION = "transition"


class SuggestionType(str, Enum):
    ACTIVITY_RECOMMENDATION = "activity_recommendation"
    MODIFICATION = "modification"
    ASSESSMENT_IDEA = "assessment_idea"
    SAFETY_TIP = "safety_tip"
    EQUIPMENT_SUGGESTION = "equipment_suggestion"
    DIFFERENTIATION = "differentiation"


class SharingType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    SCHOOL_ONLY = "school_only"


class AccessLevel(str, Enum):
    VIEW = "view"
    COPY = "copy"
    EDIT = "edit"


class UsageType(str, Enum):
    CREATED = "created"
    COPIED = "copied"
    MODIFIED = "modified"
    SHARED = "shared"
    USED_IN_CLASS = "used_in_class"


# ==================== ACTIVITY SCHEMAS ====================

class LessonPlanActivityCreate(BaseModel):
    activity_name: str = Field(..., min_length=1, max_length=255)
    activity_description: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., ge=1, le=120)
    activity_type: ActivityType
    equipment_needed: List[str] = Field(default_factory=list)
    space_required: str = Field(default="gymnasium", max_length=100)
    safety_notes: List[str] = Field(default_factory=list)
    instructions: List[str] = Field(..., min_items=1)
    modifications: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)


class LessonPlanActivityResponse(BaseModel):
    id: str
    template_id: str
    activity_name: str
    activity_description: str
    duration_minutes: int
    activity_type: ActivityType
    equipment_needed: List[str]
    space_required: str
    safety_notes: List[str]
    instructions: List[str]
    modifications: List[str]
    success_criteria: List[str]
    order_index: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== TEMPLATE SCHEMAS ====================

class LessonPlanTemplateCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    subject: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=20)
    duration_minutes: int = Field(..., ge=15, le=180)
    learning_objectives: List[str] = Field(..., min_items=1, max_items=10)
    materials_needed: List[str] = Field(default_factory=list)
    safety_considerations: List[str] = Field(default_factory=list)
    assessment_methods: List[str] = Field(default_factory=list)
    ai_generated: bool = Field(default=True)
    template_type: TemplateType = Field(default=TemplateType.STANDARD)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE)
    equipment_required: List[str] = Field(default_factory=list)
    space_requirements: str = Field(default="gymnasium", max_length=100)
    weather_dependent: bool = Field(default=False)
    is_public: bool = Field(default=False)
    activities: Optional[List[LessonPlanActivityCreate]] = None
    category_ids: Optional[List[str]] = None

    @validator('learning_objectives')
    def validate_learning_objectives(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one learning objective is required')
        return v

    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v < 15:
            raise ValueError('Duration must be at least 15 minutes')
        if v > 180:
            raise ValueError('Duration cannot exceed 180 minutes')
        return v


class LessonPlanTemplateUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    grade_level: Optional[str] = Field(None, min_length=1, max_length=20)
    duration_minutes: Optional[int] = Field(None, ge=15, le=180)
    learning_objectives: Optional[List[str]] = Field(None, min_items=1, max_items=10)
    materials_needed: Optional[List[str]] = None
    safety_considerations: Optional[List[str]] = None
    assessment_methods: Optional[List[str]] = None
    template_type: Optional[TemplateType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    equipment_required: Optional[List[str]] = None
    space_requirements: Optional[str] = Field(None, max_length=100)
    weather_dependent: Optional[bool] = None
    is_public: Optional[bool] = None
    activities: Optional[List[LessonPlanActivityCreate]] = None
    category_ids: Optional[List[str]] = None


class LessonPlanTemplateResponse(BaseModel):
    id: str
    teacher_id: str
    title: str
    description: Optional[str]
    subject: str
    grade_level: str
    duration_minutes: int
    learning_objectives: List[str]
    materials_needed: List[str]
    safety_considerations: List[str]
    assessment_methods: List[str]
    ai_generated: bool
    template_type: TemplateType
    difficulty_level: DifficultyLevel
    equipment_required: List[str]
    space_requirements: str
    weather_dependent: bool
    is_public: bool
    usage_count: int
    rating_average: float
    rating_count: int
    created_at: datetime
    updated_at: datetime
    activities: List[LessonPlanActivityResponse] = Field(default_factory=list)
    categories: List['LessonPlanCategoryResponse'] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ==================== AI SUGGESTION SCHEMAS ====================

class AISuggestionCreate(BaseModel):
    suggestion_type: SuggestionType
    subject: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=20)
    context: str = Field(..., min_length=1)
    ai_suggestion: str = Field(..., min_length=1)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)


class AISuggestionResponse(BaseModel):
    id: str
    teacher_id: str
    suggestion_type: SuggestionType
    subject: str
    grade_level: str
    context: str
    ai_suggestion: str
    confidence_score: float
    tags: List[str]
    is_applied: bool
    applied_at: Optional[datetime]
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AISuggestionRating(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


# ==================== SHARING SCHEMAS ====================

class LessonPlanSharingCreate(BaseModel):
    shared_with_teacher_id: Optional[str] = None
    sharing_type: SharingType
    access_level: AccessLevel = Field(default=AccessLevel.VIEW)
    expires_at: Optional[datetime] = None


class LessonPlanSharingResponse(BaseModel):
    id: str
    template_id: str
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


class LessonPlanSharingFeedback(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


# ==================== USAGE SCHEMAS ====================

class LessonPlanUsageCreate(BaseModel):
    template_id: str
    usage_type: UsageType
    modifications_made: List[str] = Field(default_factory=list)
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)
    effectiveness_notes: Optional[str] = None
    student_engagement_level: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    time_spent_minutes: Optional[int] = Field(None, ge=1)
    issues_encountered: List[str] = Field(default_factory=list)
    improvements_suggested: List[str] = Field(default_factory=list)


class LessonPlanUsageResponse(BaseModel):
    id: str
    template_id: str
    teacher_id: str
    usage_type: UsageType
    usage_date: datetime
    modifications_made: List[str]
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

class LessonPlanCategoryResponse(BaseModel):
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


# ==================== SEARCH AND FILTER SCHEMAS ====================

class LessonPlanSearchRequest(BaseModel):
    query: Optional[str] = None
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    template_type: Optional[TemplateType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    duration_min: Optional[int] = Field(None, ge=15)
    duration_max: Optional[int] = Field(None, le=180)
    equipment_available: Optional[List[str]] = None
    space_available: Optional[str] = None
    weather_conditions: Optional[str] = None
    category_ids: Optional[List[str]] = None
    ai_generated_only: Optional[bool] = None
    public_only: Optional[bool] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class LessonPlanSearchResponse(BaseModel):
    templates: List[LessonPlanTemplateResponse]
    total_count: int
    has_more: bool


# ==================== ANALYTICS SCHEMAS ====================

class TemplateAnalyticsResponse(BaseModel):
    templates_created: int
    usage_by_type: Dict[str, int]
    popular_templates: List[Dict[str, Any]]
    total_usage_count: int
    average_rating: float
    sharing_stats: Dict[str, int]


class TeacherAnalyticsResponse(BaseModel):
    total_templates: int
    public_templates: int
    private_templates: int
    total_usage_count: int
    templates_shared: int
    templates_received: int
    average_template_rating: float
    most_used_template: Optional[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


# ==================== AI GENERATION SCHEMAS ====================

class AIGenerationRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=20)
    duration_minutes: int = Field(..., ge=15, le=180)
    learning_objectives: List[str] = Field(..., min_items=1, max_items=10)
    equipment_available: List[str] = Field(default_factory=list)
    space_available: str = Field(default="gymnasium", max_length=100)
    weather_conditions: Optional[str] = None
    special_considerations: Optional[str] = None
    template_type: TemplateType = Field(default=TemplateType.STANDARD)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE)
    include_assessment: bool = Field(default=True)
    include_modifications: bool = Field(default=True)


class AIGenerationResponse(BaseModel):
    template: LessonPlanTemplateResponse
    suggestions: List[AISuggestionResponse]
    confidence_score: float
    generation_time_seconds: float


# ==================== BULK OPERATIONS ====================

class BulkTemplateOperation(BaseModel):
    template_ids: List[str] = Field(..., min_items=1)
    operation: str = Field(..., pattern="^(delete|duplicate|share|export)$")
    parameters: Optional[Dict[str, Any]] = None


class BulkOperationResponse(BaseModel):
    success_count: int
    failure_count: int
    errors: List[Dict[str, str]]
    results: List[Dict[str, Any]]


# Update forward references
LessonPlanTemplateResponse.model_rebuild()
LessonPlanCategoryResponse.model_rebuild()
