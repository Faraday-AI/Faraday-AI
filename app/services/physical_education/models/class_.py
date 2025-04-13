from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean, Integer, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.services.physical_education.models.class_types import ClassStatus
from pydantic import BaseModel, Field, validator

class Class(Base):
    """Model for physical education classes."""
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    grade_level = Column(String, nullable=False)
    max_students = Column(Integer, nullable=False)
    schedule = Column(JSON, nullable=False)  # Contains day, time, duration
    location = Column(String, nullable=False)
    status = Column(Enum(ClassStatus), nullable=False, default=ClassStatus.PLANNED)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    routines = relationship("Routine", back_populates="class_", cascade="all, delete-orphan")
    students = relationship("ClassStudent", back_populates="class_", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Class {self.name} - {self.grade_level}>"

class ClassStudent(Base):
    """Model for student enrollment in classes."""
    __tablename__ = "class_students"

    id = Column(String, primary_key=True)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    enrollment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    class_ = relationship("Class", back_populates="students")
    student = relationship("Student", back_populates="classes")

    def __repr__(self):
        return f"<ClassStudent {self.class_id} - {self.student_id}>"

class ClassBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: ClassStatus = ClassStatus.PLANNED
    max_students: int = Field(..., gt=0, le=50)  # Max 50 students per class
    start_date: datetime
    end_date: datetime

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or whitespace')
        return v.strip() if v else v

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
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

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip() if v else v

    @validator('description')
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or whitespace')
        return v.strip() if v else v

    @validator('end_date')
    def validate_dates(cls, v, values):
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v

class ClassResponse(ClassBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 