"""
Beta Students Model

Independent student table for the beta teacher system.
This table is completely separate from the main district system's students table
to maintain independence and avoid conflicts.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.shared_base import SharedBase as Base

# Import enums from student models
from app.models.physical_education.student.models import (
    GradeLevel, Gender, StudentStatus, StudentLevel, StudentCategory
)

import uuid


class BetaStudent(Base):
    """Student model for beta teacher system - independent from district students"""
    __tablename__ = 'beta_students'
    __table_args__ = (
        Index('idx_beta_students_email', 'email'),
        Index('idx_beta_students_teacher', 'created_by_teacher_id'),
        {'extend_existing': True}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by_teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id", ondelete="CASCADE"), nullable=False)
    
    # Basic Information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(Enum(Gender, name='beta_student_gender_enum'))
    
    # Academic Information
    grade_level = Column(Enum(GradeLevel, name='beta_student_grade_level_enum'), nullable=False)
    status = Column(Enum(StudentStatus, name='beta_student_status_enum'), default=StudentStatus.ACTIVE)
    level = Column(Enum(StudentLevel, name='beta_student_level_enum'), default=StudentLevel.BEGINNER)
    category = Column(Enum(StudentCategory, name='beta_student_category_enum'), default=StudentCategory.REGULAR)
    
    # Physical Information
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    
    # Health & Safety Information
    medical_conditions = Column(Text, nullable=True)
    emergency_contact = Column(String(100), nullable=True)
    
    # Parent/Guardian Information
    parent_name = Column(String(100), nullable=True)
    parent_phone = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="beta_students")
    
    def __repr__(self):
        return f"<BetaStudent {self.first_name} {self.last_name} (ID: {self.id})>"

