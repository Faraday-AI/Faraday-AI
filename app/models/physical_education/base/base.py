"""
Base Models

This module defines base Pydantic models for physical education models.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict

class BaseResponseModel(BaseModel):
    """Base model for all response models."""
    id: int
    uuid: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    extra_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class BaseCreateModel(BaseModel):
    """Base model for all create models."""
    extra_data: Optional[Dict[str, Any]] = None

    @field_validator('extra_data')
    @classmethod
    def validate_extra_data(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('extra_data must be a dictionary')
        return v

class BaseUpdateModel(BaseModel):
    """Base model for all update models."""
    is_active: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None

    @field_validator('extra_data')
    @classmethod
    def validate_extra_data(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError('extra_data must be a dictionary')
        return v

def validate_string_field(value: Optional[str], field_name: str) -> Optional[str]:
    """Validate string fields to ensure they are not empty or just whitespace."""
    if value is not None and not value.strip():
        raise ValueError(f'{field_name} cannot be empty or whitespace')
    return value.strip() if value else value

def validate_list_field(value: Optional[List], field_name: str) -> Optional[List]:
    """Validate list fields to ensure they are not empty."""
    if value is not None and len(value) == 0:
        raise ValueError(f'{field_name} cannot be empty')
    return value

def validate_dict_field(value: Optional[Dict], field_name: str) -> Optional[Dict]:
    """Validate dictionary fields to ensure they are not empty."""
    if value is not None and len(value) == 0:
        raise ValueError(f'{field_name} cannot be empty')
    return value 