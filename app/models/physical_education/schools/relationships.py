"""
School Relationship Models

This module defines the relationship models for connecting teachers, students, and classes to schools.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from typing import Optional

from app.models.shared_base import SharedBase

class AssignmentStatus(str, enum.Enum):
    """Status options for school assignments."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    TRANSFERRED = "transferred"
    GRADUATED = "graduated"

class TeacherSchoolAssignment(SharedBase):
    """Model for teacher assignments to schools."""
    __tablename__ = 'teacher_school_assignments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    assignment_type = Column(String(100), nullable=False)  # e.g., "Primary", "Secondary", "Substitute"
    grade_levels = Column(Text)  # e.g., "K-2", "3-5", "6-8", "9-12"
    subjects = Column(Text)  # e.g., "Physical Education", "Health", "Sports Science"
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)  # NULL for ongoing assignments
    status = Column(Enum(AssignmentStatus, name='assignment_status_enum'), default=AssignmentStatus.ACTIVE)
    
    # Assignment details
    is_department_head = Column(Boolean, default=False)
    is_lead_teacher = Column(Boolean, default=False)
    responsibilities = Column(Text)  # e.g., "Adaptive PE Coordinator", "Sports Academy Director"
    notes = Column(Text)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = relationship("app.models.core.user.User", back_populates="school_assignments")
    school = relationship("app.models.physical_education.schools.models.School", back_populates="teacher_assignments")
    
    def __repr__(self):
        return f"<TeacherSchoolAssignment {self.teacher_id} at {self.school_id}>"

class StudentSchoolEnrollment(SharedBase):
    """Model for student enrollment in schools."""
    __tablename__ = 'student_school_enrollments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    enrollment_date = Column(DateTime, nullable=False)
    withdrawal_date = Column(DateTime)  # NULL for active enrollments
    grade_level = Column(String(10), nullable=False)  # e.g., "K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"
    academic_year = Column(String(9), nullable=False)  # e.g., "2024-2025"
    status = Column(Enum(AssignmentStatus, name='enrollment_status_enum'), default=AssignmentStatus.ACTIVE)
    
    # Enrollment details
    enrollment_type = Column(String(50), default="REGULAR")  # REGULAR, TRANSFER, NEW, RETURNING
    previous_school = Column(String(200))  # For transfer students
    special_needs = Column(Text)  # Any special accommodations needed
    notes = Column(Text)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="school_enrollments")
    school = relationship("app.models.physical_education.schools.models.School", back_populates="student_enrollments")
    
    def __repr__(self):
        return f"<StudentSchoolEnrollment {self.student_id} at {self.school_id}>"

class ClassSchoolAssignment(SharedBase):
    """Model for PE class assignments to schools."""
    __tablename__ = 'class_school_assignments'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("physical_education_classes.id"), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    academic_year = Column(String(9), nullable=False)  # e.g., "2024-2025"
    semester = Column(String(20))  # e.g., "Fall", "Spring", "Full Year"
    status = Column(Enum(AssignmentStatus, name='class_assignment_status_enum'), default=AssignmentStatus.ACTIVE)
    
    # Assignment details
    room_assignment = Column(String(100))  # e.g., "Gymnasium A", "Field 1", "Weight Room"
    schedule_notes = Column(Text)  # Additional scheduling information
    capacity_override = Column(Integer)  # Override default class capacity for this school
    notes = Column(Text)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pe_class = relationship("app.models.physical_education.class_.models.PhysicalEducationClass", back_populates="school_assignments")
    school = relationship("app.models.physical_education.schools.models.School", back_populates="class_assignments")
    
    def __repr__(self):
        return f"<ClassSchoolAssignment {self.class_id} at {self.school_id}>"

class SchoolAcademicYear(SharedBase):
    """Model for tracking academic years across the district."""
    __tablename__ = 'school_academic_years'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String(9), unique=True, nullable=False)  # e.g., "2024-2025"
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_current = Column(Boolean, default=False)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, PLANNING, COMPLETED, CANCELLED
    
    # Academic year details
    description = Column(Text)
    special_events = Column(Text)  # e.g., "Olympics Week", "Fitness Challenge", "Sports Tournament"
    notes = Column(Text)
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SchoolAcademicYear {self.academic_year}>" 