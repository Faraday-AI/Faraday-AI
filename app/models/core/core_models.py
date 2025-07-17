"""
Core Models

This module contains core model definitions used across the Faraday AI application.
"""

import enum
from typing import Optional
from datetime import datetime
from app.core.enums import Region  # Import Region from core enums

class MeasurementUnit(str, enum.Enum):
    """Units of measurement."""
    METERS = "meters"
    KILOMETERS = "kilometers"
    CENTIMETERS = "centimeters"
    MILLIMETERS = "millimeters"
    INCHES = "inches"
    FEET = "feet"
    YARDS = "yards"
    MILES = "miles"
    KILOGRAMS = "kilograms"
    GRAMS = "grams"
    POUNDS = "pounds"
    OUNCES = "ounces"
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    COUNT = "count"
    SCORE = "score"
    RATING = "rating"
    LEVEL = "level"
    DEGREE = "degree"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    VOLUME = "volume"
    AREA = "area"
    SPEED = "speed"
    ACCELERATION = "acceleration"
    FORCE = "force"
    ENERGY = "energy"
    POWER = "power"
    FREQUENCY = "frequency"
    CUSTOM = "custom"

class MetricType(str, enum.Enum):
    """Types of metrics."""
    DISTANCE = "distance"
    TIME = "time"
    WEIGHT = "weight"
    HEIGHT = "height"
    SPEED = "speed"
    PACE = "pace"
    HEART_RATE = "heart_rate"
    CALORIES = "calories"
    STEPS = "steps"
    REPETITIONS = "repetitions"
    SETS = "sets"
    WEIGHT_LIFTED = "weight_lifted"
    DURATION = "duration"
    INTENSITY = "intensity"
    EFFORT = "effort"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    ACHIEVEMENT = "achievement"
    SKILL = "skill"
    ABILITY = "ability"
    CUSTOM = "custom"

class GoalAdjustment:
    """Type for tracking goal adjustments."""
    def __init__(
        self,
        goal_id: int,
        previous_target: Optional[float],
        new_target: Optional[float],
        previous_date: datetime,
        new_date: Optional[datetime],
        reason: str,
        adjusted_by: str
    ):
        self.goal_id = goal_id
        self.previous_target = previous_target
        self.new_target = new_target
        self.previous_date = previous_date
        self.new_date = new_date
        self.reason = reason
        self.adjusted_by = adjusted_by
        self.adjusted_at = datetime.utcnow()

# Core enums
class DeploymentStatus(str, enum.Enum):
    """Deployment status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    VERIFYING = "verifying"
    STAGING = "staging"
    PROMOTING = "promoting"
    COMPLETED = "completed"

class ServiceStatus(str, enum.Enum):
    """Service status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"
    MAINTENANCE = "maintenance"
    DEPLOYING = "deploying"
    ROLLING_BACK = "rolling_back"
    SCALING = "scaling"
    UPDATING = "updating"
    FAILED = "failed"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"

class FeatureFlagType(str, enum.Enum):
    """Feature flag types."""
    BOOLEAN = "boolean"
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    FLOAT = "float"
    JSON = "json"
    PERCENTAGE = "percentage"
    CUSTOM = "custom"
    MULTI_VARIANT = "multi_variant"
    EXPERIMENT = "experiment"
    ROLLOUT = "rollout"

class FeatureFlagStatus(str, enum.Enum):
    """Feature flag status."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"
    EXPERIMENTAL = "experimental"
    ROLLING_OUT = "rolling_out"
    ROLLED_BACK = "rolled_back"
    EVALUATING = "evaluating"
    EXPIRED = "expired"

class ABTestType(str, enum.Enum):
    """A/B test types."""
    FEATURE = "feature"
    UI = "ui"
    ALGORITHM = "algorithm"
    CONTENT = "content"
    PRICING = "pricing"
    MESSAGING = "messaging"
    PERFORMANCE = "performance"
    USER_EXPERIENCE = "user_experience"
    CONVERSION = "conversion"
    RETENTION = "retention"

class ABTestStatus(str, enum.Enum):
    """A/B test status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"
    ANALYZING = "analyzing"
    DECIDED = "decided"
    ROLLED_OUT = "rolled_out"

class AnalyticsEventType(str, enum.Enum):
    """Analytics event types."""
    PAGE_VIEW = "page_view"
    CLICK = "click"
    FORM_SUBMIT = "form_submit"
    API_CALL = "api_call"
    ERROR = "error"
    PERFORMANCE = "performance"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    BUSINESS_EVENT = "business_event"
    SECURITY_EVENT = "security_event"
    DEPLOYMENT_EVENT = "deployment_event"
    FEATURE_FLAG_EVENT = "feature_flag_event"
    AB_TEST_EVENT = "ab_test_event"
    ALERT_EVENT = "alert_event"
    CIRCUIT_BREAKER_EVENT = "circuit_breaker_event"
    CUSTOM = "custom"

class MetricsType(str, enum.Enum):
    """Metrics types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    RATE = "rate"
    DURATION = "duration"
    PERCENTILE = "percentile"
    DISTRIBUTION = "distribution"

class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    TRACE = "trace"
    EMERGENCY = "emergency"
    NOTICE = "notice"

class AlertStatus(str, enum.Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"
    SUPPRESSED = "suppressed"
    IGNORED = "ignored"
    ESCALATED = "escalated"
    INVESTIGATING = "investigating"

class CircuitBreakerState(str, enum.Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"
    FORCED_OPEN = "forced_open"
    FORCED_CLOSED = "forced_closed"
    DISABLED = "disabled"
    DEGRADED = "degraded"
    TESTING = "testing"
    MAINTENANCE = "maintenance"

class AdaptationType(str, enum.Enum):
    """Adaptation types."""
    DIFFICULTY = "difficulty"
    EQUIPMENT = "equipment"
    DURATION = "duration"
    INTENSITY = "intensity"
    GROUP_SIZE = "group_size"
    ENVIRONMENT = "environment"
    INSTRUCTION = "instruction"
    ASSISTANCE = "assistance"
    MODIFICATION = "modification"
    ALTERNATIVE = "alternative"
    COMPLEXITY = "complexity"
    SUPPORT = "support"

class AdaptationLevel(str, enum.Enum):
    """Adaptation levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    EXTENSIVE = "extensive"
    CUSTOM = "custom"
    NONE = "none"
    MINIMAL = "minimal"
    SIGNIFICANT = "significant"
    EXTREME = "extreme"

class AdaptationStatus(str, enum.Enum):
    """Adaptation status."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    ARCHIVED = "archived"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    REVERTED = "reverted"

class AdaptationTrigger(str, enum.Enum):
    """Adaptation triggers."""
    STUDENT_REQUEST = "student_request"
    TEACHER_INITIATED = "teacher_initiated"
    PERFORMANCE_BASED = "performance_based"
    SAFETY_CONCERN = "safety_concern"
    EQUIPMENT_LIMITATION = "equipment_limitation"
    ENVIRONMENTAL = "environmental"
    MEDICAL = "medical"
    SCHEDULED = "scheduled"
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    EVENT = "event"

class ExportFormat(str, enum.Enum):
    """Export format types."""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    XML = "xml"
    YAML = "yaml"
    TEXT = "text"
    BINARY = "binary"
    CUSTOM = "custom"

class FileType(str, enum.Enum):
    """File types."""
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"
    XML = "xml"
    YAML = "yaml"
    TXT = "txt"
    BIN = "bin"
    ZIP = "zip"
    CUSTOM = "custom"

class AssessmentType(str, enum.Enum):
    """Assessment types."""
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    PERIODIC = "periodic"
    FINAL = "final"
    EMERGENCY = "emergency"
    ROUTINE = "routine"
    SPECIALIZED = "specialized"
    COMPREHENSIVE = "comprehensive"
    QUICK = "quick"
    DETAILED = "detailed"
    CUSTOM = "custom"

class EquipmentStatus(str, enum.Enum):
    """Equipment status."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    RETIRED = "retired"
    LOST = "lost"
    DAMAGED = "damaged"
    RESERVED = "reserved"
    CLEANING = "cleaning"
    INSPECTION = "inspection"
    CUSTOM = "custom"

class AssessmentStatus(str, enum.Enum):
    """Assessment status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"
    CUSTOM = "custom"

class CriteriaType(str, enum.Enum):
    """Assessment criteria types."""
    TECHNICAL = "technical"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    SAFETY = "safety"
    SKILL = "skill"
    BEHAVIOR = "behavior"
    KNOWLEDGE = "knowledge"
    ATTITUDE = "attitude"
    PARTICIPATION = "participation"
    CUSTOM = "custom"

class ChangeType(str, enum.Enum):
    """Change types for tracking modifications."""
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    DELETED = "deleted"
    RESTORED = "restored"
    MODIFIED = "modified"
    REVERTED = "reverted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CUSTOM = "custom"

class ActivityType(str, enum.Enum):
    """Activity types."""
    INDIVIDUAL = "individual"
    GROUP = "group"
    TEAM = "team"
    PAIR = "pair"
    CLASS = "class"
    COMPETITION = "competition"
    PRACTICE = "practice"
    ASSESSMENT = "assessment"
    WARM_UP = "warm_up"
    COOL_DOWN = "cool_down"
    CUSTOM = "custom"

class DifficultyLevel(str, enum.Enum):
    """Difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    CUSTOM = "custom"

class EquipmentRequirement(str, enum.Enum):
    """Equipment requirements."""
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    EXTENSIVE = "extensive"
    SPECIALIZED = "specialized"
    CUSTOM = "custom"

class StudentType(str, enum.Enum):
    """Student types."""
    REGULAR = "regular"
    SPECIAL_NEEDS = "special_needs"
    GIFTED = "gifted"
    ELL = "ell"
    IEP = "iep"
    SECTION_504 = "section_504"
    CUSTOM = "custom"

class GoalType(str, enum.Enum):
    """Goal types."""
    SKILL = "skill"
    FITNESS = "fitness"
    BEHAVIOR = "behavior"
    PARTICIPATION = "participation"
    PERFORMANCE = "performance"
    HEALTH = "health"
    SAFETY = "safety"
    CUSTOM = "custom"

class ClassType(str, enum.Enum):
    """Class types."""
    REGULAR = "regular"
    SPECIAL_ED = "special_ed"
    ADAPTED = "adapted"
    INCLUSIVE = "inclusive"
    ADVANCED = "advanced"
    REMEDIAL = "remedial"
    CUSTOM = "custom"

class RoutineType(str, enum.Enum):
    """Routine types."""
    WARM_UP = "warm_up"
    COOL_DOWN = "cool_down"
    STRETCHING = "stretching"
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    COORDINATION = "coordination"
    CUSTOM = "custom"

class SafetyType(str, enum.Enum):
    """Safety types."""
    EQUIPMENT = "equipment"
    ENVIRONMENT = "environment"
    BEHAVIOR = "behavior"
    MEDICAL = "medical"
    EMERGENCY = "emergency"
    SUPERVISION = "supervision"
    CUSTOM = "custom"

class Gender(str, enum.Enum):
    """Gender options."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    CUSTOM = "custom"

class FitnessLevel(str, enum.Enum):
    """Fitness levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    CUSTOM = "custom"

class GoalStatus(str, enum.Enum):
    """Goal status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    FAILED = "failed"
    ARCHIVED = "archived"
    CUSTOM = "custom"

class GoalCategory(str, enum.Enum):
    """Goal categories."""
    FITNESS = "fitness"
    SKILL = "skill"
    PERFORMANCE = "performance"
    HEALTH = "health"
    BEHAVIOR = "behavior"
    PARTICIPATION = "participation"
    SAFETY = "safety"
    CUSTOM = "custom"

class GoalTimeframe(str, enum.Enum):
    """Goal timeframes."""
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"
    IMMEDIATE = "immediate"
    CUSTOM = "custom"

class SecurityLevel(str, enum.Enum):
    """Security levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CUSTOM = "custom"

class SecurityStatus(str, enum.Enum):
    """Security status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    CUSTOM = "custom"

class SecurityAction(str, enum.Enum):
    """Security actions."""
    ALLOW = "allow"
    DENY = "deny"
    MONITOR = "monitor"
    ALERT = "alert"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    LOG = "log"
    CUSTOM = "custom"

class SecurityTrigger(str, enum.Enum):
    """Security triggers."""
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_CHANGE = "permission_change"
    ACCESS_ATTEMPT = "access_attempt"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_CHANGE = "system_change"
    CUSTOM = "custom"

__all__ = [
    'MeasurementUnit',
    'MetricType',
    'GoalAdjustment',
    'DeploymentStatus',
    'ServiceStatus',
    'FeatureFlagType',
    'FeatureFlagStatus',
    'ABTestType',
    'ABTestStatus',
    'AnalyticsEventType',
    'MetricsType',
    'AlertSeverity',
    'AlertStatus',
    'CircuitBreakerState',
    'AdaptationType',
    'AdaptationLevel',
    'AdaptationStatus',
    'AdaptationTrigger',
    'ExportFormat',
    'FileType',
    'AssessmentType',
    'EquipmentStatus',
    'AssessmentStatus',
    'CriteriaType',
    'ChangeType',
    'ActivityType',
    'DifficultyLevel',
    'EquipmentRequirement',
    'StudentType',
    'GoalType',
    'ClassType',
    'RoutineType',
    'SafetyType',
    'Gender',
    'FitnessLevel',
    'GoalStatus',
    'GoalCategory',
    'GoalTimeframe',
    'SecurityLevel',
    'SecurityStatus',
    'SecurityAction',
    'SecurityTrigger'
] 