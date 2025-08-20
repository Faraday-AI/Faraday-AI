"""
Physical Education Class Models

This module defines the database models for physical education classes.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Table, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase

from app.models.physical_education.pe_enums.pe_types import (
    ClassType,
    ClassStatus,
    Subject,
    GradeLevel
)

class PhysicalEducationClass(SharedBase):
    """Model for tracking physical education classes."""
    
    __tablename__ = "physical_education_classes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    class_type = Column(Enum(ClassType, name='class_type_enum'), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    max_students = Column(Integer)
    location = Column(String(100))
    schedule = Column(Text)
    grade_level = Column(Enum(GradeLevel, name='class_grade_level_enum'), nullable=False)
    
    # Enhanced fields for better class management
    curriculum_focus = Column(Text)  # Main focus areas of the curriculum
    assessment_methods = Column(Text)  # Methods used to assess student progress
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships using full module paths to avoid circular imports
    teacher = relationship("app.models.core.user.User", back_populates="physical_education_classes", foreign_keys=[teacher_id], lazy='joined')
    class_students = relationship("app.models.physical_education.class_.models.ClassStudent", back_populates="class_", lazy='joined', overlaps="classes,students")
    # Add students relationship for easier access - go through ClassStudent model
    students = relationship("app.models.physical_education.student.models.Student", 
                          secondary="physical_education_class_students",
                          lazy='joined',
                          overlaps="class_students,classes")
    routines = relationship("app.models.physical_education.class_.models.ClassRoutine", back_populates="class_", lazy='joined')
    regular_routines = relationship("app.models.physical_education.routine.models.Routine", back_populates="class_", lazy='joined')
    adapted_routines = relationship("app.models.activity_adaptation.routine.routine.AdaptedRoutine", back_populates="class_", lazy='joined')
    environmental_checks = relationship("app.models.physical_education.safety.models.EnvironmentalCheck", back_populates="class_", lazy='joined')
    risk_assessments = relationship("app.models.physical_education.safety.models.RiskAssessment", back_populates="class_", lazy='joined')
    safety_checks = relationship("app.models.physical_education.safety.models.SafetyCheck", back_populates="class_", lazy='joined')
    equipment_checks = relationship("app.models.physical_education.safety.models.EquipmentCheck", back_populates="class_", lazy='joined')
    lesson_plans = relationship("app.models.lesson_plan.models.LessonPlan", back_populates="physical_education_class", lazy='joined')
    
    # School relationships
    school_assignments = relationship("app.models.physical_education.schools.relationships.ClassSchoolAssignment", back_populates="pe_class", lazy="select")

class ClassStudent(SharedBase):
    """Model for student enrollment in physical education classes."""
    __tablename__ = "physical_education_class_students"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("physical_education_classes.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    enrollment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(Enum(ClassStatus, name='class_student_status_enum'), nullable=False, default=ClassStatus.ACTIVE)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships using full module paths to avoid circular imports
    class_ = relationship('app.models.physical_education.class_.models.PhysicalEducationClass', back_populates='class_students', overlaps="classes,students")
    student = relationship('app.models.physical_education.student.models.Student', overlaps="classes,students")  # Remove back_populates since we changed the relationship
    
    def __repr__(self):
        return f"<ClassStudent {self.student_id} in class {self.class_id}>"

class ClassRoutine(SharedBase):
    """Model for tracking class routines."""
    
    __tablename__ = "physical_education_class_routines"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("physical_education_classes.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Float)
    sequence = Column(Text)
    equipment_needed = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships using full module path to avoid circular imports
    class_ = relationship("app.models.physical_education.class_.models.PhysicalEducationClass", back_populates="routines", foreign_keys=[class_id], lazy='joined')

    def __repr__(self):
        return f"<ClassRoutine class_id={self.class_id} name={self.name}>"

class ClassCreate(BaseModel):
    """Pydantic model for creating classes."""
    
    name: str
    description: Optional[str] = None
    class_type: ClassType
    teacher_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    max_students: Optional[int] = None
    location: Optional[str] = None
    schedule: Optional[str] = None
    grade_level: str

class ClassUpdate(BaseModel):
    """Pydantic model for updating classes."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    class_type: Optional[ClassType] = None
    teacher_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_students: Optional[int] = None
    location: Optional[str] = None
    schedule: Optional[str] = None
    grade_level: Optional[str] = None

class ClassResponse(BaseModel):
    """Pydantic model for class responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    class_type: ClassType
    teacher_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    max_students: Optional[int] = None
    location: Optional[str] = None
    schedule: Optional[str] = None
    grade_level: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 