"""Pydantic models for health and fitness-related operations."""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class FitnessAssessmentBase(BaseModel):
    """Base model for fitness assessments."""
    student_id: int = Field(..., description="ID of the student being assessed")
    assessment_type: str = Field(..., description="Type of fitness assessment")
    metrics: Dict[str, Any] = Field(..., description="Assessment metrics")
    notes: Optional[str] = Field(None, description="Additional notes")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class FitnessAssessmentCreate(FitnessAssessmentBase):
    """Model for creating a fitness assessment."""
    pass

class FitnessAssessmentResponse(FitnessAssessmentBase):
    """Model for fitness assessment responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthMetricsBase(BaseModel):
    """Base model for health metrics."""
    student_id: int = Field(..., description="ID of the student")
    metric_type: str = Field(..., description="Type of health metric")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    is_abnormal: bool = Field(False, description="Whether the value is abnormal")
    notes: Optional[str] = Field(None, description="Additional notes")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class HealthMetricsCreate(HealthMetricsBase):
    """Model for creating health metrics."""
    pass

class HealthMetricsResponse(HealthMetricsBase):
    """Model for health metrics responses."""
    id: int
    measured_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExerciseRoutineBase(BaseModel):
    """Base model for exercise routines."""
    student_id: int = Field(..., description="ID of the student")
    name: str = Field(..., description="Name of the routine")
    description: str = Field(..., description="Description of the routine")
    exercises: List[Dict[str, Any]] = Field(..., description="List of exercises")
    duration_minutes: int = Field(..., description="Duration in minutes")
    difficulty_level: str = Field(..., description="Difficulty level")
    equipment_needed: Optional[List[str]] = Field(default_factory=list)
    target_areas: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = Field(None, description="Additional notes")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ExerciseRoutineCreate(ExerciseRoutineBase):
    """Model for creating exercise routines."""
    pass

class ExerciseRoutineResponse(ExerciseRoutineBase):
    """Model for exercise routine responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthMetricHistoryResponse(BaseModel):
    """Model for health metric history responses."""
    value: float
    unit: str
    recorded_at: datetime
    is_abnormal: bool
    notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class FitnessGoalProgressResponse(BaseModel):
    """Model for fitness goal progress responses."""
    goal_id: int
    value: float
    date: datetime
    notes: Optional[str]
    is_milestone: bool
    metadata: Optional[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)

class NutritionLogBase(BaseModel):
    """Base model for nutrition logs."""
    student_id: int = Field(..., description="ID of the student")
    meal_type: str = Field(..., description="Type of meal")
    foods_consumed: List[Dict[str, Any]] = Field(..., description="List of foods consumed")
    calories: Optional[int] = Field(None, description="Total calories")
    protein: Optional[float] = Field(None, description="Protein in grams")
    carbohydrates: Optional[float] = Field(None, description="Carbohydrates in grams")
    fats: Optional[float] = Field(None, description="Fats in grams")
    hydration: Optional[float] = Field(None, description="Hydration in liters")
    notes: Optional[str] = Field(None, description="Additional notes")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class NutritionLogCreate(NutritionLogBase):
    """Model for creating nutrition logs."""
    pass

class NutritionLogResponse(NutritionLogBase):
    """Model for nutrition log responses."""
    id: int
    date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkoutSessionCreate(BaseModel):
    """Model for recording workout sessions."""
    student_id: int = Field(..., description="ID of the student")
    start_time: datetime = Field(..., description="Session start time")
    end_time: Optional[datetime] = Field(None, description="Session end time")
    completed: bool = Field(False, description="Whether the session was completed")
    performance_data: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5, description="Difficulty rating (1-5)")
    enjoyment_rating: Optional[int] = Field(None, ge=1, le=5, description="Enjoyment rating (1-5)")
    notes: Optional[str] = Field(None, description="Session notes")
    modifications_used: Optional[Dict[str, Any]] = Field(None, description="Modifications used")

    model_config = ConfigDict(from_attributes=True)

class WorkoutSessionResponse(WorkoutSessionCreate):
    """Model for workout session responses."""
    id: int
    plan_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 