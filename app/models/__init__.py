"""

Models module for Faraday AI.

This package contains all database models and data structures used throughout
the application.
"""

# Base models
from .core import (
    BaseModel,
    User,
    UserMemory,
    MemoryInteraction,
    AssistantProfile,
    AssistantCapability,
    Lesson,
    SubjectCategory
)

# Type definitions
from .core.core_models import (
    MeasurementUnit, MetricType, GoalAdjustment
)

# Physical Education Types
from .physical_education.pe_enums.pe_types import (
    ActivityType,
    AssessmentType,
    DifficultyLevel,
    ProgressionLevel,
    PerformanceLevel,
    SkillLevel,
    FitnessCategory,
    EquipmentRequirement,
    StudentType,
    ClassType,
    RoutineType,
    IncidentType,
    IncidentSeverity,
    EquipmentStatus,
    ExerciseType,
    ExerciseDifficulty,
    GoalStatus,
    GoalCategory,
    GoalTimeframe,
    GoalType
)

# Physical Education Models - Core
from .physical_education.progress import (
    Progress,
    ProgressCreate,
    ProgressUpdate,
    ProgressResponse,
    ProgressGoal,
    ProgressGoalCreate,
    ProgressGoalUpdate,
    ProgressGoalResponse,
    PhysicalEducationProgressNote,
    ProgressNoteCreate,
    ProgressNoteUpdate,
    ProgressNoteResponse,
    ProgressGoalCreate,
    ProgressGoalUpdate,
    ProgressGoalResponse,
    ProgressNoteCreate,
    ProgressNoteUpdate,
    ProgressNoteResponse
)

# Use the health_fitness Progress model as ProgressTracking for backward compatibility
from .health_fitness.progress.progress_tracking import Progress as HealthFitnessProgress
ProgressTracking = HealthFitnessProgress

# Add missing property to ProgressTracking
@property
def is_on_track(self):
    """Check if progress is on track."""
    if hasattr(self, 'progress_metrics') and self.progress_metrics:
        # Simple logic: if any metric is above 70%, consider on track
        for metric, value in self.progress_metrics.items():
            if isinstance(value, (int, float)) and value > 70:
                return True
    return False

# Add the property to the ProgressTracking class
HealthFitnessProgress.is_on_track = is_on_track

from .physical_education.activity import Activity
from .physical_education.student.models import Student
from .physical_education.class_ import PhysicalEducationClass, ClassStudent

# Import only one version of Routine models to avoid conflicts
from .physical_education.routine.models import Routine, RoutineActivity, RoutinePerformance

# Goal models
from .health_fitness.goals.goal_setting import Goal, GoalMilestone, GoalActivity, HealthFitnessGoalProgress

# Progress milestone and report models (using Progress as base)
ProgressMilestone = ProgressGoal
ProgressReport = PhysicalEducationProgressNote

# Safety models
from .physical_education.safety.models import (
    SafetyIncident, RiskAssessment, SafetyAlert, SafetyProtocol, SafetyCheck
)

# Environmental and equipment models
from .physical_education.safety.models import EnvironmentalCheck, EquipmentCheck

# Enum imports
from .physical_education.pe_enums.pe_types import (
    IncidentType, IncidentSeverity, EquipmentStatus
)

# Additional missing models
from datetime import datetime

class MetadataModel:
    """Base model for metadata."""
    
    def add_tag(self, tag: str):
        """Add a tag to the model."""
        if not hasattr(self, 'tags'):
            self.tags = []
        self.tags.append(tag)
    
    def update_metadata(self, key: str, value: str):
        """Update metadata for the model."""
        if not hasattr(self, 'metadata'):
            self.metadata = {}
        if not hasattr(self, 'version'):
            self.version = 1
        if not hasattr(self, 'version_history'):
            self.version_history = []
        
        # Store previous version
        if key in self.metadata:
            self.version_history.append({
                'version': self.version,
                'key': key,
                'old_value': self.metadata[key],
                'new_value': value,
                'timestamp': datetime.utcnow().isoformat()
            })
            self.version += 1
        
        self.metadata[key] = value

class HealthMetric:
    """Health metric model."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class AuditableModel:
    """Base model for auditable entities."""
    
    def add_audit_entry(self, action: str, user: str, details: dict = None):
        """Add an audit entry."""
        if not hasattr(self, 'audit_trail'):
            self.audit_trail = []
        
        audit_entry = {
            'action': action,
            'user': user,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        self.audit_trail.append(audit_entry)

class ValidatableModel:
    """Base model for validatable entities."""
    
    def validate(self, validation_rules=None):
        """Validate the model."""
        self.validation_errors = []
        if validation_rules:
            for field_name, rule in validation_rules.items():
                if hasattr(self, field_name):
                    value = getattr(self, field_name)
                    if not rule['validator'](value):
                        self.validation_errors.append(rule['message'])
        return len(self.validation_errors) == 0
    
    def validate_not_empty(self, field_name: str, value):
        """Validate that a field is not empty."""
        if not value or (isinstance(value, str) and not value.strip()):
            self.validation_errors.append(f"{field_name} cannot be empty")
            return False
        return True
    
    def common_validation_rules(self):
        """Get common validation rules."""
        return {
            'name': {
                'validator': lambda x: self.validate_not_empty('name', x),
                'message': 'Name cannot be empty'
            },
            'heart_rate': {
                'validator': lambda x: isinstance(x, (int, float)) and 40 <= x <= 220,
                'message': 'Heart rate must be between 40 and 220'
            },
            'blood_pressure_systolic': {
                'validator': lambda x: isinstance(x, (int, float)) and 70 <= x <= 200,
                'message': 'Systolic blood pressure must be between 70 and 200'
            }
        }

class Class:
    """Class model."""
    pass

class Safety:
    """Safety model."""
    def __init__(self, **kwargs):
        self.incidents = []
        self.protocols = []
        self.checks = []
        for key, value in kwargs.items():
            setattr(self, key, value)

class EventParticipant:
    """Event participant model."""
    pass

# Enum classes with missing values
class RiskLevel:
    """Risk level enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType:
    """Alert type enum."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    EMERGENCY = "emergency"

class CheckType:
    """Check type enum."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    EQUIPMENT = "equipment"

# Missing models
class EnvironmentalCondition:
    """Environmental condition model."""
    def __init__(self, **kwargs):
        self.risk_level = None
        self.safety_concerns = []
        for key, value in kwargs.items():
            setattr(self, key, value)

class InjuryRiskFactor:
    """Injury risk factor model."""
    def __init__(self, **kwargs):
        self.prevention_measures = []
        for key, value in kwargs.items():
            setattr(self, key, value)

class PreventionMeasure:
    """Prevention measure model."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

from .physical_education.assessment import Assessment, SkillAssessment
from .physical_education.safety import SafetyIncident, RiskAssessment
from .physical_education.exercise import Exercise
from .physical_education.teacher.models import PhysicalEducationTeacher

# Physical Education Models - Supporting
from .physical_education.activity_adaptation.activity_adaptation import (
    ActivityAdaptation,
    AdaptationHistory
)

# Activity adaptation routine models (renamed to avoid conflicts)
from .activity_adaptation.routine import (
    AdaptedRoutine,
    AdaptedRoutineActivity,
    AdaptedRoutinePerformance
)
from .activity_adaptation.routine.routine_performance import (
    AdaptedRoutinePerformanceBackup,
    AdaptedPerformanceMetrics
)

# Physical Education Models - Additional
from .physical_education.workout import (
    Workout,
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutResponse,
    WorkoutSession,
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
    WorkoutSessionResponse,
    WorkoutPlan,
    WorkoutPlanCreate,
    WorkoutPlanUpdate,
    WorkoutPlanResponse,
    WorkoutPlanWorkout,
    WorkoutPlanWorkoutCreate,
    WorkoutPlanWorkoutUpdate,
    WorkoutPlanWorkoutResponse
)

# Additional Models
# from .physical_education.health.models import (
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
from .physical_education.equipment.models import (
    Equipment,
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentUsage,
    EquipmentMaintenance,
    MaintenanceRecord,
    EquipmentCategory,
    EquipmentCategoryCreate,
    EquipmentCategoryUpdate,
    EquipmentCategoryResponse,
    EquipmentCondition,
    EquipmentConditionCreate,
    EquipmentConditionUpdate,
    EquipmentConditionResponse,
    EquipmentStatus,
    EquipmentStatusCreate,
    EquipmentStatusUpdate,
    EquipmentStatusResponse,
    EquipmentType,
    EquipmentTypeCreate,
    EquipmentTypeUpdate,
    EquipmentTypeResponse
)
from .physical_education.movement_analysis.models import (
    MovementAnalysis,
    MovementAnalysisCreate,
    MovementAnalysisUpdate,
    MovementAnalysisResponse,
    MovementPattern,
    MovementPatternCreate,
    MovementPatternUpdate,
    MovementPatternResponse,
    MovementFeedback,
    MovementFeedbackCreate,
    MovementFeedbackUpdate,
    MovementFeedbackResponse
)

# Health and Fitness Models
from .health_fitness.nutrition.nutrition import (
    NutritionPlan,
    NutritionGoal,
    MealPlan,
    NutritionRecommendation,
    NutritionEducation
)
from .physical_education.nutrition.models import PhysicalEducationNutritionLog
from .health_fitness.goals.goal_setting import (
    Goal,
    HealthFitnessGoalProgress,
    GoalMilestone,
    GoalActivity
)
from .health_fitness.goals.fitness_goals import (
    FitnessGoal,
    FitnessGoalProgressGeneral,
    GoalAdjustment,
    GoalRecommendation,
    FitnessGoalProgress
)
from .physical_education.student.student import (
    StudentHealthGoalProgress
)
from .physical_education.student.health import (
    StudentHealthGoalProgress as StudentHealthGoalProgressHealth
)

# Backward compatibility aliases for existing code
# These maintain compatibility with code that might be using the old names
StudentHealthFitnessGoal = FitnessGoal  # Alias for backward compatibility
GoalProgress = HealthFitnessGoalProgress  # Alias for backward compatibility
StudentHealthGoalRecommendation = GoalRecommendation  # Alias for backward compatibility

# Environmental and Safety
from .physical_education.environmental import EnvironmentalCondition, ActivityEnvironmentalImpact, EnvironmentalAlert
from .physical_education.injury_prevention import InjuryRiskFactor, PreventionMeasure, PreventionAssessment

# Curriculum Management
from .physical_education.curriculum import Curriculum, CurriculumUnit, CurriculumStandard

# Competition and Events
from .competition.base.competition import Competition, CompetitionEvent, CompetitionParticipant

# Rate Limiting
from .security.rate_limit import RateLimit, RateLimitPolicy, RateLimitMetrics

# Security Models
from .security import SecurityAudit, SecurityIncidentManagement
from .security.api_key import APIKey
from .security.incident.security import SecurityIncidentManagement as SecurityIncidentModel
# from .security.audit.security import SecurityAudit
from .security.rate_limit.rate_limit import RateLimit
from .security.policy.security import IPAllowlist, IPBlocklist, Session
from .security.access_control.access_control_management import (
    AccessControlRole,
    AccessControlPermission,
    UserRole,
    RolePermission,
    RoleHierarchy,
    RoleTemplate
)
from .audit_log import AuditLog

# Organization Models
from .organization import (
    Organization,
    OrganizationMember,
    OrganizationRole,
    OrganizationSettings,
    Department,
    DepartmentMember,
    OrganizationResource,
    OrganizationCollaboration,
    OrganizationProject,
    ProjectMember,
    ProjectRole,
    ProjectSettings,
    ProjectResource,
    ProjectComment,
    ProjectFeedback,
    FeedbackCategory,
    FeedbackResponse,
    FeedbackAction
)

# User Management Models
from .user_management.user.user_management import (
    Role,
    Permission,
    UserProfile,
    UserOrganization,
    UserSession
)

# User Management Preferences Models
from .user_management.preferences.user_preferences_management import (
    UserPreference,
    UserPreferenceCategory,
    UserPreferenceTemplate
)

# Dashboard models
from app.models.dashboard import CoreDashboardWidget, DashboardTheme, DashboardShareConfig, DashboardFilterConfig, DashboardExport, DashboardSearch
from app.dashboard.models.tool_registry import Tool, UserTool, user_tools
from app.dashboard.models.user import DashboardUser
from app.dashboard.models.project import DashboardProject
from app.dashboard.models.association_tables import gpt_sharing
from app.dashboard.models.ai_tool import tool_assignments
from app.models.health_fitness.workouts.injury_prevention import injury_risk_factor_safety_guidelines
from app.dashboard.models.gpt_models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTUsage,
    GPTIntegration,
    GPTAnalytics,
    GPTFeedback,
    GPTPerformance,
    GPTUsageHistory
)
# Removed dashboard context imports to avoid conflicts with core context models
from app.models.feedback.tools.user_tool import FeedbackUserTool

# Skill Assessment models
from .skill_assessment.assessment.assessment import (
    Assessment as SkillAssessmentModel,
    SkillAssessment,
    AssessmentCriteria,
    AssessmentResult,
    AssessmentHistory,
    SkillProgress,
    AssessmentMetrics
)

# Import missing models that are referenced in seed scripts
from .skill_assessment.assessment.assessment import (
    SkillAssessment,
    AssessmentResult,
    AssessmentHistory,
    AssessmentCriteria
)
from .skill_assessment.safety.safety import (
    SafetyReport,
    SkillAssessmentSafetyIncident,
    RiskAssessment as SkillAssessmentRiskAssessment,
    SafetyAlert as SkillAssessmentSafetyAlert,
    SafetyProtocol as SkillAssessmentSafetyProtocol,
    SafetyCheck as SkillAssessmentSafetyCheck
)
from .physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)
from .security.api_key.api_key import APIKey
from .health_fitness.nutrition.nutrition import NutritionPlan
from .physical_education.safety.models import SafetyIncident
from .activity_adaptation.routine.routine_performance import AdaptedPerformanceMetrics

# Setup relationships after all models are imported
# Removed automatic relationship setup to avoid circular imports

from .physical_education.goal_setting import (
    PhysicalEducationGoal
)

from .physical_education.safety import SafetyIncident, RiskAssessment
from .physical_education.safety.models import (
    SafetyIncidentBase,
    SafetyCheck,
    EnvironmentalCheck,
    SafetyProtocol,
    SafetyAlert
)

# Resource Management Models
from .resource_management.resource_management import (
    ResourceUsage,
    ResourceThreshold,
    ResourceOptimization,
    OptimizationEvent,
    ResourceSharing
)
from .resource_management.optimization.models import (
    ResourceEvent,
    ResourceAlert,
    ResourceOptimizationThreshold as OptimizationResourceThreshold,
    ResourceOptimizationRecommendation as OptimizationResourceOptimization,
    ResourceOptimizationEvent as OptimizationOptimizationEvent
)

# Context Models
from .gpt.context.models import (
    GPTContext,
    ContextInteraction,
    SharedContext,
    ContextSummary,
    ContextBackup,
    ContextData,
    ContextMetrics,
    ContextSharing,
    gpt_context_gpts
)
# from .context.base.context import context_gpts  # Removed to avoid conflicts with GPT context models

# Educational Models
from .educational import (
    Grade,
    Assignment,
    Rubric,
    Message,
    MessageBoard,
    MessageBoardPost,
    Curriculum,
    LessonPlan,
    Subject,
    Course,
    SubjectCategory,
    EducationalClass,
    EducationalClassStudent,
    Teacher,
    Instructor
)

# Analytics Models
from .analytics import (
    UserActivity,
    UserBehavior,
    UserPerformance,
    UserEngagement,
    UserPrediction,
    UserRecommendation,
    AnalyticsEvent,
    UserInsight,
    UserTrend,
    UserComparison
)

# Assessment Models
from .assessment import (
    GeneralAssessment,
    AssessmentCriteria,
    AssessmentChange,
    AssessmentHistory,
    SkillAssessment,
    SkillProgress
)

# Movement Analysis Models
from .movement_analysis import (
    MovementAnalysis,
    MovementPattern
)

# Import missing association tables and models that are failing to create
from .user_management.preferences.user_preferences_management import user_preference_template_assignments
from app.dashboard.models.association_tables import dashboard_context_gpts
from app.dashboard.models.category import gpt_categories
from .security.rate_limit.rate_limit import RateLimit, RateLimitPolicy, RateLimitMetrics, RateLimitLog
from .circuit_breaker import CircuitBreakerMetrics

__all__ = [
    'BaseModel',
    'User',
    'UserMemory',
    'MemoryInteraction',
    'AssistantProfile',
    'AssistantCapability',
    'Lesson',
    'SubjectCategory',
    
    # Base model classes
    'ValidatableModel',
    'AuditableModel', 
    'MetadataModel',
    
    # Type definitions
    'ActivityType', 'StudentType', 'Subject', 'GradeLevel', 'Gender',
    'FitnessLevel', 'MeasurementUnit', 'GoalStatus', 'GoalCategory', 'GoalTimeframe',
    'MetricType', 'GoalType', 'GoalAdjustment', 'ClassType', 'RoutineStatus', 'RoutineType',
    'AssessmentType', 'AssessmentStatus', 'AssessmentLevel', 'AssessmentTrigger',
    'CriteriaType', 'ChangeType', 'SafetyType', 'IncidentType', 'IncidentSeverity',
    'AlertType', 'CheckType', 'ExerciseType', 'ExerciseDifficulty', 'WorkoutType',
    'EquipmentType', 'MovementType', 'DifficultyLevel', 'ProgressionLevel',
    'EquipmentRequirement', 'AnalysisType', 'AnalysisStatus', 'ConfidenceLevel',
    'PerformanceLevel', 'VisualizationType', 'ChartType', 'ColorScheme',
    'InteractionMode', 'ExportFormat', 'FileType', 'CompressionType', 'DataFormat',
    'CollaborationType', 'AccessLevel', 'SharingStatus', 'NotificationType',
    'AdaptationType', 'AdaptationLevel', 'AdaptationStatus', 'AdaptationTrigger',
    'SecurityLevel', 'SecurityStatus', 'SecurityAction', 'SecurityTrigger',
    'RateLimitType', 'RateLimitLevel', 'RateLimitStatus', 'RateLimitTrigger',
    'CacheType', 'CacheLevel', 'CacheStatus', 'CacheTrigger',
    'CircuitBreakerType', 'CircuitBreakerLevel', 'CircuitBreakerStatus', 'CircuitBreakerTrigger',
    'RiskLevel', 'SkillLevel',
    
    # Physical Education Models
    'Activity', 'ActivityCreate', 'ActivityUpdate', 'ActivityResponse',
    'StudentActivityPerformance', 'StudentActivityPreference', 'ActivityProgression',
    'Student', 'StudentCreate', 'StudentUpdate', 'StudentResponse',
    'StudentAttendance', 'StudentAttendanceCreate', 'StudentAttendanceUpdate', 'StudentAttendanceResponse',
    'Class', 'ClassStudent',
    'Routine', 'RoutinePerformance', 'RoutineActivity',
    'AdaptedRoutinePerformanceBackup',
    'Assessment', 'SkillAssessment',
    'SafetyIncident', 'RiskAssessment',
    'Exercise',
    'PhysicalEducationTeacher',
    'MovementAnalysis', 'MovementAnalysisCreate', 'MovementAnalysisUpdate', 'MovementAnalysisResponse',
    'MovementPattern', 'MovementPatternCreate', 'MovementPatternUpdate', 'MovementPatternResponse',
    'MovementFeedback', 'MovementFeedbackCreate', 'MovementFeedbackUpdate', 'MovementFeedbackResponse',
    'Progress', 'ProgressCreate', 'ProgressUpdate', 'ProgressResponse',
    'ProgressGoal', 'ProgressGoalCreate', 'ProgressGoalUpdate', 'ProgressGoalResponse',
    'PhysicalEducationProgressNote', 'ProgressNoteCreate', 'ProgressNoteUpdate', 'ProgressNoteResponse',
    'PhysicalEducationGoal',
    'Equipment', 'EquipmentCreate', 'EquipmentUpdate', 'EquipmentResponse',
    'EquipmentUsage', 'EquipmentMaintenance', 'MaintenanceRecord',
    'EquipmentCategory', 'EquipmentCategoryCreate', 'EquipmentCategoryUpdate', 'EquipmentCategoryResponse',
    'EquipmentCondition', 'EquipmentConditionCreate', 'EquipmentConditionUpdate', 'EquipmentConditionResponse',
    'EquipmentStatus', 'EquipmentStatusCreate', 'EquipmentStatusUpdate', 'EquipmentStatusResponse',
    'EquipmentType', 'EquipmentTypeCreate', 'EquipmentTypeUpdate', 'EquipmentTypeResponse',
    
    # Health and Fitness Models
    'NutritionPlan', 'NutritionGoal', 'MealPlan', 'PhysicalEducationNutritionLog', 'NutritionRecommendation', 'NutritionEducation',
    'Goal', 'HealthFitnessGoalProgress', 'GoalMilestone', 'GoalActivity',
    'FitnessGoal', 'GeneralGoalProgress', 'GoalAdjustment', 'GoalRecommendation', 'FitnessGoalProgress',
    'StudentHealthGoalProgress', 'StudentHealthGoalProgressHealth',
    
    # Backward compatibility aliases
    'StudentHealthFitnessGoal', 'GoalProgress', 'StudentHealthGoalRecommendation',
    
    # Security Models
    'APIKey',
    'RateLimit', 'RateLimitPolicy', 'RateLimitMetrics',
    'SecurityIncidentModel',
    'IPAllowlist', 'IPBlocklist', 'Session',
    'AccessControlRole', 'AccessControlPermission', 'UserRole', 'RolePermission', 'RoleHierarchy', 'RoleTemplate',

    # Organization Models
    'Organization', 'OrganizationMember', 'OrganizationRole', 'OrganizationSettings',
    'Department', 'DepartmentMember', 'OrganizationResource', 'OrganizationCollaboration',
    'OrganizationProject', 'ProjectMember', 'ProjectRole', 'ProjectSettings',
    'ProjectResource', 'ProjectFeedback', 'FeedbackCategory', 'FeedbackResponse', 'FeedbackAction',

    # User Management Models
    'Role', 'Permission', 'UserProfile', 'UserOrganization', 'UserSession',
    'UserPreference', 'UserPreferenceCategory', 'UserPreferenceTemplate',

    # Dashboard models
    'UserPreferences',
    'DashboardUser',
    'DashboardProject',
    'Tool', 'UserTool', 'user_tools',
    'gpt_sharing', 'context_gpts', 'tool_assignments', 'injury_risk_factor_safety_guidelines',
    'FeedbackUserTool',
    'GPTDefinition', 'DashboardGPTSubscription', 'GPTUsage', 'GPTIntegration', 
    'GPTAnalytics', 'GPTFeedback', 'GPTPerformance', 'GPTUsageHistory',

    # Skill Assessment models
    'SkillAssessmentModel', 'SkillAssessment', 'AssessmentCriteria', 'AssessmentResult', 'AssessmentHistory', 'SkillProgress', 'AssessmentMetrics',
    'SafetyReport', 'SkillAssessmentSafetyIncident', 'SkillAssessmentRiskAssessment', 'SkillAssessmentSafetyAlert', 'SkillAssessmentSafetyProtocol', 'SkillAssessmentSafetyCheck',

    # Physical Education Safety Models
    'SafetyIncidentBase', 'SafetyCheck', 'EnvironmentalCheck', 'SafetyProtocol', 'SafetyAlert',

    # Resource Management Models
    'ResourceUsage', 'ResourceThreshold', 'ResourceOptimization', 'OptimizationEvent', 'ResourceSharing',
    'ResourceEvent', 'ResourceAlert', 'OptimizationResourceThreshold', 'OptimizationResourceOptimization', 'OptimizationOptimizationEvent',

    # Context Models
    'GPTContext', 'ContextInteraction', 'SharedContext', 'ContextSummary', 'ContextBackup', 'ContextData', 'ContextMetrics', 'ContextSharing', 'gpt_context_gpts',

    # Educational Models
    'Grade', 'Assignment', 'Rubric', 'Message', 'MessageBoard', 'MessageBoardPost', 'Curriculum', 'LessonPlan', 'Subject', 'Course', 'SubjectCategory', 'EducationalClass', 'EducationalClassStudent', 'Teacher', 'Instructor',

    # Analytics Models
    'UserActivity', 'UserBehavior', 'UserPerformance', 'UserEngagement', 'UserPrediction', 'UserRecommendation', 'AnalyticsEvent', 'UserInsight', 'UserTrend', 'UserComparison',

    # Assessment Models
    'GeneralAssessment', 'AssessmentCriteria', 'AssessmentChange', 'AssessmentHistory', 'SkillAssessment', 'SkillProgress',
    
    # Movement Analysis Models
    'MovementAnalysis', 'MovementPattern',

    # Missing models and association tables
    'user_preference_template_assignments', 'dashboard_context_gpts', 'gpt_categories',
    'RateLimit', 'RateLimitPolicy', 'RateLimitMetrics', 'RateLimitLog', 'CircuitBreakerMetrics',
    
    # Additional missing models
    'MetadataModel', 'HealthMetric', 'AuditableModel', 'ProgressTracking', 'ValidatableModel', 'ProgressMilestone', 'ProgressReport', 'Safety', 'EventParticipant', 'EquipmentCheck', 'RiskLevel', 'AlertType', 'CheckType',
] 