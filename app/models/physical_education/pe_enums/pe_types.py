"""
Physical Education Types

This module contains enums and type definitions for physical education functionality.
"""

import enum
from typing import Optional
from datetime import datetime
from app.models.app_models import (
    SecurityLevel,
    SecurityStatus,
    SecurityAction,
    SecurityTrigger,
    ExportFormat,
    FileType,
    GradeLevel,
    Subject
)

# Security Types
class SecurityType(str, enum.Enum):
    """Types of security measures."""
    ACCESS_CONTROL = "access_control"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    AUDIT = "audit"
    MONITORING = "monitoring"
    COMPLIANCE = "compliance"
    PRIVACY = "privacy"
    DATA_PROTECTION = "data_protection"
    NETWORK = "network"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"

# Teacher Types
class CertificationType(str, enum.Enum):
    """Types of teacher certifications."""
    CPR = "cpr"
    FIRST_AID = "first_aid"
    PHYSICAL_EDUCATION = "physical_education"
    COACHING = "coaching"
    SPORTS_MEDICINE = "sports_medicine"
    NUTRITION = "nutrition"
    FITNESS = "fitness"
    SPECIAL_NEEDS = "special_needs"
    ATHLETIC_TRAINING = "athletic_training"
    EXERCISE_SCIENCE = "exercise_science"
    HEALTH_EDUCATION = "health_education"
    ADAPTIVE_PE = "adaptive_pe"
    YOGA = "yoga"
    PILATES = "pilates"
    DANCE = "dance"
    MARTIAL_ARTS = "martial_arts"
    AQUATICS = "aquatics"
    OUTDOOR_EDUCATION = "outdoor_education"
    ADVENTURE_SPORTS = "adventure_sports"
    TEAM_SPORTS = "team_sports"
    INDIVIDUAL_SPORTS = "individual_sports"
    STRENGTH_TRAINING = "strength_training"
    CARDIOVASCULAR = "cardiovascular"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    COORDINATION = "coordination"

class ActivityCategory(str, enum.Enum):
    """Categories of activities."""
    WARM_UP = "warm_up"
    SKILL_PRACTICE = "skill_practice"
    SKILL_DEVELOPMENT = "skill_development"
    FITNESS_TRAINING = "fitness_training"
    GAME = "game"
    COOL_DOWN = "cool_down"
    STRETCHING = "stretching"
    STRENGTH_TRAINING = "strength_training"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    COORDINATION = "coordination"

class ActivityCategoryType(str, enum.Enum):
    """Categories of activities."""
    INDIVIDUAL = "individual"
    TEAM = "team"
    PAIR = "pair"
    GROUP = "group"
    COMPETITIVE = "competitive"
    NON_COMPETITIVE = "non_competitive"

class ActivityDifficulty(str, enum.Enum):
    """Difficulty levels for activities."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ActivityStatus(str, enum.Enum):
    """Status options for activities."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class ActivityFormat(str, enum.Enum):
    """Formats for activities."""
    INDIVIDUAL = "individual"
    PAIR = "pair"
    SMALL_GROUP = "small_group"
    LARGE_GROUP = "large_group"
    TEAM = "team"
    CLASS = "class"

class ActivityGoal(str, enum.Enum):
    """Goals for activities."""
    SKILL_DEVELOPMENT = "skill_development"
    FITNESS = "fitness"
    COORDINATION = "coordination"
    TEAMWORK = "teamwork"
    COMPETITION = "competition"
    ENJOYMENT = "enjoyment"
    HEALTH = "health"
    WELLNESS = "wellness"

# Student Types
class StudentType(str, enum.Enum):
    """Types of students."""
    REGULAR = "regular"
    SPECIAL_NEEDS = "special_needs"
    ATHLETE = "athlete"
    BEGINNER = "beginner"
    ADVANCED = "advanced"

class StudentStatus(str, enum.Enum):
    """Status options for students."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"
    TRANSFERRED = "transferred"
    ON_LEAVE = "on_leave"
    WITHDRAWN = "withdrawn"

class StudentLevel(str, enum.Enum):
    """Level options for students."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class StudentCategory(str, enum.Enum):
    """Categories of students."""
    REGULAR = "regular"
    SPECIAL_NEEDS = "special_needs"
    ATHLETE = "athlete"
    BEGINNER = "beginner"
    ADVANCED = "advanced"
    TRANSFER = "transfer"
    RETURNING = "returning"
    NEW = "new"
    INTERNATIONAL = "international"
    EXCHANGE = "exchange"
    PART_TIME = "part_time"
    FULL_TIME = "full_time"

class Gender(str, enum.Enum):
    """Student gender options."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class FitnessLevel(str, enum.Enum):
    """Student fitness level options."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"

class FitnessCategory(str, enum.Enum):
    """Categories of fitness activities."""
    CARDIOVASCULAR = "cardiovascular"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    COORDINATION = "coordination"
    ENDURANCE = "endurance"
    AGILITY = "agility"
    SPEED = "speed"
    POWER = "power"
    REACTION_TIME = "reaction_time"

class MealType(str, enum.Enum):
    """Types of meals."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"

class NutritionCategory(str, enum.Enum):
    """Categories of nutrition plans."""
    # Basic Categories
    GENERAL = "general"
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MAINTENANCE = "maintenance"
    PERFORMANCE = "performance"
    HEALTH = "health"
    RECOVERY = "recovery"
    
    # Dietary Categories
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    PALEO = "paleo"
    KETO = "keto"
    MEDITERRANEAN = "mediterranean"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    
    # Health Categories
    DIABETIC = "diabetic"
    HEART_HEALTHY = "heart_healthy"
    LOW_SODIUM = "low_sodium"
    LOW_FAT = "low_fat"
    LOW_CARB = "low_carb"
    HIGH_PROTEIN = "high_protein"
    
    # Activity Categories
    ATHLETIC = "athletic"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    COORDINATION = "coordination"
    
    # Age Categories
    CHILDREN = "children"
    TEENAGERS = "teenagers"
    ADULTS = "adults"
    SENIORS = "seniors"
    
    # Special Categories
    PREGNANCY = "pregnancy"
    LACTATION = "lactation"
    POST_SURGERY = "post_surgery"
    REHABILITATION = "rehabilitation"
    PREVENTION = "prevention"
    WELLNESS = "wellness"

class DietaryRestriction(str, enum.Enum):
    """Types of dietary restrictions."""
    # Allergies
    PEANUT_ALLERGY = "peanut_allergy"
    TREE_NUT_ALLERGY = "tree_nut_allergy"
    MILK_ALLERGY = "milk_allergy"
    EGG_ALLERGY = "egg_allergy"
    SOY_ALLERGY = "soy_allergy"
    WHEAT_ALLERGY = "wheat_allergy"
    FISH_ALLERGY = "fish_allergy"
    SHELLFISH_ALLERGY = "shellfish_allergy"
    
    # Intolerances
    LACTOSE_INTOLERANCE = "lactose_intolerance"
    GLUTEN_INTOLERANCE = "gluten_intolerance"
    FODMAP_INTOLERANCE = "fodmap_intolerance"
    HISTAMINE_INTOLERANCE = "histamine_intolerance"
    
    # Dietary Choices
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    PALEO = "paleo"
    KETO = "keto"
    MEDITERRANEAN = "mediterranean"
    
    # Religious/Cultural
    HALAL = "halal"
    KOSHER = "kosher"
    JAIN = "jain"
    BUDDHIST = "buddhist"
    
    # Medical Conditions
    DIABETES = "diabetes"
    CELIAC = "celiac"
    IBS = "ibs"
    CROHNS = "crohns"
    ULCERATIVE_COLITIS = "ulcerative_colitis"
    
    # Other
    LOW_SODIUM = "low_sodium"
    LOW_FAT = "low_fat"
    LOW_CARB = "low_carb"
    HIGH_PROTEIN = "high_protein"
    SUGAR_FREE = "sugar_free"
    ORGANIC = "organic"
    NON_GMO = "non_gmo"

class NutritionGoal(str, enum.Enum):
    """Types of nutrition goals."""
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MAINTENANCE = "maintenance"
    PERFORMANCE = "performance"
    HEALTH = "health"
    RECOVERY = "recovery"
    ENERGY = "energy"
    HYDRATION = "hydration"
    NUTRIENT_BALANCE = "nutrient_balance"
    DIETARY_RESTRICTION = "dietary_restriction"

# Goal Types
class GoalStatus(str, enum.Enum):
    """Status options for fitness goals."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ON_HOLD = "on_hold"

class GoalCategory(str, enum.Enum):
    """Categories of fitness goals."""
    CARDIOVASCULAR = "cardiovascular"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    ENDURANCE = "endurance"
    BALANCE = "balance"
    COORDINATION = "coordination"
    SPEED = "speed"
    AGILITY = "agility"
    POWER = "power"
    SPORTS_SPECIFIC = "sports_specific"
    GENERAL_FITNESS = "general_fitness"
    WEIGHT_MANAGEMENT = "weight_management"

class GoalTimeframe(str, enum.Enum):
    """Timeframe for fitness goals."""
    SHORT_TERM = "short_term"  # 1-4 weeks
    MEDIUM_TERM = "medium_term"  # 1-3 months
    LONG_TERM = "long_term"  # 3+ months
    ACADEMIC_YEAR = "academic_year"
    CUSTOM = "custom"

class GoalType(str, enum.Enum):
    """Types of fitness goals."""
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    FLEXIBILITY = "flexibility"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    SKILL_IMPROVEMENT = "skill_improvement"

class GoalLevel(str, enum.Enum):
    """Levels of fitness goals."""
    # Basic Levels
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    
    # Achievement Levels
    NOVICE = "novice"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    MASTERY = "mastery"
    
    # Performance Levels
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    OPTIMAL = "optimal"
    
    # Challenge Levels
    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"
    DIFFICULT = "difficult"
    
    # Progress Levels
    INITIAL = "initial"
    PROGRESSING = "progressing"
    ACHIEVED = "achieved"
    EXCEEDED = "exceeded"
    
    # Fitness Levels
    UNFIT = "unfit"
    AVERAGE = "average"
    FIT = "fit"
    ATHLETIC = "athletic"
    
    # Health Levels
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"

class GoalTrigger(str, enum.Enum):
    """Triggers for fitness goal events."""
    # Manual Triggers
    MANUAL = "manual"
    USER_INITIATED = "user_initiated"
    TEACHER_INITIATED = "teacher_initiated"
    STUDENT_INITIATED = "student_initiated"
    PARENT_INITIATED = "parent_initiated"
    
    # Scheduled Triggers
    SCHEDULED = "scheduled"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    CUSTOM_SCHEDULE = "custom_schedule"
    
    # Progress Triggers
    MILESTONE_REACHED = "milestone_reached"
    TARGET_ACHIEVED = "target_achieved"
    PROGRESS_UPDATE = "progress_update"
    PERFORMANCE_REVIEW = "performance_review"
    ASSESSMENT_COMPLETE = "assessment_complete"
    
    # Health Triggers
    HEALTH_CHECK = "health_check"
    FITNESS_ASSESSMENT = "fitness_assessment"
    MEDICAL_CLEARANCE = "medical_clearance"
    WELLNESS_CHECK = "wellness_check"
    VITAL_SIGNS = "vital_signs"
    
    # Activity Triggers
    ACTIVITY_START = "activity_start"
    ACTIVITY_END = "activity_end"
    CLASS_START = "class_start"
    CLASS_END = "class_end"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    
    # System Triggers
    SYSTEM = "system"
    AUTOMATIC = "automatic"
    BACKGROUND = "background"
    MAINTENANCE = "maintenance"
    UPDATE = "update"
    SYNC = "sync"
    
    # External Triggers
    WEATHER = "weather"
    ENVIRONMENT = "environment"
    EQUIPMENT = "equipment"
    FACILITY = "facility"
    EXTERNAL_SYSTEM = "external_system"
    
    # Compliance Triggers
    COMPLIANCE_CHECK = "compliance_check"
    REGULATORY_REQUIREMENT = "regulatory_requirement"
    POLICY_UPDATE = "policy_update"
    STANDARD_UPDATE = "standard_update"
    AUDIT = "audit"

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

# Class Types
class ClassType(str, enum.Enum):
    """Types of classes."""
    REGULAR = "regular"
    SPECIAL_NEEDS = "special_needs"
    ATHLETIC = "athletic"
    RECREATIONAL = "recreational"
    COMPETITIVE = "competitive"
    ADVANCED = "advanced"
    BEGINNER = "beginner"

class ClassStatus(str, enum.Enum):
    """Status options for classes."""
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Routine Types
class RoutineStatus(str, enum.Enum):
    """Status options for routines."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"

class RoutineType(str, enum.Enum):
    """Types of routines."""
    WARM_UP = "warm_up"
    COOL_DOWN = "cool_down"
    STRETCHING = "stretching"
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    COORDINATION = "coordination"
    SKILL_DEVELOPMENT = "skill_development"

class RoutineLevel(str, enum.Enum):
    """Levels of routines."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class RoutineTrigger(str, enum.Enum):
    """Triggers for routine events."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    SAFETY = "safety"
    ADAPTATION = "adaptation"
    SYSTEM = "system"

# Assessment Types
class AssessmentType(str, enum.Enum):
    """Types of assessments."""
    SKILL = "skill"
    FITNESS = "fitness"
    BEHAVIOR = "behavior"
    PROGRESS = "progress"
    SAFETY = "safety"
    MOVEMENT = "movement"

class ProgressType(str, enum.Enum):
    """Types of progress tracking."""
    SKILL = "skill"
    FITNESS = "fitness"
    BEHAVIOR = "behavior"
    PERFORMANCE = "performance"
    PARTICIPATION = "participation"
    ATTENDANCE = "attendance"
    ACHIEVEMENT = "achievement"
    DEVELOPMENT = "development"

class ProgressStatus(str, enum.Enum):
    """Status options for progress tracking."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_IMPROVEMENT = "needs_improvement"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class ProgressLevel(str, enum.Enum):
    """Levels of progress achievement."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTERY = "mastery"

class ProgressTrigger(str, enum.Enum):
    """Triggers for progress events."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    PERFORMANCE = "performance"
    ASSESSMENT = "assessment"
    GOAL_ACHIEVED = "goal_achieved"
    MILESTONE_REACHED = "milestone_reached"
    ADAPTATION = "adaptation"
    SYSTEM = "system"

class AssessmentStatus(str, enum.Enum):
    """Status options for assessments."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class AssessmentLevel(str, enum.Enum):
    """Levels of assessment performance."""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"

class AnalysisLevel(str, enum.Enum):
    """Levels of analysis detail."""
    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    EXPERT = "expert"

class AnalysisTrigger(str, enum.Enum):
    """Triggers for analysis events."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    SAFETY = "safety"
    ADAPTATION = "adaptation"
    SYSTEM = "system"

class AssessmentTrigger(str, enum.Enum):
    """Triggers for assessment events."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    SAFETY = "safety"
    ADAPTATION = "adaptation"
    SYSTEM = "system"

class AssessmentResult(str, enum.Enum):
    """Results of assessments."""
    PASS = "pass"
    FAIL = "fail"
    INCOMPLETE = "incomplete"
    NEEDS_REVIEW = "needs_review"
    EXEMPT = "exempt"
    PENDING = "pending"

class CriteriaType(str, enum.Enum):
    """Types of assessment criteria."""
    TECHNICAL = "technical"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    SAFETY = "safety"

class ChangeType(str, enum.Enum):
    """Types of changes in assessments."""
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    ARCHIVED = "archived"

# Safety Types
class SafetyType(str, enum.Enum):
    """Types of safety measures."""
    PREVENTIVE = "preventive"
    REACTIVE = "reactive"
    MONITORING = "monitoring"
    TRAINING = "training"
    EQUIPMENT = "equipment"
    ENVIRONMENTAL = "environmental"
    PROCEDURAL = "procedural"

class IncidentType(str, enum.Enum):
    """Types of safety incidents."""
    INJURY = "injury"
    NEAR_MISS = "near_miss"
    EQUIPMENT_FAILURE = "equipment_failure"
    ENVIRONMENTAL = "environmental"
    BEHAVIORAL = "behavioral"

class IncidentSeverity(str, enum.Enum):
    """Severity levels for safety incidents."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, enum.Enum):
    """Types of safety alerts."""
    HIGH_RISK = "high_risk"
    MEDIUM_RISK = "medium_risk"
    LOW_RISK = "low_risk"
    INFORMATION = "information"

class CheckType(str, enum.Enum):
    """Types of safety checks."""
    EQUIPMENT = "equipment"
    ENVIRONMENT = "environment"
    STUDENT = "student"
    INSTRUCTOR = "instructor"

# Exercise Types
class ExerciseType(str, enum.Enum):
    """Types of exercises."""
    # Basic Exercise Types
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    COORDINATION = "coordination"
    ENDURANCE = "endurance"
    SPEED = "speed"
    AGILITY = "agility"
    
    # Training Methods
    BODYWEIGHT = "bodyweight"
    RESISTANCE = "resistance"
    WEIGHT_TRAINING = "weight_training"
    MACHINE = "machine"
    FREE_WEIGHTS = "free_weights"
    CABLE = "cable"
    PLYOMETRIC = "plyometric"
    ISOMETRIC = "isometric"
    ISOTONIC = "isotonic"
    ISOKINETIC = "isokinetic"
    
    # Energy Systems
    AEROBIC = "aerobic"
    ANAEROBIC = "anaerobic"
    HIIT = "hiit"
    CROSSFIT = "crossfit"
    
    # Mind-Body Exercises
    YOGA = "yoga"
    PILATES = "pilates"
    DANCE = "dance"
    MARTIAL_ARTS = "martial_arts"
    
    # Activity Categories
    SPORTS = "sports"
    RECREATIONAL = "recreational"
    THERAPEUTIC = "therapeutic"
    REHABILITATION = "rehabilitation"
    PREHABILITATION = "prehabilitation"
    
    # Movement Patterns
    MOBILITY = "mobility"
    STABILITY = "stability"
    POSTURE = "posture"
    MOVEMENT = "movement"
    SKILL = "skill"
    TECHNIQUE = "technique"
    DRILL = "drill"
    
    # Session Components
    WARM_UP = "warm_up"
    COOL_DOWN = "cool_down"
    RECOVERY = "recovery"
    REGENERATION = "regeneration"
    MAINTENANCE = "maintenance"
    
    # Training Focus
    PREVENTION = "prevention"
    CORRECTION = "correction"
    ADAPTATION = "adaptation"
    PROGRESSION = "progression"
    REGRESSION = "regression"
    MODIFICATION = "modification"
    VARIATION = "variation"
    
    # Exercise Categories
    PRIMARY = "primary"
    SECONDARY = "secondary"
    COMPLEMENTARY = "complementary"
    SUPPLEMENTARY = "supplementary"
    ADDITIONAL = "additional"
    OPTIONAL = "optional"
    REQUIRED = "required"
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    SUGGESTED = "suggested"
    PREFERRED = "preferred"
    ALTERNATIVE = "alternative"
    SUBSTITUTE = "substitute"
    OTHER = "other"

class ExerciseDifficulty(str, enum.Enum):
    """Difficulty levels for exercises."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class WorkoutType(str, enum.Enum):
    """Types of workouts."""
    CIRCUIT = "circuit"
    HIIT = "hiit"
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    COORDINATION = "coordination"

# Equipment Types
class EquipmentType(str, enum.Enum):
    """Types of equipment."""
    BALL = "ball"
    RACKET = "racket"
    NET = "net"
    MAT = "mat"
    WEIGHT = "weight"
    RESISTANCE_BAND = "resistance_band"
    BENCH = "bench"
    BAR = "bar"
    MACHINE = "machine"

class EquipmentStatus(str, enum.Enum):
    """Status options for equipment."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    RETIRED = "retired"
    LOST = "lost"
    DAMAGED = "damaged"

class MovementType(str, enum.Enum):
    """Types of movements."""
    RUNNING = "running"
    JUMPING = "jumping"
    THROWING = "throwing"
    CATCHING = "catching"
    KICKING = "kicking"
    STRIKING = "striking"
    DRIBBLING = "dribbling"
    PASSING = "passing"
    SHOOTING = "shooting"
    DEFENDING = "defending"

class DifficultyLevel(str, enum.Enum):
    """Difficulty levels for activities and exercises."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ProgressionLevel(str, enum.Enum):
    """Levels of progression in activities."""
    NOVICE = "novice"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    ADVANCED = "advanced"
    EXPERT = "expert"

class EquipmentRequirement(str, enum.Enum):
    """Equipment requirements for activities."""
    NONE = "none"
    MINIMAL = "minimal"
    STANDARD = "standard"
    SPECIALIZED = "specialized"
    EXTENSIVE = "extensive"

# Analysis Types
class AnalysisType(str, enum.Enum):
    """Types of activity analysis."""
    MOVEMENT = "movement"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    SAFETY = "safety"
    TECHNIQUE = "technique"
    ENGAGEMENT = "engagement"
    ADAPTATION = "adaptation"
    ASSESSMENT = "assessment"

class AnalysisStatus(str, enum.Enum):
    """Status of activity analysis."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ConfidenceLevel(str, enum.Enum):
    """Confidence levels for analysis results."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"

class PerformanceLevel(str, enum.Enum):
    """Performance levels for activity analysis."""
    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"

# Visualization Types
class VisualizationType(str, enum.Enum):
    """Types of activity visualizations."""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    RADAR_CHART = "radar_chart"
    TIMELINE = "timeline"
    PROGRESS_CHART = "progress_chart"
    COMPARISON_CHART = "comparison_chart"
    DISTRIBUTION_PLOT = "distribution_plot"
    BUBBLE_CHART = "bubble_chart"
    NETWORK_GRAPH = "network_graph"

class VisualizationLevel(str, enum.Enum):
    """Levels of visualization detail."""
    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    EXPERT = "expert"

class VisualizationStatus(str, enum.Enum):
    """Status of visualization generation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VisualizationTrigger(str, enum.Enum):
    """Triggers for visualization generation."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    ADAPTATION = "adaptation"
    SYSTEM = "system"

class ChartType(str, enum.Enum):
    """Types of charts for data visualization."""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    AREA = "area"
    PIE = "pie"
    HISTOGRAM = "histogram"
    BOX = "box"
    VIOLIN = "violin"
    HEATMAP = "heatmap"
    RADAR = "radar"
    BUBBLE = "bubble"
    WATERFALL = "waterfall"

class ColorScheme(str, enum.Enum):
    """Color schemes for visualizations."""
    DEFAULT = "default"
    PASTEL = "pastel"
    CONTRAST = "contrast"
    SEQUENTIAL = "sequential"
    DIVERGING = "diverging"
    QUALITATIVE = "qualitative"
    DARK = "dark"
    LIGHT = "light"

class InteractionMode(str, enum.Enum):
    """Interaction modes for visualizations."""
    ZOOM = "zoom"
    PAN = "pan"
    SELECT = "select"
    HOVER = "hover"
    NONE = "none"

# Export Types
class CompressionType(str, enum.Enum):
    """Compression types for exported data."""
    NONE = "none"
    GZIP = "gzip"
    ZIP = "zip"
    BZIP2 = "bzip2"
    XZ = "xz"
    LZMA = "lzma"

class DataFormat(str, enum.Enum):
    """Data formats for exported content."""
    RAW = "raw"
    FORMATTED = "formatted"
    AGGREGATED = "aggregated"
    SUMMARY = "summary"
    DETAILED = "detailed"
    MINIMAL = "minimal"

# Collaboration Types
class CollaborationType(str, enum.Enum):
    """Types of activity collaboration."""
    INDIVIDUAL = "individual"
    GROUP = "group"
    CLASS = "class"
    TEAM = "team"
    PEER = "peer"
    TEACHER = "teacher"
    PARENT = "parent"

class CollaborationLevel(str, enum.Enum):
    """Levels of collaboration."""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXPERT = "expert"

class CollaborationStatus(str, enum.Enum):
    """Status of collaboration."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class CollaborationTrigger(str, enum.Enum):
    """Triggers for collaboration events."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    ADAPTATION = "adaptation"
    SYSTEM = "system"

class AccessLevel(str, enum.Enum):
    """Access levels for collaboration."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    NONE = "none"

class SharingStatus(str, enum.Enum):
    """Status of sharing requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"

class NotificationType(str, enum.Enum):
    """Types of collaboration notifications."""
    INVITATION = "invitation"
    UPDATE = "update"
    COMMENT = "comment"
    MENTION = "mention"
    ALERT = "alert"
    REMINDER = "reminder"

# Adaptation Types
class AdaptationType(str, enum.Enum):
    """Types of activity adaptations."""
    DIFFICULTY = "difficulty"
    EQUIPMENT = "equipment"
    DURATION = "duration"
    TECHNIQUE = "technique"
    ASSISTANCE = "assistance"
    MODIFICATION = "modification"
    PROGRESSION = "progression"
    REGRESSION = "regression"

class AdaptationLevel(str, enum.Enum):
    """Levels of activity adaptation."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CUSTOM = "custom"

class AdaptationStatus(str, enum.Enum):
    """Status of activity adaptations."""
    PENDING = "pending"
    APPLIED = "applied"
    REVERTED = "reverted"
    FAILED = "failed"
    EXPIRED = "expired"

class AdaptationTrigger(str, enum.Enum):
    """Triggers for activity adaptations."""
    PERFORMANCE = "performance"
    SAFETY = "safety"
    FATIGUE = "fatigue"
    SKILL_LEVEL = "skill_level"
    PREFERENCE = "preference"
    INJURY = "injury"
    MANUAL = "manual"

# Rate Limit Types
class RateLimitType(str, enum.Enum):
    """Types of rate limits."""
    REQUEST = "request"
    CONCURRENT = "concurrent"
    BURST = "burst"
    WINDOW = "window"
    CUSTOM = "custom"

class RateLimitLevel(str, enum.Enum):
    """Rate limit priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class RateLimitStatus(str, enum.Enum):
    """Status of rate limits."""
    ACTIVE = "active"
    EXCEEDED = "exceeded"
    BLOCKED = "blocked"
    DISABLED = "disabled"
    PENDING = "pending"

class RateLimitTrigger(str, enum.Enum):
    """Triggers for rate limit events."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    THRESHOLD = "threshold"
    POLICY = "policy"

# Cache Types
class CacheType(str, enum.Enum):
    """Types of caching strategies."""
    MEMORY = "memory"
    DISK = "disk"
    REDIS = "redis"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"

class CacheLevel(str, enum.Enum):
    """Cache priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class CacheStatus(str, enum.Enum):
    """Status of cache entries."""
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"
    PENDING = "pending"

class CacheTrigger(str, enum.Enum):
    """Triggers for cache events."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    THRESHOLD = "threshold"
    POLICY = "policy"

# Circuit Breaker Types
class CircuitBreakerType(str, enum.Enum):
    """Types of circuit breakers."""
    ACTIVITY = "activity"
    SERVICE = "service"
    API = "api"
    DATABASE = "database"
    EXTERNAL = "external"
    CUSTOM = "custom"

class CircuitBreakerLevel(str, enum.Enum):
    """Circuit breaker priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class CircuitBreakerStatus(str, enum.Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"

class CircuitBreakerTrigger(str, enum.Enum):
    """Triggers for circuit breaker events."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    THRESHOLD = "threshold"
    POLICY = "policy"

# Risk Types
class RiskLevel(str, enum.Enum):
    """Risk levels for safety assessments."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Skill Types
class SkillLevel(str, enum.Enum):
    """Skill level options."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

# Planning Types
class PlanningType(str, enum.Enum):
    """Types of activity planning."""
    INDIVIDUAL = "individual"
    GROUP = "group"
    CLASS = "class"
    TEAM = "team"
    CUSTOM = "custom"

class PlanningLevel(str, enum.Enum):
    """Levels of activity planning."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class PlanningStatus(str, enum.Enum):
    """Status options for activity planning."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PlanningTrigger(str, enum.Enum):
    """Triggers for activity planning."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    ADAPTATION = "adaptation"
    SYSTEM = "system"

class TrackingType(str, enum.Enum):
    """Types of activity tracking."""
    PARTICIPATION = "participation"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    ATTENDANCE = "attendance"
    ENGAGEMENT = "engagement"
    BEHAVIOR = "behavior"
    SAFETY = "safety"
    HEALTH = "health"
    FITNESS = "fitness"
    SKILL = "skill"
    MOVEMENT = "movement"
    RECOVERY = "recovery"
    ADAPTATION = "adaptation"

class TrackingLevel(str, enum.Enum):
    """Levels of tracking detail."""
    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    EXPERT = "expert"

class TrackingTrigger(str, enum.Enum):
    """Triggers for tracking events."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    SAFETY = "safety"
    ADAPTATION = "adaptation"
    SYSTEM = "system"

class TrackingStatus(str, enum.Enum):
    """Status options for activity tracking."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    NEEDS_ATTENTION = "needs_attention"
    OVERDUE = "overdue"
    MISSED = "missed"
    RESCHEDULED = "rescheduled"

# Metric Types
class MetricType(str, enum.Enum):
    """Types of metrics for health and fitness tracking."""
    # Health Metrics
    HEIGHT = "height"
    WEIGHT = "weight"
    BMI = "bmi"
    HEART_RATE = "heart_rate"
    RESPIRATORY_RATE = "respiratory_rate"  # Added this line
    BLOOD_PRESSURE = "blood_pressure"
    OXYGEN_SATURATION = "oxygen_saturation"
    TEMPERATURE = "temperature"
    RESTING_HEART_RATE = "resting_heart_rate"
    MAXIMUM_HEART_RATE = "maximum_heart_rate"
    RECOVERY_HEART_RATE = "recovery_heart_rate"
    VO2_MAX = "vo2_max"
    LACTATE_THRESHOLD = "lactate_threshold"
    ANAEROBIC_THRESHOLD = "anaerobic_threshold"
    RESTING_METABOLIC_RATE = "resting_metabolic_rate"
    CALORIC_EXPENDITURE = "caloric_expenditure"
    SLEEP_QUALITY = "sleep_quality"
    STRESS_LEVEL = "stress_level"
    FATIGUE_LEVEL = "fatigue_level"
    PAIN_LEVEL = "pain_level"
    MOBILITY = "mobility"
    STABILITY = "stability"
    POSTURE = "posture"
    MOVEMENT_QUALITY = "movement_quality"
    SKILL_LEVEL = "skill_level"
    PERFORMANCE_SCORE = "performance_score"
    PROGRESS_SCORE = "progress_score"
    BODY_COMPOSITION = "body_composition"
    MUSCLE_MASS = "muscle_mass"
    BODY_FAT = "body_fat"
    BONE_DENSITY = "bone_density"
    HYDRATION = "hydration"
    NUTRITION = "nutrition"
    VITAMIN_LEVELS = "vitamin_levels"
    MINERAL_LEVELS = "mineral_levels"
    HORMONE_LEVELS = "hormone_levels"
    IMMUNE_FUNCTION = "immune_function"
    INFLAMMATION = "inflammation"
    RECOVERY = "recovery"
    REGENERATION = "regeneration"
    ADAPTATION = "adaptation"
    PERFORMANCE = "performance"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    POWER = "power"
    SPEED = "speed"
    AGILITY = "agility"
    BALANCE = "balance"
    COORDINATION = "coordination"
    REACTION_TIME = "reaction_time"
    AEROBIC_CAPACITY = "aerobic_capacity"
    ANAEROBIC_CAPACITY = "anaerobic_capacity"
    MUSCULAR_ENDURANCE = "muscular_endurance"
    MUSCULAR_STRENGTH = "muscular_strength"
    MENTAL_HEALTH = "mental_health"
    EMOTIONAL_HEALTH = "emotional_health"
    SOCIAL_HEALTH = "social_health"
    COGNITIVE_HEALTH = "cognitive_health"
    BEHAVIORAL_HEALTH = "behavioral_health"
    LIFESTYLE = "lifestyle"
    DIET = "diet"
    EXERCISE = "exercise"
    SLEEP = "sleep"
    STRESS = "stress"
    RELAXATION = "relaxation"
    MEDITATION = "meditation"
    MINDFULNESS = "mindfulness"
    WELLNESS = "wellness"
    QUALITY_OF_LIFE = "quality_of_life"
    HEALTH_STATUS = "health_status"
    DISEASE_RISK = "disease_risk"
    LONGEVITY = "longevity"
    BIOLOGICAL_AGE = "biological_age"
    FUNCTIONAL_AGE = "functional_age"
    HEALTH_AGE = "health_age"
    FITNESS_AGE = "fitness_age"
    METABOLIC_AGE = "metabolic_age"
    CARDIOVASCULAR_AGE = "cardiovascular_age"
    MUSCULOSKELETAL_AGE = "musculoskeletal_age"
    NEUROLOGICAL_AGE = "neurological_age"
    IMMUNE_AGE = "immune_age"
    HORMONAL_AGE = "hormonal_age"
    CELLULAR_AGE = "cellular_age"
    GENETIC_AGE = "genetic_age"
    EPIGENETIC_AGE = "epigenetic_age"
    TELOMERE_LENGTH = "telomere_length"
    OXIDATIVE_STRESS = "oxidative_stress"
    INFLAMMATORY_MARKERS = "inflammatory_markers"
    HORMONAL_MARKERS = "hormonal_markers"
    METABOLIC_MARKERS = "metabolic_markers"
    NUTRITIONAL_MARKERS = "nutritional_markers"
    IMMUNE_MARKERS = "immune_markers"
    NEUROLOGICAL_MARKERS = "neurological_markers"
    CARDIOVASCULAR_MARKERS = "cardiovascular_markers"
    MUSCULOSKELETAL_MARKERS = "musculoskeletal_markers"
    CELLULAR_MARKERS = "cellular_markers"
    GENETIC_MARKERS = "genetic_markers"
    EPIGENETIC_MARKERS = "epigenetic_markers"
    BIOMARKERS = "biomarkers"
    HEALTH_MARKERS = "health_markers"
    DISEASE_MARKERS = "disease_markers"
    RISK_MARKERS = "risk_markers"
    PROGNOSIS_MARKERS = "prognosis_markers"
    DIAGNOSTIC_MARKERS = "diagnostic_markers"
    SCREENING_MARKERS = "screening_markers"
    MONITORING_MARKERS = "monitoring_markers"
    TREATMENT_MARKERS = "treatment_markers"
    OUTCOME_MARKERS = "outcome_markers"
    PROGRESS_MARKERS = "progress_markers"
    RECOVERY_MARKERS = "recovery_markers"
    REGENERATION_MARKERS = "regeneration_markers"
    ADAPTATION_MARKERS = "adaptation_markers"
    PERFORMANCE_MARKERS = "performance_markers"
    FITNESS_MARKERS = "fitness_markers"
    WELLNESS_MARKERS = "wellness_markers"
    LIFESTYLE_MARKERS = "lifestyle_markers"
    BEHAVIORAL_MARKERS = "behavioral_markers"
    PSYCHOLOGICAL_MARKERS = "psychological_markers"
    SOCIAL_MARKERS = "social_markers"
    ENVIRONMENTAL_MARKERS = "environmental_markers"
    OCCUPATIONAL_MARKERS = "occupational_markers"
    ECONOMIC_MARKERS = "economic_markers"
    CULTURAL_MARKERS = "cultural_markers"
    SPIRITUAL_MARKERS = "spiritual_markers"
    EXISTENTIAL_MARKERS = "existential_markers"
    QUALITY_OF_LIFE_MARKERS = "quality_of_life_markers"
    HEALTH_STATUS_MARKERS = "health_status_markers"
    DISEASE_RISK_MARKERS = "disease_risk_markers"
    LONGEVITY_MARKERS = "longevity_markers"
    BIOLOGICAL_AGE_MARKERS = "biological_age_markers"
    FUNCTIONAL_AGE_MARKERS = "functional_age_markers"
    HEALTH_AGE_MARKERS = "health_age_markers"
    FITNESS_AGE_MARKERS = "fitness_age_markers"
    METABOLIC_AGE_MARKERS = "metabolic_age_markers"
    CARDIOVASCULAR_AGE_MARKERS = "cardiovascular_age_markers"
    MUSCULOSKELETAL_AGE_MARKERS = "musculoskeletal_age_markers"
    NEUROLOGICAL_AGE_MARKERS = "neurological_age_markers"
    IMMUNE_AGE_MARKERS = "immune_age_markers"
    HORMONAL_AGE_MARKERS = "hormonal_age_markers"
    CELLULAR_AGE_MARKERS = "cellular_age_markers"
    GENETIC_AGE_MARKERS = "genetic_age_markers"
    EPIGENETIC_AGE_MARKERS = "epigenetic_age_markers"

class MetricLevel(str, enum.Enum):
    """Levels of metrics."""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"
    CRITICAL = "critical"

class MetricStatus(str, enum.Enum):
    """Status of metrics."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class MetricTrigger(str, enum.Enum):
    """Triggers for metric events."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    PERFORMANCE = "performance"
    PROGRESS = "progress"
    SAFETY = "safety"
    ADAPTATION = "adaptation"
    SYSTEM = "system"

class MeasurementUnit(str, enum.Enum):
    """Units of measurement for health and fitness metrics."""
    # Length Units
    CENTIMETERS = "cm"
    METERS = "m"
    MILLIMETERS = "mm"
    INCHES = "in"
    FEET = "ft"
    YARDS = "yd"
    MILES = "mi"
    KILOMETERS = "km"
    
    # Weight/Mass Units
    KILOGRAMS = "kg"
    GRAMS = "g"
    MILLIGRAMS = "mg"
    POUNDS = "lbs"
    OUNCES = "oz"
    
    # Time Units
    SECONDS = "s"
    MINUTES = "min"
    HOURS = "h"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
    
    # Volume Units
    MILLILITERS = "ml"
    LITERS = "L"
    CUBIC_CENTIMETERS = "cc"
    CUBIC_METERS = "m³"
    FLUID_OUNCES = "fl_oz"
    CUPS = "cups"
    PINTS = "pints"
    QUARTS = "quarts"
    GALLONS = "gallons"
    
    # Temperature Units
    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    KELVIN = "K"
    
    # Pressure Units
    PASCALS = "Pa"
    KILOPASCALS = "kPa"
    MILLIMETERS_OF_MERCURY = "mmHg"
    POUNDS_PER_SQUARE_INCH = "psi"
    ATMOSPHERES = "atm"
    
    # Speed/Velocity Units
    METERS_PER_SECOND = "m/s"
    KILOMETERS_PER_HOUR = "km/h"
    MILES_PER_HOUR = "mph"
    FEET_PER_SECOND = "ft/s"
    
    # Force Units
    NEWTONS = "N"
    POUND_FORCE = "lbf"
    KILOGRAM_FORCE = "kgf"
    
    # Energy Units
    JOULES = "J"
    KILOJOULES = "kJ"
    CALORIES = "cal"
    KILOCALORIES = "kcal"
    WATT_HOURS = "Wh"
    KILOWATT_HOURS = "kWh"
    
    # Power Units
    WATTS = "W"
    KILOWATTS = "kW"
    HORSEPOWER = "hp"
    
    # Frequency Units
    HERTZ = "Hz"
    CYCLES_PER_SECOND = "cps"
    BEATS_PER_MINUTE = "bpm"
    REVOLUTIONS_PER_MINUTE = "rpm"
    
    # Angle Units
    DEGREES = "°"
    RADIANS = "rad"
    GRADIANS = "grad"
    
    # Area Units
    SQUARE_METERS = "m²"
    SQUARE_CENTIMETERS = "cm²"
    SQUARE_MILLIMETERS = "mm²"
    SQUARE_INCHES = "in²"
    SQUARE_FEET = "ft²"
    SQUARE_YARDS = "yd²"
    SQUARE_MILES = "mi²"
    ACRES = "acres"
    HECTARES = "ha"
    
    # Concentration Units
    PERCENT = "%"
    PARTS_PER_MILLION = "ppm"
    PARTS_PER_BILLION = "ppb"
    MILLIGRAMS_PER_DECILITER = "mg/dL"
    MILLIMOLES_PER_LITER = "mmol/L"
    MILLIEQUIVALENTS_PER_LITER = "mEq/L"
    INTERNATIONAL_UNITS = "IU"
    MILLIGRAMS_PER_KILOGRAM = "mg/kg"
    MILLIGRAMS_PER_LITER = "mg/L"
    
    # Rate Units
    MILLILITERS_PER_KILOGRAM_PER_MINUTE = "ml/kg/min"
    MILLILITERS_PER_MINUTE = "ml/min"
    LITERS_PER_MINUTE = "L/min"
    LITERS_PER_SECOND = "L/s"
    CUBIC_METERS_PER_MINUTE = "m³/min"
    CUBIC_METERS_PER_SECOND = "m³/s"
    
    # Count Units
    COUNT = "count"
    REPETITIONS = "reps"
    SETS = "sets"
    ROUNDS = "rounds"
    LAPS = "laps"
    STEPS = "steps"
    STRIDES = "strides"
    JUMPS = "jumps"
    THROWS = "throws"
    CATCHES = "catches"
    KICKS = "kicks"
    STRIKES = "strikes"
    DRIBBLES = "dribbles"
    PASSES = "passes"
    SHOTS = "shots"
    BLOCKS = "blocks"
    STEALS = "steals"
    ASSISTS = "assists"
    GOALS = "goals"
    POINTS = "points"
    SCORES = "scores"
    WINS = "wins"
    LOSSES = "losses"
    TIES = "ties"
    GAMES = "games"
    MATCHES = "matches"
    TOURNAMENTS = "tournaments"
    SEASONS = "seasons"
    
    # Time Count Units
    YEARS_COUNT = "years"
    MONTHS_COUNT = "months"
    WEEKS_COUNT = "weeks"
    DAYS_COUNT = "days"
    HOURS_COUNT = "hours"
    MINUTES_COUNT = "minutes"
    SECONDS_COUNT = "seconds"
    MILLISECONDS = "ms"
    MICROSECONDS = "µs"
    NANOSECONDS = "ns"
    
    # Subjective Units
    SCORE = "score"
    RATING = "rating"
    LEVEL = "level"
    INDEX = "index"
    RATIO = "ratio"

# Safety Types
class SafetyLevel(str, enum.Enum):
    """Levels of safety measures."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SafetyStatus(str, enum.Enum):
    """Status of safety measures."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    REVIEW = "review"
    EXPIRED = "expired"

class SafetyTrigger(str, enum.Enum):
    """Triggers for safety events."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    INCIDENT = "incident"
    RISK = "risk"
    SYSTEM = "system"

class SafetyCheckType(str, enum.Enum):
    """Types of safety checks."""
    EQUIPMENT_INSPECTION = "equipment_inspection"
    ENVIRONMENTAL_ASSESSMENT = "environmental_assessment"
    STUDENT_HEALTH_CHECK = "student_health_check"
    EMERGENCY_PROCEDURES_REVIEW = "emergency_procedures_review"
    ACTIVITY_SPECIFIC_SAFETY = "activity_specific_safety"
    FACILITY_INSPECTION = "facility_inspection"
    WEATHER_ASSESSMENT = "weather_assessment"
    MEDICAL_CLEARANCE = "medical_clearance"

class SafetyCheckLevel(str, enum.Enum):
    """Levels of safety checks."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    EMERGENCY = "emergency"

class SafetyCheckStatus(str, enum.Enum):
    """Status of safety checks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_ATTENTION = "requires_attention"
    CANCELLED = "cancelled"

class SafetyCheckTrigger(str, enum.Enum):
    """Triggers for safety check events."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    INCIDENT = "incident"
    RISK = "risk"
    SYSTEM = "system"
    PRE_ACTIVITY = "pre_activity"
    POST_ACTIVITY = "post_activity"

class IncidentLevel(str, enum.Enum):
    """Levels of incident severity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, enum.Enum):
    """Status of incidents."""
    REPORTED = "reported"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"
    PENDING = "pending"

class IncidentTrigger(str, enum.Enum):
    """Triggers for incident events."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    SYSTEM = "system"

class RiskType(str, enum.Enum):
    """Types of risks."""
    PHYSICAL = "physical"
    ENVIRONMENTAL = "environmental"
    EQUIPMENT = "equipment"
    BEHAVIORAL = "behavioral"
    MEDICAL = "medical"
    WEATHER = "weather"

class RiskStatus(str, enum.Enum):
    """Status of risk assessments."""
    PENDING = "pending"
    ASSESSED = "assessed"
    MITIGATED = "mitigated"
    MONITORING = "monitoring"
    CLOSED = "closed"

class RiskTrigger(str, enum.Enum):
    """Triggers for risk events."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    INCIDENT = "incident"
    SYSTEM = "system"

# Health Metric Types
class HealthMetricType(str, enum.Enum):
    """Types of health metrics."""
    HEIGHT = "height"
    WEIGHT = "weight"
    BMI = "bmi"
    HEART_RATE = "heart_rate"
    RESPIRATORY_RATE = "respiratory_rate"
    BLOOD_PRESSURE = "blood_pressure"
    OXYGEN_SATURATION = "oxygen_saturation"
    TEMPERATURE = "temperature"
    RESTING_HEART_RATE = "resting_heart_rate"
    MAXIMUM_HEART_RATE = "maximum_heart_rate"
    RECOVERY_HEART_RATE = "recovery_heart_rate"
    VO2_MAX = "vo2_max"
    LACTATE_THRESHOLD = "lactate_threshold"
    ANAEROBIC_THRESHOLD = "anaerobic_threshold"
    RESTING_METABOLIC_RATE = "resting_metabolic_rate"
    CALORIC_EXPENDITURE = "caloric_expenditure"
    SLEEP_QUALITY = "sleep_quality"
    STRESS_LEVEL = "stress_level"
    FATIGUE_LEVEL = "fatigue_level"
    PAIN_LEVEL = "pain_level"
    MOBILITY = "mobility"
    STABILITY = "stability"
    POSTURE = "posture"
    MOVEMENT_QUALITY = "movement_quality"
    SKILL_LEVEL = "skill_level"
    PERFORMANCE_SCORE = "performance_score"
    PROGRESS_SCORE = "progress_score"
    PARTICIPATION_SCORE = "participation_score"
    ENGAGEMENT_SCORE = "engagement_score"
    MOTIVATION_SCORE = "motivation_score"
    CONFIDENCE_SCORE = "confidence_score"
    SATISFACTION_SCORE = "satisfaction_score"
    ENJOYMENT_SCORE = "enjoyment_score"
    EFFORT_SCORE = "effort_score"
    ATTITUDE_SCORE = "attitude_score"
    BEHAVIOR_SCORE = "behavior_score"
    SOCIAL_SCORE = "social_score"
    EMOTIONAL_SCORE = "emotional_score"
    COGNITIVE_SCORE = "cognitive_score"
    PHYSICAL_SCORE = "physical_score"
    MENTAL_SCORE = "mental_score"
    OVERALL_SCORE = "overall_score"
    BODY_COMPOSITION = "body_composition"
    MUSCLE_MASS = "muscle_mass"
    BODY_FAT = "body_fat"
    BONE_DENSITY = "bone_density"
    HYDRATION = "hydration"
    NUTRITION = "nutrition"
    VITAMIN_LEVELS = "vitamin_levels"
    MINERAL_LEVELS = "mineral_levels"
    HORMONE_LEVELS = "hormone_levels"
    IMMUNE_FUNCTION = "immune_function"
    INFLAMMATION = "inflammation"
    RECOVERY = "recovery"
    REGENERATION = "regeneration"
    ADAPTATION = "adaptation"
    PERFORMANCE = "performance"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    POWER = "power"
    SPEED = "speed"
    AGILITY = "agility"
    BALANCE = "balance"
    COORDINATION = "coordination"
    REACTION_TIME = "reaction_time"
    AEROBIC_CAPACITY = "aerobic_capacity"
    ANAEROBIC_CAPACITY = "anaerobic_capacity"
    MUSCULAR_ENDURANCE = "muscular_endurance"
    MUSCULAR_STRENGTH = "muscular_strength"
    MENTAL_HEALTH = "mental_health"
    EMOTIONAL_HEALTH = "emotional_health"
    SOCIAL_HEALTH = "social_health"
    COGNITIVE_HEALTH = "cognitive_health"
    BEHAVIORAL_HEALTH = "behavioral_health"
    LIFESTYLE = "lifestyle"
    DIET = "diet"
    EXERCISE = "exercise"
    SLEEP = "sleep"
    STRESS = "stress"
    RELAXATION = "relaxation"
    MEDITATION = "meditation"
    MINDFULNESS = "mindfulness"
    WELLNESS = "wellness"
    QUALITY_OF_LIFE = "quality_of_life"
    HEALTH_STATUS = "health_status"
    DISEASE_RISK = "disease_risk"
    LONGEVITY = "longevity"
    BIOLOGICAL_AGE = "biological_age"
    FUNCTIONAL_AGE = "functional_age"
    HEALTH_AGE = "health_age"
    FITNESS_AGE = "fitness_age"
    METABOLIC_AGE = "metabolic_age"
    CARDIOVASCULAR_AGE = "cardiovascular_age"
    MUSCULOSKELETAL_AGE = "musculoskeletal_age"
    NEUROLOGICAL_AGE = "neurological_age"
    IMMUNE_AGE = "immune_age"
    HORMONAL_AGE = "hormonal_age"
    CELLULAR_AGE = "cellular_age"
    GENETIC_AGE = "genetic_age"
    EPIGENETIC_AGE = "epigenetic_age"
    TELOMERE_LENGTH = "telomere_length"
    OXIDATIVE_STRESS = "oxidative_stress"
    INFLAMMATORY_MARKERS = "inflammatory_markers"
    HORMONAL_MARKERS = "hormonal_markers"
    METABOLIC_MARKERS = "metabolic_markers"
    NUTRITIONAL_MARKERS = "nutritional_markers"
    IMMUNE_MARKERS = "immune_markers"
    NEUROLOGICAL_MARKERS = "neurological_markers"
    CARDIOVASCULAR_MARKERS = "cardiovascular_markers"
    MUSCULOSKELETAL_MARKERS = "musculoskeletal_markers"
    CELLULAR_MARKERS = "cellular_markers"
    GENETIC_MARKERS = "genetic_markers"
    EPIGENETIC_MARKERS = "epigenetic_markers"
    BIOMARKERS = "biomarkers"
    HEALTH_MARKERS = "health_markers"
    DISEASE_MARKERS = "disease_markers"
    RISK_MARKERS = "risk_markers"
    PROGNOSIS_MARKERS = "prognosis_markers"
    DIAGNOSTIC_MARKERS = "diagnostic_markers"
    SCREENING_MARKERS = "screening_markers"
    MONITORING_MARKERS = "monitoring_markers"
    TREATMENT_MARKERS = "treatment_markers"
    OUTCOME_MARKERS = "outcome_markers"
    PROGRESS_MARKERS = "progress_markers"
    RECOVERY_MARKERS = "recovery_markers"
    REGENERATION_MARKERS = "regeneration_markers"
    ADAPTATION_MARKERS = "adaptation_markers"
    PERFORMANCE_MARKERS = "performance_markers"
    FITNESS_MARKERS = "fitness_markers"
    WELLNESS_MARKERS = "wellness_markers"
    LIFESTYLE_MARKERS = "lifestyle_markers"
    BEHAVIORAL_MARKERS = "behavioral_markers"
    PSYCHOLOGICAL_MARKERS = "psychological_markers"
    SOCIAL_MARKERS = "social_markers"
    ENVIRONMENTAL_MARKERS = "environmental_markers"
    OCCUPATIONAL_MARKERS = "occupational_markers"
    ECONOMIC_MARKERS = "economic_markers"
    CULTURAL_MARKERS = "cultural_markers"
    SPIRITUAL_MARKERS = "spiritual_markers"
    EXISTENTIAL_MARKERS = "existential_markers"
    QUALITY_OF_LIFE_MARKERS = "quality_of_life_markers"
    HEALTH_STATUS_MARKERS = "health_status_markers"
    DISEASE_RISK_MARKERS = "disease_risk_markers"
    LONGEVITY_MARKERS = "longevity_markers"
    BIOLOGICAL_AGE_MARKERS = "biological_age_markers"
    FUNCTIONAL_AGE_MARKERS = "functional_age_markers"
    HEALTH_AGE_MARKERS = "health_age_markers"
    FITNESS_AGE_MARKERS = "fitness_age_markers"
    METABOLIC_AGE_MARKERS = "metabolic_age_markers"
    CARDIOVASCULAR_AGE_MARKERS = "cardiovascular_age_markers"
    MUSCULOSKELETAL_AGE_MARKERS = "musculoskeletal_age_markers"
    NEUROLOGICAL_AGE_MARKERS = "neurological_age_markers"
    IMMUNE_AGE_MARKERS = "immune_age_markers"
    HORMONAL_AGE_MARKERS = "hormonal_age_markers"
    CELLULAR_AGE_MARKERS = "cellular_age_markers"
    GENETIC_AGE_MARKERS = "genetic_age_markers"
    EPIGENETIC_AGE_MARKERS = "epigenetic_age_markers"

class HealthMetricLevel(str, enum.Enum):
    """Levels of health metrics."""
    # Basic Levels
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"
    
    # Comparative Levels
    OPTIMAL = "optimal"
    ABOVE_AVERAGE = "above_average"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    
    # Severity Levels
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"
    
    # Status Levels
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    ELEVATED = "elevated"
    DEPRESSED = "depressed"
    
    # Range Levels
    HIGH = "high"
    LOW = "low"
    VERY_HIGH = "very_high"
    VERY_LOW = "very_low"
    EXTREMELY_HIGH = "extremely_high"
    EXTREMELY_LOW = "extremely_low"
    DANGEROUSLY_HIGH = "dangerously_high"
    DANGEROUSLY_LOW = "dangerously_low"
    
    # Emergency Levels
    LIFE_THREATENING = "life_threatening"
    EMERGENCY = "emergency"
    URGENT = "urgent"
    
    # Stability Levels
    STABLE = "stable"
    UNSTABLE = "unstable"
    IMPROVING = "improving"
    DETERIORATING = "deteriorating"
    FLUCTUATING = "fluctuating"
    STEADY = "steady"
    PROGRESSING = "progressing"
    REGRESSING = "regressing"
    
    # Quality Levels
    MAINTAINED = "maintained"
    COMPROMISED = "compromised"
    OPTIMIZED = "optimized"
    SUBOPTIMAL = "suboptimal"
    DEFICIENT = "deficient"
    EXCESSIVE = "excessive"
    BALANCED = "balanced"
    IMBALANCED = "imbalanced"
    
    # Adequacy Levels
    ADEQUATE = "adequate"
    INADEQUATE = "inadequate"
    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"
    APPROPRIATE = "appropriate"
    INAPPROPRIATE = "inappropriate"
    ACCEPTABLE = "acceptable"
    UNACCEPTABLE = "unacceptable"
    SATISFACTORY = "satisfactory"
    UNSATISFACTORY = "unsatisfactory"
    
    # Preference Levels
    DESIRABLE = "desirable"
    UNDESIRABLE = "undesirable"
    PREFERRED = "preferred"
    NON_PREFERRED = "non_preferred"
    RECOMMENDED = "recommended"
    NOT_RECOMMENDED = "not_recommended"
    
    # Requirement Levels
    REQUIRED = "required"
    OPTIONAL = "optional"
    MANDATORY = "mandatory"
    DISCRETIONARY = "discretionary"
    ESSENTIAL = "essential"
    NON_ESSENTIAL = "non_essential"
    VITAL = "vital"
    NON_VITAL = "non_vital"
    
    # Importance Levels
    IMPORTANT = "important"
    UNIMPORTANT = "unimportant"
    SIGNIFICANT = "significant"
    INSIGNIFICANT = "insignificant"
    RELEVANT = "relevant"
    IRRELEVANT = "irrelevant"
    APPLICABLE = "applicable"
    INAPPLICABLE = "inapplicable"
    
    # Validity Levels
    VALID = "valid"
    INVALID = "invalid"
    RELIABLE = "reliable"
    UNRELIABLE = "unreliable"
    ACCURATE = "accurate"
    INACCURATE = "inaccurate"
    PRECISE = "precise"
    IMPRECISE = "imprecise"
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    
    # Predictability Levels
    PREDICTABLE = "predictable"
    UNPREDICTABLE = "unpredictable"
    CONTROLLABLE = "controllable"
    UNCONTROLLABLE = "uncontrollable"
    MANAGEABLE = "manageable"
    UNMANAGEABLE = "unmanageable"
    
    # Medical Condition Levels
    TREATABLE = "treatable"
    UNTREATABLE = "untreatable"
    CURABLE = "curable"
    INCURABLE = "incurable"
    PREVENTABLE = "preventable"
    UNPREVENTABLE = "unpreventable"
    REVERSIBLE = "reversible"
    IRREVERSIBLE = "irreversible"
    TEMPORARY = "temporary"
    PERMANENT = "permanent"
    ACUTE = "acute"
    CHRONIC = "chronic"
    PROGRESSIVE = "progressive"
    REGRESSIVE = "regressive"

class HealthMetricStatus(str, enum.Enum):
    """Status of health metrics."""
    # Basic Status
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    
    # Measurement Status
    MEASURED = "measured"
    NOT_MEASURED = "not_measured"
    IN_PROGRESS = "in_progress"
    SCHEDULED = "scheduled"
    OVERDUE = "overdue"
    MISSED = "missed"
    
    # Validation Status
    VALIDATED = "validated"
    INVALID = "invalid"
    NEEDS_REVIEW = "needs_review"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    
    # Processing Status
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    QUEUED = "queued"
    RETRYING = "retrying"
    TIMEOUT = "timeout"
    
    # Update Status
    UPDATED = "updated"
    OUTDATED = "outdated"
    STALE = "stale"
    CURRENT = "current"
    EXPIRED = "expired"
    REFRESHED = "refreshed"
    
    # Health Status
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    AT_RISK = "at_risk"
    MONITORING = "monitoring"
    STABLE = "stable"
    UNSTABLE = "unstable"
    
    # Trend Status
    IMPROVING = "improving"
    DETERIORATING = "deteriorating"
    FLUCTUATING = "fluctuating"
    STEADY = "steady"
    PROGRESSING = "progressing"
    REGRESSING = "regressing"
    
    # Alert Status
    ALERT = "alert"
    WARNING = "warning"
    CRITICAL = "critical"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    IGNORED = "ignored"
    
    # Compliance Status
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    EXEMPT = "exempt"
    WAIVED = "waived"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    
    # Documentation Status
    DOCUMENTED = "documented"
    UNDOCUMENTED = "undocumented"
    PARTIALLY_DOCUMENTED = "partially_documented"
    NEEDS_DOCUMENTATION = "needs_documentation"
    DOCUMENTATION_COMPLETE = "documentation_complete"
    DOCUMENTATION_INCOMPLETE = "documentation_incomplete"

class HealthMetricTrigger(str, enum.Enum):
    """Triggers for health metric events."""
    # Manual Triggers
    MANUAL = "manual"
    USER_INITIATED = "user_initiated"
    ADMIN_INITIATED = "admin_initiated"
    TEACHER_INITIATED = "teacher_initiated"
    STUDENT_INITIATED = "student_initiated"
    PARENT_INITIATED = "parent_initiated"
    
    # Scheduled Triggers
    SCHEDULED = "scheduled"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    CUSTOM_SCHEDULE = "custom_schedule"
    
    # Event Triggers
    ACTIVITY_START = "activity_start"
    ACTIVITY_END = "activity_end"
    CLASS_START = "class_start"
    CLASS_END = "class_end"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    
    # Health Triggers
    HEALTH_CHECK = "health_check"
    MEDICAL_CHECK = "medical_check"
    FITNESS_ASSESSMENT = "fitness_assessment"
    WELLNESS_CHECK = "wellness_check"
    VITAL_SIGNS = "vital_signs"
    SYMPTOM_REPORT = "symptom_report"
    
    # Alert Triggers
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    ABNORMAL_VALUE = "abnormal_value"
    TREND_DETECTED = "trend_detected"
    PATTERN_DETECTED = "pattern_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    RISK_DETECTED = "risk_detected"
    
    # System Triggers
    SYSTEM = "system"
    AUTOMATIC = "automatic"
    BACKGROUND = "background"
    MAINTENANCE = "maintenance"
    UPDATE = "update"
    SYNC = "sync"
    
    # External Triggers
    WEATHER = "weather"
    ENVIRONMENT = "environment"
    EQUIPMENT = "equipment"
    FACILITY = "facility"
    EXTERNAL_SYSTEM = "external_system"
    THIRD_PARTY = "third_party"
    
    # Compliance Triggers
    COMPLIANCE_CHECK = "compliance_check"
    REGULATORY_REQUIREMENT = "regulatory_requirement"
    POLICY_UPDATE = "policy_update"
    STANDARD_UPDATE = "standard_update"
    AUDIT = "audit"
    CERTIFICATION = "certification"
    
    # Documentation Triggers
    DOCUMENTATION_UPDATE = "documentation_update"
    RECORD_UPDATE = "record_update"
    REPORT_GENERATION = "report_generation"
    DATA_EXPORT = "data_export"
    BACKUP = "backup"
    ARCHIVE = "archive"

# Activity Types
class ActivityType(str, enum.Enum):
    """Types of activities."""
    # Basic Activities
    WARM_UP = "warm_up"
    COOL_DOWN = "cool_down"
    STRETCHING = "stretching"
    STRENGTH_TRAINING = "strength_training"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    COORDINATION = "coordination"
    
    # Sports Activities
    TEAM_SPORTS = "team_sports"
    INDIVIDUAL_SPORTS = "individual_sports"
    RACKET_SPORTS = "racket_sports"
    WATER_SPORTS = "water_sports"
    WINTER_SPORTS = "winter_sports"
    COMBAT_SPORTS = "combat_sports"
    
    # Fitness Activities
    HIIT = "hiit"
    CROSSFIT = "crossfit"
    YOGA = "yoga"
    PILATES = "pilates"
    DANCE = "dance"
    MARTIAL_ARTS = "martial_arts"
    
    # Recreational Activities
    GAMES = "games"
    PLAY = "play"
    OUTDOOR = "outdoor"
    ADVENTURE = "adventure"
    RECREATIONAL = "recreational"
    
    # Educational Activities
    SKILL_DEVELOPMENT = "skill_development"
    TECHNIQUE_PRACTICE = "technique_practice"
    DRILLS = "drills"
    EXERCISES = "exercises"
    ASSESSMENTS = "assessments"
    
    # Therapeutic Activities
    REHABILITATION = "rehabilitation"
    PREHABILITATION = "prehabilitation"
    THERAPEUTIC = "therapeutic"
    RECOVERY = "recovery"
    REGENERATION = "regeneration"
    
    # Movement Activities
    MOBILITY = "mobility"
    STABILITY = "stability"
    POSTURE = "posture"
    MOVEMENT = "movement"
    SKILL = "skill"
    TECHNIQUE = "technique"
    
    # Session Components
    MAINTENANCE = "maintenance"
    PREVENTION = "prevention"
    CORRECTION = "correction"
    ADAPTATION = "adaptation"
    PROGRESSION = "progression"
    REGRESSION = "regression"
    
    # Other Activities
    MODIFICATION = "modification"
    VARIATION = "variation"
    ALTERNATIVE = "alternative"
    SUBSTITUTE = "substitute"
    OTHER = "other"

# Activity Level Types
class ActivityLevel(str, enum.Enum):
    """Levels of activities."""
    # Basic Levels
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    
    # Achievement Levels
    NOVICE = "novice"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    MASTERY = "mastery"
    
    # Performance Levels
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    OPTIMAL = "optimal"
    
    # Challenge Levels
    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"
    DIFFICULT = "difficult"
    
    # Progress Levels
    INITIAL = "initial"
    PROGRESSING = "progressing"
    ACHIEVED = "achieved"
    EXCEEDED = "exceeded"
    
    # Fitness Levels
    UNFIT = "unfit"
    AVERAGE = "average"
    FIT = "fit"
    ATHLETIC = "athletic"
    
    # Health Levels
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"

__all__ = [
    'ActivityType',
    'ActivityLevel',
    'ActivityCategory',
    'ActivityCategoryType',
    'ActivityDifficulty',
    'ActivityStatus',
    'ActivityFormat',
    'ActivityGoal',
    'StudentType',
    'StudentStatus',
    'StudentLevel',
    'StudentCategory',
    'Gender',
    'FitnessLevel',
    'FitnessCategory',
    'MealType',
    'NutritionCategory',
    'NutritionGoal',
    'GoalStatus',
    'GoalCategory',
    'GoalTimeframe',
    'GoalType',
    'GoalLevel',
    'GoalTrigger',
    'GoalAdjustment',
    'ClassType',
    'ClassStatus',
    'RoutineStatus',
    'RoutineType',
    'RoutineLevel',
    'RoutineTrigger',
    'AssessmentType',
    'ProgressType',
    'ProgressStatus',
    'ProgressLevel',
    'ProgressTrigger',
    'AssessmentStatus',
    'AssessmentLevel',
    'AnalysisLevel',
    'AnalysisTrigger',
    'AssessmentTrigger',
    'AssessmentResult',
    'CriteriaType',
    'ChangeType',
    'SafetyType',
    'IncidentType',
    'IncidentSeverity',
    'AlertType',
    'CheckType',
    'ExerciseType',
    'ExerciseDifficulty',
    'WorkoutType',
    'EquipmentType',
    'EquipmentStatus',
    'MovementType',
    'DifficultyLevel',
    'ProgressionLevel',
    'EquipmentRequirement',
    'AnalysisType',
    'AnalysisStatus',
    'ConfidenceLevel',
    'PerformanceLevel',
    'VisualizationType',
    'VisualizationLevel',
    'VisualizationStatus',
    'VisualizationTrigger',
    'ChartType',
    'ColorScheme',
    'InteractionMode',
    'CompressionType',
    'DataFormat',
    'CollaborationType',
    'CollaborationLevel',
    'CollaborationStatus',
    'CollaborationTrigger',
    'AccessLevel',
    'SharingStatus',
    'NotificationType',
    'AdaptationType',
    'AdaptationLevel',
    'AdaptationStatus',
    'AdaptationTrigger',
    'RateLimitType',
    'RateLimitLevel',
    'RateLimitStatus',
    'RateLimitTrigger',
    'CacheType',
    'CacheLevel',
    'CacheStatus',
    'CacheTrigger',
    'CircuitBreakerType',
    'CircuitBreakerLevel',
    'CircuitBreakerStatus',
    'CircuitBreakerTrigger',
    'RiskLevel',
    'SkillLevel',
    'PlanningType',
    'PlanningLevel',
    'PlanningStatus',
    'PlanningTrigger',
    'TrackingType',
    'TrackingLevel',
    'TrackingStatus',
    'TrackingTrigger',
    'MetricType',
    'MetricLevel',
    'MetricStatus',
    'MetricTrigger',
    'SafetyLevel',
    'SafetyStatus',
    'SafetyTrigger',
    'IncidentLevel',
    'IncidentStatus',
    'IncidentTrigger',
    'RiskType',
    'RiskStatus',
    'RiskTrigger',
    'HealthMetricType',
    'HealthMetricLevel',
    'HealthMetricStatus',
    'HealthMetricTrigger',
    'SafetyCheckType',
    'SafetyCheckLevel',
    'SafetyCheckStatus',
    'SafetyCheckTrigger',
    'MeasurementUnit'
]
