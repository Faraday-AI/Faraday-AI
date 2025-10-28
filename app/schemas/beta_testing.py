"""
Pydantic schemas for Beta Testing Infrastructure
Defines data validation and serialization models for beta testing features
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# Enums
class ProgramStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ParticipantStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    DROPPED = "dropped"

class FeedbackType(str, Enum):
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    USABILITY_ISSUE = "usability_issue"
    PERFORMANCE_ISSUE = "performance_issue"
    GENERAL_FEEDBACK = "general_feedback"

class FeedbackPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SurveyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    TEXT = "text"
    RATING = "rating"
    LIKERT_SCALE = "likert_scale"
    YES_NO = "yes_no"

class NotificationType(str, Enum):
    PROGRAM_UPDATE = "program_update"
    SURVEY_REMINDER = "survey_reminder"
    FEEDBACK_REQUEST = "feedback_request"
    FEATURE_ANNOUNCEMENT = "feature_announcement"
    SYSTEM_ALERT = "system_alert"

class ReportType(str, Enum):
    PARTICIPANT_SUMMARY = "participant_summary"
    FEEDBACK_ANALYSIS = "feedback_analysis"
    USAGE_ANALYTICS = "usage_analytics"
    SURVEY_RESULTS = "survey_results"
    FEATURE_ADOPTION = "feature_adoption"

# Base schemas
class BetaTestingProgramBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    objectives: List[str] = Field(default_factory=list)
    target_audience: str = Field(..., max_length=500)
    start_date: datetime
    end_date: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, gt=0)
    requirements: List[str] = Field(default_factory=list)
    incentives: Optional[str] = Field(None, max_length=1000)
    status: ProgramStatus = ProgramStatus.DRAFT

class BetaTestingProgramCreate(BetaTestingProgramBase):
    pass

class BetaTestingProgramUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    objectives: Optional[List[str]] = None
    target_audience: Optional[str] = Field(None, max_length=500)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, gt=0)
    requirements: Optional[List[str]] = None
    incentives: Optional[str] = Field(None, max_length=1000)
    status: Optional[ProgramStatus] = None

class BetaTestingProgramResponse(BetaTestingProgramBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    participant_count: int = 0
    feedback_count: int = 0
    survey_count: int = 0

    class Config:
        from_attributes = True

class BetaTestingParticipantBase(BaseModel):
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    organization: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, max_length=100)
    experience_level: Optional[str] = Field(None, max_length=50)
    interests: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=1000)

class BetaTestingParticipantCreate(BetaTestingParticipantBase):
    pass

class BetaTestingParticipantUpdate(BaseModel):
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    organization: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, max_length=100)
    experience_level: Optional[str] = Field(None, max_length=50)
    interests: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None, pattern="^(active|inactive|suspended)$")

class BetaTestingParticipantResponse(BetaTestingParticipantBase):
    id: uuid.UUID
    program_id: uuid.UUID
    status: ParticipantStatus
    joined_at: datetime
    last_activity: Optional[datetime] = None
    feedback_count: int = 0
    survey_responses_count: int = 0

    class Config:
        from_attributes = True

class BetaTestingFeedbackBase(BaseModel):
    program_id: uuid.UUID
    feedback_type: FeedbackType
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=5000)
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    category: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    steps_to_reproduce: Optional[str] = Field(None, max_length=2000)
    expected_behavior: Optional[str] = Field(None, max_length=1000)
    actual_behavior: Optional[str] = Field(None, max_length=1000)
    attachments: List[str] = Field(default_factory=list)
    is_anonymous: bool = False

class BetaTestingFeedbackCreate(BetaTestingFeedbackBase):
    pass

class BetaTestingFeedbackUpdate(BaseModel):
    feedback_type: Optional[str] = Field(None, pattern="^(bug_report|feature_request|general|usability)$")
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, pattern="^(open|in_progress|resolved|closed)$")
    tags: Optional[List[str]] = None

class BetaTestingFeedbackResponse(BetaTestingFeedbackBase):
    id: uuid.UUID
    participant_id: Optional[uuid.UUID] = None
    status: str = "open"
    assigned_to: Optional[uuid.UUID] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SurveyQuestionBase(BaseModel):
    question_text: str = Field(..., min_length=1, max_length=1000)
    question_type: QuestionType
    options: Optional[List[str]] = None
    required: bool = True
    order: int = Field(..., ge=0)
    help_text: Optional[str] = Field(None, max_length=500)

class SurveyQuestionCreate(SurveyQuestionBase):
    pass

class SurveyQuestionResponse(SurveyQuestionBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class BetaTestingSurveyBase(BaseModel):
    program_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    instructions: Optional[str] = Field(None, max_length=2000)
    questions: List[SurveyQuestionCreate]
    status: SurveyStatus = SurveyStatus.DRAFT
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_anonymous: bool = False
    allow_multiple_responses: bool = False

class BetaTestingSurveyCreate(BetaTestingSurveyBase):
    pass

class BetaTestingSurveyResponse(BetaTestingSurveyBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    response_count: int = 0
    questions: List[SurveyQuestionResponse]

    class Config:
        from_attributes = True

class SurveyResponseAnswerBase(BaseModel):
    question_id: uuid.UUID
    answer_text: Optional[str] = None
    answer_choice: Optional[str] = None
    answer_rating: Optional[int] = Field(None, ge=1, le=10)
    answer_boolean: Optional[bool] = None

class SurveyResponseAnswerCreate(SurveyResponseAnswerBase):
    pass

class SurveyResponseAnswerResponse(SurveyResponseAnswerBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class BetaTestingSurveyResponseCreate(BaseModel):
    survey_id: uuid.UUID
    answers: List[SurveyResponseAnswerCreate]
    comments: Optional[str] = Field(None, max_length=2000)
    is_anonymous: bool = False

class BetaTestingSurveyResponseResponse(BaseModel):
    id: uuid.UUID
    survey_id: uuid.UUID
    participant_id: Optional[uuid.UUID] = None
    answers: List[SurveyResponseAnswerResponse]
    comments: Optional[str] = None
    submitted_at: datetime
    is_anonymous: bool

    class Config:
        from_attributes = True

class UsageMetricBase(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: Union[int, float] = Field(..., ge=0)
    metric_unit: Optional[str] = Field(None, max_length=50)
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class UsageMetricCreate(UsageMetricBase):
    pass

class UsageMetricResponse(UsageMetricBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class BetaTestingUsageAnalyticsResponse(BaseModel):
    program_id: Optional[uuid.UUID] = None
    total_participants: int
    active_participants: int
    total_feedback: int
    total_surveys: int
    total_responses: int
    average_session_duration: Optional[float] = None
    feature_usage: Dict[str, int] = Field(default_factory=dict)
    daily_active_users: List[Dict[str, Any]] = Field(default_factory=list)
    weekly_metrics: List[Dict[str, Any]] = Field(default_factory=list)
    top_feedback_categories: List[Dict[str, Any]] = Field(default_factory=list)
    participant_engagement_score: Optional[float] = None

class BetaTestingFeatureFlagBase(BaseModel):
    program_id: uuid.UUID
    flag_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_enabled: bool = True
    rollout_percentage: int = Field(100, ge=0, le=100)
    target_audience: Optional[str] = Field(None, max_length=500)
    conditions: Optional[Dict[str, Any]] = None

class BetaTestingFeatureFlagCreate(BetaTestingFeatureFlagBase):
    pass

class BetaTestingFeatureFlagUpdate(BaseModel):
    feature_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    target_percentage: Optional[int] = Field(None, ge=0, le=100)
    conditions: Optional[Dict[str, Any]] = None

class BetaTestingFeatureFlagResponse(BetaTestingFeatureFlagBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BetaTestingNotificationBase(BaseModel):
    program_id: uuid.UUID
    notification_type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=2000)
    target_audience: Optional[str] = Field(None, max_length=500)
    scheduled_at: Optional[datetime] = None
    is_urgent: bool = False
    attachments: List[str] = Field(default_factory=list)

class BetaTestingNotificationCreate(BetaTestingNotificationBase):
    pass

class BetaTestingNotificationResponse(BetaTestingNotificationBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivery_status: str = "pending"
    recipient_count: int = 0

    class Config:
        from_attributes = True

class BetaTestingReportBase(BaseModel):
    program_id: uuid.UUID
    report_type: ReportType
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    parameters: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class BetaTestingReportResponse(BetaTestingReportBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    generated_at: Optional[datetime] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    status: str = "pending"

    class Config:
        from_attributes = True

class BetaTestingReportCreate(BaseModel):
    program_id: uuid.UUID
    report_type: str = Field(..., pattern="^(summary|detailed|analytics)$")
    title: str = Field(..., min_length=1, max_length=255)
    content: Dict[str, Any] = Field(..., min_items=1)

class BetaTestingDashboardResponse(BaseModel):
    program_id: Optional[uuid.UUID] = None
    total_programs: int
    active_programs: int
    total_participants: int
    active_participants: int
    total_feedback: int
    open_feedback: int
    total_surveys: int
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)
    feedback_summary: Dict[str, Any] = Field(default_factory=dict)
    participant_engagement: Dict[str, Any] = Field(default_factory=dict)
    top_programs: List[Dict[str, Any]] = Field(default_factory=list)
    system_health: Dict[str, Any] = Field(default_factory=dict)

# Request/Response models for bulk operations
class BulkParticipantCreate(BaseModel):
    participants: List[BetaTestingParticipantCreate]
    program_id: uuid.UUID

class BulkFeedbackCreate(BaseModel):
    feedback_items: List[BetaTestingFeedbackCreate]

class BulkNotificationCreate(BaseModel):
    notifications: List[BetaTestingNotificationCreate]

# Search and filter models
class BetaTestingSearchRequest(BaseModel):
    query: Optional[str] = None
    program_id: Optional[uuid.UUID] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

class BetaTestingSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    page: int
    pages: int
    has_next: bool
    has_prev: bool

class BetaTestingDashboardSummary(BaseModel):
    total_programs: int
    active_programs: int
    total_participants: int
    active_participants: int
    total_feedback: int
    open_feedback: int
    total_surveys: int
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)

class BetaTestingAnalyticsSummary(BaseModel):
    participant_engagement: Dict[str, Any] = Field(default_factory=dict)
    feedback_summary: Dict[str, Any] = Field(default_factory=dict)
    usage_metrics: Dict[str, Any] = Field(default_factory=dict)
    top_features: List[Dict[str, Any]] = Field(default_factory=list)
    system_health: Dict[str, Any] = Field(default_factory=dict)
