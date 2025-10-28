"""
Base schemas for the Faraday AI application.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator

from app.core.validators import (
    validate_achievements,
    validate_categories,
    validate_equipment_needed,
    validate_goals,
    validate_ingredients,
    validate_instructions,
    validate_measurements,
    validate_metadata,
    validate_notes,
    validate_nutritional_info,
    validate_safety_precautions,
    validate_tags,
    validate_target_audience,
    validate_target_muscle_groups,
)

# Type variables
T = TypeVar('T')

class BaseSchema(BaseModel):
    """Base schema with common fields and methods."""
    
    class Config:
        """Pydantic config."""
        orm_mode = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }

class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class UUIDSchema(BaseSchema):
    """Schema with UUID field."""
    uuid: UUID = Field(default_factory=UUID)

class MetadataSchema(BaseSchema):
    """Schema with metadata field."""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("metadata")
    def validate_metadata(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata."""
        return validate_metadata(v)

class TagSchema(BaseSchema):
    """Schema with tags field."""
    tags: List[str] = Field(default_factory=list)

    @validator("tags")
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags."""
        return validate_tags(v)

class CategorySchema(BaseSchema):
    """Schema with categories field."""
    categories: List[str] = Field(default_factory=list)

    @validator("categories")
    def validate_categories(cls, v: List[str]) -> List[str]:
        """Validate categories."""
        return validate_categories(v)

class NoteSchema(BaseSchema):
    """Schema with notes field."""
    notes: str = Field(default="")

    @validator("notes")
    def validate_notes(cls, v: str) -> str:
        """Validate notes."""
        return validate_notes(v)

class InstructionSchema(BaseSchema):
    """Schema with instructions field."""
    instructions: List[str] = Field(default_factory=list)

    @validator("instructions")
    def validate_instructions(cls, v: List[str]) -> List[str]:
        """Validate instructions."""
        return validate_instructions(v)

class SafetyPrecautionSchema(BaseSchema):
    """Schema with safety precautions field."""
    safety_precautions: List[str] = Field(default_factory=list)

    @validator("safety_precautions")
    def validate_safety_precautions(cls, v: List[str]) -> List[str]:
        """Validate safety precautions."""
        return validate_safety_precautions(v)

class MuscleGroupSchema(BaseSchema):
    """Schema with target muscle groups field."""
    target_muscle_groups: List[str] = Field(default_factory=list)

    @validator("target_muscle_groups")
    def validate_target_muscle_groups(cls, v: List[str]) -> List[str]:
        """Validate target muscle groups."""
        return validate_target_muscle_groups(v)

class EquipmentSchema(BaseSchema):
    """Schema with equipment needed field."""
    equipment_needed: List[str] = Field(default_factory=list)

    @validator("equipment_needed")
    def validate_equipment_needed(cls, v: List[str]) -> List[str]:
        """Validate equipment needed."""
        return validate_equipment_needed(v)

class AudienceSchema(BaseSchema):
    """Schema with target audience field."""
    target_audience: List[str] = Field(default_factory=list)

    @validator("target_audience")
    def validate_target_audience(cls, v: List[str]) -> List[str]:
        """Validate target audience."""
        return validate_target_audience(v)

class IngredientSchema(BaseSchema):
    """Schema with ingredients field."""
    ingredients: List[Dict[str, Any]] = Field(default_factory=list)

    @validator("ingredients")
    def validate_ingredients(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate ingredients."""
        return validate_ingredients(v)

class NutritionalInfoSchema(BaseSchema):
    """Schema with nutritional information field."""
    nutritional_info: Dict[str, float] = Field(default_factory=dict)

    @validator("nutritional_info")
    def validate_nutritional_info(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate nutritional information."""
        return validate_nutritional_info(v)

class MeasurementSchema(BaseSchema):
    """Schema with measurements field."""
    measurements: Dict[str, float] = Field(default_factory=dict)

    @validator("measurements")
    def validate_measurements(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate measurements."""
        return validate_measurements(v)

class GoalSchema(BaseSchema):
    """Schema with goals field."""
    goals: List[Dict[str, Any]] = Field(default_factory=list)

    @validator("goals")
    def validate_goals(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate goals."""
        return validate_goals(v)

class AchievementSchema(BaseSchema):
    """Schema with achievements field."""
    achievements: List[Dict[str, Any]] = Field(default_factory=list)

    @validator("achievements")
    def validate_achievements(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate achievements."""
        return validate_achievements(v)

class BaseResponseSchema(BaseSchema):
    """Base response schema."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class BaseCreateSchema(BaseSchema):
    """Base create schema."""
    pass

class BaseUpdateSchema(BaseSchema):
    """Base update schema."""
    pass

class BaseFilterSchema(BaseSchema):
    """Base filter schema."""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(None, pattern="^(asc|desc)$")
    search: Optional[str] = None

class BaseSearchSchema(BaseSchema):
    """Base search schema."""
    query: str
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(None, pattern="^(asc|desc)$")

class BaseExportSchema(BaseSchema):
    """Base export schema."""
    format: str = Field(..., pattern="^(csv|json|excel)$")
    fields: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None

class BaseImportSchema(BaseSchema):
    """Base import schema."""
    format: str = Field(..., pattern="^(csv|json|excel)$")
    file: bytes
    options: Optional[Dict[str, Any]] = None

class BaseAuditSchema(BaseSchema):
    """Base audit schema."""
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

class BaseVersionSchema(BaseSchema):
    """Base version schema."""
    version: int = Field(default=1, ge=1)
    is_latest: bool = Field(default=True)
    previous_version: Optional[int] = None

class BaseStatusSchema(BaseSchema):
    """Base status schema."""
    is_active: bool = Field(default=True)
    status: str = Field(default="active")
    status_reason: Optional[str] = None
    status_updated_at: Optional[datetime] = None
    status_updated_by: Optional[int] = None

class BasePrioritySchema(BaseSchema):
    """Base priority schema."""
    priority: int = Field(default=0, ge=0, le=100)
    priority_reason: Optional[str] = None
    priority_updated_at: Optional[datetime] = None
    priority_updated_by: Optional[int] = None

class BaseOrderSchema(BaseSchema):
    """Base order schema."""
    order: int = Field(default=0, ge=0)
    order_updated_at: Optional[datetime] = None
    order_updated_by: Optional[int] = None

class BaseSlugSchema(BaseSchema):
    """Base slug schema."""
    slug: str
    slug_updated_at: Optional[datetime] = None
    slug_updated_by: Optional[int] = None

class BaseCodeSchema(BaseSchema):
    """Base code schema."""
    code: str
    code_updated_at: Optional[datetime] = None
    code_updated_by: Optional[int] = None

class BaseExternalIDSchema(BaseSchema):
    """Base external ID schema."""
    external_id: str
    external_id_updated_at: Optional[datetime] = None
    external_id_updated_by: Optional[int] = None

# Validation Schemas
class ValidationSchema(BaseSchema):
    """Schema with validation fields."""
    is_valid: bool = Field(default=True)
    validation_errors: List[Dict[str, Any]] = Field(default_factory=list)
    validation_warnings: List[Dict[str, Any]] = Field(default_factory=list)
    validated_at: Optional[datetime] = None
    validated_by: Optional[int] = None

    @root_validator
    def validate_all(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all fields."""
        errors = []
        warnings = []
        
        # Add validation logic here
        
        values["validation_errors"] = errors
        values["validation_warnings"] = warnings
        values["is_valid"] = len(errors) == 0
        
        return values

# Relationship Schemas
class RelationshipSchema(BaseSchema):
    """Schema with relationship fields."""
    parent_id: Optional[int] = None
    parent_type: Optional[str] = None
    child_ids: List[int] = Field(default_factory=list)
    child_types: List[str] = Field(default_factory=list)
    relationship_type: Optional[str] = None
    relationship_metadata: Dict[str, Any] = Field(default_factory=dict)

# State Schemas
class StateSchema(BaseSchema):
    """Schema with state fields."""
    state: str = Field(default="draft")
    state_history: List[Dict[str, Any]] = Field(default_factory=list)
    state_metadata: Dict[str, Any] = Field(default_factory=dict)
    state_updated_at: Optional[datetime] = None
    state_updated_by: Optional[int] = None

    @validator("state")
    def validate_state(cls, v: str) -> str:
        """Validate state."""
        valid_states = ["draft", "active", "inactive", "archived", "deleted"]
        if v not in valid_states:
            raise ValueError(f"Invalid state: {v}. Must be one of {valid_states}")
        return v

# Audit Schemas
class AuditSchema(BaseSchema):
    """Schema with audit fields."""
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)

# Export/Import Schemas
class ExportSchema(BaseSchema):
    """Schema with export fields."""
    format: str = Field(..., pattern="^(csv|json|excel|pdf)$")
    fields: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    export_metadata: Dict[str, Any] = Field(default_factory=dict)

class ImportSchema(BaseSchema):
    """Schema with import fields."""
    format: str = Field(..., pattern="^(csv|json|excel)$")
    file: bytes
    options: Optional[Dict[str, Any]] = None
    import_metadata: Dict[str, Any] = Field(default_factory=dict)
    validation_rules: Optional[Dict[str, Any]] = None

# Search Schemas
class SearchSchema(BaseSchema):
    """Schema with search fields."""
    query: str
    fields: List[str] = Field(default_factory=list)
    filters: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    search_metadata: Dict[str, Any] = Field(default_factory=dict)

# Filter Schemas
class FilterSchema(BaseSchema):
    """Schema with filter fields."""
    filters: Dict[str, Any] = Field(default_factory=dict)
    operators: Dict[str, str] = Field(default_factory=dict)
    options: Optional[Dict[str, Any]] = None
    filter_metadata: Dict[str, Any] = Field(default_factory=dict)

# Response Schemas
class ResponseSchema(BaseSchema, Generic[T]):
    """Schema with response fields."""
    data: Optional[T] = None
    message: Optional[str] = None
    status: str = Field(default="success")
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PaginatedResponseSchema(ResponseSchema[T]):
    """Schema with paginated response fields."""
    total: int = Field(default=0)
    page: int = Field(default=1)
    per_page: int = Field(default=10)
    total_pages: int = Field(default=1)
    has_next: bool = Field(default=False)
    has_prev: bool = Field(default=False)

# Error Schemas
class ErrorSchema(BaseSchema):
    """Schema with error fields."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    error_metadata: Dict[str, Any] = Field(default_factory=dict)

# Success Schemas
class SuccessSchema(BaseSchema):
    """Schema with success fields."""
    message: str
    details: Optional[Dict[str, Any]] = None
    success_metadata: Dict[str, Any] = Field(default_factory=dict) 