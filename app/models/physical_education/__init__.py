"""
Physical Education Models Package

This package contains all models related to physical education functionality.
"""

from app.models.physical_education.base.base import (
    BaseResponseModel,
    BaseCreateModel,
    BaseUpdateModel,
    validate_string_field
)

from app.models.mixins import TimestampedMixin
from app.models.base import BaseModel

# Re-export for backward compatibility
TimestampMixin = TimestampedMixin
BaseModelMixin = BaseModel

from app.models.physical_education.student import (
    Student,
    HealthMetricThreshold,
    StudentHealthFitnessGoal,
    StudentHealthGoalProgress,
    StudentHealthGoalRecommendation
)

from .activity import (
    Activity,
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    StudentActivityPerformance,
    StudentActivityPreference,
    ActivityProgression
)

from .activity_adaptation.activity_adaptation import (
    ActivityAdaptation,
    AdaptationHistory
)

from .pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    ProgressionLevel,
    EquipmentRequirement,
    ActivityCategoryType,
    RoutineType,
    RoutineStatus,
    RateLimitType,
    RateLimitLevel,
    RateLimitStatus,
    RateLimitTrigger,
    RiskLevel,
    IncidentSeverity,
    IncidentType,
    AlertType,
    CheckType
)

from app.models.physical_education.class_ import (
    PhysicalEducationClass,
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassStudent,
    ClassRoutine
)

from app.models.physical_education.routine import (
    Routine,
    RoutineBase,
    RoutineCreate,
    RoutineUpdate,
    RoutineResponse,
    RoutineActivity,
    RoutinePerformanceMetrics
)

from app.models.physical_education.assessment import (
    Assessment,
    SkillAssessment,
    FitnessAssessment,
    MovementAssessment
)

from app.models.physical_education.safety import (
    SafetyIncident,
    SafetyIncidentBase,
    SafetyIncidentCreate,
    SafetyIncidentUpdate,
    SafetyIncidentResponse,
    Equipment,
    EquipmentBase,
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentMaintenance
)

from app.models.physical_education.exercise import (
    Exercise,
    ExerciseBaseModel,
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseResponse,
    ExerciseWorkout,
    ExerciseWorkoutExercise
)

from app.models.physical_education.progress import (
    Progress,
    ProgressBase,
    ProgressCreate,
    ProgressUpdate,
    ProgressResponse,
    ProgressGoal,
    ProgressGoalBase,
    ProgressGoalCreate,
    ProgressGoalUpdate,
    ProgressGoalResponse,
    PhysicalEducationProgressNote,
    ProgressNoteBase,
    ProgressNoteCreate,
    ProgressNoteUpdate,
    ProgressNoteResponse,
    ProgressMilestone,
    ProgressAssessment
)

from app.models.physical_education.goal_setting import (
    PhysicalEducationGoal
)

from app.models.physical_education.nutrition import (
    NutritionPlan,
    NutritionPlanCreate,
    NutritionPlanUpdate,
    NutritionPlanResponse,
    Meal,
    MealCreate,
    MealUpdate,
    MealResponse,
    MealFood,
    MealFoodCreate,
    MealFoodUpdate,
    MealFoodResponse,
    Food,
    FoodCreate,
    FoodUpdate,
    FoodResponse,
    NutritionGoal,
    PhysicalEducationNutritionLog,
    PhysicalEducationNutritionLogCreate,
    PhysicalEducationNutritionLogUpdate,
    PhysicalEducationNutritionLogResponse,
    PhysicalEducationNutritionRecommendation,
    PhysicalEducationNutritionRecommendationCreate,
    PhysicalEducationNutritionRecommendationUpdate,
    PhysicalEducationNutritionRecommendationResponse,
    NutritionEducation,
    NutritionEducationCreate,
    NutritionEducationUpdate,
    NutritionEducationResponse,
)

# from app.models.physical_education.health.models import (
#     HealthMetric,
#     HealthMetricCreate,
#     HealthMetricUpdate,
#     HealthMetricResponse,
#     HealthCondition,
#     HealthConditionCreate,
#     HealthConditionUpdate,
#     HealthConditionResponse,
#     HealthAlert,
#     HealthAlertCreate,
#     HealthAlertUpdate,
#     HealthAlertResponse,
#     HealthCheck,
#     HealthCheckCreate,
#     HealthCheckUpdate,
#     HealthCheckResponse,
#     HealthMetricHistory,
#     HealthMetricHistoryCreate,
#     HealthMetricHistoryUpdate,
#     HealthMetricHistoryResponse
# )

__all__ = [
    # Base models and utilities
    'TimestampMixin',
    'BaseModelMixin',
    'BaseResponseModel',
    'BaseCreateModel',
    'BaseUpdateModel',
    'validate_string_field',
    
    # Student models
    'Student',
    'HealthMetricThreshold',
    'StudentHealthFitnessGoal',
    'StudentHealthGoalProgress',
    'StudentHealthGoalRecommendation',
    
    # Activity Models
    'Activity', 'ActivityCreate', 'ActivityUpdate', 'ActivityResponse',
    'StudentActivityPerformance', 'StudentActivityPreference', 'ActivityProgression',
    
    # Adaptation Models
    'ActivityAdaptation', 'AdaptationHistory',
    
    # Class models
    'PhysicalEducationClass',
    'ClassCreate',
    'ClassUpdate',
    'ClassResponse',
    'ClassStudent',
    'ClassRoutine',
    
    # Routine models
    'Routine',
    'RoutineBase',
    'RoutineCreate',
    'RoutineUpdate',
    'RoutineResponse',
    'RoutineActivity',
    'RoutinePerformanceMetrics',
    
    # Assessment models
    'Assessment',
    'SkillAssessment',
    'FitnessAssessment',
    'MovementAssessment',
    
    # Safety models
    'SafetyIncident',
    'SafetyIncidentBase',
    'SafetyIncidentCreate',
    'SafetyIncidentUpdate',
    'SafetyIncidentResponse',
    'Equipment',
    'EquipmentBase',
    'EquipmentCreate',
    'EquipmentUpdate',
    'EquipmentResponse',
    'EquipmentMaintenance',
    
    # Exercise models
    'Exercise',
    'ExerciseBaseModel',
    'ExerciseCreate',
    'ExerciseUpdate',
    'ExerciseResponse',
    'ExerciseWorkout',
    'ExerciseWorkoutExercise',
    
    # Types
    'ActivityType', 'DifficultyLevel', 'ProgressionLevel', 'EquipmentRequirement',
    'ActivityCategoryType', 'RoutineType', 'RoutineStatus', 'RateLimitType',
    'RateLimitLevel', 'RateLimitStatus', 'RateLimitTrigger', 'RiskLevel',
    'IncidentSeverity', 'IncidentType', 'AlertType', 'CheckType',
    
    # Progress models
    'Progress',
    'ProgressBase',
    'ProgressCreate',
    'ProgressUpdate',
    'ProgressResponse',
    'ProgressGoal',
    'ProgressGoalBase',
    'ProgressGoalCreate',
    'ProgressGoalUpdate',
    'ProgressGoalResponse',
    'PhysicalEducationProgressNote',
    'ProgressNoteBase',
    'ProgressNoteCreate',
    'ProgressNoteUpdate',
    'ProgressNoteResponse',
    'ProgressMilestone',
    'ProgressAssessment',
    'EventParticipant',
    'PhysicalEducationGoal',
    
    # Nutrition models
    'NutritionPlan',
    'NutritionPlanCreate',
    'NutritionPlanUpdate',
    'NutritionPlanResponse',
    'Meal',
    'MealCreate',
    'MealUpdate',
    'MealResponse',
    'MealFood',
    'MealFoodCreate',
    'MealFoodUpdate',
    'MealFoodResponse',
    'Food',
    'FoodCreate',
    'FoodUpdate',
    'FoodResponse',
    'NutritionGoal',
    'PhysicalEducationNutritionLog',
    'PhysicalEducationNutritionLogCreate',
    'PhysicalEducationNutritionLogUpdate',
    'PhysicalEducationNutritionLogResponse',
    'PhysicalEducationNutritionRecommendation',
    'PhysicalEducationNutritionRecommendationCreate',
    'PhysicalEducationNutritionRecommendationUpdate',
    'PhysicalEducationNutritionRecommendationResponse',
    'NutritionEducation',
    'NutritionEducationCreate',
    'NutritionEducationUpdate',
    'NutritionEducationResponse',
] 