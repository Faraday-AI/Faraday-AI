from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator, ConfigDict
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.core.auth import get_current_active_user, oauth2_scheme
from app.core.rate_limit import rate_limit
from app.core.cache import cache_manager
from app.services.physical_education.health_metrics_manager import health_metrics_manager
from app.services.physical_education.fitness_goal_manager import fitness_goal_manager
from app.services.physical_education.workout_planner import workout_planner
from app.services.physical_education.nutrition_planner import nutrition_planner
from app.models.student import (
    Student,
    HealthMetricThreshold,
    StudentHealthFitnessGoal,
    StudentHealthGoalProgress,
    StudentHealthGoalRecommendation,
    MetricType,
    MeasurementUnit,
    GoalType,
    GoalStatus
)
from app.models.health_fitness.metrics.health import HealthMetric, HealthMetricHistory
from app.services.physical_education.health_fitness_service import HealthFitnessService
from app.schemas.health_fitness import (
    FitnessAssessmentCreate,
    FitnessAssessmentResponse,
    HealthMetricsCreate,
    HealthMetricsResponse,
    ExerciseRoutineCreate,
    ExerciseRoutineResponse,
    WorkoutSessionCreate,
    WorkoutSessionResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/health-fitness",
    tags=["health-fitness"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many requests"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

# Rate limiting configuration
RATE_LIMIT = {
    "health_metrics": {"requests": 30, "period": 60},
    "fitness_goals": {"requests": 20, "period": 60},
    "workout_plans": {"requests": 20, "period": 60},
    "nutrition_plans": {"requests": 20, "period": 60}
}

# Response Models
class HealthMetricResponse(BaseModel):
    """Response model for health metrics."""
    id: int
    student_id: int
    metric_type: str
    value: float
    unit: str
    is_abnormal: bool
    notes: Optional[str]
    metadata: Dict[str, Any]
    measured_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthMetricRequest(BaseModel):
    """Request model for recording health metrics."""
    metric_type: str = Field(..., min_length=1, max_length=50)
    value: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=20)
    notes: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('metric_type')
    def validate_metric_type(cls, v):
        valid_types = ['HEART_RATE', 'RESPIRATORY_RATE', 'FLEXIBILITY', 'ENDURANCE']
        if v not in valid_types:
            raise ValueError(f"Metric type must be one of: {', '.join(valid_types)}")
        return v

    model_config = ConfigDict(from_attributes=True)

class FitnessGoalResponse(BaseModel):
    """Response model for fitness goals."""
    id: int
    student_id: int
    category: str
    description: str
    target_value: Optional[float]
    current_value: Optional[float]
    start_date: datetime
    target_date: datetime
    status: str
    timeframe: str
    priority: int
    notes: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FitnessGoalRequest(BaseModel):
    """Request model for creating fitness goals."""
    category: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)
    target_value: Optional[float] = Field(None, gt=0)
    timeframe: str = Field(..., min_length=1, max_length=20)
    priority: int = Field(1, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['CARDIOVASCULAR', 'STRENGTH', 'FLEXIBILITY', 'ENDURANCE']
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v

    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = ['SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM', 'ACADEMIC_YEAR']
        if v not in valid_timeframes:
            raise ValueError(f"Timeframe must be one of: {', '.join(valid_timeframes)}")
        return v

    model_config = ConfigDict(from_attributes=True)

class WorkoutPlanResponse(BaseModel):
    """Response model for workout plans."""
    id: int
    student_id: int
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    frequency: int
    goals: Dict[str, Any]
    progress_metrics: Dict[str, Any]
    schedule: Dict[str, Any]
    adaptations_needed: Optional[Dict[str, Any]]
    notes: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkoutPlanRequest(BaseModel):
    """Request model for creating workout plans."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    frequency: int = Field(..., ge=1, le=7)
    goals: Dict[str, Any] = Field(..., min_items=1)
    schedule: Dict[str, Any] = Field(..., min_items=1)
    adaptations_needed: Optional[Dict[str, Any]] = None
    notes: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

class NutritionPlanResponse(BaseModel):
    """Response model for nutrition plans."""
    id: int
    student_id: int
    category: str
    name: str
    description: str
    start_date: datetime
    end_date: Optional[datetime]
    dietary_restrictions: List[str]
    caloric_target: Optional[int]
    macronutrient_targets: Dict[str, float]
    hydration_target: Optional[float]
    special_instructions: Optional[str]
    medical_considerations: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NutritionPlanRequest(BaseModel):
    """Request model for creating nutrition plans."""
    category: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    dietary_restrictions: List[str] = Field(default_factory=list)
    caloric_target: Optional[int] = Field(None, gt=0)
    macronutrient_targets: Dict[str, float] = Field(default_factory=dict)
    hydration_target: Optional[float] = Field(None, gt=0)
    special_instructions: Optional[str] = Field(None, max_length=500)
    medical_considerations: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['GENERAL', 'PERFORMANCE', 'WEIGHT_MANAGEMENT', 'SPECIAL_NEEDS']
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v

    model_config = ConfigDict(from_attributes=True)

class NutritionLogRequest(BaseModel):
    """Request model for logging nutrition intake."""
    student_id: int = Field(..., description="Student ID")
    meal_type: str = Field(..., min_length=1, max_length=50, description="Type of meal")
    foods_consumed: List[Dict[str, Any]] = Field(..., description="List of foods consumed")
    calories: Optional[int] = Field(None, gt=0, description="Total calories")
    protein: Optional[float] = Field(None, gt=0, description="Protein in grams")
    carbohydrates: Optional[float] = Field(None, gt=0, description="Carbohydrates in grams")
    fats: Optional[float] = Field(None, gt=0, description="Fats in grams")
    hydration: Optional[float] = Field(None, gt=0, description="Hydration in liters")
    notes: Optional[str] = Field(None, max_length=500, description="Log notes")

    @validator('meal_type')
    def validate_meal_type(cls, v):
        valid_types = ['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK', 'PRE_WORKOUT', 'POST_WORKOUT']
        if v not in valid_types:
            raise ValueError(f"Meal type must be one of: {', '.join(valid_types)}")
        return v

    model_config = ConfigDict(from_attributes=True)

# Health Metrics Endpoints
@router.post(
    "/students/{student_id}/health-metrics",
    response_model=HealthMetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record health metric",
    description="Records a new health metric measurement for a student",
    response_description="The recorded health metric",
    responses={
        201: {"description": "Health metric recorded successfully"},
        400: {"description": "Invalid health metric data"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["health_metrics"]["requests"], period=RATE_LIMIT["health_metrics"]["period"])
async def record_health_metric(
    student_id: int,
    request: HealthMetricRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Record a new health metric measurement."""
    try:
        metric = await health_metrics_manager.record_metric(
            student_id=student_id,
            metric_type=request.metric_type,
            value=request.value,
            unit=request.unit,
            notes=request.notes,
            metadata=request.metadata
        )
        return metric
    except Exception as e:
        logger.error(f"Error recording health metric: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record health metric"
        )

@router.get(
    "/students/{student_id}/health-metrics",
    response_model=List[HealthMetricResponse],
    summary="Get health metrics",
    description="Retrieves health metrics for a student",
    response_description="List of health metrics",
    responses={
        200: {"description": "Successfully retrieved health metrics"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["health_metrics"]["requests"], period=RATE_LIMIT["health_metrics"]["period"])
async def get_health_metrics(
    student_id: int,
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get health metrics for a student."""
    try:
        metrics = await health_metrics_manager.get_metrics(
            student_id=student_id,
            metric_type=metric_type,
            start_date=start_date,
            end_date=end_date
        )
        return metrics
    except Exception as e:
        logger.error(f"Error retrieving health metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health metrics"
        )

@router.get(
    "/students/{student_id}/health-metrics/history",
    response_model=List[Dict[str, Any]],
    summary="Get health metric history",
    description="Retrieves historical health metric data for a student",
    response_description="List of historical health metric data",
    responses={
        200: {"description": "Successfully retrieved health metric history"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["health_metrics"]["requests"], period=RATE_LIMIT["health_metrics"]["period"])
async def get_health_metric_history(
    student_id: int,
    metric_type: str = Query(..., description="Metric type to get history for"),
    timeframe: str = Query("1M", description="Timeframe for history (1D, 1W, 1M, 3M, 6M, 1Y)"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get historical health metric data."""
    try:
        history = await health_metrics_manager.get_history(
            student_id=student_id,
            metric_type=metric_type,
            timeframe=timeframe
        )
        return history
    except Exception as e:
        logger.error(f"Error retrieving health metric history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health metric history"
        )

# Fitness Goals Endpoints
@router.post(
    "/students/{student_id}/fitness-goals",
    response_model=FitnessGoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create fitness goal",
    description="Creates a new fitness goal for a student",
    response_description="The created fitness goal",
    responses={
        201: {"description": "Fitness goal created successfully"},
        400: {"description": "Invalid fitness goal data"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["fitness_goals"]["requests"], period=RATE_LIMIT["fitness_goals"]["period"])
async def create_fitness_goal(
    student_id: int,
    request: FitnessGoalRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new fitness goal."""
    try:
        goal = await fitness_goal_manager.create_goal(
            student_id=student_id,
            category=request.category,
            description=request.description,
            target_value=request.target_value,
            timeframe=request.timeframe,
            priority=request.priority,
            notes=request.notes,
            metadata=request.metadata
        )
        return goal
    except Exception as e:
        logger.error(f"Error creating fitness goal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create fitness goal"
        )

@router.get(
    "/students/{student_id}/fitness-goals",
    response_model=List[FitnessGoalResponse],
    summary="Get fitness goals",
    description="Retrieves fitness goals for a student",
    response_description="List of fitness goals",
    responses={
        200: {"description": "Successfully retrieved fitness goals"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["fitness_goals"]["requests"], period=RATE_LIMIT["fitness_goals"]["period"])
async def get_fitness_goals(
    student_id: int,
    status: Optional[str] = Query(None, description="Filter by goal status"),
    category: Optional[str] = Query(None, description="Filter by goal category"),
    timeframe: Optional[str] = Query(None, description="Filter by goal timeframe"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get fitness goals for a student."""
    try:
        goals = await fitness_goal_manager.get_student_goals(
            student_id=student_id,
            status=status,
            category=category,
            timeframe=timeframe
        )
        return goals
    except Exception as e:
        logger.error(f"Error retrieving fitness goals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve fitness goals"
        )

@router.post(
    "/fitness-goals/{goal_id}/progress",
    response_model=Dict[str, Any],
    summary="Update goal progress",
    description="Records progress towards a fitness goal",
    response_description="The updated goal progress",
    responses={
        200: {"description": "Goal progress updated successfully"},
        400: {"description": "Invalid progress data"},
        401: {"description": "Unauthorized"},
        404: {"description": "Goal not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["fitness_goals"]["requests"], period=RATE_LIMIT["fitness_goals"]["period"])
async def update_goal_progress(
    goal_id: int,
    value: float = Query(..., description="Current progress value"),
    notes: Optional[str] = Query(None, description="Progress notes"),
    is_milestone: bool = Query(False, description="Whether this is a milestone achievement"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update progress towards a fitness goal."""
    try:
        progress = await fitness_goal_manager.update_progress(
            goal_id=goal_id,
            value=value,
            notes=notes,
            is_milestone=is_milestone
        )
        return progress
    except Exception as e:
        logger.error(f"Error updating goal progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update goal progress"
        )

@router.post(
    "/fitness-goals/{goal_id}/adjust",
    response_model=Dict[str, Any],
    summary="Adjust fitness goal",
    description="Adjusts a fitness goal's target or date",
    response_description="The adjusted goal",
    responses={
        200: {"description": "Goal adjusted successfully"},
        400: {"description": "Invalid adjustment data"},
        401: {"description": "Unauthorized"},
        404: {"description": "Goal not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["fitness_goals"]["requests"], period=RATE_LIMIT["fitness_goals"]["period"])
async def adjust_fitness_goal(
    goal_id: int,
    new_target: Optional[float] = Query(None, description="New target value"),
    new_date: Optional[datetime] = Query(None, description="New target date"),
    reason: str = Query(..., description="Reason for adjustment"),
    adjusted_by: str = Query("system", description="Who made the adjustment"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Adjust a fitness goal."""
    try:
        adjustment = await fitness_goal_manager.adjust_goal(
            goal_id=goal_id,
            new_target=new_target,
            new_date=new_date,
            reason=reason,
            adjusted_by=adjusted_by
        )
        return adjustment
    except Exception as e:
        logger.error(f"Error adjusting fitness goal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to adjust fitness goal"
        )

# Workout Plan Endpoints
@router.post(
    "/students/{student_id}/workout-plans",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create workout plan",
    description="Creates a new workout plan for a student",
    response_description="The created workout plan",
    responses={
        201: {"description": "Workout plan created successfully"},
        400: {"description": "Invalid workout plan data"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["workout_plans"]["requests"], period=RATE_LIMIT["workout_plans"]["period"])
async def create_workout_plan(
    student_id: int,
    request: WorkoutPlanRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new workout plan."""
    try:
        plan = await workout_planner.create_workout_plan(
            student_id=student_id,
            name=request.name,
            description=request.description,
            frequency=request.frequency,
            workouts=request.goals,
            schedule=request.schedule,
            adaptations_needed=request.adaptations_needed,
            notes=request.notes,
            metadata=request.metadata
        )
        return plan
    except Exception as e:
        logger.error(f"Error creating workout plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workout plan"
        )

@router.get(
    "/students/{student_id}/workout-plans",
    response_model=List[WorkoutPlanResponse],
    summary="Get workout plans",
    description="Retrieves workout plans for a student",
    response_description="List of workout plans",
    responses={
        200: {"description": "Successfully retrieved workout plans"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["workout_plans"]["requests"], period=RATE_LIMIT["workout_plans"]["period"])
async def get_workout_plans(
    student_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get workout plans for a student."""
    try:
        plans = await workout_planner.get_student_workouts(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date
        )
        return plans
    except Exception as e:
        logger.error(f"Error retrieving workout plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workout plans"
        )

@router.post(
    "/workout-plans/{plan_id}/sessions",
    response_model=WorkoutSessionResponse,
    summary="Record workout session",
    description="Records a workout session for a plan",
    response_description="The recorded workout session",
    responses={
        200: {"description": "Workout session recorded successfully"},
        400: {"description": "Invalid session data"},
        401: {"description": "Unauthorized"},
        404: {"description": "Plan not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["workout_plans"]["requests"], period=RATE_LIMIT["workout_plans"]["period"])
async def record_workout_session(
    plan_id: int,
    request: WorkoutSessionCreate,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Record a workout session."""
    try:
        session = await workout_planner.record_workout_session(
            db=next(get_db()),
            workout_id=plan_id,
            student_id=request.student_id,
            start_time=request.start_time,
            end_time=request.end_time,
            completed=request.completed,
            performance_data=request.performance_data,
            difficulty_rating=request.difficulty_rating,
            enjoyment_rating=request.enjoyment_rating,
            notes=request.notes,
            modifications_used=request.modifications_used
        )
        
        return session
        
    except SQLAlchemyError as e:
        logger.error(f"Error recording workout session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error recording workout session"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Nutrition Plan Endpoints
@router.post(
    "/students/{student_id}/nutrition-plans",
    response_model=NutritionPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create nutrition plan",
    description="Creates a new nutrition plan for a student",
    response_description="The created nutrition plan",
    responses={
        201: {"description": "Nutrition plan created successfully"},
        400: {"description": "Invalid nutrition plan data"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["nutrition_plans"]["requests"], period=RATE_LIMIT["nutrition_plans"]["period"])
async def create_nutrition_plan(
    student_id: int,
    request: NutritionPlanRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new nutrition plan."""
    try:
        plan = await nutrition_planner.create_nutrition_plan(
            student_id=student_id,
            category=request.category,
            name=request.name,
            description=request.description,
            dietary_restrictions=request.dietary_restrictions,
            caloric_target=request.caloric_target,
            macronutrient_targets=request.macronutrient_targets,
            hydration_target=request.hydration_target,
            special_instructions=request.special_instructions,
            medical_considerations=request.medical_considerations,
            metadata=request.metadata
        )
        return plan
    except Exception as e:
        logger.error(f"Error creating nutrition plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create nutrition plan"
        )

@router.get(
    "/students/{student_id}/nutrition-plans",
    response_model=List[NutritionPlanResponse],
    summary="Get nutrition plans",
    description="Retrieves nutrition plans for a student",
    response_description="List of nutrition plans",
    responses={
        200: {"description": "Successfully retrieved nutrition plans"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["nutrition_plans"]["requests"], period=RATE_LIMIT["nutrition_plans"]["period"])
async def get_nutrition_plans(
    student_id: int,
    category: Optional[str] = Query(None, description="Filter by plan category"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get nutrition plans for a student."""
    try:
        plans = await nutrition_planner.get_nutrition_history(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date
        )
        return plans
    except Exception as e:
        logger.error(f"Error retrieving nutrition plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve nutrition plans"
        )

@router.post(
    "/nutrition-plans/{plan_id}/logs",
    response_model=Dict[str, Any],
    summary="Log nutrition intake",
    description="Records nutrition intake for a plan",
    response_description="The recorded nutrition log",
    responses={
        200: {"description": "Nutrition log recorded successfully"},
        400: {"description": "Invalid log data"},
        401: {"description": "Unauthorized"},
        404: {"description": "Plan not found"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["nutrition_plans"]["requests"], period=RATE_LIMIT["nutrition_plans"]["period"])
async def log_nutrition(
    plan_id: int,
    request: NutritionLogRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Log nutrition intake."""
    try:
        log = await nutrition_planner.log_nutrition(
            student_id=request.student_id,
            meal_type=request.meal_type,
            foods_consumed=request.foods_consumed,
            calories=request.calories,
            protein=request.protein,
            carbohydrates=request.carbohydrates,
            fats=request.fats,
            hydration=request.hydration,
            notes=request.notes
        )
        return log
    except Exception as e:
        logger.error(f"Error logging nutrition: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log nutrition"
        )

@router.get(
    "/students/{student_id}/nutrition-recommendations",
    response_model=List[Dict[str, Any]],
    summary="Get nutrition recommendations",
    description="Retrieves nutrition recommendations for a student",
    response_description="List of nutrition recommendations",
    responses={
        200: {"description": "Successfully retrieved nutrition recommendations"},
        401: {"description": "Unauthorized"},
        404: {"description": "Student not found"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(requests=RATE_LIMIT["nutrition_plans"]["requests"], period=RATE_LIMIT["nutrition_plans"]["period"])
async def get_nutrition_recommendations(
    student_id: int,
    activity_level: str = Query("moderate", description="Student's activity level"),
    dietary_restrictions: Optional[List[str]] = Query(None, description="List of dietary restrictions"),
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get nutrition recommendations."""
    try:
        recommendations = await nutrition_planner.generate_recommendations(
            student_id=student_id,
            activity_level=activity_level,
            dietary_restrictions=dietary_restrictions
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error generating nutrition recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate nutrition recommendations"
        ) 