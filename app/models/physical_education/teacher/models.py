"""
Teacher Models

This module defines teacher models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Boolean, Enum, Date
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    Gender,
    CertificationType
)
from app.models.physical_education.class_.models import PhysicalEducationClass
from app.models.physical_education.teacher.enums import SpecializationType

# Re-export for backward compatibility
BaseModelMixin = SharedBase
TimestampMixin = TimestampedMixin

class PhysicalEducationTeacher(SharedBase, TimestampedMixin):
    """Model for physical education teachers."""
    __tablename__ = "physical_education_teachers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20))
    specialization = Column(String, nullable=True)
    certification = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    teacher_metadata = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("app.models.core.user.User", back_populates="physical_education_teacher")
    certifications = relationship("app.models.physical_education.teacher.models.TeacherCertification", back_populates="teacher")
    # classes = relationship("PhysicalEducationClass", back_populates="teacher")
    schedules = relationship("TeacherSchedule", back_populates="teacher")
    qualifications = relationship("TeacherQualification", back_populates="teacher")
    availability = relationship("TeacherAvailability", back_populates="teacher")
    preferences = relationship("TeacherPreference", back_populates="teacher")
    specializations = relationship("TeacherSpecialization", back_populates="teacher")

class TeacherSchedule(BaseModelMixin, TimestampMixin):
    """Model for teacher schedules."""
    
    __tablename__ = "teacher_schedules"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("physical_education_teachers.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("physical_education_classes.id"), nullable=False)
    schedule_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="SCHEDULED")
    schedule_notes = Column(Text)
    schedule_metadata = Column(JSON)
    
    # Relationships
    teacher = relationship("app.models.physical_education.teacher.models.PhysicalEducationTeacher", back_populates="schedules")
    physical_education_class = relationship("app.models.physical_education.class_.models.PhysicalEducationClass")

class TeacherQualification(BaseModelMixin, TimestampMixin):
    """Model for teacher qualifications."""
    
    __tablename__ = "teacher_qualifications"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("physical_education_teachers.id"), nullable=False)
    qualification_name = Column(String(100), nullable=False)
    issuing_organization = Column(String(100))
    issue_date = Column(DateTime)
    expiry_date = Column(DateTime)
    qualification_notes = Column(Text)
    qualification_metadata = Column(JSON)
    
    # Relationships
    teacher = relationship("app.models.physical_education.teacher.models.PhysicalEducationTeacher", back_populates="qualifications")

class TeacherCertification(BaseModelMixin, TimestampMixin):
    """Model for teacher certifications."""
    
    __tablename__ = "teacher_certifications"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("physical_education_teachers.id"), nullable=False)
    type = Column(Enum(CertificationType, name='certification_type_enum'), nullable=False)
    certification_number = Column(String(50), nullable=False)
    issue_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    issuing_organization = Column(String(100), nullable=False)
    certification_metadata = Column(JSON)
    
    # Relationships
    teacher = relationship("app.models.physical_education.teacher.models.PhysicalEducationTeacher", back_populates="certifications")

class TeacherAvailability(BaseModelMixin, TimestampMixin):
    """Model for teacher availability."""
    
    __tablename__ = "teacher_availability"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("physical_education_teachers.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0-6 for Monday-Sunday
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, default=True)
    availability_metadata = Column(JSON)
    
    # Relationships
    teacher = relationship("app.models.physical_education.teacher.models.PhysicalEducationTeacher", back_populates="availability")

class TeacherPreference(BaseModelMixin, TimestampMixin):
    """Model for teacher preferences."""
    
    __tablename__ = "teacher_preferences"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("physical_education_teachers.id"), nullable=False)
    preference_type = Column(String(50), nullable=False)
    preference_value = Column(String(100), nullable=False)
    preference_metadata = Column(JSON)
    
    # Relationships
    teacher = relationship("app.models.physical_education.teacher.models.PhysicalEducationTeacher", back_populates="preferences")

# Pydantic models for API
class PhysicalEducationTeacherCreate(BaseModel):
    """Pydantic model for creating teachers."""
    
    user_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    specialization: Optional[SpecializationType] = None
    certification: Optional[str] = None
    years_experience: Optional[int] = None
    teacher_metadata: Optional[dict] = None

class PhysicalEducationTeacherUpdate(BaseModel):
    """Pydantic model for updating teachers."""
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    specialization: Optional[SpecializationType] = None
    certification: Optional[str] = None
    years_experience: Optional[int] = None
    teacher_metadata: Optional[dict] = None

class PhysicalEducationTeacherResponse(BaseModel):
    """Pydantic model for teacher responses."""
    
    id: int
    user_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    specialization: Optional[SpecializationType] = None
    certification: Optional[str] = None
    years_experience: Optional[int] = None
    teacher_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TeacherCertificationBase(BaseModelMixin, TimestampMixin):
    """Base class for teacher certification models."""
    __tablename__ = "teacher_certification_base"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    type = Column(Enum(CertificationType, name='certification_type_enum'), nullable=False)
    name = Column(String(100), nullable=False)
    issuing_organization = Column(String(100), nullable=False)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    teacher_id = Column(Integer, ForeignKey('physical_education_teachers.id'), nullable=False)

class TeacherCertificationCreate(BaseModel):
    """Pydantic model for creating teacher certifications."""
    
    type: CertificationType
    name: str
    issuing_organization: str
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    teacher_id: int

class TeacherCertificationUpdate(BaseModel):
    """Pydantic model for updating teacher certifications."""
    
    type: Optional[CertificationType] = None
    name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None

class TeacherCertificationResponse(BaseModel):
    """Pydantic model for teacher certification responses."""
    
    id: int
    type: CertificationType
    name: str
    issuing_organization: str
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    teacher_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TeacherSpecialization(BaseModelMixin, TimestampMixin):
    """Model for teacher specializations."""
    __tablename__ = "teacher_specializations"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("physical_education_teachers.id"), nullable=False)
    specialization_name = Column(String(100), nullable=False)
    description = Column(Text)
    years_experience = Column(Integer)
    specialization_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    teacher = relationship("app.models.physical_education.teacher.models.PhysicalEducationTeacher", back_populates="specializations") 