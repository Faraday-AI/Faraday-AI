from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.physical_education.pe_enums.class_types import ClassStatus

class ClassBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: ClassStatus = ClassStatus.PLANNED
    max_students: int = Field(..., gt=0, le=50)  # Max 50 students per class
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or whitespace')
        return v.strip() if v else v

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, values):
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[ClassStatus] = None
    max_students: Optional[int] = Field(None, gt=0, le=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip() if v else v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or whitespace')
        return v.strip() if v else v

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, values):
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v

class ClassResponse(ClassBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 