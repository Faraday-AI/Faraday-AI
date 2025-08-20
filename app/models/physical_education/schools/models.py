"""
School Models for Multi-School District

This module defines the database models for schools in the district.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from typing import Optional, List

from app.models.shared_base import SharedBase

class SchoolType(str, enum.Enum):
    """Types of schools in the district."""
    ELEMENTARY = "elementary"      # K-5
    MIDDLE = "middle"              # 6-8
    HIGH = "high"                  # 9-12
    K8 = "k8"                      # K-8 (combined)
    K12 = "k12"                    # K-12 (combined)

class SchoolStatus(str, enum.Enum):
    """Status options for schools."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PLANNING = "planning"
    CONSTRUCTION = "construction"
    CLOSED = "closed"

class School(SharedBase):
    """Model for district schools."""
    __tablename__ = 'schools'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    school_code = Column(String(20), unique=True, nullable=False)  # e.g., "LIN-EL", "SPR-MS"
    school_type = Column(Enum(SchoolType, name='school_type_enum'), nullable=False)
    status = Column(Enum(SchoolStatus, name='school_status_enum'), default=SchoolStatus.ACTIVE)
    
    # Address and location
    address = Column(String(300), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False, default="NJ")
    zip_code = Column(String(10), nullable=False)
    phone = Column(String(20))
    email = Column(String(200))
    
    # School characteristics
    principal_name = Column(String(200))
    assistant_principal_name = Column(String(200))
    enrollment_capacity = Column(Integer)
    current_enrollment = Column(Integer, default=0)
    
    # Grade levels served
    min_grade = Column(String(10), nullable=False)  # e.g., "K", "6", "9"
    max_grade = Column(String(10), nullable=False)  # e.g., "5", "8", "12"
    
    # PE program specifics
    pe_department_head = Column(String(200))
    pe_teacher_count = Column(Integer, default=0)
    pe_class_count = Column(Integer, default=0)
    gymnasium_count = Column(Integer, default=1)
    outdoor_facilities = Column(Text)  # e.g., "Football field, Track, Tennis courts"
    
    # Additional information
    description = Column(Text)
    special_programs = Column(Text)  # e.g., "Adaptive PE, Sports Academy, Wellness Program"
    facilities_notes = Column(Text)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Additional data
    additional_data = Column(JSON)  # Additional flexible data
    
    # Relationships
    teacher_assignments = relationship("app.models.physical_education.schools.relationships.TeacherSchoolAssignment", back_populates="school", lazy="select")
    student_enrollments = relationship("app.models.physical_education.schools.relationships.StudentSchoolEnrollment", back_populates="school", lazy="select")
    class_assignments = relationship("app.models.physical_education.schools.relationships.ClassSchoolAssignment", back_populates="school", lazy="select")
    
    def __repr__(self):
        return f"<School {self.name} ({self.school_code})>"
    
    @property
    def grade_range(self) -> str:
        """Get the grade range as a string."""
        return f"{self.min_grade}-{self.max_grade}"
    
    @property
    def is_elementary(self) -> bool:
        """Check if this is an elementary school."""
        return self.school_type == SchoolType.ELEMENTARY
    
    @property
    def is_middle(self) -> bool:
        """Check if this is a middle school."""
        return self.school_type == SchoolType.MIDDLE
    
    @property
    def is_high(self) -> bool:
        """Check if this is a high school."""
        return self.school_type == SchoolType.HIGH

class SchoolFacility(SharedBase):
    """Model for school facilities and equipment."""
    __tablename__ = 'school_facilities'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    facility_name = Column(String(200), nullable=False)
    facility_type = Column(String(100), nullable=False)  # e.g., "Gymnasium", "Field", "Court"
    capacity = Column(Integer)  # Number of students it can accommodate
    description = Column(Text)
    equipment_included = Column(Text)  # Equipment available in this facility
    maintenance_schedule = Column(String(100))
    last_maintenance = Column(DateTime)
    next_maintenance = Column(DateTime)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, MAINTENANCE, OUT_OF_SERVICE
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="facilities")
    
    def __repr__(self):
        return f"<SchoolFacility {self.facility_name} at {self.school.name}>"

# Add facilities relationship to School
School.facilities = relationship("SchoolFacility", back_populates="school", cascade="all, delete-orphan") 