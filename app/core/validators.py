"""
Validation functions for the Faraday AI application.
"""

import re
import json
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union, Type
from uuid import UUID
import hashlib
import base64
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column

from app.models.core.core_models import (
    Region,
    ServiceStatus,
    DeploymentStatus,
    FeatureFlagType,
    FeatureFlagStatus,
    ABTestType,
    ABTestStatus,
    AlertSeverity,
    AlertStatus,
    CircuitBreakerState
)

from app.core.enums import (
    ActivityType,
    AssessmentStatus,
    AssessmentType,
    CertificationType,
    ClassType,
    DifficultyLevel,
    EquipmentRequirement,
    EquipmentStatus,
    ExerciseDifficulty,
    ExerciseType,
    FitnessCategory,
    Gender,
    GradeLevel,
    IncidentSeverity,
    IncidentType,
    MealType,
    NutritionGoal,
    PerformanceLevel,
    ProgressStatus,
    ProgressType,
    ProgressionLevel,
    RoutineType,
    SkillLevel,
    StudentType,
    UserRole,
    UserStatus,
)

def validate_string_field(value: str, field_name: str) -> str:
    """Validate string fields."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value.strip()

def validate_list_field(value: List[Any], field_name: str) -> List[Any]:
    """Validate list fields."""
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    return value

def validate_dict_field(value: Dict[str, Any], field_name: str) -> Dict[str, Any]:
    """Validate dictionary fields."""
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    return value

def validate_email(email: str) -> str:
    """Validate email format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    return email.lower()

def validate_phone_number(phone: str) -> str:
    """Validate phone number format."""
    phone_pattern = r'^\+?1?\d{9,15}$'
    if not re.match(phone_pattern, phone):
        raise ValueError("Invalid phone number format")
    return phone

def validate_date_range(start_date: date, end_date: date) -> None:
    """Validate date range."""
    if start_date > end_date:
        raise ValueError("Start date must be before end date")

def validate_age(birth_date: date, min_age: int = 0, max_age: int = 120) -> None:
    """Validate age based on birth date."""
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if not min_age <= age <= max_age:
        raise ValueError(f"Age must be between {min_age} and {max_age} years")

def validate_enum_value(value: Any, enum_class: type) -> Any:
    """Validate enum values."""
    if not isinstance(value, enum_class):
        try:
            return enum_class(value)
        except ValueError:
            raise ValueError(f"Invalid value for {enum_class.__name__}")
    return value

def validate_uuid(value: Union[str, UUID]) -> UUID:
    """Validate UUID format."""
    if isinstance(value, str):
        try:
            return UUID(value)
        except ValueError:
            raise ValueError("Invalid UUID format")
    return value

def validate_percentage(value: float) -> float:
    """Validate percentage values."""
    if not 0 <= value <= 100:
        raise ValueError("Percentage must be between 0 and 100")
    return value

def validate_positive_number(value: float) -> float:
    """Validate positive numbers."""
    if value <= 0:
        raise ValueError("Value must be positive")
    return value

def validate_non_negative_number(value: float) -> float:
    """Validate non-negative numbers."""
    if value < 0:
        raise ValueError("Value must be non-negative")
    return value

def validate_time_duration(minutes: int) -> int:
    """Validate time duration in minutes."""
    if not 0 < minutes <= 480:  # 8 hours max
        raise ValueError("Duration must be between 1 and 480 minutes")
    return minutes

def validate_grade_level(grade: str) -> str:
    """Validate grade level."""
    return validate_enum_value(grade, GradeLevel)

def validate_gender(gender: str) -> str:
    """Validate gender."""
    return validate_enum_value(gender, Gender)

def validate_user_role(role: str) -> str:
    """Validate user role."""
    return validate_enum_value(role, UserRole)

def validate_user_status(status: str) -> str:
    """Validate user status."""
    return validate_enum_value(status, UserStatus)

def validate_activity_type(activity_type: str) -> str:
    """Validate activity type."""
    return validate_enum_value(activity_type, ActivityType)

def validate_difficulty_level(difficulty: str) -> str:
    """Validate difficulty level."""
    return validate_enum_value(difficulty, DifficultyLevel)

def validate_assessment_type(assessment_type: str) -> str:
    """Validate assessment type."""
    return validate_enum_value(assessment_type, AssessmentType)

def validate_assessment_status(status: str) -> str:
    """Validate assessment status."""
    return validate_enum_value(status, AssessmentStatus)

def validate_equipment_status(status: str) -> str:
    """Validate equipment status."""
    return validate_enum_value(status, EquipmentStatus)

def validate_incident_type(incident_type: str) -> str:
    """Validate incident type."""
    return validate_enum_value(incident_type, IncidentType)

def validate_incident_severity(severity: str) -> str:
    """Validate incident severity."""
    return validate_enum_value(severity, IncidentSeverity)

def validate_certification_type(cert_type: str) -> str:
    """Validate certification type."""
    return validate_enum_value(cert_type, CertificationType)

def validate_meal_type(meal_type: str) -> str:
    """Validate meal type."""
    return validate_enum_value(meal_type, MealType)

def validate_nutrition_goal(goal: str) -> str:
    """Validate nutrition goal."""
    return validate_enum_value(goal, NutritionGoal)

def validate_progress_type(progress_type: str) -> str:
    """Validate progress type."""
    return validate_enum_value(progress_type, ProgressType)

def validate_progress_status(status: str) -> str:
    """Validate progress status."""
    return validate_enum_value(status, ProgressStatus)

def validate_exercise_type(exercise_type: str) -> str:
    """Validate exercise type."""
    return validate_enum_value(exercise_type, ExerciseType)

def validate_exercise_difficulty(difficulty: str) -> str:
    """Validate exercise difficulty."""
    return validate_enum_value(difficulty, ExerciseDifficulty)

def validate_routine_type(routine_type: str) -> str:
    """Validate routine type."""
    return validate_enum_value(routine_type, RoutineType)

def validate_student_type(student_type: str) -> str:
    """Validate student type."""
    return validate_enum_value(student_type, StudentType)

def validate_equipment_requirement(requirement: str) -> str:
    """Validate equipment requirement."""
    return validate_enum_value(requirement, EquipmentRequirement)

def validate_fitness_category(category: str) -> str:
    """Validate fitness category."""
    return validate_enum_value(category, FitnessCategory)

def validate_skill_level(level: str) -> str:
    """Validate skill level."""
    return validate_enum_value(level, SkillLevel)

def validate_performance_level(level: str) -> str:
    """Validate performance level."""
    return validate_enum_value(level, PerformanceLevel)

def validate_progression_level(level: str) -> str:
    """Validate progression level."""
    return validate_enum_value(level, ProgressionLevel)

def validate_region(region: str) -> str:
    """Validate region."""
    return validate_enum_value(region, Region)

def validate_environment(env: str) -> str:
    """Validate environment."""
    return validate_enum_value(env, Environment)

def validate_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate metadata dictionary."""
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary")
    return metadata

def validate_tags(tags: List[str]) -> List[str]:
    """Validate tags list."""
    if not isinstance(tags, list):
        raise ValueError("Tags must be a list")
    return [tag.strip() for tag in tags if tag.strip()]

def validate_categories(categories: List[str]) -> List[str]:
    """Validate categories list."""
    if not isinstance(categories, list):
        raise ValueError("Categories must be a list")
    return [category.strip() for category in categories if category.strip()]

def validate_notes(notes: str) -> str:
    """Validate notes field."""
    if not notes:
        return ""
    return notes.strip()

def validate_instructions(instructions: List[str]) -> List[str]:
    """Validate instructions list."""
    if not isinstance(instructions, list):
        raise ValueError("Instructions must be a list")
    return [instruction.strip() for instruction in instructions if instruction.strip()]

def validate_safety_precautions(precautions: List[str]) -> List[str]:
    """Validate safety precautions list."""
    if not isinstance(precautions, list):
        raise ValueError("Safety precautions must be a list")
    return [precaution.strip() for precaution in precautions if precaution.strip()]

def validate_target_muscle_groups(muscles: List[str]) -> List[str]:
    """Validate target muscle groups list."""
    if not isinstance(muscles, list):
        raise ValueError("Target muscle groups must be a list")
    return [muscle.strip() for muscle in muscles if muscle.strip()]

def validate_equipment_needed(equipment: List[str]) -> List[str]:
    """Validate equipment needed list."""
    if not isinstance(equipment, list):
        raise ValueError("Equipment needed must be a list")
    return [item.strip() for item in equipment if item.strip()]

def validate_target_audience(audience: List[str]) -> List[str]:
    """Validate target audience list."""
    if not isinstance(audience, list):
        raise ValueError("Target audience must be a list")
    return [group.strip() for group in audience if group.strip()]

def validate_ingredients(ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate ingredients list."""
    if not isinstance(ingredients, list):
        raise ValueError("Ingredients must be a list")
    for ingredient in ingredients:
        if not isinstance(ingredient, dict):
            raise ValueError("Each ingredient must be a dictionary")
        if "name" not in ingredient or "amount" not in ingredient:
            raise ValueError("Each ingredient must have a name and amount")
    return ingredients

def validate_nutritional_info(info: Dict[str, float]) -> Dict[str, float]:
    """Validate nutritional information."""
    if not isinstance(info, dict):
        raise ValueError("Nutritional information must be a dictionary")
    required_fields = ["calories", "protein", "carbs", "fat"]
    for field in required_fields:
        if field not in info:
            raise ValueError(f"Missing required nutritional field: {field}")
        if not isinstance(info[field], (int, float)) or info[field] < 0:
            raise ValueError(f"Invalid value for {field}")
    return info

def validate_measurements(measurements: Dict[str, float]) -> Dict[str, float]:
    """Validate physical measurements."""
    if not isinstance(measurements, dict):
        raise ValueError("Measurements must be a dictionary")
    for key, value in measurements.items():
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"Invalid measurement value for {key}")
    return measurements

def validate_goals(goals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate goals list."""
    if not isinstance(goals, list):
        raise ValueError("Goals must be a list")
    for goal in goals:
        if not isinstance(goal, dict):
            raise ValueError("Each goal must be a dictionary")
        if "type" not in goal or "target" not in goal:
            raise ValueError("Each goal must have a type and target")
    return goals

def validate_achievements(achievements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate achievements list."""
    if not isinstance(achievements, list):
        raise ValueError("Achievements must be a list")
    for achievement in achievements:
        if not isinstance(achievement, dict):
            raise ValueError("Each achievement must be a dictionary")
        if "type" not in achievement or "date" not in achievement:
            raise ValueError("Each achievement must have a type and date")
    return achievements

# Input Validation
def validate_input_length(value: str, min_length: int = 0, max_length: int = None) -> str:
    """Validate input length."""
    if len(value) < min_length:
        raise ValueError(f"Input must be at least {min_length} characters long")
    if max_length and len(value) > max_length:
        raise ValueError(f"Input must be at most {max_length} characters long")
    return value

def validate_input_pattern(value: str, pattern: str, field_name: str) -> str:
    """Validate input against regex pattern."""
    if not re.match(pattern, value):
        raise ValueError(f"Invalid {field_name} format")
    return value

def validate_input_range(value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float]) -> Union[int, float]:
    """Validate input range."""
    if not min_value <= value <= max_value:
        raise ValueError(f"Value must be between {min_value} and {max_value}")
    return value

def validate_input_choice(value: Any, choices: List[Any]) -> Any:
    """Validate input against choices."""
    if value not in choices:
        raise ValueError(f"Value must be one of {choices}")
    return value

# Data Validation
def validate_json_string(value: str) -> Dict[str, Any]:
    """Validate JSON string."""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")

def validate_base64_string(value: str) -> str:
    """Validate base64 string."""
    try:
        base64.b64decode(value)
        return value
    except Exception:
        raise ValueError("Invalid base64 format")

def validate_hash_string(value: str, algorithm: str = "sha256") -> str:
    """Validate hash string."""
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    if not re.match(f"^[a-f0-9]{{{hashlib.new(algorithm).digest_size * 2}}}$", value.lower()):
        raise ValueError(f"Invalid {algorithm} hash format")
    return value

def validate_url(url: str) -> str:
    """Validate URL format."""
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError("Invalid URL format")
        return url
    except Exception:
        raise ValueError("Invalid URL format")

# Business Logic Validation
def validate_business_rule(value: Any, rule: callable, error_message: str) -> Any:
    """Validate business rule."""
    if not rule(value):
        raise ValueError(error_message)
    return value

def validate_dependency(value: Any, dependency: Any, error_message: str) -> Any:
    """Validate dependency."""
    if not dependency:
        raise ValueError(error_message)
    return value

def validate_constraint(value: Any, constraint: callable, error_message: str) -> Any:
    """Validate constraint."""
    if not constraint(value):
        raise ValueError(error_message)
    return value

def validate_condition(value: Any, condition: callable, error_message: str) -> Any:
    """Validate condition."""
    if not condition(value):
        raise ValueError(error_message)
    return value

# Security Validation
def validate_password_strength(password: str) -> str:
    """Validate password strength."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    return password

def validate_token_format(token: str) -> str:
    """Validate token format."""
    if not re.match(r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$", token):
        raise ValueError("Invalid token format")
    return token

def validate_api_key_format(key: str) -> str:
    """Validate API key format."""
    if not re.match(r"^[A-Za-z0-9]{32,}$", key):
        raise ValueError("Invalid API key format")
    return key

def validate_secret_format(secret: str) -> str:
    """Validate secret format."""
    if not re.match(r"^[A-Za-z0-9+/]{32,}={0,2}$", secret):
        raise ValueError("Invalid secret format")
    return secret

# Format Validation
def validate_date_format(value: str, format: str = "%Y-%m-%d") -> str:
    """Validate date format."""
    try:
        datetime.strptime(value, format)
        return value
    except ValueError:
        raise ValueError(f"Invalid date format. Expected {format}")

def validate_time_format(value: str, format: str = "%H:%M:%S") -> str:
    """Validate time format."""
    try:
        datetime.strptime(value, format)
        return value
    except ValueError:
        raise ValueError(f"Invalid time format. Expected {format}")

def validate_datetime_format(value: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Validate datetime format."""
    try:
        datetime.strptime(value, format)
        return value
    except ValueError:
        raise ValueError(f"Invalid datetime format. Expected {format}")

def validate_file_format(value: str, allowed_formats: List[str]) -> str:
    """Validate file format."""
    extension = value.lower().split(".")[-1]
    if extension not in allowed_formats:
        raise ValueError(f"Invalid file format. Allowed formats: {allowed_formats}")
    return value

# Relationship Validation
def validate_relationship_type(value: str, valid_types: List[str]) -> str:
    """Validate relationship type."""
    if value not in valid_types:
        raise ValueError(f"Invalid relationship type. Must be one of {valid_types}")
    return value

def validate_relationship_cardinality(value: str) -> str:
    """Validate relationship cardinality."""
    valid_cardinalities = ["one-to-one", "one-to-many", "many-to-one", "many-to-many"]
    if value not in valid_cardinalities:
        raise ValueError(f"Invalid relationship cardinality. Must be one of {valid_cardinalities}")
    return value

def validate_relationship_constraint(value: str) -> str:
    """Validate relationship constraint."""
    valid_constraints = ["required", "optional", "unique", "cascade"]
    if value not in valid_constraints:
        raise ValueError(f"Invalid relationship constraint. Must be one of {valid_constraints}")
    return value

def validate_relationship_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate relationship metadata."""
    required_fields = ["type", "cardinality", "constraint"]
    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"Missing required field in relationship metadata: {field}")
    return metadata

# State Validation
def validate_state_transition(current_state: str, new_state: str, valid_transitions: Dict[str, List[str]]) -> str:
    """Validate state transition."""
    if new_state not in valid_transitions.get(current_state, []):
        raise ValueError(f"Invalid state transition from {current_state} to {new_state}")
    return new_state

def validate_state_condition(state: str, condition: callable, error_message: str) -> str:
    """Validate state condition."""
    if not condition(state):
        raise ValueError(error_message)
    return state

def validate_state_constraint(state: str, constraint: callable, error_message: str) -> str:
    """Validate state constraint."""
    if not constraint(state):
        raise ValueError(error_message)
    return state

def validate_state_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate state metadata."""
    required_fields = ["previous_state", "transition_reason", "transitioned_by"]
    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"Missing required field in state metadata: {field}")
    return metadata

# Audit Validation
def validate_audit_action(action: str, valid_actions: List[str]) -> str:
    """Validate audit action."""
    if action not in valid_actions:
        raise ValueError(f"Invalid audit action. Must be one of {valid_actions}")
    return action

def validate_audit_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate audit metadata."""
    required_fields = ["action", "actor", "timestamp", "resource_type", "resource_id"]
    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"Missing required field in audit metadata: {field}")
    return metadata

def validate_audit_trail(trail: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate audit trail."""
    for entry in trail:
        validate_audit_metadata(entry)
    return trail

def validate_audit_constraint(constraint: Dict[str, Any]) -> Dict[str, Any]:
    """Validate audit constraint."""
    required_fields = ["type", "condition", "action"]
    for field in required_fields:
        if field not in constraint:
            raise ValueError(f"Missing required field in audit constraint: {field}")
    return constraint 