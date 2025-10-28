"""
Pydantic schemas for Assessment Tools
Defines request/response models for assessment template creation and management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class AssessmentType(str, Enum):
    FORMATIVE = "formative"
    SUMMATIVE = "summative"
    DIAGNOSTIC = "diagnostic"
    PEER_ASSESSMENT = "peer_assessment"
    SELF_ASSESSMENT = "self_assessment"
    PERFORMANCE = "performance"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AssessmentMethod(str, Enum):
    OBSERVATION = "observation"
    CHECKLIST = "checklist"
    RUBRIC = "rubric"
    TEST = "test"
    PERFORMANCE = "performance"
    PORTFOLIO = "portfolio"
    PEER_REVIEW = "peer_review"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    PRACTICAL = "practical"
    MATCHING = "matching"
    FILL_IN_BLANK = "fill_in_blank"


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


# ==================== CRITERIA SCHEMAS ====================

class AssessmentCriteriaCreate(BaseModel):
    criterion_name: str = Field(..., min_length=1, max_length=255)
    criterion_description: str = Field(..., min_length=1)
    max_points: int = Field(..., ge=1, le=1000)
    weight_percentage: float = Field(..., ge=0.0, le=100.0)
    assessment_method: AssessmentMethod
    order_index: Optional[int] = Field(default=1, ge=1)


class AssessmentCriteriaResponse(BaseModel):
    id: str
    template_id: str
    criterion_name: str
    criterion_description: str
    max_points: int
    weight_percentage: float
    assessment_method: AssessmentMethod
    order_index: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== RUBRIC SCHEMAS ====================

class AssessmentRubricCreate(BaseModel):
    criterion_id: Optional[str] = None
    rubric_name: str = Field(..., min_length=1, max_length=255)
    rubric_description: Optional[str] = None
    performance_levels: List[str] = Field(..., min_items=2, max_items=6)
    performance_descriptions: List[str] = Field(..., min_items=1)
    point_values: List[int] = Field(..., min_items=1)
    order_index: Optional[int] = Field(default=1, ge=1)

    @validator('performance_descriptions')
    def validate_performance_descriptions(cls, v, values):
        if 'performance_levels' in values and len(v) != len(values['performance_levels']):
            raise ValueError('Performance descriptions must match performance levels count')
        return v

    @validator('point_values')
    def validate_point_values(cls, v, values):
        if 'performance_levels' in values and len(v) != len(values['performance_levels']):
            raise ValueError('Point values must match performance levels count')
        return v


class AssessmentRubricResponse(BaseModel):
    id: str
    template_id: str
    criterion_id: Optional[str]
    rubric_name: str
    rubric_description: Optional[str]
    performance_levels: List[str]
    performance_descriptions: List[str]
    point_values: List[int]
    order_index: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== QUESTION SCHEMAS ====================

class AssessmentQuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=1)
    question_type: QuestionType
    correct_answer: Optional[str] = None
    possible_answers: Optional[List[str]] = Field(default_factory=list)
    points: int = Field(..., ge=1, le=100)
    order_index: Optional[int] = Field(default=1, ge=1)

    @validator('possible_answers')
    def validate_possible_answers(cls, v, values):
        if values.get('question_type') == QuestionType.MULTIPLE_CHOICE and not v:
            raise ValueError('Multiple choice questions must have possible answers')
        return v

    @validator('correct_answer')
    def validate_correct_answer(cls, v, values):
        if values.get('question_type') in [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE, QuestionType.SHORT_ANSWER] and not v:
            raise ValueError('Objective questions must have a correct answer')
        return v


class AssessmentQuestionResponse(BaseModel):
    id: str
    template_id: str
    question_text: str
    question_type: QuestionType
    correct_answer: Optional[str]
    possible_answers: Optional[List[str]]
    points: int
    order_index: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== CHECKLIST SCHEMAS ====================

class AssessmentChecklistCreate(BaseModel):
    checklist_item: str = Field(..., min_length=1, max_length=255)
    item_description: Optional[str] = None
    is_required: bool = Field(default=True)
    points: int = Field(..., ge=1, le=100)
    order_index: Optional[int] = Field(default=1, ge=1)


class AssessmentChecklistResponse(BaseModel):
    id: str
    template_id: str
    checklist_item: str
    item_description: Optional[str]
    is_required: bool
    points: int
    order_index: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== STANDARDS SCHEMAS ====================

class AssessmentStandardCreate(BaseModel):
    standard_code: str = Field(..., min_length=1, max_length=50)
    standard_description: str = Field(..., min_length=1)
    standard_framework: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=20)
    subject: str = Field(..., min_length=1, max_length=100)


class AssessmentStandardResponse(BaseModel):
    id: str
    template_id: str
    standard_code: str
    standard_description: str
    standard_framework: str
    grade_level: str
    subject: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== TEMPLATE SCHEMAS ====================

class AssessmentTemplateCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    subject: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=20)
    assessment_type: AssessmentType
    duration_minutes: int = Field(..., ge=5, le=300)
    total_points: int = Field(default=100, ge=1, le=1000)
    instructions: str = Field(..., min_length=1)
    materials_needed: List[str] = Field(default_factory=list)
    safety_considerations: List[str] = Field(default_factory=list)
    ai_generated: bool = Field(default=True)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE)
    equipment_required: List[str] = Field(default_factory=list)
    space_requirements: str = Field(default="gymnasium", max_length=100)
    weather_dependent: bool = Field(default=False)
    is_public: bool = Field(default=False)
    criteria: Optional[List[AssessmentCriteriaCreate]] = None
    rubrics: Optional[List[AssessmentRubricCreate]] = None
    questions: Optional[List[AssessmentQuestionCreate]] = None
    checklists: Optional[List[AssessmentChecklistCreate]] = None
    standards: Optional[List[AssessmentStandardCreate]] = None
    category_ids: Optional[List[str]] = None

    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v < 5:
            raise ValueError('Duration must be at least 5 minutes')
        if v > 300:
            raise ValueError('Duration cannot exceed 300 minutes')
        return v

    @validator('total_points')
    def validate_total_points(cls, v):
        if v < 1:
            raise ValueError('Total points must be at least 1')
        if v > 1000:
            raise ValueError('Total points cannot exceed 1000')
        return v


class AssessmentTemplateUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    grade_level: Optional[str] = Field(None, min_length=1, max_length=20)
    assessment_type: Optional[AssessmentType] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=300)
    total_points: Optional[int] = Field(None, ge=1, le=1000)
    instructions: Optional[str] = Field(None, min_length=1)
    materials_needed: Optional[List[str]] = None
    safety_considerations: Optional[List[str]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    equipment_required: Optional[List[str]] = None
    space_requirements: Optional[str] = Field(None, max_length=100)
    weather_dependent: Optional[bool] = None
    is_public: Optional[bool] = None
    criteria: Optional[List[AssessmentCriteriaCreate]] = None
    rubrics: Optional[List[AssessmentRubricCreate]] = None
    questions: Optional[List[AssessmentQuestionCreate]] = None
    checklists: Optional[List[AssessmentChecklistCreate]] = None
    standards: Optional[List[AssessmentStandardCreate]] = None
    category_ids: Optional[List[str]] = None


class AssessmentTemplateResponse(BaseModel):
    id: str
    teacher_id: str
    title: str
    description: Optional[str]
    subject: str
    grade_level: str
    assessment_type: AssessmentType
    duration_minutes: int
    total_points: int
    instructions: str
    materials_needed: List[str]
    safety_considerations: List[str]
    ai_generated: bool
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
    criteria: List[AssessmentCriteriaResponse] = Field(default_factory=list)
    rubrics: List[AssessmentRubricResponse] = Field(default_factory=list)
    questions: List[AssessmentQuestionResponse] = Field(default_factory=list)
    checklists: List[AssessmentChecklistResponse] = Field(default_factory=list)
    standards: List[AssessmentStandardResponse] = Field(default_factory=list)
    categories: List['AssessmentCategoryResponse'] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ==================== SHARING SCHEMAS ====================

class AssessmentTemplateSharingCreate(BaseModel):
    shared_with_teacher_id: Optional[str] = None
    sharing_type: SharingType
    access_level: AccessLevel = Field(default=AccessLevel.VIEW)
    expires_at: Optional[datetime] = None


class AssessmentTemplateSharingResponse(BaseModel):
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


class AssessmentTemplateSharingFeedback(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


# ==================== USAGE SCHEMAS ====================

class AssessmentTemplateUsageCreate(BaseModel):
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


class AssessmentTemplateUsageResponse(BaseModel):
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

class AssessmentCategoryResponse(BaseModel):
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

class AssessmentTemplateSearchRequest(BaseModel):
    query: Optional[str] = None
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    assessment_type: Optional[AssessmentType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    duration_min: Optional[int] = Field(None, ge=5)
    duration_max: Optional[int] = Field(None, le=300)
    points_min: Optional[int] = Field(None, ge=1)
    points_max: Optional[int] = Field(None, le=1000)
    equipment_available: Optional[List[str]] = None
    space_available: Optional[str] = None
    weather_conditions: Optional[str] = None
    category_ids: Optional[List[str]] = None
    ai_generated_only: Optional[bool] = None
    public_only: Optional[bool] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class AssessmentTemplateSearchResponse(BaseModel):
    templates: List[AssessmentTemplateResponse]
    total_count: int
    has_more: bool


# ==================== ANALYTICS SCHEMAS ====================

class AssessmentTemplateAnalyticsResponse(BaseModel):
    templates_created: int
    usage_by_type: Dict[str, int]
    popular_templates: List[Dict[str, Any]]
    total_usage_count: int
    average_rating: float
    sharing_stats: Dict[str, int]
    assessment_type_distribution: Dict[str, int]
    difficulty_level_distribution: Dict[str, int]


class TeacherAssessmentAnalyticsResponse(BaseModel):
    total_templates: int
    public_templates: int
    private_templates: int
    total_usage_count: int
    templates_shared: int
    templates_received: int
    average_template_rating: float
    most_used_template: Optional[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    assessment_type_breakdown: Dict[str, int]
    subject_distribution: Dict[str, int]


# ==================== AI GENERATION SCHEMAS ====================

class AIAssessmentGenerationRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=20)
    assessment_type: AssessmentType
    duration_minutes: int = Field(..., ge=5, le=300)
    total_points: int = Field(default=100, ge=1, le=1000)
    learning_objectives: List[str] = Field(..., min_items=1, max_items=10)
    equipment_available: List[str] = Field(default_factory=list)
    space_available: str = Field(default="gymnasium", max_length=100)
    weather_conditions: Optional[str] = None
    special_considerations: Optional[str] = None
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE)
    include_rubrics: bool = Field(default=True)
    include_questions: bool = Field(default=True)
    include_checklists: bool = Field(default=True)
    standards_framework: Optional[str] = None


class AIAssessmentGenerationResponse(BaseModel):
    template: AssessmentTemplateResponse
    confidence_score: float
    generation_time_seconds: float
    standards_aligned: List[AssessmentStandardResponse]


# ==================== BULK OPERATIONS ====================

class BulkAssessmentTemplateOperation(BaseModel):
    template_ids: List[str] = Field(..., min_items=1)
    operation: str = Field(..., pattern="^(delete|duplicate|share|export)$")
    parameters: Optional[Dict[str, Any]] = None


class BulkAssessmentOperationResponse(BaseModel):
    success_count: int
    failure_count: int
    errors: List[Dict[str, str]]
    results: List[Dict[str, Any]]


# ==================== RUBRIC BUILDER SCHEMAS ====================

class RubricBuilderRequest(BaseModel):
    criterion_name: str = Field(..., min_length=1, max_length=255)
    criterion_description: str = Field(..., min_length=1)
    performance_levels: List[str] = Field(..., min_items=2, max_items=6)
    max_points: int = Field(..., ge=1, le=100)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE)
    grade_level: str = Field(..., min_length=1, max_length=20)
    subject: str = Field(..., min_length=1, max_length=100)


class RubricBuilderResponse(BaseModel):
    rubric: AssessmentRubricResponse
    suggestions: List[str]
    confidence_score: float


# Update forward references
AssessmentTemplateResponse.model_rebuild()
AssessmentCategoryResponse.model_rebuild()
