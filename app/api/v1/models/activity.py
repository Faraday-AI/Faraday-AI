from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, ConfigDict
from enum import Enum

class ActivityStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ActivityData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    student_id: str = Field(..., description="ID of the student")
    date: datetime = Field(..., description="Date of the activity")
    score: float = Field(..., description="Score achieved in the activity", ge=0, le=100)
    category: str = Field(..., description="Category of the activity")
    activity_type: str = Field(..., description="Type of activity")
    duration: int = Field(..., description="Duration in minutes", gt=0)
    intensity: str = Field(..., description="Intensity level of the activity")
    notes: Optional[str] = Field(None, description="Additional notes about the activity", max_length=500)
    status: ActivityStatus = Field(ActivityStatus.PLANNED, description="Status of the activity")

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['strength', 'endurance', 'flexibility', 'balance', 'coordination']
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v.lower()

    @validator('intensity')
    def validate_intensity(cls, v):
        valid_intensities = ['low', 'medium', 'high']
        if v.lower() not in valid_intensities:
            raise ValueError(f'Intensity must be one of: {", ".join(valid_intensities)}')
        return v.lower()

class BatchActivityRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    activities: List[ActivityData] = Field(..., description="List of activities to create")
    batch_notes: Optional[str] = Field(None, description="Notes for the batch of activities")

    @validator('activities')
    def validate_activities(cls, v):
        if not v:
            raise ValueError('At least one activity must be provided')
        return v

class ActivityStatusUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: ActivityStatus = Field(..., description="New status of the activity")
    notes: Optional[str] = Field(None, description="Notes about the status update")

class ActivityCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., description="Name of the category")
    description: str = Field(..., description="Description of the category")
    target_score: float = Field(..., description="Target score for this category", ge=0, le=100)
    weight: float = Field(..., description="Weight of this category in overall score", ge=0, le=1)

    @validator('name')
    def validate_name(cls, v):
        valid_categories = ['strength', 'endurance', 'flexibility', 'balance', 'coordination']
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v.lower()

class ActivityType(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., description="Name of the activity type")
    category: str = Field(..., description="Category this type belongs to")
    description: str = Field(..., description="Description of the activity type")
    min_duration: int = Field(..., description="Minimum duration in minutes", gt=0)
    max_duration: int = Field(..., description="Maximum duration in minutes", gt=0)
    target_intensity: str = Field(..., description="Target intensity level")

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['strength', 'endurance', 'flexibility', 'balance', 'coordination']
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v.lower()

    @validator('target_intensity')
    def validate_target_intensity(cls, v):
        valid_intensities = ['low', 'medium', 'high']
        if v.lower() not in valid_intensities:
            raise ValueError(f'Target intensity must be one of: {", ".join(valid_intensities)}')
        return v.lower()

    @validator('max_duration')
    def validate_duration_range(cls, v, values):
        if 'min_duration' in values and v < values['min_duration']:
            raise ValueError('Maximum duration must be greater than minimum duration')
        return v

class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    activity_id: str = Field(..., description="Unique identifier for the activity")
    student_id: str = Field(..., description="ID of the student")
    date: datetime = Field(..., description="Date of the activity")
    score: float = Field(..., description="Score achieved in the activity", ge=0, le=100)
    category: str = Field(..., description="Category of the activity")
    activity_type: str = Field(..., description="Type of activity")
    duration: int = Field(..., description="Duration in minutes", gt=0)
    intensity: str = Field(..., description="Intensity level of the activity")
    notes: Optional[str] = Field(None, description="Additional notes about the activity", max_length=500)
    status: ActivityStatus = Field(..., description="Status of the activity")
    created_at: datetime = Field(..., description="When the activity was created")
    updated_at: datetime = Field(..., description="When the activity was last updated")

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['strength', 'endurance', 'flexibility', 'balance', 'coordination']
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v.lower()

    @validator('intensity')
    def validate_intensity(cls, v):
        valid_intensities = ['low', 'medium', 'high']
        if v.lower() not in valid_intensities:
            raise ValueError(f'Intensity must be one of: {", ".join(valid_intensities)}')
        return v.lower()

class ActivityListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    activities: List[ActivityResponse] = Field(..., description="List of activities")
    total_count: int = Field(..., description="Total number of activities")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    @validator('activities')
    def validate_activities(cls, v):
        if not v:
            raise ValueError('Activities list cannot be empty')
        return v

    @validator('total_pages')
    def validate_total_pages(cls, v, values):
        if 'page_size' in values and 'total_count' in values:
            expected_pages = (values['total_count'] + values['page_size'] - 1) // values['page_size']
            if v != expected_pages:
                raise ValueError(f'Total pages should be {expected_pages} based on total_count and page_size')
        return v

class ActivityProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    current_score: float = Field(..., description="Current score", ge=0, le=100)
    target_score: float = Field(..., description="Target score", ge=0, le=100)
    progress_percentage: float = Field(..., description="Progress percentage", ge=0, le=100)
    last_updated: datetime = Field(..., description="When the progress was last updated")
    trend: str = Field(..., description="Trend of progress (improving, stable, declining)")
    confidence: float = Field(..., description="Confidence in the progress assessment", ge=0, le=1)

    @validator('target_score')
    def validate_target_score(cls, v, values):
        if 'current_score' in values and v < values['current_score']:
            raise ValueError('Target score must be greater than or equal to current score')
        return v

    @validator('trend')
    def validate_trend(cls, v):
        valid_trends = ['improving', 'stable', 'declining']
        if v.lower() not in valid_trends:
            raise ValueError(f'Trend must be one of: {", ".join(valid_trends)}')
        return v.lower()

class ActivityRecommendation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    activity_type: str = Field(..., description="Type of activity recommended")
    category: str = Field(..., description="Category of the activity")
    duration: int = Field(..., description="Recommended duration in minutes", gt=0)
    intensity: str = Field(..., description="Recommended intensity level")
    priority: str = Field(..., description="Priority of the recommendation")
    reason: str = Field(..., description="Reason for the recommendation")
    expected_improvement: float = Field(..., description="Expected improvement percentage", ge=0, le=100)

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['strength', 'endurance', 'flexibility', 'balance', 'coordination']
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v.lower()

    @validator('intensity')
    def validate_intensity(cls, v):
        valid_intensities = ['low', 'medium', 'high']
        if v.lower() not in valid_intensities:
            raise ValueError(f'Intensity must be one of: {", ".join(valid_intensities)}')
        return v.lower()

    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['high', 'medium', 'low']
        if v.lower() not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v.lower()

class ActivitySchedule(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    activity_type: str = Field(..., description="Type of activity")
    category: str = Field(..., description="Category of the activity")
    scheduled_date: datetime = Field(..., description="Scheduled date and time")
    duration: int = Field(..., description="Planned duration in minutes", gt=0)
    location: str = Field(..., description="Location of the activity")
    instructor: Optional[str] = Field(None, description="Instructor for the activity")
    notes: Optional[str] = Field(None, description="Additional notes about the schedule", max_length=500)

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['strength', 'endurance', 'flexibility', 'balance', 'coordination']
        if v.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v.lower()

class EquipmentCheck(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    activity_id: str = Field(..., description="ID of the activity")
    checked_by: str = Field(..., description="ID of the person who performed the check")
    check_date: datetime = Field(..., description="Date and time of the check")
    status: str = Field(..., description="Status of the equipment check")
    equipment_items: List[Dict[str, Any]] = Field(..., description="List of equipment items checked")
    notes: Optional[str] = Field(None, description="Additional notes about the equipment check", max_length=500)
    next_check_date: Optional[datetime] = Field(None, description="Scheduled date for next equipment check")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['safe', 'unsafe', 'requires_attention', 'pending_review']
        if v.lower() not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v.lower()

    @validator('equipment_items')
    def validate_equipment_items(cls, v):
        if not isinstance(v, list):
            raise ValueError('Equipment items must be a list')
        required_fields = {'item_id', 'name', 'condition', 'last_maintenance'}
        for item in v:
            if not isinstance(item, dict):
                raise ValueError('Each equipment item must be a dictionary')
            missing_fields = required_fields - set(item.keys())
            if missing_fields:
                raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
            if not isinstance(item['condition'], str) or item['condition'] not in ['good', 'fair', 'poor', 'needs_replacement']:
                raise ValueError('Condition must be one of: good, fair, poor, needs_replacement')
        return v

    @validator('next_check_date')
    def validate_next_check_date(cls, v, values):
        if v is not None and 'check_date' in values and v <= values['check_date']:
            raise ValueError('Next check date must be after current check date')
        return v

class SafetyCheck(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    activity_id: str = Field(..., description="ID of the activity")
    checked_by: str = Field(..., description="ID of the person who performed the check")
    check_date: datetime = Field(..., description="Date and time of the check")
    status: str = Field(..., description="Status of the safety check")
    location: str = Field(..., description="Location of the activity")
    hazards: List[Dict[str, Any]] = Field(..., description="List of identified hazards")
    safety_measures: List[Dict[str, Any]] = Field(..., description="List of safety measures in place")
    emergency_procedures: List[Dict[str, Any]] = Field(..., description="List of emergency procedures")
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
        required_fields = {'hazard_id', 'description', 'severity', 'mitigation'}
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
        required_fields = {'measure_id', 'description', 'status', 'responsible_party'}
        for measure in v:
            if not isinstance(measure, dict):
                raise ValueError('Each safety measure must be a dictionary')
            missing_fields = required_fields - set(measure.keys())
            if missing_fields:
                raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
            if not isinstance(measure['status'], str) or measure['status'] not in ['implemented', 'pending', 'not_applicable']:
                raise ValueError('Status must be one of: implemented, pending, not_applicable')
        return v

    @validator('emergency_procedures')
    def validate_emergency_procedures(cls, v):
        if not isinstance(v, list):
            raise ValueError('Emergency procedures must be a list')
        required_fields = {'procedure_id', 'description', 'contact_person', 'location'}
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
            if not isinstance(v, dict):
                raise ValueError('Weather conditions must be a dictionary')
            missing_fields = required_fields - set(v.keys())
            if missing_fields:
                raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
        return v

    @validator('next_check_date')
    def validate_next_check_date(cls, v, values):
        if v is not None and 'check_date' in values and v <= values['check_date']:
            raise ValueError('Next check date must be after current check date')
        return v

class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    activity_id: str = Field(..., description="ID of the activity")
    student_id: str = Field(..., description="ID of the student")
    progress: ActivityProgress = Field(..., description="Progress information")
    recommendations: List[ActivityRecommendation] = Field(..., description="List of recommendations")
    next_steps: List[str] = Field(..., description="List of next steps")
    estimated_completion: datetime = Field(..., description="Estimated completion date")

class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schedule_id: str = Field(..., description="ID of the schedule")
    activity: ActivitySchedule = Field(..., description="Activity schedule information")
    participants: List[str] = Field(..., description="List of participant IDs")
    equipment_status: List[EquipmentCheck] = Field(..., description="Equipment check status")
    safety_status: SafetyCheck = Field(..., description="Safety check status")
    status: str = Field(..., description="Status of the schedule")
    created_at: datetime = Field(..., description="When the schedule was created")
    updated_at: datetime = Field(..., description="When the schedule was last updated") 