from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean, Float, Integer, Enum, Date
from sqlalchemy.orm import relationship
from app.core.database import Base
from .student_types import Gender, FitnessLevel
from pydantic import BaseModel, Field, validator, EmailStr

class Student(Base):
    """Model for students."""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    fitness_level = Column(Enum(FitnessLevel), nullable=False)
    medical_notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    safety_incidents = relationship("SafetyIncident", back_populates="student", cascade="all, delete-orphan")
    activity_performances = relationship("StudentActivityPerformance", back_populates="student", cascade="all, delete-orphan")
    activity_preferences = relationship("StudentActivityPreference", back_populates="student", cascade="all, delete-orphan")
    activity_progressions = relationship("ActivityProgression", back_populates="student", cascade="all, delete-orphan")
    activity_plans = relationship("ActivityPlan", back_populates="student", cascade="all, delete-orphan")
    classes = relationship("ClassStudent", back_populates="student", cascade="all, delete-orphan")
    movement_analyses = relationship("MovementAnalysis", back_populates="student", cascade="all, delete-orphan")
    skill_assessments = relationship("SkillAssessment", back_populates="student", cascade="all, delete-orphan")
    assessments = relationship("SkillAssessment", back_populates="student")
    performances = relationship("RoutinePerformance", back_populates="student")

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}>"

class StudentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    date_of_birth: datetime
    gender: Gender
    fitness_level: FitnessLevel
    medical_notes: Optional[str] = Field(None, max_length=500)

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

    @validator('medical_notes')
    def validate_medical_notes(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Medical notes cannot be empty or whitespace')
        return v.strip() if v else v

    @validator('date_of_birth')
    def validate_age(cls, v):
        age = (datetime.now() - v).days / 365
        if age < 5 or age > 18:
            raise ValueError('Student must be between 5 and 18 years old')
        return v

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[Gender] = None
    fitness_level: Optional[FitnessLevel] = None
    medical_notes: Optional[str] = Field(None, max_length=500)

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip() if v else v

    @validator('medical_notes')
    def validate_medical_notes(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Medical notes cannot be empty or whitespace')
        return v.strip() if v else v

    @validator('date_of_birth')
    def validate_age(cls, v):
        if v is not None:
            age = (datetime.now() - v).days / 365
            if age < 5 or age > 18:
                raise ValueError('Student must be between 5 and 18 years old')
        return v

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 