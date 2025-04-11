from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, status, Request, Security
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.services.physical_education.services.activity_manager import ActivityManager
from app.services.physical_education.services.activity_visualization_manager import ActivityVisualizationManager
from app.services.physical_education.services.activity_collaboration_manager import ActivityCollaborationManager
from app.services.physical_education.services.activity_export_manager import ActivityExportManager
from app.services.physical_education.services.activity_analysis_manager import ActivityAnalysisManager
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "activities:read": "Read activities",
        "activities:write": "Write activities",
        "activities:admin": "Admin activities"
    }
)

# Initialize managers
activity_manager = ActivityManager()
visualization_manager = ActivityVisualizationManager()
collaboration_manager = ActivityCollaborationManager()
export_manager = ActivityExportManager()
analysis_manager = ActivityAnalysisManager()

# Security settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Rate limiting settings
RATE_LIMIT_REQUESTS = 100  # requests
RATE_LIMIT_WINDOW = 60  # seconds

# Initialize Redis for rate limiting
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

# Request/Response Models
class ActivityData(BaseModel):
    student_id: str = Field(..., description="Unique identifier for the student", min_length=1, max_length=50)
    date: datetime = Field(..., description="Date and time of the activity")
    score: float = Field(..., ge=0, le=100, description="Activity score between 0 and 100")
    category: str = Field(..., description="Activity category", min_length=1, max_length=50)
    activity_type: str = Field(..., description="Type of activity", min_length=1, max_length=50)
    duration: int = Field(..., gt=0, description="Duration in minutes")
    intensity: float = Field(..., ge=0, le=1, description="Activity intensity between 0 and 1")
    notes: Optional[str] = Field(None, description="Additional notes about the activity", max_length=500)

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['strength', 'endurance', 'flexibility', 'balance', 'coordination']
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v.lower()

    @validator('activity_type')
    def validate_activity_type(cls, v):
        valid_types = ['running', 'swimming', 'cycling', 'weight_lifting', 'yoga', 'team_sports']
        if v.lower() not in valid_types:
            raise ValueError(f'Activity type must be one of: {", ".join(valid_types)}')
        return v.lower()

    @validator('duration')
    def validate_duration(cls, v):
        if v > 240:  # 4 hours
            raise ValueError('Activity duration cannot exceed 4 hours')
        return v

    @validator('intensity')
    def validate_intensity(cls, v):
        if v < 0.1:
            raise ValueError('Activity intensity must be at least 0.1')
        return v

class SkillData(BaseModel):
    student_id: str
    skill: str
    score: float = Field(..., ge=0, le=100)
    category: str
    target_score: float = Field(..., ge=0, le=100)
    progress: float
    notes: Optional[str] = None

class VisualizationRequest(BaseModel):
    student_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    visualization_types: List[str]
    interactive: bool = True
    drill_down: bool = True

class CollaborationSessionRequest(BaseModel):
    session_id: str
    participants: List[str]
    activity_ids: List[str]
    settings: Optional[Dict[str, Any]] = None

class ExportRequest(BaseModel):
    student_id: str
    visualization_type: str
    format: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class AnalysisRequest(BaseModel):
    student_id: str
    start_date: datetime
    end_date: datetime
    metrics: Optional[List[str]] = None

class ActivityTemplate(BaseModel):
    name: str
    description: str
    category: str
    activity_type: str
    default_duration: int = Field(..., gt=0)
    default_intensity: float = Field(..., ge=0, le=1)
    required_skills: List[str] = []
    recommended_skills: List[str] = []
    equipment_needed: List[str] = []
    setup_instructions: Optional[str] = None
    safety_guidelines: Optional[str] = None
    variations: List[str] = []
    difficulty_level: str = Field(..., pattern="^(beginner|intermediate|advanced)$")

class ActivityGoal(BaseModel):
    student_id: str
    activity_id: str
    target_score: float = Field(..., ge=0, le=100)
    target_date: datetime
    priority: str = Field(..., pattern="^(low|medium|high)$")
    notes: Optional[str] = None

class ActivityFeedback(BaseModel):
    activity_id: str = Field(..., description="Unique identifier for the activity", min_length=1, max_length=50)
    student_id: str = Field(..., description="ID of the student providing feedback", min_length=1, max_length=50)
    timestamp: datetime = Field(default_factory=datetime.now, description="Date and time of the feedback")
    rating: int = Field(..., description="Overall rating of the activity (1-5)", ge=1, le=5)
    difficulty_level: str = Field(..., description="Perceived difficulty level of the activity")
    engagement_score: int = Field(..., description="Engagement score (1-10)", ge=1, le=10)
    enjoyment_score: int = Field(..., description="Enjoyment score (1-10)", ge=1, le=10)
    learning_outcomes: List[str] = Field(..., description="List of achieved learning outcomes", min_items=1)
    suggestions: Optional[str] = Field(None, description="Suggestions for improvement", max_length=1000)
    challenges_faced: List[str] = Field(default_factory=list, description="List of challenges faced during the activity")
    strengths_identified: List[str] = Field(default_factory=list, description="List of strengths identified during the activity")
    areas_for_improvement: List[str] = Field(default_factory=list, description="List of areas needing improvement")
    instructor_feedback: Optional[str] = Field(None, description="Instructor's feedback on the activity", max_length=1000)
    peer_feedback: List[Dict[str, Any]] = Field(default_factory=list, description="Feedback from peers")
    self_reflection: Optional[str] = Field(None, description="Student's self-reflection", max_length=1000)
    follow_up_actions: List[Dict[str, Any]] = Field(default_factory=list, description="List of follow-up actions")

    @validator('difficulty_level')
    def validate_difficulty_level(cls, v):
        valid_levels = ['very_easy', 'easy', 'moderate', 'challenging', 'very_challenging']
        if v.lower() not in valid_levels:
            raise ValueError(f'Difficulty level must be one of: {", ".join(valid_levels)}')
        return v.lower()

    @validator('learning_outcomes')
    def validate_learning_outcomes(cls, v):
        if not v:
            raise ValueError('At least one learning outcome must be specified')
        for outcome in v:
            if not isinstance(outcome, str) or len(outcome.strip()) < 5:
                raise ValueError('Each learning outcome must be a non-empty string of at least 5 characters')
        return v

    @validator('challenges_faced')
    def validate_challenges_faced(cls, v):
        for challenge in v:
            if not isinstance(challenge, str) or len(challenge.strip()) < 5:
                raise ValueError('Each challenge must be a non-empty string of at least 5 characters')
        return v

    @validator('strengths_identified')
    def validate_strengths_identified(cls, v):
        for strength in v:
            if not isinstance(strength, str) or len(strength.strip()) < 5:
                raise ValueError('Each strength must be a non-empty string of at least 5 characters')
        return v

    @validator('areas_for_improvement')
    def validate_areas_for_improvement(cls, v):
        for area in v:
            if not isinstance(area, str) or len(area.strip()) < 5:
                raise ValueError('Each area for improvement must be a non-empty string of at least 5 characters')
        return v

    @validator('peer_feedback')
    def validate_peer_feedback(cls, v):
        required_fields = {'peer_id', 'rating', 'comments'}
        for feedback in v:
            if not isinstance(feedback, dict):
                raise ValueError('Each peer feedback must be a dictionary')
            missing_fields = required_fields - set(feedback.keys())
            if missing_fields:
                raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
            if not isinstance(feedback['rating'], int) or feedback['rating'] < 1 or feedback['rating'] > 5:
                raise ValueError('Peer rating must be between 1 and 5')
        return v

    @validator('follow_up_actions')
    def validate_follow_up_actions(cls, v):
        required_fields = {'action_id', 'description', 'due_date', 'status'}
        for action in v:
            if not isinstance(action, dict):
                raise ValueError('Each follow-up action must be a dictionary')
            missing_fields = required_fields - set(action.keys())
            if missing_fields:
                raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
            if not isinstance(action['status'], str) or action['status'] not in ['pending', 'in_progress', 'completed']:
                raise ValueError('Status must be one of: pending, in_progress, completed')
        return v

class BatchActivityRequest(BaseModel):
    activities: List[ActivityData] = Field(..., description="List of activities to be created in batch", min_items=1)
    template_id: Optional[str] = Field(None, description="Optional template ID to apply to all activities", min_length=1, max_length=50)
    validate_only: bool = Field(False, description="If True, only validate the activities without creating them")

    @validator('activities')
    def validate_activities(cls, v):
        if not v:
            raise ValueError('At least one activity must be provided')
        for activity in v:
            if not isinstance(activity, ActivityData):
                raise ValueError('Each activity must be an instance of ActivityData')
        return v

    @validator('template_id')
    def validate_template_id(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Template ID cannot be empty if provided')
        return v

class ActivityStatusUpdate(BaseModel):
    activity_id: str = Field(..., description="Unique identifier for the activity", min_length=1, max_length=50)
    status: str = Field(..., description="Current status of the activity")
    progress: float = Field(..., description="Progress percentage of the activity", ge=0, le=100)
    notes: Optional[str] = Field(None, description="Additional notes about the status update", max_length=1000)
    updated_by: str = Field(..., description="ID of the user updating the status", min_length=1, max_length=50)
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the status update")
    previous_status: Optional[str] = Field(None, description="Previous status of the activity")
    next_checkpoint: Optional[datetime] = Field(None, description="Next scheduled checkpoint")
    completion_date: Optional[datetime] = Field(None, description="Date when the activity was completed")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['not_started', 'in_progress', 'completed', 'on_hold', 'cancelled']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v.lower()

    @validator('progress')
    def validate_progress(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('Progress must be a number')
        if v < 0 or v > 100:
            raise ValueError('Progress must be between 0 and 100')
        return float(v)

    @validator('next_checkpoint')
    def validate_next_checkpoint(cls, v, values):
        if v is not None and 'timestamp' in values and v < values['timestamp']:
            raise ValueError('Next checkpoint cannot be in the past')
        return v

    @validator('completion_date')
    def validate_completion_date(cls, v, values):
        if v is not None:
            if 'timestamp' in values and v < values['timestamp']:
                raise ValueError('Completion date cannot be in the past')
            if 'status' in values and values['status'] != 'completed':
                raise ValueError('Completion date can only be set when status is "completed"')
        return v

    @validator('previous_status')
    def validate_previous_status(cls, v):
        if v is not None:
            valid_statuses = ['not_started', 'in_progress', 'completed', 'on_hold', 'cancelled']
            if v.lower() not in valid_statuses:
                raise ValueError(f'Previous status must be one of: {", ".join(valid_statuses)}')
        return v

class ActivityCategory(BaseModel):
    name: str = Field(..., description="Name of the activity category", min_length=1, max_length=50)
    description: str = Field(..., description="Description of the activity category", min_length=1, max_length=500)
    parent_category: Optional[str] = Field(None, description="Parent category ID if this is a subcategory", min_length=1, max_length=50)
    color_code: Optional[str] = Field(None, description="Color code for the category in hex format", pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, description="Icon identifier for the category", min_length=1, max_length=50)
    is_active: bool = Field(True, description="Whether the category is active")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the category was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the category was last updated")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the category")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Category name cannot be empty')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Category description cannot be empty')
        return v.strip()

    @validator('parent_category')
    def validate_parent_category(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Parent category ID cannot be empty if provided')
        return v

    @validator('color_code')
    def validate_color_code(cls, v):
        if v is not None:
            if not v.startswith('#'):
                raise ValueError('Color code must start with #')
            if len(v) != 7:
                raise ValueError('Color code must be 7 characters long (including #)')
            try:
                int(v[1:], 16)
            except ValueError:
                raise ValueError('Color code must be a valid hex color')
        return v

    @validator('icon')
    def validate_icon(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Icon identifier cannot be empty if provided')
        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError('Metadata must be a dictionary')
            for key, value in v.items():
                if not isinstance(key, str):
                    raise ValueError('Metadata keys must be strings')
                if not isinstance(value, (str, int, float, bool, list, dict)):
                    raise ValueError('Metadata values must be of type string, number, boolean, list, or dictionary')
        return v

class ActivityType(BaseModel):
    name: str = Field(..., description="Name of the activity type", min_length=1, max_length=50)
    description: str = Field(..., description="Description of the activity type", min_length=1, max_length=500)
    category: str = Field(..., description="Category ID this activity type belongs to", min_length=1, max_length=50)
    metrics: List[str] = Field(..., description="List of metrics used to measure this activity type", min_items=1)
    scoring_rules: Dict[str, Any] = Field(..., description="Rules for scoring this activity type")
    validation_rules: Dict[str, Any] = Field(..., description="Rules for validating this activity type")
    is_active: bool = Field(True, description="Whether the activity type is active")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the activity type was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the activity type was last updated")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the activity type")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Activity type name cannot be empty')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Activity type description cannot be empty')
        return v.strip()

    @validator('category')
    def validate_category(cls, v):
        if not v.strip():
            raise ValueError('Category ID cannot be empty')
        return v.strip()

    @validator('metrics')
    def validate_metrics(cls, v):
        if not v:
            raise ValueError('At least one metric must be specified')
        for metric in v:
            if not isinstance(metric, str) or not metric.strip():
                raise ValueError('Each metric must be a non-empty string')
        return v

    @validator('scoring_rules')
    def validate_scoring_rules(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Scoring rules must be a dictionary')
        required_fields = {'min_score', 'max_score', 'passing_score'}
        missing_fields = required_fields - set(v.keys())
        if missing_fields:
            raise ValueError(f'Missing required scoring rule fields: {", ".join(missing_fields)}')
        if not isinstance(v['min_score'], (int, float)) or v['min_score'] < 0:
            raise ValueError('Minimum score must be a non-negative number')
        if not isinstance(v['max_score'], (int, float)) or v['max_score'] <= v['min_score']:
            raise ValueError('Maximum score must be greater than minimum score')
        if not isinstance(v['passing_score'], (int, float)) or v['passing_score'] < v['min_score'] or v['passing_score'] > v['max_score']:
            raise ValueError('Passing score must be between minimum and maximum scores')
        return v

    @validator('validation_rules')
    def validate_validation_rules(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Validation rules must be a dictionary')
        required_fields = {'required_fields', 'field_types', 'field_ranges'}
        missing_fields = required_fields - set(v.keys())
        if missing_fields:
            raise ValueError(f'Missing required validation rule fields: {", ".join(missing_fields)}')
        if not isinstance(v['required_fields'], list):
            raise ValueError('Required fields must be a list')
        if not isinstance(v['field_types'], dict):
            raise ValueError('Field types must be a dictionary')
        if not isinstance(v['field_ranges'], dict):
            raise ValueError('Field ranges must be a dictionary')
        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError('Metadata must be a dictionary')
            for key, value in v.items():
                if not isinstance(key, str):
                    raise ValueError('Metadata keys must be strings')
                if not isinstance(value, (str, int, float, bool, list, dict)):
                    raise ValueError('Metadata values must be of type string, number, boolean, list, or dictionary')
        return v

# Response Models
class ActivityResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the activity", min_length=1, max_length=50)
    student_id: str = Field(..., description="ID of the student who performed the activity", min_length=1, max_length=50)
    date: datetime = Field(..., description="Date and time when the activity was performed")
    score: float = Field(..., description="Score achieved in the activity", ge=0, le=100)
    category: str = Field(..., description="Category of the activity", min_length=1, max_length=50)
    activity_type: str = Field(..., description="Type of activity performed", min_length=1, max_length=50)
    duration: int = Field(..., description="Duration of the activity in minutes", gt=0)
    intensity: float = Field(..., description="Intensity level of the activity", ge=0, le=1)
    notes: Optional[str] = Field(None, description="Additional notes about the activity", max_length=1000)
    status: str = Field(..., description="Current status of the activity")
    progress: float = Field(..., description="Progress percentage of the activity", ge=0, le=100)
    created_at: datetime = Field(..., description="Timestamp when the activity was created")
    updated_at: datetime = Field(..., description="Timestamp when the activity was last updated")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the activity")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['not_started', 'in_progress', 'completed', 'on_hold', 'cancelled']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v.lower()

    @validator('score')
    def validate_score(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('Score must be a number')
        if v < 0 or v > 100:
            raise ValueError('Score must be between 0 and 100')
        return float(v)

    @validator('duration')
    def validate_duration(cls, v):
        if not isinstance(v, int):
            raise ValueError('Duration must be an integer')
        if v <= 0:
            raise ValueError('Duration must be greater than 0')
        return v

    @validator('intensity')
    def validate_intensity(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('Intensity must be a number')
        if v < 0 or v > 1:
            raise ValueError('Intensity must be between 0 and 1')
        return float(v)

    @validator('progress')
    def validate_progress(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('Progress must be a number')
        if v < 0 or v > 100:
            raise ValueError('Progress must be between 0 and 100')
        return float(v)

    @validator('metadata')
    def validate_metadata(cls, v):
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError('Metadata must be a dictionary')
            for key, value in v.items():
                if not isinstance(key, str):
                    raise ValueError('Metadata keys must be strings')
                if not isinstance(value, (str, int, float, bool, list, dict)):
                    raise ValueError('Metadata values must be of type string, number, boolean, list, or dictionary')
        return v

class VisualizationResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the visualization", min_length=1, max_length=50)
    student_id: str = Field(..., description="ID of the student the visualization is for", min_length=1, max_length=50)
    visualization_type: str = Field(..., description="Type of visualization generated", min_length=1, max_length=50)
    data: Dict[str, Any] = Field(..., description="Data used to generate the visualization")
    created_at: datetime = Field(..., description="Timestamp when the visualization was created")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata for the visualization")
    format: str = Field(..., description="Format of the visualization", min_length=1, max_length=50)
    size: int = Field(..., description="Size of the visualization in bytes", gt=0)
    url: Optional[str] = Field(None, description="URL to access the visualization", max_length=500)
    is_interactive: bool = Field(False, description="Whether the visualization is interactive")
    drill_down_enabled: bool = Field(False, description="Whether drill-down functionality is enabled")
    accessibility_features: List[str] = Field(default_factory=list, description="List of accessibility features supported")
    theme: Optional[str] = Field(None, description="Theme used for the visualization", min_length=1, max_length=50)

    @validator('visualization_type')
    def validate_visualization_type(cls, v):
        valid_types = ['line_chart', 'bar_chart', 'pie_chart', 'scatter_plot', 'heatmap', 'sankey', 'treemap', 'sunburst']
        if v.lower() not in valid_types:
            raise ValueError(f'Visualization type must be one of: {", ".join(valid_types)}')
        return v.lower()

    @validator('format')
    def validate_format(cls, v):
        valid_formats = ['png', 'svg', 'pdf', 'html', 'json']
        if v.lower() not in valid_formats:
            raise ValueError(f'Format must be one of: {", ".join(valid_formats)}')
        return v.lower()

    @validator('data')
    def validate_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Data must be a dictionary')
        required_fields = {'x_axis', 'y_axis', 'values'}
        missing_fields = required_fields - set(v.keys())
        if missing_fields:
            raise ValueError(f'Missing required data fields: {", ".join(missing_fields)}')
        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Metadata must be a dictionary')
        required_fields = {'title', 'description', 'created_by'}
        missing_fields = required_fields - set(v.keys())
        if missing_fields:
            raise ValueError(f'Missing required metadata fields: {", ".join(missing_fields)}')
        return v

    @validator('accessibility_features')
    def validate_accessibility_features(cls, v):
        valid_features = ['high_contrast', 'screen_reader', 'keyboard_navigation', 'alt_text', 'color_blind']
        for feature in v:
            if feature.lower() not in valid_features:
                raise ValueError(f'Accessibility feature must be one of: {", ".join(valid_features)}')
        return v

    @validator('theme')
    def validate_theme(cls, v):
        if v is not None:
            valid_themes = ['light', 'dark', 'high_contrast', 'color_blind']
            if v.lower() not in valid_themes:
                raise ValueError(f'Theme must be one of: {", ".join(valid_themes)}')
        return v

class CollaborationSessionResponse(BaseModel):
    session_id: str
    participants: List[str]
    activity_ids: List[str]
    settings: Dict[str, Any]
    created_at: datetime
    status: str
    chat_history: List[Dict[str, Any]]

class ExportResponse(BaseModel):
    file_id: str
    student_id: str
    format: str
    file_path: str
    created_at: datetime
    size: int
    metadata: Dict[str, Any]

class AnalysisResponse(BaseModel):
    student_id: str
    start_date: datetime
    end_date: datetime
    metrics: Dict[str, Any]
    recommendations: List[str]
    trends: Dict[str, Any]
    strengths: List[str]
    areas_for_improvement: List[str]

# Response Models for remaining endpoints
class ChatMessageResponse(BaseModel):
    message_id: str
    session_id: str
    user_id: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]

class SkillResponse(BaseModel):
    id: str
    student_id: str
    skill: str
    score: float
    category: str
    target_score: float
    progress: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# New Request/Response Models
class ActivityProgress(BaseModel):
    activity_id: str = Field(..., description="Unique identifier for the activity", min_length=1, max_length=50)
    student_id: str = Field(..., description="Unique identifier for the student", min_length=1, max_length=50)
    current_stage: str = Field(..., description="Current stage of the activity", min_length=1, max_length=50)
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage between 0 and 100")
    milestones: List[Dict[str, Any]] = Field(default_factory=list, description="List of activity milestones")
    last_updated: datetime = Field(default_factory=datetime.now, description="Timestamp of last progress update")
    next_checkpoint: Optional[datetime] = Field(None, description="Next scheduled checkpoint")
    notes: Optional[str] = Field(None, description="Additional progress notes", max_length=500)

    @validator('current_stage')
    def validate_current_stage(cls, v):
        valid_stages = ['not_started', 'in_progress', 'completed', 'on_hold', 'needs_review']
        if v.lower() not in valid_stages:
            raise ValueError(f'Current stage must be one of: {", ".join(valid_stages)}')
        return v.lower()

    @validator('milestones')
    def validate_milestones(cls, v):
        if not isinstance(v, list):
            raise ValueError('Milestones must be a list')
        for milestone in v:
            if not isinstance(milestone, dict):
                raise ValueError('Each milestone must be a dictionary')
            required_fields = ['name', 'status', 'due_date']
            for field in required_fields:
                if field not in milestone:
                    raise ValueError(f'Milestone missing required field: {field}')
        return v

    @validator('next_checkpoint')
    def validate_next_checkpoint(cls, v, values):
        if v is not None and 'last_updated' in values and v < values['last_updated']:
            raise ValueError('Next checkpoint cannot be in the past')
        return v

class ActivityRecommendation(BaseModel):
    student_id: str = Field(..., description="Unique identifier for the student", min_length=1, max_length=50)
    activity_type: str = Field(..., description="Type of recommended activity", min_length=1, max_length=50)
    category: str = Field(..., description="Category of the recommended activity", min_length=1, max_length=50)
    priority: int = Field(..., ge=1, le=5, description="Priority level from 1 (lowest) to 5 (highest)")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1")
    rationale: str = Field(..., description="Explanation for the recommendation", min_length=10, max_length=500)
    suggested_duration: int = Field(..., ge=5, le=240, description="Suggested duration in minutes (5-240)")
    prerequisites: List[str] = Field(default_factory=list, description="List of prerequisite activities")
    target_skills: List[str] = Field(default_factory=list, description="List of skills targeted by this activity")
    estimated_difficulty: float = Field(..., ge=0, le=1, description="Estimated difficulty level between 0 and 1")
    last_updated: datetime = Field(default_factory=datetime.now, description="Timestamp of last update")

    @validator('activity_type')
    def validate_activity_type(cls, v):
        valid_types = ['individual', 'group', 'team', 'assessment', 'practice']
        if v.lower() not in valid_types:
            raise ValueError(f'Activity type must be one of: {", ".join(valid_types)}')
        return v.lower()

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['strength', 'endurance', 'flexibility', 'coordination', 'balance']
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v.lower()

    @validator('prerequisites')
    def validate_prerequisites(cls, v):
        if not isinstance(v, list):
            raise ValueError('Prerequisites must be a list')
        for item in v:
            if not isinstance(item, str):
                raise ValueError('Each prerequisite must be a string')
        return v

    @validator('target_skills')
    def validate_target_skills(cls, v):
        if not isinstance(v, list):
            raise ValueError('Target skills must be a list')
        for item in v:
            if not isinstance(item, str):
                raise ValueError('Each target skill must be a string')
        return v

class ActivitySchedule(BaseModel):
    student_id: str = Field(..., description="Unique identifier for the student", min_length=1, max_length=50)
    activity_id: str = Field(..., description="Unique identifier for the activity", min_length=1, max_length=50)
    start_time: datetime = Field(..., description="Scheduled start time of the activity")
    end_time: datetime = Field(..., description="Scheduled end time of the activity")
    status: str = Field(..., description="Current status of the scheduled activity")
    location: str = Field(..., description="Location where the activity will take place", min_length=1, max_length=100)
    instructor_id: Optional[str] = Field(None, description="ID of the instructor if assigned", min_length=1, max_length=50)
    equipment_needed: List[str] = Field(default_factory=list, description="List of required equipment")
    notes: Optional[str] = Field(None, description="Additional notes about the schedule", max_length=500)
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern if activity repeats")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the schedule was created")
    last_modified: datetime = Field(default_factory=datetime.now, description="Timestamp of last modification")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v.lower()

    @validator('recurrence_pattern')
    def validate_recurrence_pattern(cls, v):
        if v is not None:
            valid_patterns = ['daily', 'weekly', 'biweekly', 'monthly']
            if v.lower() not in valid_patterns:
                raise ValueError(f'Recurrence pattern must be one of: {", ".join(valid_patterns)}')
        return v

    @validator('equipment_needed')
    def validate_equipment(cls, v):
        if not isinstance(v, list):
            raise ValueError('Equipment needed must be a list')
        for item in v:
            if not isinstance(item, str):
                raise ValueError('Each equipment item must be a string')
        return v

class EquipmentCheck(BaseModel):
    activity_id: str = Field(..., description="Unique identifier for the activity", min_length=1, max_length=50)
    equipment_items: List[Dict[str, Any]] = Field(..., description="List of equipment items to check")
    checked_by: str = Field(..., description="ID of the person performing the check", min_length=1, max_length=50)
    check_date: datetime = Field(default_factory=datetime.now, description="Date and time of the equipment check")
    status: str = Field(..., description="Overall status of the equipment check")
    notes: Optional[str] = Field(None, description="Additional notes about the equipment check", max_length=500)
    next_check_date: Optional[datetime] = Field(None, description="Scheduled date for next equipment check")
    maintenance_required: bool = Field(False, description="Whether maintenance is required")
    maintenance_notes: Optional[str] = Field(None, description="Notes about required maintenance", max_length=500)

    @validator('equipment_items')
    def validate_equipment_items(cls, v):
        if not isinstance(v, list):
            raise ValueError('Equipment items must be a list')
        required_fields = {'item_id', 'name', 'condition', 'quantity'}
        for item in v:
            if not isinstance(item, dict):
                raise ValueError('Each equipment item must be a dictionary')
            missing_fields = required_fields - set(item.keys())
            if missing_fields:
                raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
            if not isinstance(item['quantity'], int) or item['quantity'] < 0:
                raise ValueError('Quantity must be a non-negative integer')
            if not isinstance(item['condition'], str) or item['condition'] not in ['excellent', 'good', 'fair', 'poor', 'needs_repair']:
                raise ValueError('Condition must be one of: excellent, good, fair, poor, needs_repair')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'in_progress', 'completed', 'failed']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v.lower()

    @validator('next_check_date')
    def validate_next_check_date(cls, v, values):
        if v is not None and 'check_date' in values and v <= values['check_date']:
            raise ValueError('Next check date must be after current check date')
        return v

class SafetyCheck(BaseModel):
    activity_id: str = Field(..., description="Unique identifier for the activity", min_length=1, max_length=50)
    checked_by: str = Field(..., description="ID of the person performing the safety check", min_length=1, max_length=50)
    check_date: datetime = Field(default_factory=datetime.now, description="Date and time of the safety check")
    status: str = Field(..., description="Overall status of the safety check")
    location: str = Field(..., description="Location where the safety check was performed", min_length=1, max_length=100)
    hazards: List[Dict[str, Any]] = Field(default_factory=list, description="List of identified hazards")
    safety_measures: List[Dict[str, Any]] = Field(default_factory=list, description="List of implemented safety measures")
    emergency_procedures: List[Dict[str, Any]] = Field(default_factory=list, description="List of emergency procedures")
    notes: Optional[str] = Field(None, description="Additional notes about the safety check", max_length=500)
    next_check_date: Optional[datetime] = Field(None, description="Scheduled date for next safety check")
    weather_conditions: Optional[Dict[str, Any]] = Field(None, description="Weather conditions during the check")
    participant_count: Optional[int] = Field(None, description="Number of participants during the check", ge=0)
    supervisor_present: bool = Field(False, description="Whether a supervisor was present during the check")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['safe', 'unsafe', 'requires_attention', 'pending_review']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v.lower()

    @validator('hazards')
    def validate_hazards(cls, v):
        if not isinstance(v, list):
            raise ValueError('Hazards must be a list')
        required_fields = {'hazard_id', 'description', 'severity', 'mitigation_plan'}
        for hazard in v:
            if not isinstance(hazard, dict):
                raise ValueError('Each hazard must be a dictionary')
            missing_fields = required_fields - set(hazard.keys())
            if missing_fields:
                raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
            if not isinstance(hazard['severity'], str) or hazard['severity'] not in ['low', 'medium', 'high', 'critical']:
                raise ValueError('Severity must be one of: low, medium, high, critical')
        return v

    @validator('safety_measures')
    def validate_safety_measures(cls, v):
        if not isinstance(v, list):
            raise ValueError('Safety measures must be a list')
        required_fields = {'measure_id', 'description', 'implementation_status'}
        for measure in v:
            if not isinstance(measure, dict):
                raise ValueError('Each safety measure must be a dictionary')
            missing_fields = required_fields - set(measure.keys())
            if missing_fields:
                raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
            if not isinstance(measure['implementation_status'], str) or measure['implementation_status'] not in ['planned', 'in_progress', 'completed']:
                raise ValueError('Implementation status must be one of: planned, in_progress, completed')
        return v

    @validator('emergency_procedures')
    def validate_emergency_procedures(cls, v):
        if not isinstance(v, list):
            raise ValueError('Emergency procedures must be a list')
        required_fields = {'procedure_id', 'description', 'contact_person', 'contact_number'}
        for procedure in v:
            if not isinstance(procedure, dict):
                raise ValueError('Each emergency procedure must be a dictionary')
            missing_fields = required_fields - set(procedure.keys())
            if missing_fields:
                raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
        return v

    @validator('weather_conditions')
    def validate_weather_conditions(cls, v):
        if v is not None:
            required_fields = {'temperature', 'conditions', 'wind_speed'}
            missing_fields = required_fields - set(v.keys())
            if missing_fields:
                raise ValueError(f'Missing required weather fields: {", ".join(missing_fields)}')
            if not isinstance(v['temperature'], (int, float)):
                raise ValueError('Temperature must be a number')
            if not isinstance(v['wind_speed'], (int, float)) or v['wind_speed'] < 0:
                raise ValueError('Wind speed must be a non-negative number')
        return v

    @validator('next_check_date')
    def validate_next_check_date(cls, v, values):
        if v is not None and 'check_date' in values and v <= values['check_date']:
            raise ValueError('Next check date must be after current check date')
        return v

# New Response Models
class ProgressResponse(BaseModel):
    activity_id: str
    student_id: str
    progress: ActivityProgress
    recommendations: List[ActivityRecommendation]
    next_steps: List[str]
    estimated_completion: datetime

class ScheduleResponse(BaseModel):
    schedule_id: str
    activity: ActivitySchedule
    participants: List[str]
    equipment_status: List[EquipmentCheck]
    safety_status: SafetyCheck
    status: str
    created_at: datetime
    updated_at: datetime

# Security models
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: List[str] = []

class UserInDB(User):
    hashed_password: str

# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["activities:read"])
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Rate limiting middleware
@router.middleware("http")
async def add_rate_limiting(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    # Get current request count
    current = redis_client.get(key)
    if current is None:
        redis_client.setex(key, RATE_LIMIT_WINDOW, 1)
    else:
        current = int(current)
        if current >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )
        redis_client.incr(key)
    
    response = await call_next(request)
    return response

# Authentication middleware
@router.middleware("http")
async def add_authentication(request: Request, call_next):
    if request.url.path not in ["/token", "/docs", "/openapi.json"]:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme"
                )
            await get_current_user(SecurityScopes([]), token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    response = await call_next(request)
    return response

# Token endpoints
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "scopes": user.scopes}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/token/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    current_user: User = Depends(get_current_active_user)
):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username, "scopes": payload.get("scopes", [])},
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            data={"sub": username, "scopes": payload.get("scopes", [])}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": new_refresh_token
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

# Activity Management Endpoints
@router.post(
    "/activities",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new activity",
    description="Creates a new activity record with the provided data",
    response_description="The created activity record"
)
async def create_activity(
    activity: ActivityData,
    token: str = Depends(oauth2_scheme)
):
    """Create a new activity record."""
    try:
        result = await activity_manager.create_activity(
            student_id=activity.student_id,
            date=activity.date,
            score=activity.score,
            category=activity.category,
            activity_type=activity.activity_type,
            duration=activity.duration,
            intensity=activity.intensity,
            notes=activity.notes
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the activity: {str(e)}"
        )

@router.get(
    "/activities/{student_id}",
    response_model=List[ActivityResponse],
    summary="Get activities for a student",
    description="Retrieves activities for a specific student with optional filters",
    response_description="List of activities matching the criteria"
)
async def get_activities(
    student_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get activities for a student with optional filters."""
    try:
        result = await activity_manager.get_activities(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
            category=category
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving activities: {str(e)}"
        )

# Visualization Endpoints
@router.post(
    "/visualizations",
    response_model=List[VisualizationResponse],
    summary="Generate visualizations",
    description="Generates visualizations for a student's activities",
    response_description="List of generated visualizations"
)
async def generate_visualizations(
    request: VisualizationRequest,
    token: str = Depends(oauth2_scheme)
):
    """Generate visualizations for a student."""
    try:
        activities = await activity_manager.get_activities(
            student_id=request.student_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        skills = await activity_manager.get_skills(
            student_id=request.student_id
        )
        
        result = await visualization_manager.generate_visualizations(
            student_id=request.student_id,
            performance_data=activities,
            skill_data=skills,
            visualization_types=request.visualization_types,
            interactive=request.interactive,
            drill_down=request.drill_down
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating visualizations: {str(e)}"
        )

# Collaboration Endpoints
@router.post(
    "/collaboration/sessions",
    response_model=CollaborationSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create collaboration session",
    description="Creates a new collaboration session for activities",
    response_description="The created collaboration session"
)
async def create_collaboration_session(
    request: CollaborationSessionRequest,
    token: str = Depends(oauth2_scheme)
):
    """Create a new collaboration session."""
    try:
        result = await collaboration_manager.start_collaborative_session(
            session_id=request.session_id,
            participants=request.participants,
            activity_ids=request.activity_ids,
            settings=request.settings
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the collaboration session: {str(e)}"
        )

@router.post(
    "/collaboration/sessions/{session_id}/chat",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add chat message",
    description="Adds a chat message to a collaboration session",
    response_description="The created chat message"
)
async def add_chat_message(
    session_id: str,
    user_id: str,
    message: str,
    token: str = Depends(oauth2_scheme)
):
    """Add a chat message to a collaboration session."""
    try:
        result = await collaboration_manager.add_chat_message(
            session_id=session_id,
            user_id=user_id,
            message=message
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while adding the chat message: {str(e)}"
        )

# Export Endpoints
@router.post(
    "/export",
    response_model=ExportResponse,
    summary="Export visualization",
    description="Exports a visualization in the specified format",
    response_description="The exported file information"
)
async def export_visualization(
    request: ExportRequest,
    token: str = Depends(oauth2_scheme)
):
    """Export a visualization in the specified format."""
    try:
        activities = await activity_manager.get_activities(
            student_id=request.student_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        visualization = await visualization_manager.generate_visualizations(
            student_id=request.student_id,
            performance_data=activities,
            visualization_types=[request.visualization_type],
            interactive=False
        )[0]
        
        result = await export_manager.export_visualization(
            visualization=visualization,
            format=request.format,
            student_id=request.student_id
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while exporting the visualization: {str(e)}"
        )

# Analysis Endpoints
@router.post(
    "/analysis",
    response_model=AnalysisResponse,
    summary="Analyze performance",
    description="Analyzes student performance for the given period",
    response_description="The analysis results"
)
async def analyze_performance(
    request: AnalysisRequest,
    token: str = Depends(oauth2_scheme)
):
    """Analyze student performance."""
    try:
        result = await analysis_manager.analyze_student_performance(
            student_id=request.student_id,
            start_date=request.start_date,
            end_date=request.end_date,
            metrics=request.metrics
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing performance: {str(e)}"
        )

# Skill Management Endpoints
@router.post(
    "/skills",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create skill record",
    description="Creates a new skill record for a student",
    response_description="The created skill record"
)
async def create_skill(
    skill: SkillData,
    token: str = Depends(oauth2_scheme)
):
    """Create a new skill record."""
    try:
        result = await activity_manager.create_skill(
            student_id=skill.student_id,
            skill=skill.skill,
            score=skill.score,
            category=skill.category,
            target_score=skill.target_score,
            progress=skill.progress,
            notes=skill.notes
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the skill record: {str(e)}"
        )

@router.get(
    "/skills/{student_id}",
    response_model=List[SkillResponse],
    summary="Get student skills",
    description="Retrieves skills for a specific student with optional category filter",
    response_description="List of skills matching the criteria"
)
async def get_skills(
    student_id: str,
    category: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get skills for a student with optional category filter."""
    try:
        result = await activity_manager.get_skills(
            student_id=student_id,
            category=category
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving skills: {str(e)}"
        )

# Activity Template Endpoints
@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_activity_template(
    template: ActivityTemplate,
    token: str = Depends(oauth2_scheme)
):
    """Create a new activity template."""
    try:
        return await activity_manager.create_activity_template(template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_activity_templates(
    category: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get activity templates with optional filters."""
    try:
        return await activity_manager.get_activity_templates(
            category=category,
            difficulty_level=difficulty_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Activity Goals Endpoints
@router.post("/goals", status_code=status.HTTP_201_CREATED)
async def create_activity_goal(
    goal: ActivityGoal,
    token: str = Depends(oauth2_scheme)
):
    """Create a new activity goal."""
    try:
        return await activity_manager.create_activity_goal(goal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/goals/{student_id}")
async def get_activity_goals(
    student_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get activity goals for a student with optional filters."""
    try:
        return await activity_manager.get_activity_goals(
            student_id=student_id,
            status=status,
            priority=priority
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Activity Feedback Endpoints
@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_activity_feedback(
    feedback: ActivityFeedback,
    token: str = Depends(oauth2_scheme)
):
    """Submit feedback for an activity."""
    try:
        return await activity_manager.submit_activity_feedback(feedback)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/{activity_id}")
async def get_activity_feedback(
    activity_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Get feedback for a specific activity."""
    try:
        return await activity_manager.get_activity_feedback(activity_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Batch Operations Endpoints
@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_batch_activities(
    request: BatchActivityRequest,
    token: str = Depends(oauth2_scheme)
):
    """Create multiple activities in a single request."""
    try:
        return await activity_manager.create_batch_activities(
            activities=request.activities,
            template_id=request.template_id,
            validate_only=request.validate_only
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Activity Status Endpoints
@router.put("/status")
async def update_activity_status(
    update: ActivityStatusUpdate,
    token: str = Depends(oauth2_scheme)
):
    """Update the status of an activity."""
    try:
        return await activity_manager.update_activity_status(update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Activity Categories Endpoints
@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_activity_category(
    category: ActivityCategory,
    token: str = Depends(oauth2_scheme)
):
    """Create a new activity category."""
    try:
        return await activity_manager.create_activity_category(category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_activity_categories(
    parent_category: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get activity categories with optional parent filter."""
    try:
        return await activity_manager.get_activity_categories(
            parent_category=parent_category
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Activity Types Endpoints
@router.post("/types", status_code=status.HTTP_201_CREATED)
async def create_activity_type(
    activity_type: ActivityType,
    token: str = Depends(oauth2_scheme)
):
    """Create a new activity type."""
    try:
        return await activity_manager.create_activity_type(activity_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types")
async def get_activity_types(
    category: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get activity types with optional category filter."""
    try:
        return await activity_manager.get_activity_types(category=category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New Endpoints
@router.post(
    "/progress",
    response_model=ProgressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Track activity progress",
    description="Tracks and updates the progress of an activity",
    response_description="The updated progress information"
)
async def track_progress(
    progress: ActivityProgress,
    token: str = Depends(oauth2_scheme)
):
    """Track and update activity progress."""
    try:
        result = await activity_manager.track_progress(progress)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while tracking progress: {str(e)}"
        )

@router.get(
    "/recommendations/{student_id}",
    response_model=List[ActivityRecommendation],
    summary="Get activity recommendations",
    description="Gets personalized activity recommendations for a student",
    response_description="List of recommended activities"
)
async def get_recommendations(
    student_id: str,
    category: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get activity recommendations for a student."""
    try:
        result = await activity_manager.get_recommendations(
            student_id=student_id,
            category=category,
            difficulty_level=difficulty_level
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while getting recommendations: {str(e)}"
        )

@router.post(
    "/schedule",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule an activity",
    description="Creates a new activity schedule",
    response_description="The created schedule"
)
async def create_schedule(
    schedule: ActivitySchedule,
    token: str = Depends(oauth2_scheme)
):
    """Create a new activity schedule."""
    try:
        result = await activity_manager.create_schedule(schedule)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the schedule: {str(e)}"
        )

@router.post(
    "/equipment/check",
    response_model=List[EquipmentCheck],
    summary="Check equipment status",
    description="Performs equipment safety and maintenance checks",
    response_description="List of equipment check results"
)
async def check_equipment(
    equipment_checks: List[EquipmentCheck],
    token: str = Depends(oauth2_scheme)
):
    """Perform equipment safety and maintenance checks."""
    try:
        result = await activity_manager.check_equipment(equipment_checks)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while checking equipment: {str(e)}"
        )

@router.post(
    "/safety/check",
    response_model=SafetyCheck,
    summary="Perform safety check",
    description="Performs a comprehensive safety check for an activity",
    response_description="The safety check results"
)
async def perform_safety_check(
    safety_check: SafetyCheck,
    token: str = Depends(oauth2_scheme)
):
    """Perform a comprehensive safety check."""
    try:
        result = await activity_manager.perform_safety_check(safety_check)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while performing safety check: {str(e)}"
        ) 