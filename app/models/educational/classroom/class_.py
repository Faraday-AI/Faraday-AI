"""Class models for physical education."""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean, Float, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from app.models.core.base import BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin

# Class Type Enums
class ClassStatus(str, Enum):
    """Class status options."""
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class ClassType(str, Enum):
    REGULAR = "regular"
    SPECIAL_NEEDS = "special_needs"
    ADVANCED = "advanced"
    BEGINNER = "beginner"
    ATHLETIC = "athletic"

class EducationalClass(BaseModel, NamedMixin, TimestampedMixin, StatusMixin):
    """Model for educational classes."""
    __tablename__ = "educational_classes"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)
    grade_level = Column(String, nullable=False)
    max_students = Column(Integer, nullable=False)
    schedule = Column(JSON, nullable=False)  # Contains day, time, duration
    location = Column(String, nullable=False)
    class_type = Column(SQLEnum(ClassType, name='class_type_enum'), nullable=True)  # Added for legacy compatibility
    instructor_id = Column(Integer, ForeignKey("educational_teachers.id"), nullable=True)  # Optional
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum(ClassStatus, name='class_status_enum'), nullable=False, default=ClassStatus.PLANNED)

    # Relationships
    students = relationship("EducationalClassStudent", back_populates="class_", cascade="all, delete-orphan", overlaps="student,classes")
    attendance_records = relationship("ClassAttendance", back_populates="class_", cascade="all, delete-orphan", overlaps="class_,attendance_records")
    detailed_schedules = relationship("ClassSchedule", back_populates="class_", cascade="all, delete-orphan", overlaps="class_,detailed_schedules")
    instructor = relationship("app.models.educational.staff.teacher.Teacher", back_populates="classes", overlaps="instructor,classes")  # Optional

    def __repr__(self):
        return f"<EducationalClass {self.name} - {self.grade_level}>"

class ClassAttendance(BaseModel, TimestampedMixin):
    """Model for tracking class attendance."""
    __tablename__ = "class_attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("educational_classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    present = Column(Boolean, nullable=False, default=False)
    notes = Column(String)

    # Relationships
    class_ = relationship("EducationalClass", back_populates="attendance_records", overlaps="class_,attendance_records")
    student = relationship("Student", back_populates="educational_attendance_records", overlaps="student,attendance_records")

    def __repr__(self):
        return f"<ClassAttendance {self.class_id} - {self.student_id} - {self.date}>"

class ClassSchedule(BaseModel, TimestampedMixin):
    """Model for detailed class schedules."""
    __tablename__ = "class_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("educational_classes.id"), nullable=False)
    day_of_week = Column(String, nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    recurring = Column(Boolean, default=True)

    # Relationships
    class_ = relationship("EducationalClass", back_populates="detailed_schedules", overlaps="class_,detailed_schedules")

    def __repr__(self):
        return f"<ClassSchedule {self.class_id} - {self.day_of_week}>" 